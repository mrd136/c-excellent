# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    patient_registration_product_id = fields.Many2one('product.product', 
        related='company_id.patient_registration_product_id',
        domain=[('type','=','service')],
        string='Patient Registration Invoice Product', 
        ondelete='cascade', help='Registration Product', readonly=False)
    treatment_registration_product_id = fields.Many2one('product.product', 
        related='company_id.treatment_registration_product_id',
        domain=[('type','=','service')],
        string='Treatment Registration Invoice Product', 
        ondelete='cascade', help='Registration Product', readonly=False)
    consultation_product_id = fields.Many2one('product.product', 
        related='company_id.consultation_product_id',
        domain=[('type','=','service')],
        string='Consultation Invoice Product', 
        ondelete='cascade', help='Consultation Product', readonly=False)
    followup_days = fields.Float('Followup Days', related='company_id.followup_days', default=30, readonly=False)
    followup_product_id = fields.Many2one('product.product', 
        related='company_id.followup_product_id',
        domain=[('type','=','service')],
        string='Follow-up Invoice Product', 
        ondelete='cascade', help='Followup Product', readonly=False)
    birthday_mail_template = fields.Many2one('mail.template', 
        related='company_id.birthday_mail_template',
        string='Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.", readonly=False)
    registration_date = fields.Char(related='company_id.registration_date', string='Date of Registration', readonly=False)
    appointment_anytime_invoice = fields.Boolean(related='company_id.appointment_anytime_invoice', string="Allow Invoice Anytime in Appointment", readonly=False)
    appo_invoice_advance = fields.Boolean(related='company_id.appo_invoice_advance', string="Invoice before Confirmation in Appointment", readonly=False)
    appointment_usage_location = fields.Many2one('stock.location', 
        related='company_id.appointment_usage_location',
        domain=[('usage','=','customer')],
        string='Usage Location for Consumed Products in Appointment', readonly=False)
    appointment_stock_location = fields.Many2one('stock.location', 
        related='company_id.appointment_stock_location',
        domain=[('usage','=','internal')],
        string='Stock Location for Consumed Products in Appointment', readonly=False)
    group_patient_registartion_invoicing = fields.Boolean("Patient Registration Invoicing", implied_group='acs_hms.group_patient_registartion_invoicing')
    group_treatment_invoicing = fields.Boolean("Treatment Invoicing", implied_group='acs_hms.group_treatment_invoicing')

    @api.onchange('appointment_anytime_invoice')
    def onchnage_appointment_anytime_invoice(self):
        if self.appointment_anytime_invoice:
            self.appo_invoice_advance = False

    @api.onchange('appo_invoice_advance')
    def onchnage_appo_invoice_advance(self):
        if self.appo_invoice_advance:
            self.appointment_anytime_invoice = False
