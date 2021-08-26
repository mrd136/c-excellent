# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import pytz
from odoo import fields, models, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import models,_
from odoo.exceptions import UserError
#from odoo.exceptions import AccessError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_session_report = fields.Boolean(string='Session Report ')

class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_return_order = fields.Boolean(string='Return Order')

    
    def refund(self):
        res = super(PosOrder, self).refund()
        self.env['pos.order'].search([('id', '=', res['res_id'])]).is_return_order = True
        return res

class PosSession(models.Model):
    _inherit = 'pos.session'

    def get_payment_details(self):
        orders = self.env['pos.order'].search([('session_id', '=', self.id)])
        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
                SELECT aj.name, sum(amount) total
                FROM account_bank_statement_line AS absl,
                     account_bank_statement AS abs,
                     account_journal AS aj
                WHERE absl.statement_id = abs.id
                    AND abs.journal_id = aj.id
                    AND absl.id IN %s
                GROUP BY aj.name
            """, (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []
        return payments

    def get_session_detail(self):
        if self.state != 'closed' and not self.env.user.has_group('custom_pos_receipt.group_pos_session_end_report_value'):
            return {
                'total_sale': False,
                'discount': False,
                'tax': False,
                'products_sold': False,
                'prods_sold': False,
                'total_gross': False,
                'total_return': False,
                'total_internal': False,
                'total_delivery': False,
                'total_takeaway': False,
                'starting_cash': False,
                'expected_in_cash': False,
                'cash_register_balance_end_real': False,
                'cash_register_difference': False,
                'payment_methods': False
            }
        order_ids = self.env['pos.order'].search([('session_id', '=', self.id)])

        total_internal = 0.0
        total_delivery = 0.0
        total_takeaway = 0.0
        discount = 0.0
        taxes = 0.0
        total_sale = 0.0
        total_gross = 0.0
        total_return = 0.0
        return_total = 0.0
        products_sold = {}
        prods_sold = {}
        for order in order_ids:
            for line in order.lines:
                if line.product_id.name:
                    if line.product_id.name in prods_sold:
                        prods_sold[line.product_id.name] += line.qty
                    else:
                        prods_sold.update({
                            line.product_id.name: line.qty
                        })

        for order in order_ids:
            total_sale += order.amount_total
            currency = order.session_id.currency_id
            total_gross += order.amount_total
            for line in order.lines:
                if line.product_id.pos_categ_id.name:
                    if line.product_id.pos_categ_id.name in products_sold:
                        products_sold[line.product_id.pos_categ_id.name] += line.qty
                    else:
                        products_sold.update({
                            line.product_id.pos_categ_id.name: line.qty
                        })
                else:
                    if 'undefine' in products_sold:
                        products_sold['undefine'] += line.qty
                    else:
                        products_sold.update({
                                'undefine': line.qty
                                })
                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes += tax.get('amount', 0)
                discount += line.discount
            if order.amount_total < 0:
                total_return -= order.amount_total
                return_total += order.amount_total

            # if order.delivery_type == 'internal':
            #     total_internal = total_internal + order.amount_total
            # if order.delivery_type == 'delivery':
            #     total_delivery = total_delivery + order.amount_total
            # if order.delivery_type == 'takeaway':
            #     total_takeaway = total_takeaway + order.amount_total

        starting_cash = self.cash_register_balance_start
        expected_in_cash = self.cash_register_balance_start + total_sale

        return {
            'total_sale': total_sale,
            'discount': discount,
            'tax': total_sale-(total_sale/1.15),
            'products_sold': products_sold or False,
            'prods_sold': prods_sold or False,
            'total_gross': total_gross - (total_sale-(total_sale/1.15)) - discount,
            'total_return': int(total_return),
            'total_internal': total_internal,
            'total_delivery': total_delivery,
            'total_takeaway': total_takeaway,
            'starting_cash': starting_cash,
            'expected_in_cash': expected_in_cash,
            'cash_register_balance_end_real': self.cash_register_balance_end_real,
            'cash_register_difference': self.cash_register_balance_end_real - expected_in_cash,
            'payment_methods': [{
                'method': method.name,
                'amount': self.get_amount(method.id, self.id) or 0.00
            } for method in self.env['pos.config'].search([('id', '=', self.config_id.id)]).payment_method_ids]
        }

    def get_amount(self, method_id=False, session_id=False):
        sessions = self.env['pos.session'].search([('id', '=', session_id)])
        if sessions:
            self.env.cr.execute("""
            SELECT SUM(amount) FROM pos_payment
            WHERE session_id in %s
            AND payment_method_id = %s
            """, (tuple(sessions.ids), method_id))
            amount = self.env.cr.dictfetchall()
            return amount[0]['sum']

    def get_current_datetime(self):
        if self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '+':
            date_time = datetime.now() + timedelta(hours=hour_tz, minutes=min_tz)
        if sign == '-':
            date_time = datetime.now() - timedelta(hours=hour_tz, minutes=min_tz)
        return date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_session_open_date(self):
        #return self.start_at.strftime(DEFAULT_SERVER_DATE_FORMAT)
        d1 = datetime.strptime(str(self.start_at), DEFAULT_SERVER_DATETIME_FORMAT)
        return d1

    def get_session_open_time(self):
        #return self.start_at.strftime("%I:%M %p")
        d1 = datetime.strptime(str(self.start_at), DEFAULT_SERVER_DATETIME_FORMAT)
        return d1
