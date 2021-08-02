# -*- coding: utf-8 -*-


from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
	_inherit = 'stock.picking'
	is_return = fields.Boolean('Is Return', default=False)


	def	action_account_move(self):
		action = self.env.ref('account.action_move_journal_line').read()[0]
		action['context'] = {'default_type': 'entry'}
		action['view_mode'] = 'tree'
		action['domain'] = [('picking_id', 'in', self.ids)]
		# action['domain'] = [('stock_move_id', 'in', self.move_lines.ids)]
		return action


	def	action_view_return(self):
		stock_move = self.env['stock.move'].search([('origin_returned_move_id.picking_id','in',self.ids)]).picking_id
		picking_return = self.env['stock.picking'].search([('id','=',stock_move.ids)])
		return {
			'name':_('Return'),
			'type':'ir.actions.act_window',
			'res_model':'stock.picking',
			'view_mode': 'tree',
			'view_id':self.env.ref('stock.vpicktree').id,
			'domain': [('id', 'in', picking_return.ids)]
			}
	

	def _calculate_account_move(self,debit_account, credit_account):
		entry_lines = []
		move = self.move_ids_without_package.filtered(lambda r:r.account_move_ids)
		if move:
			for line in self.move_ids_without_package:
				for move in line.account_move_ids:
					for move_line in move.line_ids:
						if credit_account and debit_account:
							if move_line.credit and not move_line.debit:
								credit_entry_line = {
									'account_id': credit_account.id,
									'name': move_line.name,
									'debit': 0.0,
									'credit': move_line.credit,
									'company_id': move_line.company_id.id,
									'company_currency_id': move_line.company_id.currency_id.id,
									}
								move_line.update(credit_entry_line)
								entry_lines.append((0,0,credit_entry_line))
							if move_line.debit and not move_line.credit:
								debit_entry_line = {
									'account_id': debit_account.id,
									'name': move_line.name,
									'debit': move_line.debit,
									'credit': 0.0,
									'company_id': move_line.company_id.id,
									'company_currency_id': move_line.company_id.currency_id.id,
									}
								if move.picking_id.inter_company_transfer_id.type == 'pos' and move.picking_id.picking_type_id.code == 'incoming':
									account_analytic_id = move.picking_id.inter_company_transfer_id.pos_config.account_analytic_id
									debit_entry_line = {
										'account_id': debit_account.id,
										'name': move_line.name,
										'debit': move_line.debit,
										'credit': 0.0,
										'analytic_account_id': account_analytic_id.id,
										'company_id': move_line.company_id.id,
										'company_currency_id': move_line.company_id.currency_id.id,
										}
								move_line.update(debit_entry_line)
								entry_lines.append((0,0,debit_entry_line))
					move.sudo().button_draft()
					# move.sudo().with_context({'force_delete':True}).unlink()
		else:
			for move in self.move_ids_without_package:
				if move.product_id.type == 'product':
					if credit_account and debit_account:
						debit_amount = credit_amount = (move.product_id.standard_price * move.product_uom_qty) or 0.0
						if move.purchase_line_id:
							debit_amount = credit_amount = (move.purchase_line_id.price_unit*move.product_uom_qty) or 0.0
						if move.sale_line_id:
							debit_amount = credit_amount = (move.sale_line_id.price_unit*move.product_uom_qty) or 0.0
						credit_entry_line = {
							'account_id': credit_account.id,
							'name':move.name + ' - '+ move.product_id.name,
							'debit': 0.0,
							'credit': credit_amount,
							'company_id': self.company_id.id,
							'company_currency_id': self.company_id.currency_id.id,
							}
						entry_lines.append((0, 0, credit_entry_line))
						debit_entry_line = {
							'account_id': debit_account.id,
							'name': move.name + ' - '+  move.product_id.name,
							'debit': debit_amount,
							'credit': 0.0,
							'company_id': self.company_id.id,
							'company_currency_id': self.company_id.currency_id.id,
							}
						if move.picking_id.inter_company_transfer_id.type == 'pos' and move.picking_id.picking_type_id.code == 'incoming':
							account_analytic_id = move.picking_id.inter_company_transfer_id.pos_config.account_analytic_id
							if account_analytic_id:
								debit_entry_line = {
									'account_id': debit_account.id,
									'name': move.name + ' - ' + move.product_id.name,
									'debit': debit_amount,
									'credit': 0.0,
									'analytic_account_id': account_analytic_id.id,
									'company_id': self.company_id.id,
									'company_currency_id': self.company_id.currency_id.id,
								}
						entry_lines.append((0, 0, debit_entry_line))
			for move in self.move_ids_without_package:
				journal_id = move.product_id.categ_id.property_stock_journal
				if not journal_id:
					raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
			val = {
					'ref':self.name,
					'line_ids':entry_lines,
					'picking_id': self.id,
					'journal_id':journal_id.id,
					'state':'draft',
				}
			if move.product_id.categ_id.property_valuation != 'real_time':
				move = False
			elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'service':
				move = False
			elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'product':
				move = self.env['account.move'].sudo().create(val)
			elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'consu':
				move = False

		return move

	def _material_account_moves(self,is_return):
		entry_lines = []

		for move in self.move_ids_without_package:
			# move.account_move_ids.sudo().with_context({'force_delete': True}).unlink()

			if move.product_id.type == 'product':
				# # Get debit and credit accounts, throw validation error if not found
				if not is_return:
					credit_account = self.location_id.account_id or False
					debit_account = move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id or False
					if not credit_account:
						raise UserError(_("Please define stock ( %s/%s ) account !!") % (self.location_id.location_id.name,self.location_id.name))

					if not debit_account:
						raise UserError(_("Please define an expense account for item: %s, or category: %s") % (move.product_id.name, move.product_id.categ_id.name))
					if move.material_line_id:
					   analytic_account = move.material_line_id.request_id.dept_id.analytic_account_id #self.env.user.department_id.analytic_account_id
					if not analytic_account:
						raise UserError(_('Department of user can not analytic account !!'))
					debit_amount = credit_amount = (move.product_id.standard_price*move.product_uom_qty) or 0.0

					credit_entry_line = {
						'account_id': credit_account.id,
						'name': 'Material Deliver / '+move.product_id.name,
						'debit': 0.0,
						'credit': credit_amount,
						'company_id': self.company_id.id,
						'company_currency_id': self.company_id.currency_id.id
						}
					entry_lines.append((0,0,credit_entry_line))
					debit_entry_line = {
						'account_id': debit_account.id,
						'name': 'Material Deliver / '+move.product_id.name,
						'debit': debit_amount,
						'credit': 0.0,
						'company_id': self.company_id.id,
						'company_currency_id': self.company_id.currency_id.id,
						'analytic_account_id': analytic_account.id
						}
					entry_lines.append((0,0,debit_entry_line))

				else:
					debit_account = self.location_dest_id.account_id or False
					credit_account = move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id or False
					if not debit_account:
						raise UserError(_("Please define stock (%s/%s) account !!") % (self.location_dest_id.location_id.name, self.location_dest_id.name))

					if not credit_account:
						raise UserError(_("Please define an expense account for item: %s, or category: %s") % (move.product_id.name, move.product_id.categ_id.name))


					analytic_account = self.env.user.department_id.analytic_account_id
					if not analytic_account:
						raise UserError(_('Department of user can not analytic account !!'))
					debit_amount = credit_amount = (move.product_id.standard_price*move.product_uom_qty) or 0.0

					credit_entry_line = {
						'account_id': credit_account.id,
						'name': 'Material Deliver / '+move.product_id.name,
						'debit': 0.0,
						'credit': credit_amount,
						'company_id': self.company_id.id,
						'company_currency_id': self.company_id.currency_id.id,
						'analytic_account_id': analytic_account.id

						}
					entry_lines.append((0,0,credit_entry_line))
					debit_entry_line = {
						'account_id': debit_account.id,
						'name': 'Material Deliver / '+move.product_id.name,
						'debit': debit_amount,
						'credit': 0.0,
						'company_id': self.company_id.id,
						'company_currency_id': self.company_id.currency_id.id,
						}
					entry_lines.append((0,0,debit_entry_line))

		for move in self.move_ids_without_package:
			journal_id = move.product_id.categ_id.property_stock_journal
			if not journal_id:
					raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
		val = {
					'ref':self.name,
					'line_ids':entry_lines,
					'picking_id': self.id,
					'journal_id':journal_id.id,
					'state':'draft',
				}
		if move.product_id.categ_id.property_valuation != 'real_time':
			move = False
		elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'service':
			move = False
		elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'product':
			move = self.env['account.move'].sudo().create(val)
		elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'consu':
			move = False
		return move


	def action_done(self):
		res = super(StockPicking, self).action_done()
		is_return = False
		picking_id = None
		for rec in self.move_ids_without_package:
			if rec.origin_returned_move_id:
				is_return = True
				picking_id = rec.origin_returned_move_id.picking_id
			if self.sale_id and self.picking_type_id.code =='incoming':
				picking_id = self
				is_return = True

				break

		if not is_return:
			if not self.material_request_id :
				if self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_dest_id:
					credit_account = self.location_dest_id.account_id or False
					debit_account = self.location_id.account_id or False
					if credit_account and debit_account:
						if self.purchase_id :
							#debit_account = self.picking_type_id.default_location_src_id.account_id #elf.env['stock.location'].sudo().search([('usage','=','supplier')],limit = 1).account_id #self.picking_type_id.default_location_src_id.account_id or False
							# debit_account = self.company_id.property_stock_account_input_company_id
							if self.location_id.account_id:
								debit_account = self.location_id.account_id
							else:
								debit_account = self.company_id.property_stock_account_input_company_id
						if self.sale_id :
							# credit_account = self.env['stock.location'].sudo().search([('usage','=','customer')],limit = 1).account_id
							# credit_account = self.sale_id.team_id.cost_account_id
							if self.location_dest_id.account_id:
								credit_account = self.location_dest_id.account_id
							else:
								credit_account = self.company_id.property_stock_account_output_company_id
						new_move = self._calculate_account_move(credit_account, debit_account)
						for move in self.move_ids_without_package:
							journal_id = move.product_id.categ_id.property_stock_journal
							if not journal_id:
								raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
						val = {
							'ref':self.name,
							# 'line_ids':lines,
							'picking_id': self.id,
							'journal_id':journal_id.id,
							# 'state':'draft',
							}
						if new_move:
							new_move.write(val)
							if new_move.state == 'draft':
								# account_move = self.env['account.move'].sudo().create(val)
								new_move.post()
					else:
						if not credit_account:
							raise ValidationError(_("Please define stock (%s/%s) account !!") % (str(self.picking_type_id.default_location_dest_id.location_id.name),str(self.picking_type_id.default_location_dest_id.name)))
						if not debit_account:
							raise ValidationError(_("Please define stock (%s/%s) account !!") % (str(self.picking_type_id.default_location_src_id.location_id.name),str(self.picking_type_id.default_location_src_id.name)))
				else:
					raise ValidationError(_("Please check source and destination location of picking!!"))


			else:
				new_move = self._material_account_moves(is_return)
				for move in self.move_ids_without_package:
					journal_id = move.product_id.categ_id.property_stock_journal
					if not journal_id:
						raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
				val = {
				'ref':self.name,
				# 'line_ids':lines,
				'picking_id': self.id,
				'journal_id':journal_id.id,
				# 'state':'draft',
				}
				new_move.write(val)
				if new_move.state == 'draft':
					# account_move = self.env['account.move'].sudo().create(val)
					new_move.post()

		else:
			if not picking_id.material_request_id :
				if self.picking_type_id:
					try:
						if self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_dest_id:
							credit_account = self.location_id.account_id or False
							debit_account = self.location_dest_id.account_id or False
							if credit_account and debit_account:
								name = str(self.origin)
								op_type = ""
								if picking_id.sale_id:
									op_type = 'Sale'
									credit_account = self.picking_type_id.default_location_dest_id.account_id or False
									debit_account = self.env['stock.location'].sudo().search([('usage', '=', 'customer')], limit=1).account_id #.sale_id.team_id.cost_account_id
								if picking_id.purchase_id:
									op_type = 'Purchase'

									debit_account = self.picking_type_id.default_location_src_id.account_id or False
									credit_account = self.picking_type_id.default_location_dest_id.account_id #self.env['stock.location'].sudo().search([('usage', '=', 'supplier')],limit=1).account_id  # self.picking_type_id.default_location_src_id.account_id or False
								if picking_id.transfer_id:
									op_type = picking_id.transfer_id.type
								new_move = self._calculate_account_move(credit_account, debit_account)
								for move in self.move_ids_without_package:
									journal_id = move.product_id.categ_id.property_stock_journal
									if not journal_id:
										raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)

								val = {
									'ref':self.name,
									# 'line_ids':lines,
									'picking_id': self.id,
									'journal_id':journal_id.id,
									# 'state':'draft',
									}
								new_move.write(val)
								if new_move.state == 'draft':
									# account_move = self.env['account.move'].sudo().create(val)
									new_move.post()
								


							else:
								if not credit_account:
									raise ValidationError(_("Please define stock (%s/%s) account !!") % (self.picking_type_id.default_location_src_id.location_id.name, self.picking_type_id.default_location_src_id.name))
								if not debit_account:
									raise ValidationError(_("Please define stock (%s/%s) account !!") % (self.picking_type_id.default_location_dest_id.location_id.name,self.picking_type_id.default_location_dest_id.name))

					except ValueError:
						raise ValidationError(_("Please check sourse and destination location of picking!!"))


			else:
				new_move = self._material_account_moves(is_return)
				name = 'Matrial Request'

				for move in self.move_ids_without_package:
					journal_id = move.product_id.categ_id.property_stock_journal
					if not journal_id:
						raise UserError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
				val = {
				'ref':self.name,
				# 'line_ids':lines,
				'picking_id': self.id,
				'journal_id':journal_id.id,
				# 'state':'draft',
				}
				new_move.write(val)
				if new_move.state == 'draft':
					# account_move = self.env['account.move'].sudo().create(val)
					new_move.post()
		return res
