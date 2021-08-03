# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PatientLabTest(models.Model):
    _name = "patient.laboratory.test"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']
    _description = "Patient Laboratory Test"
    _order = 'date_analysis desc, id desc'

    STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    def _acs_attachemnt_count(self):
        AttachmentObj = self.env['ir.attachment']
        for rec in self:
            attachments = AttachmentObj.search([
                ('res_model', '=', self._name),
                ('res_id', '=', rec.id)])
            rec.attachment_ids = [(6,0,attachments.ids)]
            rec.attach_count = len(attachments.ids)

    attach_count = fields.Integer(compute="_acs_attachemnt_count", readonly=True, string="Documents")
    attachment_ids = fields.Many2many('ir.attachment', 'attachment_laboratory_rel', 'laboratory_id', 'attachment_id', compute="_acs_attachemnt_count", string="Attachments")

    name = fields.Char(string='Test ID', help="Lab result ID", readonly="1",copy=False, index=True, tracking=True)
    test_id = fields.Many2one('acs.lab.test', string='Test', required=True, ondelete='restrict', states=STATES, tracking=True)
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, ondelete='restrict', states=STATES, tracking=True)
    user_id = fields.Many2one('res.users',string='Responsible User', default=lambda self: self.env.user, states=STATES)
    physician_id = fields.Many2one('hms.physician',string='Prescribing Doctor', help="Doctor who requested the test", ondelete='restrict', states=STATES)
    diagnosis = fields.Text(string='Diagnosis', states=STATES)
    critearea_ids = fields.One2many('lab.test.critearea', 'patient_lab_id', string='Test Cases', copy=True, states=STATES)
    date_requested = fields.Datetime(string='Request Date', states=STATES)
    date_analysis = fields.Date(string='Test Date', default=fields.Date.context_today, states=STATES)
    request_id = fields.Many2one('acs.laboratory.request', string='Lab Request', ondelete='restrict', states=STATES)
    laboratory_id = fields.Many2one('acs.laboratory', related="request_id.laboratory_id", string='Laboratory', readonly=True, store=True)
    report = fields.Text(string='Test Report', states=STATES)
    note = fields.Text(string='Extra Info', states=STATES)
    hospitalization_id = fields.Many2one('acs.hospitalization', string='Hospitalization', ondelete='restrict', states=STATES)
    print_in_discharge = fields.Boolean("Print in Discharge Report")
    appointment_id = fields.Many2one('hms.appointment', string='Appointment', ondelete='restrict', states=STATES)
    treatment_id = fields.Many2one('hms.treatment', string='Treatment', ondelete='restrict', states=STATES)
    sample_ids = fields.Many2many('acs.patient.laboratory.sample', 'test_lab_sample_rel', 'test_id', 'sample_id', string='Test Samples', states=STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company',default=lambda self: self.env.user.company_id.id, states=STATES)
    state = fields.Selection([
        ('draft','Draft'),
        ('done','Done'),
        ('cancel','Cancel'),
    ], string='State',readonly=True, default='draft', tracking=True)
    consumable_line_ids = fields.One2many('hms.consumable.line', 'patient_lab_test_id',
        string='Consumable Line', states=STATES)

    _sql_constraints = [
        ('name_company_uniq', 'unique (name,company_id)', 'Test Name must be unique per company !')
    ]

    def action_view_attachments(self):
        self.ensure_one()
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('id', 'in', self.attachment_ids.ids)]
        action['context'] = {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_is_document': True}
        return action

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('patient.laboratory.test')
        return super(PatientLabTest, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_("Lab Test can be delete only in Draft state."))
        return super(PatientLabTest, self).unlink()

    @api.onchange('request_id')
    def onchange_request_id(self):
        if self.request_id and self.request_id.date:
            self.requested_date = self.request_id.date

    @api.onchange('test_id')
    def on_change_test(self):
        test_lines = []
        if self.test_id:
            gender = self.patient_id.gender
            self.results = self.test_id.description
            for line in self.test_id.critearea_ids:
                test_lines.append((0,0,{
                    'sequence': line.sequence,
                    'name': line.name,
                    'normal_range': line.normal_range_female if gender=='female' else line.normal_range_male,
                    #'result': line.result,
                    'uom_id': line.uom_id and line.uom_id.id or False,
                    'lab_uom_id': line.lab_uom_id and line.lab_uom_id.id or False,
                    'remark': line.remark,
                }))
            self.critearea = test_lines

    def action_done(self):
        self.consume_lab_material()
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def consume_lab_material(self):
        for rec in self:
            if not rec.company_id.laboratory_usage_location:
                raise UserError(_('Please define a location where the consumables will be used during the Laboratory test in company.'))
            if not rec.company_id.laboratory_stock_location:
                raise UserError(_('Please define a Laboratory location from where the consumables will be taken.'))
 
            dest_location_id  = rec.company_id.laboratory_usage_location.id
            source_location_id  = rec.company_id.laboratory_stock_location.id
            for line in rec.consumable_line_ids.filtered(lambda s: not s.move_id):
                move = self.consume_material(source_location_id, dest_location_id,
                    {
                        'product': line.product_id,
                        'qty': line.qty,
                    })
                move.laboratory_id = rec.id
                line.move_id = move.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: