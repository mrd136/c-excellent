# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from odoo.addons.ehcs_qr_code_base.models.qr_code_base import generate_qr_code


class QRCodeInvoice(models.Model):
    _inherit = 'account.move'

    qr_image = fields.Binary("QR Code")
    qr_in_report = fields.Boolean('Show QR in Report')

    def _generate_qr_code(self):
        # base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        # base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        # text = 'Ref : %s \n Total : %s ' % (self.name, self.amount_total)

        customer_name = ""
        customer_vat = ""
        if self.type in ('out_invoice', 'out_refund'):
            sellername = str(self.company_id.name)
            seller_vat_no = self.company_id.vat or ''
            if self.partner_id.company_type == 'company':
                customer_name = self.partner_id.name
                customer_vat = self.partner_id.vat

        else:
            sellername = str(self.partner_id.name)
            seller_vat_no = self.partner_id.vat
            customer_name = self.company_id.name
            customer_vat = self.company_id.vat

        qr_code = ' \n Seller Name: ' + sellername
        qr_code += ' \n Seller VAT NO.: ' + seller_vat_no if seller_vat_no else ' '
        qr_code += ' \n Date: ' + str(self.invoice_date) if self.invoice_date else str(self.create_date)
        qr_code += ' \n Total Tax: ' + str(self.amount_tax)
        qr_code += ' \n Total Amount: ' + str(self.amount_total)
        if customer_name:
            qr_code += ' \n Customer Name: ' + customer_name
        if customer_vat:
            qr_code += ' \n Customer Vat: ' + customer_vat
        self.qr_image = generate_qr_code(qr_code)

    def action_post(self):
        res = super(QRCodeInvoice, self).action_post()
        self._generate_qr_code()
