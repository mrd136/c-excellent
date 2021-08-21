# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class Referral(models.Model):
    _name = 'hms.referral'
    _description = "Referral"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']
    _order = "id desc"

    @api.depends('height', 'weight')
    def get_bmi_data(self):
        for rec in self:
            bmi = 0
            bmi_state = False
            if rec.height and rec.weight:
                try:
                    bmi = float(rec.weight) / ((float(rec.height) / 100) ** 2)
                except:
                    bmi = 0

                bmi_state = 'normal'
                if bmi < 18.5:
                    bmi_state = 'low_weight'
                elif 25 < bmi < 30:
                    bmi_state = 'over_weight'
                elif bmi > 30:
                    bmi_state = 'obesity'
            rec.bmi = bmi
            rec.bmi_state = bmi_state

    @api.depends('patient_id', 'patient_id.birthday', 'date')
    def get_patient_age(self):
        for rec in self:
            age = ''
            if rec.patient_id.birthday:
                end_data = rec.date or fields.Datetime.now()
                delta = relativedelta(end_data, rec.patient_id.birthday)
                if delta.years <= 2:
                    age = str(delta.years) + _(" Year") + str(delta.months) + _(" Month ") + str(delta.days) + _(
                        " Days")
                else:
                    age = str(delta.years) + _(" Year")
            rec.age = age

    READONLY_STATES = {'reject': [('readonly', True)], 'accept': [('readonly', True)], 'waiting': [('readonly', True)],
                       'requested': [('readonly', True)],
                       'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Referral Id', copy=False, tracking=True, states=READONLY_STATES)
    patient_id = fields.Many2one('hms.patient', ondelete='restrict', string='Patient',
                                 required=True, index=True, help='Patient Name', states=READONLY_STATES, tracking=True)
    image_128 = fields.Binary(related='patient_id.image_128', string='Image', readonly=True)
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Physician',
                                   index=True, help='Physician\'s Name', states=READONLY_STATES, tracking=True)
    department_id = fields.Many2one('hr.department', ondelete='restrict',
                                    domain=[('patient_depatment', '=', True)], string='Department', tracking=True,
                                    states=READONLY_STATES)
    service_id = fields.Many2one('hms.referral.service', string='Service', tracking=True,
                                 states=READONLY_STATES)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, states=READONLY_STATES, tracking=True)
    appointment_id = fields.Many2one("hms.appointment", 'Appointment', states=READONLY_STATES)
    weight = fields.Float(string="Weight")
    height = fields.Float(string="Height")
    temp = fields.Char(string="temp")
    hr = fields.Char(string="hr")
    rr = fields.Char(string="rr")
    bp = fields.Char(string="bp")
    spo2 = fields.Char(string="spo2")
    bmi = fields.Float(compute="get_bmi_data", string='Body Mass Index', store=True)
    bmi_state = fields.Selection([
        ('low_weight', 'Low Weight'),
        ('normal', 'Normal'),
        ('over_weight', 'Over Weight'),
        ('obesity', 'Obesity')], compute="get_bmi_data", string='BMI State', store=True)
    differencial_diagnosis = fields.Text(string="differencial_diagnosis", states=READONLY_STATES)
    present_illness = fields.Text(string="present_illness", states=READONLY_STATES)
    lab_report = fields.Text(string='Lab Report', states=READONLY_STATES, help="Details of the lab report.")
    radiological_report = fields.Text(string='Radiological Report', states=READONLY_STATES,
                                      help="Details of the Radiological Report")
    past_history = fields.Text(string='Past History', states=READONLY_STATES, help="Past history of any diseases.")
    urgency = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string='Urgency Level',
                               default='1', states=READONLY_STATES)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('waiting', 'Waiting For Accept'),
        ('accept', 'Accepted'),
        ('waiting_ar', 'Waiting For Patient Arrival'),
        ('arrival', 'Confirmation of patient arrival'),
        ('reject', 'Rejected'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string=' State', default='draft', required=True, copy=False, tracking=True,
        states=READONLY_STATES)
    age = fields.Char(compute="get_patient_age", string='Age', store=True,
                      help="Computed patient age at the moment of the evaluation")
    company_id = fields.Many2one('res.company', ondelete='restrict', states=READONLY_STATES,
                                 string='Hospital', default=lambda self: self.env.user.company_id.id)
    referral_type = fields.Selection([('center', 'To Health center'), ('hospital', 'To General Hospital'),
                                      ('specialty', 'To Specialty Hospital')], string='Referral Type',
                                     required=True, default='hospital', states=READONLY_STATES)
    from_hospital_id = fields.Many2one('operating.unit', ondelete='restrict', states=READONLY_STATES,
                                       string='From Hospital',
                                       default=lambda self: self.env.user.default_operating_unit_id.id)
    to_hospital_id = fields.Many2one('operating.unit', ondelete='restrict', states=READONLY_STATES,
                                     string='To Hospital')
    diseas_id = fields.Many2one('hms.diseases', 'Disease', states=READONLY_STATES)
    medical_history = fields.Text(related='patient_id.medical_history',
                                  string="Past Medical History", readonly=True)
    patient_diseases = fields.One2many('hms.patient.disease',
                                       related='patient_id.patient_diseases', string='Diseases',
                                       help='Mark if the patient has died', readonly=True)
    responsible_id = fields.Many2one('hms.physician', "Responsible Jr. Doctor", states=READONLY_STATES)
    notes = fields.Text(string='Notes', states=READONLY_STATES)
    referral_reason = fields.Text(string="Referral Reason", states=READONLY_STATES)
    current_is_accept_user = fields.Boolean(compute='is_accept_user', string='Accept User')
    requested_date = fields.Datetime('Requested Date', states=READONLY_STATES)
    accept_date = fields.Datetime('Accept/Reject Date', states=READONLY_STATES)
    arrival_date = fields.Datetime('Patient Arrival Date', states=READONLY_STATES)
    waiting_duration = fields.Float('Wait Time', readonly=True)
    arrival_duration = fields.Float('Patient Arrival Duration', readonly=True)
    source_id = fields.Many2one('hms.multi.referral', 'Source')
    hospital_action = fields.Selection([
        ('hypnotize', 'Hypnotize the patient'), ('go', 'Go Home'),
        ('loss', 'Patient life loss')], string='Patient State')

    @api.onchange('from_hospital_id', 'referral_type')
    def onchange_referral_type(self):
        """to get just all operation unit expect from hos"""
        if self.referral_type == 'center':
            self.to_hospital_id = self.env['operating.unit'].search([('type', '=', 'center'),
                                                                     ('parent_id', '=', self.from_hospital_id.id)]).id
        elif self.referral_type == 'specialty':
            domain = [('id', 'in',
                       self.env['operating.unit'].search([('type', '=', 'hospital'), ('specialty_hospital', '=', True),
                                                          ('id', '!=', self.from_hospital_id.id)]).ids)]
            domain = {'domain': {'to_hospital_id': domain}}
            # if self.from_hospital_id.specialty_hospital:
            #     raise UserError(_('You can not referral from Specialty Hospital To Specialty Hospital'))
            # self.to_hospital_id = self.env['operating.unit'].search([('specialty_hospital', '=', True)]).id
        elif self.referral_type == 'hospital':
            domain = [('id', 'in',
                       self.env['operating.unit'].search([('type', '=', 'hospital'), ('specialty_hospital', '=', False),
                                                          ('id', '!=', self.from_hospital_id.id)]).ids)]
            domain = {'domain': {'to_hospital_id': domain}}
            return domain

    def is_accept_user(self):
        for rec in self:
            rec.current_is_accept_user = False
            user_id = rec.to_hospital_id.referral_coordinator_ids.filtered(lambda v: v.id == self.env.uid)
            if user_id:
                rec.current_is_accept_user = True

    # def action_create_appointment(self):
    #     dic = {
    #         'diseas_id': self.diseas_id.id,
    #         'state': 'draft',
    #         'patient_id': self.patient_id.id,
    #         'urgency': self.urgency,
    #         'past_history': self.past_history,
    #         'radiological_report': self.radiological_report,
    #         'lab_report': self.lab_report,
    #         'present_illness': self.present_illness,
    #         'differencial_diagnosis': self.differencial_diagnosis,
    #         'spo2': self.spo2,
    #         'bp': self.bp,
    #         'rr': self.rr,
    #         'hr': self.hr,
    #         'temp': self.temp,
    #         'height': self.height,
    #         'weight': self.weight,
    #     }
    #     self.env['hms.appointment'].create(dic)

    def action_requested(self):
        self.state = 'requested'

    def action_waiting(self):
        if self.service_id.is_emergency:
            self.state = 'waiting_ar'
        elif self.service_id.is_obstetrics:
            self.state = 'waiting'
        elif self.from_hospital_id.specialty_hospital:
            self.state = 'waiting_ar'
        else:
            self.state = 'waiting'
        self.requested_date = datetime.now()

    def action_arrival(self):
        self.state = 'arrival'
        datetime_diff = datetime.now() - self.requested_date
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        self.arrival_duration = float(('%0*d') % (2, h) + '.' + ('%0*d') % (2, m * 1.677966102))
        self.arrival_date = datetime.now()

    def action_accept(self):
        self.state = 'accept'
        if self.source_id:
            for referral in self.source_id.referral_ids.filtered(lambda v: v.id != self.id):
                referral.action_cancel()
                self.source_id.state = 'done'
        datetime_diff = datetime.now() - self.requested_date
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        self.waiting_duration = float(('%0*d') % (2, h) + '.' + ('%0*d') % (2, m * 1.677966102))
        self.accept_date = datetime.now()

    def action_reject(self):
        self.state = 'reject'
        datetime_diff = datetime.now() - self.requested_date
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        self.waiting_duration = float(('%0*d') % (2, h) + '.' + ('%0*d') % (2, m * 1.677966102))
        self.accept_date = datetime.now()

    def action_done(self):
        self.state = 'done'
        # self.action_create_appointment()

    def action_cancel(self):
        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, values):
        if values.get('appointment_id'):
            appointment_id = self.env['hms.appointment'].browse(values.get('appointment_id'))
            appointment_id.state = 'referral'
        if not values.get('name'):
            values['name'] = self.env['ir.sequence'].next_by_code('hms.referral')
        return super(Referral, self).create(values)

    def unlink(self):
        for data in self:
            if data.state in ['done']:
                raise UserError(_('You can not delete record in done state'))
        return super(Referral, self).unlink()


