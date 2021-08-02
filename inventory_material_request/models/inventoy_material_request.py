# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_round

class InvnetoryMaterialRequest(models.Model):
	_name = 'material.request'
	_description = 'Inventory Material Request'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_order = 'name asc, date_request asc, id asc'

	READONLY_STATES = {
		'deliver': [('readonly', True)],
		'receipt': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}


	name = fields.Char('Request ID', requird=True, index=True, copy=False, default="New", readonly=True)
	user_id = fields.Many2one('res.users', 'Representative', index=True, tracking=True, default=lambda self: self.env.user, check_company=True, readonly=True)
	dept_id = fields.Many2one('hr.department', string="Department", states=READONLY_STATES, default=lambda self:self.env.user.department_id)
	date_request = fields.Datetime('Request Date', default=fields.Datetime.now, readonly=True)
	location_id = fields.Many2one('stock.location','Location', required=True,tracking=True, domain="[('usage','=','internal')]",)
	state = fields.Selection([
		('draft','Draft'),
		('confirm','Confirm'),
		('deliver','Deliver'),
		('in process','In Process'),
		('done','Done'),
		('cancel','Cancel')], string='Status', copy=False, index=True, readonly=True, tracking=True, default='draft')
	line_ids = fields.One2many('material.request.line', 'request_id', 'Request Line', states=READONLY_STATES)
	picking_deliver_id = fields.Many2one('stock.picking','Devliver Picking')
	note = fields.Text('Note' , tracking=True, states=READONLY_STATES)


	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			location = self.env['stock.location'].browse(vals['location_id'])
			seq_code = 'material.request.' + ' ' + str(location.code) + ' / '+ '.' +  'MR'
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix':str(location.code) + '/' + 'MR' + '/',
					'number_next' : 1,
					'number_increment' : 1,
					'padding' : 5,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			vals['name'] = seq
		return super(InvnetoryMaterialRequest, self).create(vals)


	def action_confirm(self):
		for rec in self.line_ids:
			if rec.product_qty > rec.onhand_qty:
				raise UserError(_("Product '%s' quantity must be less quantity!!")% rec.product_id.name)
			if not rec.product_qty:
				raise UserError(_("Product '%s' quantity must be != 0.0 !!")% rec.product_id.name)
		if not all(obj.line_ids for obj in self):
			raise UserError(_("Please insert at least one product !!"))
		self.write({'state': 'confirm'})

	def action_deliver(self):
		picking_type_id = self.env['stock.picking.type'].search([
							('code', 'ilike', 'outgoing'),
							('default_location_src_id', '=',self.location_id.id),
							('op_type','=','material')
							],limit=1)

		if not picking_type_id:
			raise UserError(_("You have not deliver operation type material location (%s/%s) !!") % (self.location_id.location_id.name, self.location_id.name))
		if not picking_type_id.default_location_dest_id:
			raise UserError(_("You have not destination location from '%s' operation  !!") % picking_type_id.name)
		sp_lines = []
		for line in self.line_ids:
			qty_request = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id, rounding_method='HALF-UP')
			
			location_src = self.location_id
			stock_qty = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('location_id','child_of',self.location_id.id)])
			for location in stock_qty:
				if location.quantity >= line.product_qty:
					location_src = location.location_id
					break
			sp_lines.append((0, 0, {
						'name': _('Product ')+line.product_id.name,
						'product_uom': line.product_id.uom_id.id,
						'product_id': line.product_id.id,
						'product_uom_qty': qty_request,
						'qty_request':str(line.product_qty)+ ' (' + line.product_uom.name + ')',
						'date_expected': datetime.now().date(),
						'picking_type_id': picking_type_id.id,
						'location_id': location_src.id,
						'material_line_id':line.id,
						'deliver_type':'deliver'
									}))

		sp = self.env['stock.picking'].sudo().create({
								'origin': self.name,
								'location_id': self.location_id.id,
								'location_dest_id': picking_type_id.default_location_dest_id.id,
								'picking_type_id': picking_type_id.id,
								'move_ids_without_package': sp_lines,
								'material_request_id': self.id,
							})
		sp.action_assign()
		self.picking_deliver_id = sp
		self.write({'state': 'deliver'})


	def action_done(self):
		self.write({'state': 'done'})


	def action_view_deliver(self):
		if self.picking_deliver_id: 
			return {
				'name':_('Deliver'),
				'type':'ir.actions.act_window',
				'res_model':'stock.picking',
				'view_type': 'form',
				'view_mode': 'form',
				'view_id':self.env.ref('stock.view_picking_form').id,
				'res_id': self.picking_deliver_id.id
				}


	def action_reset_draft(self):
		self.write({'state': 'draft'})


	def action_cancel(self):
		if all(r.deliver_qty != 0.0  for r in self.line_ids): 
			raise UserError(_('You can not cancel because all deliver quantity is 0.0 !!!'))
		self.write({'state': 'cancel'})

	@api.onchange('location_id')
	def _onchang_location_id(self):
		for line in self.line_ids:
			quant = self.env['stock.quant']
			onhand_qty = sum(r.quantity for r in quant.search([
				('product_id', '=', line.product_id.id),
				('location_id', '=', self.location_id.id)]))
			line.onhand_qty = onhand_qty


class MaterialRequestLine(models.Model):
	_name = 'material.request.line'
	_description = 'Material Request Line'
	_order = 'request_id, id'


	name = fields.Char('Name')
	request_id = fields.Many2one('material.request')
	product_id = fields.Many2one('product.product', 'Product', domain="[('type', 'in', ['product', 'consu']),('can_be_expensed','=','True'),('sale_ok','=',False)]", index=True, required=True,
	)	
	product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
	onhand_qty = fields.Float('On hand Quantity', readonly=True,store=True)
	product_qty = fields.Float(string="Quantity", required=True, default=0.0)
	deliver_qty = fields.Float('Delivered', compute='_compute_qty_delivered', store=True , readonly=True)
	move_ids = fields.One2many('stock.move', 'material_line_id', string='Stock Moves')


	@api.onchange('product_id')
	def _onchange_product_id(self):
		quant = self.env['stock.quant']
		onhand_qty = sum(r.quantity for r in quant.search([
				('product_id', '=', self.product_id.id),
				('location_id', '=', self.request_id.location_id.id)]))
		self.onhand_qty = onhand_qty
		self.product_uom = self.product_id.uom_id.id
		res = {
			'domain': {
				'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]
				}
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
			moves = self.env['stock.move'].search([('material_line_id','=',line.id),('product_id','=',line.product_id.id)])
			outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
			for move in outgoing_moves:
				if move.state != 'done':
					continue
				if move.deliver_type == 'deliver':
					qty_deliver += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
				
					
			for move in incoming_moves:
				if move.state != 'done':
					continue
				if move.deliver_type == 'deliver':
					qty_deliver -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
				
			line.deliver_qty = qty_deliver


