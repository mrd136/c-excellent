# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_round


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	material_request_id = fields.Many2one('material.request')

	def button_validate(self):
		res = super(StockPicking, self).button_validate()
		if self.material_request_id:
			self.material_request_id.action_done()
		
		return res 


class StockPickingType(models.Model):
	_inherit = 'stock.picking.type'

	op_type = fields.Selection([
		('material', 'Material'),
		('sale', 'Sale'),
		('purchase', 'Purchase')
		],'Type')