class MultiReferral(models.Model):
    # _inherit = "hms.referral"
    _name = 'hms.multi.referral'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']

    name = fields.Char(string='Multi Referral Id', copy=False, tracking=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, tracking=True)
    patient_id = fields.Many2one('hms.patient', ondelete='restrict', string='Patient',
                                 required=True, index=True, help='Patient Name')
    image_128 = fields.Binary(related='patient_id.image_128', string='Image', readonly=True)
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Physician',
                                   index=True, help='Physician\'s Name', tracking=True)
    department_id = fields.Many2one('hr.department', ondelete='restrict',
                                    domain=[('patient_depatment', '=', True)], string='Department', tracking=True)
    service_id = fields.Many2one('hms.referral.service', string='Service', tracking=True)
    from_hospital_id = fields.Many2one('operating.unit', ondelete='restrict',
                                       string='From Hospital',
                                       default=lambda self: self.env.user.default_operating_unit_id.id)
    to_hospital_ids = fields.Many2many('operating.unit', ondelete='restrict', string='To Hospital')
    diseas_id = fields.Many2one('hms.diseases', 'Disease')
    differencial_diagnosis = fields.Text(string="differencial_diagnosis")
    present_illness = fields.Text(string="present_illness")
    lab_report = fields.Text(string='Lab Report', help="Details of the lab report.")
    radiological_report = fields.Text(string='Radiological Report', help="Details of the Radiological Report")
    past_history = fields.Text(string='Past History', help="Past history of any diseases.")
    referral_ids = fields.One2many('hms.referral', 'source_id', string='Diseases', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('done', 'Done'), ('cancel', 'Cancelled')]
                             , string=' State', default='draft', required=True, copy=False, tracking=True)
    urgency = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string='Urgency Level',
                               default='1')
    referral_reason = fields.Text(string="Referral Reason")

    @api.onchange('from_hospital_id', 'referral_type')
    def onchange_referral_type(self):
        """to get just all operation unit expect from hos"""
        domain = [('id', 'in',
                   self.env['operating.unit'].search([('type', '=', 'hospital'),
                                                      ('id', '!=', self.from_hospital_id.id)]).ids)]
        domain = {'domain': {'to_hospital_ids': domain}}
        return domain

    @api.model
    def create(self, values):
        if not values.get('name'):
            values['name'] = self.env['ir.sequence'].next_by_code('hms.multi.referral')
        return super(MultiReferral, self).create(values)

    def action_requested(self):
        self.state = 'requested'
        self.action_create_referral()

    def action_cancel(self):
        self.state = 'cancel'

    def action_create_referral(self):
        for unit in self.to_hospital_ids:
            dic = {'to_hospital_id': unit.id,
                   'patient_id': self.patient_id.id,
                   'state': 'waiting',
                   'physician_id': self.physician_id.id,
                   'urgency': self.urgency,
                   'department_id': self.department_id.id,
                   'radiological_report': self.radiological_report,
                   'lab_report': self.lab_report,
                   'present_illness': self.present_illness,
                   'differencial_diagnosis': self.differencial_diagnosis,
                   'service_id': self.service_id.id,
                   'from_hospital_id': self.from_hospital_id.id,
                   'diseas_id': self.diseas_id.id,
                   'past_history': self.past_history,
                   'source_id': self.id,
                   'requested_date': datetime.now()
                   }
            self.env['hms.referral'].create(dic)

