# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	def _calculate_po_so_account_move(self,debit_account, credit_account, type):
		entry_lines = []
		for move in self.move_ids_without_package:
			if move.product_id.type == 'product':
				# # Get debit and credit accounts, throw validation error if not found
				debit_amount = credit_amount = move.product_id.uom_id._compute_price(move.product_id.standard_price, move.product_uom)  or 0.0
				if  not debit_account:
					debit_account = move.product_id.categ_id.property_stock_valuation_account_id or False
				if not credit_account:
					credit_account = move.product_id.categ_id.property_stock_valuation_account_id or False
				credit_entry_line = {
					'account_id': credit_account.id,
					'name': type + ' - '+move.product_id.name,
					'debit': 0.0,
					'credit': credit_amount,
					'company_id': self.company_id.id,
					'company_currency_id': self.company_id.currency_id.id,
					}
				entry_lines.append((0,0,credit_entry_line))
				debit_entry_line = {
					'account_id': debit_account.id,
					'name': type + ' - ' + move.product_id.name,
					'debit': debit_amount,
					'credit': 0.0,
					'company_id': self.company_id.id,
					'company_currency_id': self.company_id.currency_id.id,
					}
				entry_lines.append((0,0,debit_entry_line))
		return entry_lines

	def button_validate(self):
		res = super(StockPicking, self).button_validate()
		name = ''
		credit_account = None
		debit_account = None
		transfer_type = None
		lines = []
		# if self.transfer_id:
		# 	if self.transfer_id.type == 'feeding' and self.deliver_type == 'deliver':
		# 		transfer_type = 'Deliver'
		# 		debit_account = self.transfer_id.location_transit_id.account_id or False
		# 		credit_account = self.transfer_id.location_main_id.account_id or False
		# 	if self.transfer_id.type == 'feeding' and self.deliver_type == 'receipt':
		# 		transfer_type = 'Receipt'
		# 		credit_account = self.transfer_id.location_transit_id.account_id or False
		# 		debit_account = self.transfer_id.location_branch_id.account_id or False
		# 	if self.transfer_id.type == 'internal' and self.deliver_type == 'deliver':
		# 		transfer_type = 'Deliver'
		# 		debit_account = self.transfer_id.location_transit_id.account_id or False
		# 		credit_account = self.transfer_id.location_branch_id.account_id or False
		# 	if self.transfer_id.type == 'internal' and self.deliver_type == 'receipt':
		# 		transfer_type = 'Receipt'
		# 		credit_account = self.transfer_id.location_transit_id.account_id or False
		# 		debit_account = self.transfer_id.location_main_id.account_id or False
		# 	if not credit_account:
		# 		raise UserError(_("Please define stock  '%s' account !!") % (self.transfer_id.location_main_id.name))
		# 	if not debit_account:
		# 		raise UserError(_("Please define stock  '%s' account !!") % (self.transfer_id.location_transit_id.name))
		# 	lines = self._calculate_account_move(credit_account, debit_account ,transfer_type)
		# 	if self.transfer_id:
		# 		name = str(self.transfer_id.name) + ' - ' + transfer_type  

		# 	for move in self.move_ids_without_package:
		# 		journal_id = move.product_id.categ_id.property_stock_journal
		# 		if not journal_id:
		# 			raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)

		# 	vals = {
		# 		'ref':name,
		# 		'line_ids':lines,
		# 		'picking_id': self.id,
		# 		'journal_id':journal_id.id,
		# 		'state':'draft',
		# 		}
		# 	account_move = self.env['account.move'].create(vals)
		# 	account_move.post()

		# if self.material_request_id :
		# 	lines = self._material_account_moves()
		# 	name = 'Matrial Request'

		# 	vals = {
		# 	'ref':name,
		# 	'line_ids':lines,
		# 	'picking_id': self.id,
		# 	'journal_id':journal_id.id,
		# 	'state':'draft',
		# 	}
		# 	account_move = self.env['account.move'].create(vals)
		# 	account_move.post()

		# if self.sale_id:
		# 	credit_account = self.location_id.account_id or False
		# 	debit_account = self.location_id.valuation_account_id or False
		# 	# if not credit_account:
		# 	# 	raise UserError(_("Please define stock  '%s' account !!") % (self.location_id.name))
		# 	# if not debit_account:
		# 	# 	raise UserError(_("Please define stock  '%s' valuation account !!") % (self.location_id.name))
		# 	name = self.sale_id.name
		# 	lines = self._calculate_po_so_account_move(credit_account, debit_account, 'Sale')
		# 	for move in self.move_ids_without_package:
		# 		journal_id = move.product_id.categ_id.property_stock_journal
		# 		if not journal_id:
		# 			raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
		# 	vals = {
		# 	'ref':name,
		# 	'line_ids':lines,
		# 	'picking_id': self.id,
		# 	'journal_id':journal_id.id,
		# 	'state':'draft',
		# 	}
		# 	account_move = self.env['account.move'].create(vals)
		# 	# account_move.post()

		if self.purchase_id:
			credit_account = self.location_dest_id.valuation_account_id or False
			debit_account = self.location_dest_id.account_id or False

			if not debit_account:
				# raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % self.location_id.name)
				raise UserError(_("Please define stock  '%s' valuation account !!") % (self.location_dest_id.name))
			if not debit_account:
				raise UserError(_("Please define stock  '%s' account !!") % (self.location_dest_id.name))

			lines = self._calculate_po_so_account_move(credit_account, debit_account, 'Purchase')
			for move in self.move_ids_without_package:
				journal_id = move.product_id.categ_id.property_stock_journal
				if not journal_id:
					raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
			name = self.purchase_id.name
			vals = {
			'ref':name,
			'line_ids':lines,
			'picking_id': self.id,
			'journal_id':journal_id.id,
			'state':'draft',
			}
			account_move = self.env['account.move'].create(vals)
			# account_move.post()
		return res 


