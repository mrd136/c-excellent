# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_round


class TransferRequest(models.Model):
	_name = 'transfer.request'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_description = 'Transfer Request'
	_order = 'name asc, date_request asc, id asc'

	READONLY_STATES = {
		'deliver': [('readonly', True)],
		'receipt': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	name = fields.Char('Request ID', requird=True, index=True, copy=False, default="New", readonly=True)
	user_id = fields.Many2one('res.users', 'Representative', index=True, tracking=True, default=lambda self: self.env.user, check_company=True, readonly=True)
	date_request = fields.Datetime('Request Date', default=fields.Datetime.now, readonly=True)
	location_main_id = fields.Many2one('stock.location','Destnation Location', required=True,tracking=True, domain="[('usage','=','internal')]",readonly=True)
	location_branch_id = fields.Many2one('stock.location', 'Source Location', tracking=True, domain="[('usage','=','internal')]", states=READONLY_STATES, required=True)
	location_transit_id = fields.Many2one('stock.location','Tranist Location',tracking=True)
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
	type = fields.Selection([
		('internal','Internal'),
		('feeding','Feeding')], 'Type', required=True)
	state = fields.Selection([
		('draft','Draft'),
		('confirm','Confirm'),
		('deliver','Deliver'),
		('receipt','Ready to Receipt'),
		('in process','In Process'),
		('done','Done'),
		('cancel','Cancel')], string='Status', copy=False, index=True, readonly=True, tracking=True, default='draft')
	line_ids = fields.One2many('transfer.request.line', 'request_id', 'Request Line', states=READONLY_STATES)
	picking_deliver_id = fields.Many2one('stock.picking','Devliver Picking')
	picking_receipt_id = fields.Many2one('stock.picking', 'Receipt Picking')
	categ_ids = fields.Many2many('product.category', string='Product Category', states=READONLY_STATES)
	date_sales_from = fields.Date('Sales From', tracking=True, states=READONLY_STATES)
	date_sales_to = fields.Date('Sales To', tracking=True , states=READONLY_STATES)
	note = fields.Text('Note' , tracking=True, states=READONLY_STATES)
	oper_type = fields.Selection([('add', 'Add'),('clean','Clean'),('remove_zero_line','Remove 0 lines')], default='add', string="Operation Type", states=READONLY_STATES)
	is_sales = fields.Boolean('Sales',default=True, states=READONLY_STATES)


	@api.onchange('location_branch_id')
	def _onchang_location_id(self):
		for line in self.line_ids:
			quant = self.env['stock.quant']
			qty_src = qty_dest = 0.0
			if self.type == 'internal':
				qty_src = sum(r.quantity for r in quant.search([
					('product_id','=', line.product_id.id),
					('location_id', 'child_of', self.location_branch_id.id)]))
				qty_dest = sum(r.quantity for r in quant.search([
					('product_id', '=', line.product_id.id),
					('location_id', 'child_of', self.location_main_id.id)]))
			else:
				qty_src = sum(r.quantity for r in quant.search([
					('product_id', '=', line.product_id.id),
					('location_id', 'child_of', self.location_main_id.id)]))
				qty_dest = sum(r.quantity for r in quant.search([
					('product_id','=',line.product_id.id),
					('location_id','child_of',self.location_branch_id.id)]))

			line.onhand_src_qty = qty_src
			line.onhand_dest_qty = qty_dest

	@api.constrains('location_main_id','location_branch_id')
	def _constrains_location(self):
		if self.location_branch_id == self.location_main_id:
			raise UserError(_('Location from and location to must be different !!'))

	@api.model
	def create(self, vals):
		if 'name' not in vals or not vals['name']:
			if self._context.get('default_type') == 'internal':
				location = self.env['stock.location'].browse(vals['location_main_id'])
				seq_code = 'internal.transfer.' + ' ' + str(location.code) + ' / '+ '.' +  'IT'
				seq = self.env['ir.sequence'].next_by_code( seq_code )
				if not seq:
					self.env['ir.sequence'].create({
						'name' : seq_code,
						'code' : seq_code,
						'prefix':str(location.code) + '/' + 'IT' + '/',
						'number_next' : 1,
						'number_increment' : 1,
						'padding' : 5,
						})
					seq = self.env['ir.sequence'].next_by_code( seq_code )

			elif self._context.get('default_type') == 'feeding':
				location = self.env['stock.location'].browse(vals['location_main_id'])
				seq_code = 'internal.transfer.' + ' ' + str(location.code) + ' / '+ '.' +  'IF'
				seq = self.env['ir.sequence'].next_by_code( seq_code )
				if not seq:
					self.env['ir.sequence'].create({
						'name' : seq_code,
						'code' : seq_code,
						'prefix':str(location.code) + '/' + 'IF' + '/',
						'number_next' : 1,
						'number_increment' : 1,
						'padding' : 5,
						})
					seq = self.env['ir.sequence'].next_by_code( seq_code )
			vals['name'] = seq
		return super(TransferRequest, self).create(vals)


	@api.model
	def default_get(self, default_fields):
		res = super(TransferRequest, self).default_get(default_fields)
		partner = self.env.user.partner_id
		locations = self.env['stock.location'].search([('usage','=','internal')])
		for loc in locations:
			for owner in loc.owner_ids:
				if partner.id == owner.id:
					res['location_main_id'] = loc.id
					return res
		return res


	def action_confirm(self):
		location = self.env['stock.location'].search([('usage','=','transit'),('is_transfer_location','=',True)], limit=1)
		if not location:
			raise UserError(_('You have not traniste location for transfer!!'))
		self.location_transit_id = location.id
		for rec in self.line_ids:
			if rec.product_qty > rec.onhand_src_qty:
				raise UserError(_("Product '%s' quantity must be less than quantity in from location !!")% rec.product_id.name)
			if not rec.product_qty:
				raise UserError(_("Product '%s' quantity must be != 0.0 click remove 0 line if want!!")% rec.product_id.name)
		if not all(obj.line_ids for obj in self):
			raise UserError(_("Please insert at least one product !!"))

		self.env['mail.activity'].sudo().create({
			'res_name':self.name,
			'activity_type_id':self.env.ref('mail.mail_activity_data_todo').id,
			'note': ('Transfer'),
			'date_deadline': self.date_request,
			'summary': 'Transfer',
			'user_id': self.user_id.id,
			'res_id':self.id,
			'res_model_id':self.env.ref('inventory_custome.model_transfer_request').id,
			})
		self.write({'state': 'confirm'})


	def _prepare_sp_lines(self, location_src, location_dest):
		picking_lines = []
		picking_type_id = self.env['stock.picking.type'].search([
								('code', 'ilike', 'outgoing'),
								('default_location_src_id', '=', location_src.id),
								('default_location_dest_id', '=', location_dest.id)
								],limit=1)
		for rec in self:
			if rec.line_ids:
				for line in rec.line_ids:
					stock_qty = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('location_id','child_of',location_src.id)])
					qty = 0.0
					for location in stock_qty:
						if location.quantity >= line.product_qty:
							location_src = location.location_id
							break
					# qty = 0.0					
					# if stock_qty.quantity >= line.product_qty:
					# 	qty = line.product_qty
					# else:
					# 	qty = stock_qty.quantity
					qty_request = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id, rounding_method='HALF-UP')
					picking_lines.append((0, 0, {
								'name': _('Product ')+line.product_id.name,
								'product_uom': line.product_id.uom_id.id,
								'product_id': line.product_id.id,
								'product_uom_qty': line.product_qty,
								'reserved_availability': line.product_qty,
								'qty_request':str(line.product_qty) + ' (' + line.product_uom.name + ')',
								'date_expected': datetime.now().date(),
								'picking_type_id': picking_type_id.id,
								'location_id': location_src.id,
								'location_dest_id': location_dest.id,
								'transfer_line_id':line.id,
								'deliver_type':'deliver'

											}))
		return picking_lines 

	def create_activity(self, user):
		for rec in user:
			activity = self.env['mail.activity']
			activity.sudo().create({
				'res_name':self.name,
				'activity_type_id':self.env.ref('mail.mail_activity_data_todo').id,
				'note': self.name,
				'date_deadline': fields.Date.today(),
				'summary': self.name,
				'user_id': rec.id,
				'res_id': self.id,
				'res_model_id':self.env['ir.model']._get('transfer.request').id
				})

	def action_deliver(self):
		for rec in self.line_ids:
			rec._onchange_product_id()
			print (rec.product_qty,rec.onhand_dest_qty,rec.onhand_src_qty)
			if rec.product_qty > rec.onhand_src_qty:
				raise UserError(_("Product '%s' is not available!")% rec.product_id.name)

		location_src  = None
		location_dest = None
		if self.type == 'internal':
			location_src = self.location_branch_id
			location_dest = self.location_transit_id
			dest_name = self.location_main_id.name

		elif self.type == 'feeding':
			location_src = self.location_main_id
			location_dest = self.location_transit_id
			dest_name = self.location_branch_id.name


		picking_type_id = self.env['stock.picking.type'].sudo().search([
								('code', 'ilike', 'outgoing'),
								('default_location_src_id', '=',location_src.id),
								('default_location_dest_id', '=', location_dest.id)
								],limit=1)
		if not picking_type_id:
			raise UserError(_("You have not deliver operation source location (%s/%s) and destination transit location (%s/%s) !!") % (
				location_src.location_id.name,location_src.name,location_dest.location_id.name,location_dest.name))

		sp_lines = self._prepare_sp_lines(location_src=location_src, location_dest=location_dest)
		sp = self.env['stock.picking'].sudo().create({
								'origin': self.name + ' -- (' + dest_name +')',
								'location_id':	location_src.id,
								'location_dest_id': location_dest.id,
								'picking_type_id': picking_type_id.id,
								'move_ids_without_package': sp_lines,
								'transfer_id': self.id,
								'deliver_type':'deliver'
							})

		sp.action_assign()
		self.picking_deliver_id = sp
		self.write({'state': 'deliver'})
		if type == 'internal':
			user = self.env['res.users'].search([('partner_id','in',self.location_branch_id.owner_ids.ids)])
		else:
			user = self.env['res.users'].search([('partner_id','in',self.location_main_id.owner_ids.ids)])
		if user:
			self.create_activity(user=user)


	def action_receipt(self):
		if type == 'internal':
			user = self.env['res.users'].search([('partner_id','in',self.location_main_id.owner_ids.ids)])
		else:
			user = self.env['res.users'].search([('partner_id','in',self.location_branch_id.owner_ids.ids)])
		if user:
			self.create_activity(user=user)
		self.write({'state': 'receipt'})

	def action_done(self):
		self.write({'state': 'done'})

	def action_view_deliver(self):
		action = self.env.ref('stock.action_picking_tree_all').read()[0]

		backorder_id = self.env['stock.picking'].search([('backorder_id', '!=', False )])
		pickings = self.env['stock.picking'].search([('transfer_id', '=', self.id)])
		if len(pickings) > 1:
			action['domain'] = [('transfer_id', '=', self.id),('deliver_type', '=', 'deliver')]
		elif pickings:
			form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
			if 'views' in action:
				action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
				action['res_id'] = self.picking_deliver_id.id
	
			else:
				action['views'] = form_view

		return action

		# if self.picking_deliver_id:	
		# 	return {
		# 		'name':_('Deliver'),
		# 		'type':'ir.actions.act_window',
		# 		'res_model':'stock.picking',
		# 		'view_type': 'form',
		# 		'view_mode': 'form',
		# 		'view_id':self.env.ref('stock.view_picking_form').id,
		# 		'res_id': self.picking_deliver_id.id
		# 		}


	def action_view_receipt(self):
		action = self.env.ref('stock.action_picking_tree_all').read()[0]

		pickings = self.env['stock.picking'].search([('transfer_id', '=', self.id)])
		if len(pickings) > 1:
			action['domain'] = [('transfer_id', '=', self.id),('deliver_type', '=', 'receipt')]
		elif pickings:
			form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
			if 'views' in action:
				action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
				action['res_id'] = self.picking_receipt_id.id
	
			else:
				action['views'] = form_view

		return action

		# if self.picking_receipt_id:
		# 	return {
		# 		'name':_('Receipt'),
		# 		'type':'ir.actions.act_window',
		# 		'res_model':'stock.picking',
		# 		'view_type': 'form',
		# 		'view_mode': 'form',
		# 		'view_id':self.env.ref('stock.view_picking_form').id,
		# 		'res_id': self.picking_receipt_id.id
		# 		}


	def action_reset_draft(self):
		if self.picking_deliver_id.state == 'ready':
			raise UserError(_('You can not cancel because has picking done'))
		else:
			self.picking_deliver_id.action_cancel()
		self.write({'state': 'draft'})


	def action_cancel(self):
		if all(r.deliver_qty != 0.0 and r.receipt_qty != 0.0 for r in self.line_ids):
			raise UserError(_('You can not cancel because all deliver and receipt quantity is 0.0 !!!'))
		else:
			self.picking_deliver_id.action_cancel()
		self.write({'state': 'cancel'})

	def action_done(self):
		self.write({'state': 'done'})

	def _compute_sales_count(self,product, date_from, date_to):
		sales_count = 0.0
		location  = None
		if self.type == 'internal':
			location = self.location_branch_id.id
		elif self.type == 'feeding':
			location = self.location_main_id.id
		so_line = self.env['sale.order.line'].search([
							('state', 'in', ['sale', 'done', 'paid']),
							('order_id.date_order', '>=', date_from),
							('order_id.date_order', '<=', date_to),
							('product_id', '=' ,product.id)])

		for line in so_line.move_ids:
			if line.location_id.id == location:
				sales_count += line.product_uom_qty
		return sales_count


	def prepare_products(self):
		domain = []
		if self.categ_ids:
			domain.append(('categ_id', 'child_of', self.categ_ids.ids))
		if self.oper_type == 'add':
			config = self.env['res.config.settings'].search([('company_id','=',self.env.user.company_id.id)])
			product_line = []
			'''if config:
				if config[-1].module_product_expiry:
					lot = self.env['stock.production.lot'].search([('removal_date', '>', fields.Datetime.now())])
					domain.append(('id', 'not in', [r.product_id.id for r in lot]))
					lot = self.env['stock.production.lot'].search([('removal_date', '>', fields.Datetime.now())])
					domain.append(('id', 'not in', [r.product_id.id for r in lot]))'''
			product_obj = self.env['product.product'].search(domain)
			for product in product_obj:
				quant = self.env['stock.quant']
				qty_src = qty_dest = 0.0
				if self.type == 'internal':
					qty_src = sum((r.quantity - r.reserved_quantity) for r in quant.search([
							('product_id', '=', product.id),
							('location_id','child_of', self.location_main_id.id)]))
					qty_dest = sum((r.quantity - r.reserved_quantity) for r in quant.search([
						('product_id', '=', product.id),
						('location_id', 'child_of', self.location_branch_id.id)]))
				else:
					qty_dest = sum((r.quantity - r.reserved_quantity) for r in quant.search([
						('product_id', '=', product.id),
						('location_id','child_of',self.location_branch_id.id)]))
					qty_src = sum((r.quantity - r.reserved_quantity) for r in quant.search([
						('product_id', '=', product.id),
						('location_id', 'child_of',self.location_main_id.id)]))

				product_line.append((0,0,{
					'request_id': self.id,
					'name': _('Product ')+product.name,
					'product_id': product.id,
					'product_uom': product.uom_id.id,
					'onhand_src_qty': qty_src,
					'onhand_dest_qty': qty_dest,
					'sold_qty': self._compute_sales_count(product, self.date_sales_from, self.date_sales_to), 
					}))
			self.line_ids = product_line
		elif self.oper_type == 'clean':
			self.update({
					'line_ids': [(5, _, _)],
					})
		else:
			for rec in self.line_ids:
				if not rec.product_qty:
					self.write({'line_ids':[(2,rec.id,_)]})



