from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class ConsumDetails(models.AbstractModel):

    _name = 'report.custom_pos_receipt.consum_report'
    _description = 'Consumption Report'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_id=False, product_id=False):
        sessions = self.env['pos.session'].search(
            [('config_id', '=', config_id), ('start_at', '>=', date_start),
             ('start_at', '<=', date_stop)])
        print("SSSSSEEEEEEEEEESSSSSSSSSIIIIIOOONNNNNNNNSSSSSSSS", sessions.ids)
        order_ids = self.env['pos.order'].search([('session_id', 'in', sessions.ids)])
        sold = []
        prods_sold = {}
        main_product = self.env['product.product'].search([('id', '=', product_id)]).name
        total_consumption = 0
        # for order in order_ids:
        #     for line in order.lines:
        #         if line.product_id.bom_ids:
        #             flag = False
        #             for r in line.product_id.bom_ids:
        #                 for lin in r.bom_line_ids:
        #                     if lin.product_id.id == product_id:
        #                         flag = True
        #                         cons_qty = lin.product_qty
        #             if flag:
        #                 flag2 = False
        #                 for s in sold:
        #                     if s['name'] == line.product_id.name:
        #                         s['qty'] += line.qty
        #                         flag2 = True
        #                 if not flag2:
        #                     prods_sold.update({
        #                         'name': line.product_id.name,
        #                         'qty': line.qty,
        #                         'cons_qty': cons_qty
        #                     })
        #                     sold.append(prods_sold)
        print("order_idsssssssssssssssss : ", order_ids)
        for order in order_ids:
            for line in order.lines:
                if line.product_id:
                    if line.product_id in prods_sold:
                        prods_sold[line.product_id] += line.qty
                    else:
                        prods_sold.update({
                            line.product_id: line.qty
                        })

        for p in prods_sold:
            for b in p.bom_ids:
                for lin in b.bom_line_ids:
                    if lin.product_id.id == product_id:
                        sold.append({'name': p.name, 'qty': prods_sold[p], 'cons_qty': prods_sold[p]*lin.product_qty})
                        total_consumption += prods_sold[p]*lin.product_qty

        print("prods_soldddddddddddddddddddddddd : ", prods_sold)
        img = self.env['pos.config'].search([('id', '=', config_id)]).image
        if not img:
            img = self.env.company.logo
        return {
            'company_name': self.env.company.name,
            'pos': self.env['pos.config'].search([('id', '=', config_id)]).name,
            'pos_logo': img,
            'product': main_product,
            'total_consumption': total_consumption,
            'sold': sold
        }

    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], data['config_id'], data['product_id']))
        return data
