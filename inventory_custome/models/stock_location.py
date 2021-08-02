# -*- coding:utf-8 -*-
from odoo import models, fields, api

class StockLocation(models.Model):
	_inherit = "stock.location"

	code = fields.Char('Code')
	owner_ids = fields.Many2many('res.partner', string='Owner')
	is_transfer_location = fields.Boolean('Is Transit Transfer Location?')
	account_id = fields.Many2one('account.account', string='Account')
	valuation_account_id = fields.Many2one('account.account', string='Valuation Account')
	warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
	
class StockMove(models.Model):
	_inherit = "stock.move"

	transfer_line_id = fields.Many2one('transfer.request.line', 'Transfer Line', index=True)
	deliver_type = fields.Selection([('deliver','Deliver'),('receipt','Recipt')])
