# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import Warning
import random
from datetime import date, datetime


class pos_order(models.Model):
	_inherit = 'pos.order'

	def print_pos_receipt(self):
		output = []
		discount = 0
		order_id = self.search([('id', '=', self.id)], limit=1)
		client = order_id.partner_id.id
		barcode = order_id.barcode
		orderlines = self.env['pos.order.line'].search([('order_id', '=', order_id.id)])
		payments = self.env['pos.payment'].search([('pos_order_id', '=', order_id.id)])
		paymentlines = []
		subtotal = 0
		total = 0
		tax = 0
		change = 0
		delivery_type = ""
		for payment in payments:
			if payment.amount > 0:
				temp = {
					'amount': payment.amount,
					'name': payment.payment_method_id.name
				}
				paymentlines.append(temp)
			else:
				change += payment.amount
			 
		for orderline in orderlines:
			extra_items = []
			extra = self.env['pos.order.line'].search([('order_id', '=', order_id.id), ('parent_line_id', '=', orderline.id)])
			if extra:
				for r in extra:
					extra_vals = {
						'id': r.product_id.id,
						'en_trans': r.product_id.en_trans,
						'ar_trans': r.product_id.ar_trans,
						'display_name': r.product_id.display_name,
						'note': r.note,
						'product_id': r.product_id.name,
						'total_price': r.product_id.lst_price*orderline.qty,
						'qty': r.qty,
						'price_unit': r.product_id.lst_price,
						'discount': r.discount,
					}
					extra_items.append(extra_vals)
			new_vals = {
				'id': orderline.product_id.id,
				'en_trans': orderline.product_id.en_trans,
				'ar_trans': orderline.product_id.ar_trans,
				'note': orderline.note,
				'product_id': orderline.product_id.name,
				'total_price': orderline.price_subtotal_incl,
				'qty': orderline.qty,
				'price_unit': orderline.price_unit,
				'discount': orderline.discount,
				'extra_items': extra_items,
				'parent_line_id': orderline.parent_line_id.id or False,
				}

			discount += (orderline.price_unit * orderline.qty * orderline.discount) / 100
			subtotal +=orderline.price_subtotal
			total +=orderline.price_subtotal_incl
			tax += (orderline.price_subtotal_incl - orderline.price_subtotal)
			
			output.append(new_vals)

			delivery_type = order_id.delivery_type
			sequence_number = order_id.sequence_number
			date_order = order_id.date_order
			pos_reference = order_id.pos_reference

		return [output, discount, paymentlines, change, subtotal, tax, barcode, total, delivery_type, client, sequence_number, date_order, pos_reference]

