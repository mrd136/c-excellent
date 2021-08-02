# -*- coding:utf-8 -*-
from odoo import models, fields, api

class StockMove(models.Model):
	_inherit = "stock.move"

	qty_request = fields.Char('Quantity Request')