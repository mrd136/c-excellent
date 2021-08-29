# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime


class ResPartner(models.Model):
    _inherit= "res.partner"

    @api.depends('birthday', 'date_of_death')
    def _get_age(self):
        for rec in self:
            age = ''
            if rec.birthday:
                end_data = rec.date_of_death or fields.Datetime.now()
                delta = relativedelta(end_data, rec.birthday)
                if delta.years <= 2:
                    age = str(delta.years) + _(" Year") + str(delta.months) + _(" Month ") + str(delta.days) + _(" Days")
                else:
                    age = str(delta.years) + _(" Year")
            rec.age = age

    name = fields.Char(tracking=True)
    code = fields.Char(string='Identification Code', default='/',
        help='Identifier provided by the Health Center.', copy=False, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')], string='Gender', required=True, default='male', tracking=True)
    birthday = fields.Date(string='Date of Birth', tracking=True)
    date_of_death = fields.Date(string='Date of Death')
    age = fields.Char(string='Age', compute='_get_age')
    is_referring_doctor = fields.Boolean(string="Is Refereinng Physician")
    hospital_name = fields.Char()
    blood_group = fields.Selection([
        ('A+', 'A+'),('A-', 'A-'),
        ('B+', 'B+'),('B-', 'B-'),
        ('AB+', 'AB+'),('AB-', 'AB-'),
        ('O+', 'O+'),('O-', 'O-')], string='Blood Group')

    is_patient = fields.Boolean(compute='_is_patient', search='_patient_search',
        string='Is Patient', help="Check if customer is linked with patient.")
    # acs_amount_due = fields.Monetary(compute='_compute_acs_amount_due')

    # def _compute_acs_amount_due(self):
    #     MoveLine = self.env['account.move.line']
    #     for record in self:
    #         amount_due = 0
    #         unreconciled_aml_ids = MoveLine.sudo().search([('reconciled', '=', False),
    #            ('account_id.deprecated', '=', False),
    #            ('account_id.internal_type', '=', 'receivable'),
    #            ('move_id.state', '=', 'posted'),
    #            ('partner_id', '=', record.id),
    #            ('company_id','=',self.env.company.id)])
    #         for aml in unreconciled_aml_ids:
    #             amount_due += aml.amount_residual
    #         record.acs_amount_due = amount_due

    def _is_patient(self):
        Patient = self.env['hms.patient'].sudo()
        for rec in self:
            patient = Patient.search([('partner_id', '=', rec.id)], limit=1)
            rec.is_patient = True if patient else False

    def _patient_search(self, operator, value):
        patients = self.env['hms.patient'].sudo().search([])
        return [('id', 'in', patients.mapped('partner_id').ids)]


class ResUsers(models.Model):
    _inherit= "res.users"

    @api.depends('physician_ids')
    def _compute_physician_count(self):
        for user in self.with_context(active_test=False):
            user.physician_count = len(user.physician_ids)

    def _compute_patient_count(self):
        Patient = self.env['hms.patient']
        for user in self.with_context(active_test=False):
            user.patient_count = Patient.search_count([('partner_id','=', user.partner_id.id)])

    # department_ids = fields.Many2many('hr.department', 'user_department_rel', 'user_id','department_id',
    #     domain=[('patient_depatment', '=', True)], string='Departments')
    physician_count = fields.Integer(string="#Physician", compute="_compute_physician_count")
    physician_ids = fields.One2many('hms.physician', 'user_id', string='Related Physician')
    patient_count = fields.Integer(string="#Patient", compute="_compute_patient_count")

    def action_create_physician(self):
        self.ensure_one()
        self.env['hms.physician'].create({
            'user_id': self.id,
            'name': self.name,
        })

    def action_create_patient(self):
        self.ensure_one()
        self.env['hms.patient'].create({
            'partner_id': self.partner_id.id,
            'name': self.name,
        })


# class HospitalDepartment(models.Model):
#     _inherit = 'hr.department'
#
#     note = fields.Text('Note')
#     #ACS: TYPO instead of department it is depatment
#     patient_depatment = fields.Boolean("Patient Department", default=True)
#     #   = fields.One2many("hms.appointment", "department_id", "Appointments")


class ACSEthnicity(models.Model):
    _description = "Ethnicity"
    _name = 'acs.ethnicity'

    name = fields.Char(string='Name', required=True ,translate=True)
    code = fields.Char(string='Code')
    notes = fields.Char(string='Notes')

    _sql_constraints = [('name_uniq', 'UNIQUE(name)', 'Name must be unique!')]


# class ACSMedicalAlert(models.Model):
#     _name = 'acs.medical.alert'
#     _description = "Medical Alert for Patient"
#
#     name = fields.Char(required=True)
#     description = fields.Text('Description')


# class HrEmployeePublic(models.Model):
#     _inherit = 'hr.employee.public'
#
#     birthday = fields.Date('Date of Birth', tracking=True)


class ACSFamilyRelation(models.Model):
    _name = 'acs.family.relation'
    _description = "Family Relation"
    _order = "sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    inverse_relation_id = fields.Many2one("acs.family.relation", string="Inverse Relation")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name 
            if rec.inverse_relation_id:
                name += ' - ' + rec.inverse_relation_id.name
            result.append((rec.id, name))
        return result

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Relation must be unique!')
    ]

    def manage_inverser_relation(self):
        for rec in self:
            if rec.inverse_relation_id and not rec.inverse_relation_id.inverse_relation_id:
                rec.inverse_relation_id.inverse_relation_id = rec.id

    @api.model
    def create(self, values):
        res = super(ACSFamilyRelation, self).create(values)
        res.manage_inverser_relation()
        return res

    def write(self, values):
        res = super(ACSFamilyRelation, self).write(values)
        self.manage_inverser_relation()
        return res