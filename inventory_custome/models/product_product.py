# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_round

class ProductProcuct(models.Model):
	_inherit = "product.product"


	def _compute_sales_count_inv(self,date_from,date_to):
		r = {}
		sales_count = 0
		if not self.user_has_groups('sales_team.group_sale_salesman'):
			return r
		done_states = self.env['sale.report']._get_done_states()
		
		domain_move = [('product_id','=',self.id),('sale_line_id','!=',False),('origin_returned_move_id','!=',False),('state','=','done')]
		if date_from:
			domain_move.append(('date', '>=', date_from))
		if date_to:
			domain_move.append(('date', '<=', date_to))

		move = self.env['stock.move'].search(domain_move)
		qty = sum(r.product_uom_qty for r in move)
		domain = [
			('state', 'in', done_states),
			('product_id', 'in', self.ids)
		]
		if date_from:
			domain.append(('date', '>=', date_from))
		if date_to:
			domain.append(('date', '<=', date_to))
		
		for group in self.env['sale.report'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
			r[group['product_id'][0]] = group['product_uom_qty']
		for product in self:
			if not product.id:
				product.sales_count = 0.0
				continue
			sales_count = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding) - qty
		return sales_count


	def _compute_forcase_qty(self):
		po_line = self.env['purchase.order.line'].search([('product_id','=',self.id),('order_id.state','=','purchase')])
		forecast_qty = 0.0
		for rec in po_line:
			for picking in rec.order_id.picking_ids:
				if picking != 'done':	
					forecast_qty += rec.product_qty	
		return forecast_qty
