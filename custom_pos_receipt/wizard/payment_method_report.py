from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class ReportSaleDetails(models.AbstractModel):

    _name = 'report.custom_pos_receipt.payment_method_report'
    _description = 'Payment Method Report'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_id=False):
        img = self.env['pos.config'].search([('id', '=', config_id)]).image
        if not img:
            img = self.env.company.logo
        return {
            'company_name': self.env.company.name,
            'pos': self.env['pos.config'].search([('id', '=', config_id)]).name,
            'pos_logo': img,
            'payment_methods': [{
                'method': method.name,
                'amount': self.get_amount(method.id, date_start, date_stop, config_id) or 0.00
            } for method in self.env['pos.config'].search([('id', '=', config_id)]).payment_method_ids]
        }

    def get_amount(self, method_id=False, date_start=False, date_stop=False, config_id=False):
        sessions = self.env['pos.session'].search([('config_id', '=', config_id)])
        if sessions:
            self.env.cr.execute("""
            SELECT SUM(amount) FROM pos_payment
            WHERE session_id in %s
            AND payment_date >= %s
            AND payment_date <= %s
            AND payment_method_id = %s
            """, (tuple(sessions.ids), date_start, date_stop, method_id))
            amount = self.env.cr.dictfetchall()
            return amount[0]['sum']

    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], data['config_id']))
        return data
