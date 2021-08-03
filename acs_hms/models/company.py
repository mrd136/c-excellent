# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _description = "Hospital"
    _inherit = "res.company"

    patient_registration_product_id = fields.Many2one('product.product', 
        domain=[('type','=','service')],
        string='Patient Registration Invoice Product', 
        ondelete='cascade', help='Registration Product')
    treatment_registration_product_id = fields.Many2one('product.product', 
        domain=[('type','=','service')],
        string='Treatment Registration Invoice Product', 
        ondelete='cascade', help='Registration Product')
    consultation_product_id = fields.Many2one('product.product', 
        domain=[('type','=','service')],
        string='Consultation Invoice Product', 
        ondelete='cascade', help='Consultation Product')
    followup_days = fields.Float('Followup Days', default=30)
    followup_product_id = fields.Many2one('product.product', 
        domain=[('type','=','service')],
        string='Follow-up Invoice Product', 
        ondelete='cascade', help='Followup Product')
    birthday_mail_template = fields.Many2one('mail.template', 'Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.")
    registration_date = fields.Char(string='Date of Registration')
    appointment_anytime_invoice = fields.Boolean("Allow Invoice Anytime in Appointment")
    appo_invoice_advance = fields.Boolean("Invoice before Confirmation in Appointment")
    appointment_usage_location = fields.Many2one('stock.location', 
        string='Usage Location for Consumed Products in Appointment')
    appointment_stock_location = fields.Many2one('stock.location', 
        string='Stock Location for Consumed Products in Appointment')
    