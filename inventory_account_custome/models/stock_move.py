# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
	_inherit = "stock.move"

	def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
		self.ensure_one()
		AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
		# new_move_lines = []
		move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
		if move_lines:
			move_exist = False
			date = self._context.get('force_period_date', fields.Date.context_today(self))
			#picking_id = self.env['stock.picking'].search([('id','=',self.picking_id.id)])
			#inventory_id = self.env['stock.inventory'].search([('id','=',self.reference.replace('INV:', ''))])

			if self.picking_id:
				move_exist = self.env['account.move'].search([('picking_id','=',self.picking_id.id)])
			if self.inventory_id:
				move_exist = self.env['account.move'].search([('stock_inventory_id','=',self.inventory_id.id)])

			if not move_exist:
				new_account_move = AccountMove.sudo().create({
						'journal_id': journal_id,
						'line_ids': move_lines,
						'date': date,
						'ref': description,
						'stock_move_id': self.id,
						'stock_valuation_layer_ids': [(6, None, [svl_id])],
						'type': 'entry',
						'picking_id': self.picking_id.id,
						'stock_inventory_id': self.inventory_id.id
					})

				self.write({'account_move_ids':[(4, new_account_move.id)]})
			else:
				move_exist.write({'line_ids': move_lines})
				self.write({'account_move_ids':[(4, move_exist.id)]})
