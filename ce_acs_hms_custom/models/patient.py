# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_
from odoo.exceptions import UserError
from datetime import datetime
from odoo.osv import expression


class ACSPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='restrict')
    gov_code = fields.Char(string='Government Identity', copy=False, tracking=True)
    marital_status = fields.Selection([
        ('single', 'Single'), 
        ('married', 'Married')], string='Marital Status', default="single")
    is_corpo_tieup = fields.Boolean(string='Corporate Tie-Up', 
        help="If not checked, these Corporate Tie-Up Group will not be visible at all.")
    corpo_company_id = fields.Many2one('res.partner', string='Corporate Company', 
        domain="[('is_company', '=', True)]", ondelete='restrict')
    emp_code = fields.Char(string='Employee Code')
    user_id = fields.Many2one('res.users', string='Related User', ondelete='cascade', 
        help='User-related data of the patient')
    primary_doctor = fields.Many2one('hms.physician', 'Physician')
    ref_doctor = fields.Many2many('res.partner', 'rel_doc_pat', 'doc_id', 
        'patient_id', 'Referring Doctors', domain=[('is_referring_doctor','=',True)])
    #ACS NOTE: CAN BE deleted?
    hospitalized = fields.Boolean()
    discharged = fields.Boolean()
    #Diseases
    medical_history = fields.Text(string="Past Medical History")
    patient_diseases = fields.One2many('hms.patient.disease', 'patient_id', string='Diseases')
    #Family Form Tab
    genetic_risks = fields.One2many('hms.patient.genetic.risk', 'patient_id', 'Genetic Risks')
    family_history = fields.One2many('hms.patient.family.diseases', 'patient_id', 'Family Diseases History')
    ethnic_group = fields.Many2one('acs.ethnicity', string='Ethnic group')
    cod = fields.Many2one('hms.diseases', string='Cause of Death')
    family_member_ids = fields.One2many('acs.family.member', 'patient_id', string='Family')
    occupation = fields.Char("Occupation")
    religion = fields.Char("Religion")
    caste = fields.Char("Tribe")
    nationality = fields.Selection([('saudi', 'Saudi'), ('non', 'Non Saudis'),
                                    ('unknown', 'Unknown Patient')], default='saudi', required=True, string="Nationality")

    age = fields.Char(string='Age')
    # is_unknown_patient = fields.Boolean('Is Unknown Patient?')
    # is_saudi = fields.Boolean('Is a Saudi?')

    @api.model
    def create(self, values):
        if values.get('code','/')=='/':
            values['code'] = self.env['ir.sequence'].next_by_code('hms.patient') or ''
        # values['customer_rank'] = True
        return super(ACSPatient, self).create(values)

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    @api.model
    def send_birthday_email(self):
        wish_template_id = self.env.ref('acs_hms.email_template_birthday_wish', raise_if_not_found=False)
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        patient_ids = self.search([('birthday', 'like', today_month_day)])
        for patient_id in patient_ids:
            if patient_id.email:
                wish_temp = patient_id.company_id.birthday_mail_template or wish_template_id
                wish_temp.sudo().send_mail(patient_id.id, force_send=True)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            criteria_operator = ['|'] if operator not in expression.NEGATIVE_TERM_OPERATORS else ['&', '!']
            domain = criteria_operator + ['|', ('gov_code', '=ilike', name + '%'), ('code', '=ilike', name + '%'), ('name', operator, name)]
        group_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(group_ids).with_user(name_get_uid))


class ACSFamilyMember(models.Model):
    _name = 'acs.family.member'
    _description= 'Family Member'

    #ACS14: Remove member field as added new related_patient_id
    member = fields.Many2one('res.partner', string='Member', help='Family Member Name')
    role = fields.Char(string='Old Relation')

    related_patient_id = fields.Many2one('hms.patient', string='Family Member', help='Family Member Name', required=True)    
    patient_id = fields.Many2one('hms.patient', string='Patient')
    relation_id = fields.Many2one('acs.family.relation', string='Relation', required=True)
    inverse_relation_id = fields.Many2one("acs.family.member", string="Inverse Relation")

    def create(self, values):
        res = super(ACSFamilyMember, self).create(values)
        if not res.inverse_relation_id and res.relation_id.inverse_relation_id:
            inverse_relation_id = self.create({
                'inverse_relation_id': res.id,
                'relation_id': res.relation_id.inverse_relation_id.id,
                'patient_id': res.related_patient_id.id,
                'related_patient_id': res.patient_id.id,
            })
            res.inverse_relation_id = inverse_relation_id.id
        return res

    def unlink(self):
        inverse_relation_id = self.mapped('inverse_relation_id')
        res = super(ACSFamilyMember, self).unlink()
        if inverse_relation_id:
            inverse_relation_id.unlink()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: