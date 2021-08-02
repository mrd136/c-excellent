# -*- coding:utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
	_inherit = "account.move"

	picking_id = fields.Many2one('stock.picking', 'Stock Picking')
	stock_inventory_id = fields.Many2one('stock.inventory', string='Stock inventory', index=True)