class TransferRequestLine(models.Model):
	_name = 'transfer.request.line'
	_description = 'Transfer Request Line'
	_order = 'request_id, id'


	name = fields.Char('Name')
	request_id = fields.Many2one('transfer.request')
	product_id = fields.Many2one('product.product', 'Product', domain="[('type', 'in', ['product', 'consu'])]", index=True, required=True)	
	product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
	product_qty = fields.Float(string="Quantity", required=True, default=0.0)
	deliver_qty = fields.Float('Delivered', compute='_compute_qty_delivered', store=True , readonly=True)
	receipt_qty = fields.Float('Receipted', compute='_compute_qty_delivered', store=True, readonly=True)
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
	onhand_src_qty = fields.Float('Qty From' , store=True)
	onhand_dest_qty = fields.Float('Qty To' , store=True)
	sold_qty = fields.Float('Sub-inventory sales', readonly=True, store=True)
	move_ids = fields.One2many('stock.move', 'transfer_line_id', string='Stock Moves')


	@api.constrains('request_id', 'product_id')
	def check_product_id(self):
		for rec in self:
			product_count = self.env['transfer.request.line'].search_count([('request_id','=',rec.request_id.id),('product_id','=', rec.product_id.id)])
			if product_count > 1 :
				raise UserError(_("Product '%s' Should be Unique!")% rec.product_id.name)


	@api.onchange('product_id')
	def _onchange_product_id(self):
		quant = self.env['stock.quant']
		qty_src = qty_dest = 0.0
		if self.request_id.type == 'internal':
			qty_src = sum(r.quantity - r.reserved_quantity for r in quant.search([
				('product_id','=', self.product_id.id),
				('location_id', 'child_of', self.request_id.location_branch_id.id)]))
			qty_dest = sum(r.quantity- r.reserved_quantity for r in quant.search([
				('product_id', '=', self.product_id.id),
				('location_id', 'child_of', self.request_id.location_main_id.id)]))
		if self.request_id.type == 'feeding':
				qty_src = sum(r.quantity- r.reserved_quantity for r in quant.search([
				('product_id', '=', self.product_id.id),
				('location_id', 'child_of', self.request_id.location_main_id.id)]))
				qty_dest = sum(r.quantity - r.reserved_quantity for r in quant.search([
				('product_id','=',self.product_id.id),
				('location_id','child_of',self.request_id.location_branch_id.id)]))

		self.onhand_src_qty = qty_src
		self.onhand_dest_qty = qty_dest
		self.sold_qty =  self.product_id._compute_sales_count_inv(self.request_id.date_sales_from, self.request_id.date_sales_to)
		self.product_uom = self.product_id.uom_id.id
		res = {}
		res['domain'] = {
			'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]
			}
		return res		

	def _get_outgoing_incoming_moves(self):
		outgoing_moves = self.env['stock.move']
		incoming_moves = self.env['stock.move']

		for move in self.move_ids.filtered(lambda r: r.state != 'cancel' and not r.scrapped and self.product_id == r.product_id):
			if not  move.to_refund:
				if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
					outgoing_moves |= move
			elif move.to_refund:
				incoming_moves |= move

		return outgoing_moves, incoming_moves

	
	@api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
	def _compute_qty_delivered(self):
		for line in self:
			qty_deliver = 0.0
			qty_reciept = 0.0
			moves = self.env['stock.move'].search([('transfer_line_id','=',line.id),('product_id','=',line.product_id.id)])
			outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
			for move in outgoing_moves:
				if move.state != 'done':
					continue
				if move.deliver_type == 'deliver':
					qty_deliver += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
				else:
					qty_reciept += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
					
			for move in incoming_moves:
				if move.state != 'done':
					continue
				if move.deliver_type == 'deliver':
					qty_deliver -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
				else:
					qty_reciept -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
			line.deliver_qty = qty_deliver
			line.receipt_qty = qty_reciept
