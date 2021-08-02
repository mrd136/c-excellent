# -*- coding:utf-8 -*-
from odoo import models, fields, api


class StockMove(models.Model):
	_inherit = "stock.move"
	material_line_id = fields.Many2one('material.request.line', 'material Line', index=True)
