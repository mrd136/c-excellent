# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PhysicianSpecialty(models.Model):
    _name = 'physician.specialty'
    _description = "Physician Specialty"

    code = fields.Char(string='Code')
    name = fields.Char(string='Specialty', required=True, translate=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class PhysicianDegree(models.Model):
    _name = 'physician.degree'
    _description = "Physician Degree"

    name = fields.Char(string='Degree')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class Physician(models.Model):
    _name = 'hms.physician'
    _description = "Physician"
    _inherits = {'res.users': 'user_id'}


    def _treatment_count(self):
        for record in self:
            Count=self.env['hms.treatment'].search_count([('physician_id', '=', record.id)])
            record.treatment_count=Count

    def _appointment_count(self):
        for record in self:
            Count=self.env['hms.appointment'].search_count([('physician_id', '=', record.id)])
            record.appointment_count=Count

    def _prescription_count(self):
        for record in self:
            Count=self.env['prescription.order'].search_count([('physician_id', '=', record.id)])
            record.prescription_count=Count

    user_id = fields.Many2one('res.users',string='Related User', required=True,
        ondelete='cascade', help='User-related data of the physician')
    code = fields.Char(string='Physician ID', default='/', tracking=True)
    degree_ids = fields.Many2many('physician.degree', 'physician_rel_education', 'physician_ids','degree_ids', string='Degree')
    specialty = fields.Many2one('physician.specialty', ondelete='set null', string='Specialty', help='Specialty Code', tracking=True)
    #ACS14: can be renamed to Medical License
    government_id = fields.Char(string='Government ID', tracking=True)
    consul_service = fields.Many2one('product.product', ondelete='restrict', string='Consultation Service')
    followup_service = fields.Many2one('product.product', ondelete='restrict', string='Followup Service')
    is_primary_surgeon = fields.Boolean(string='Primary Surgeon')
    is_consultation_doctor = fields.Boolean(string='Consultation Physician')
    signature = fields.Binary('Signature')
    hr_presence_state = fields.Selection(related='user_id.employee_id.hr_presence_state')
    appointment_ids = fields.One2many("hms.appointment", "physician_id", "Appointments")

    treatment_count = fields.Integer(compute='_treatment_count', string='# Treatments')
    appointment_count = fields.Integer(compute='_appointment_count', string='# Appointment')
    prescription_count = fields.Integer(compute='_prescription_count', string='# Prescriptions')
    

    @api.model
    def create(self, values):
        if values.get('code','/') == '/':
            values['code'] = self.env['ir.sequence'].next_by_code('hms.physician')
        if values.get('email'):
            values['login'] = values['email']
        return super(Physician, self).create(values)

    def action_treatment(self):
        action = self.env.ref('acs_hms.acs_action_form_hospital_treatment').read()[0]
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_appointment(self):
        action = self.env.ref('acs_hms.action_appointment').read()[0]
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_prescription(self):
        action = self.env.ref('acs_hms.act_open_hms_prescription_order_view').read()[0]
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    