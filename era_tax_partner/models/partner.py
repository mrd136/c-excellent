# -*- coding: utf-8 -*-
from odoo import models, api, _

class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res

    def get_qr_code_data(self):
        customer_name = ""
        customer_vat = ""
        if self.move_type in ('out_invoice', 'out_refund'):
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

        qr_code = " Seller Name: " + sellername
        qr_code += " Seller VAT NO.: " + seller_vat_no if seller_vat_no else " "
        qr_code += " | Date: " + str(self.invoice_date) if self.invoice_date else str(self.create_date)
        qr_code += " | Total Tax: " + str(self.amount_tax)
        qr_code += " | Total Amount: " + str(self.amount_total)
        if customer_name:
            qr_code += " | Customer Name: " + customer_name
        if customer_vat:
            qr_code += " | Customer Vat: " + customer_vat
        # print(qr_code)
        return qr_code


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res

