# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class StockBackorderConfirmation(models.TransientModel):
	_inherit = 'stock.backorder.confirmation'
	

	def _process(self, cancel_backorder=False):
		res = super(StockBackorderConfirmation,self)._process()
		transfer_id = [pick.transfer_id.id for pick in self.pick_ids ][0]

		for pick_id in self.pick_ids:
			backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', pick_id.id)])
			backorder_pick.write({'transfer_id':transfer_id , 'deliver_type': pick_id.deliver_type})
		return res 
