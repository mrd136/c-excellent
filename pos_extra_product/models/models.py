# -*- coding: utf-8 -*-

import ast

from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.template"

    extra_product_ids = fields.Many2many(
        'product.product', 'product_extra_product_rel', 'product_id', 'extra_product_id', string='Extra Items')


class Order(models.Model):
    _inherit = "pos.order"

    is_void = fields.Boolean("Void Order ?")
    line_id = fields.Many2one('pos.order.line', string="Line id")

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res.update({
            'is_void': ui_order.get('is_void', 0),
	    'line_id': ui_order.get('line_id', 0)
        })
        return res

    @api.model
    def create(self, vals):
        record = super(Order, self).create(vals)
        Product = self.env['product.product']

        for line in record.lines.filtered('extra_items'):
            for extra in ast.literal_eval(line.extra_items):
                pid = extra.get('id')
                product = Product.browse(pid)
                line.create({
                    'product_id': pid,
                    'price_unit': product.list_price,
                    'qty': line.qty,
                    'name': product.display_name,
                    'tax_ids': [(6, 0, product.taxes_id.ids)],
                    'parent_line_id': line.id,
                    'order_id': record.id,
                    'price_subtotal': 0,
                    'price_subtotal_incl': 0,
                })
        return record


class OrderLine(models.Model):
    _inherit = "pos.order.line"

    extra_items = fields.Text("Extra Products")
    is_void = fields.Boolean("Void Order Line ?")
    parent_line_id = fields.Many2one('pos.order.line', string="Parent Line")
    line_id = fields.Many2one('pos.order.line', string="Line id")
    line_unit_price = fields.Float("Line Price")

    def _order_line_fields(self, line, session_id=None):
        if line and len(line) >= 2:
            if line[2].get('extra_items'):
                line[2].update({
                    'price_unit': line[2].get('line_unit_price')
                })
        return line
