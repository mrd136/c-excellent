from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportSaleDetails(models.AbstractModel):

    _name = 'report.custom_pos_receipt.tax_report'
    _description = 'Point of Sale Details'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, sessions=False):
        img = self.env['pos.config'].search([('id','=',config_ids)]).image
        if not img:
            img = self.env.company.logo
        return {
            'company_name': self.env.company.name,
            'pos': self.env['pos.config'].search([('id','=',config_ids)]).name,
            'pos_logo': img,
            'sessions': [{
                'date': session.start_at.date(),
                'state': session.state,
                'name': session.name,
                'opening_total': session.cash_register_balance_start,
                'sale': session.get_session_detail().get('total_sale', 0) + abs(self.get_payment(session)),
                'tax': session.get_session_detail().get('tax', 0),
                'return': abs(self.get_payment(session)),
                'total_return': session.get_session_detail().get('total_gross', 0),
                'total_sale': session.get_session_detail().get('total_sale', 0),
                'total_tax': session.get_session_detail().get('tax', 0),
                'return_total': abs(session.total_return),
            } for session in sessions]
        }

    def get_payment(self,session_id=False):
        session = self.env['pos.session'].search([('id','=',session_id.id)])
        orders = self.env['pos.order'].search([('session_id', '=', session.id)])
        total = 0
        for r in orders:
            total = total+r.amount_total
        return total

    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        sessions = self.env['pos.session'].search([('config_id','=',data['config_id']),('start_at', '>=', data['date_start']), ('start_at', '<=', data['date_stop'])])
        configs = data['config_id']
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], configs, sessions))
        return data
