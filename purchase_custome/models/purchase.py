# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools.float_utils import float_round
from odoo.tools import float_utils, float_is_zero, float_compare
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	is_sales = fields.Boolean('Sales',default=True)
	categ_ids = fields.Many2many('product.category', string='Product Category')
	date_sales_from = fields.Date('Sales From', tracking=True)
	date_sales_to = fields.Date('Sales To', tracking=True)
	state = fields.Selection(selection_add=[
		('draft', 'Draft'),
		('confirm', 'Purchase Department Manager'),
		('sent', 'RFQ Sent'),
		('to approve', 'General Manager'),
		('purchase', 'Confirm'),
		('done_po','Done'),
		('done', 'Locked'),
		('cancel', 'Cancelled')
	], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
	
	oper_type = fields.Selection([('add', 'Add'),('clean','Clean'),('remove_zero_line','Remove 0 lines')], default='add', string="Operation Type")

	documents_to_clearance = fields.Date(
		string='Documents Sent To Clearance',
	)
	
	shipping_policy_number = fields.Char(
		string='Shipping Policy Number',
	)
	
	clearance_cost = fields.Float(
		string='Clearance Cost',
	)

	total_cost = fields.Float(
		string='Total Cost',
		compute='_compute_total_cost',
		readonly = True,
		store = True )

	
	proforma_invoice_date = fields.Date(
		string='Proforma Invoice Date',
	)

	
	transfer_date = fields.Date(
		string='Transfer Date',
	)

	
	container_count = fields.Float(
		string='Container Count',
	)
	
	
	
		
	@api.depends('clearance_cost', 'amount_untaxed')
	def _compute_total_cost(self):
		for record in self:
			record.total_cost = record.clearance_cost + record.amount_untaxed
		
	
	 
	def compute_forcase_qty(self,product_id):
		po_line = self.env['purchase.order.line'].search([('product_id','=',product_id.id),('order_id.check_fully_delivery','=',False),('order_id.check_partially_delivery','=',False),('order_id.state','in',('purchase','confirm'))])
		forecast_qty = 0.0
		for rec in po_line:
			for picking in rec.order_id.picking_ids:
				if picking != 'done':
					forecast_qty += rec.product_qty
		return forecast_qty

	def compute_sold_qty(self,product_id,date_sales_from,date_sales_to):
		domain = [('product_id','=',product_id.id),('order_id.child_order_id','=',False),('order_id.state','in',('sale','done','delivery_done'))]
		if date_sales_from :
			domain += [('order_id.date_order','>=',date_sales_from)]
		if date_sales_to :
			domain += [('order_id.date_order','<=',date_sales_to)]
		so_line = self.env['sale.order.line'].search(domain)
		sold_qty = 0.0
		for rec in so_line:
			sold_qty += rec.product_uom_qty

		return sold_qty

	def compute_sold_count(self,product_id,date_sales_from,date_sales_to):
		domain = [('product_uom_qty','!=',0.0),('product_id','=',product_id.id),('order_id.child_order_id','=',False),('order_id.state','in',('sale','done','delivery_done'))]
		if date_sales_from :
			domain += [('order_id.date_order','>=',date_sales_from)]
		if date_sales_to :
			domain += [('order_id.date_order','<=',date_sales_to)]
		so_line = self.env['sale.order.line'].search(domain)
		sold_count = 0
		for rec in so_line:
			sold_count += 1
		return sold_count

	def _prepare_account_move_line(self, move):
		self.ensure_one()
		account_id = self.order_id.picking_type_id.default_location_dest_id.valuation_account_id.id
		if self.product_id.purchase_method == 'purchase':
			qty = self.product_qty - self.qty_invoiced
		else:
			qty = self.qty_received - self.qty_invoiced
		if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
			qty = 0.0

		if self.currency_id == move.company_id.currency_id:
			currency = False
		else:
			currency = move.currency_id

		return {
			'name': '%s: %s' % (self.order_id.name, self.name),
			'move_id': move.id,
			'account_id':account_id,
			'currency_id': currency and currency.id or False,
			'purchase_line_id': self.id,
			'date_maturity': move.invoice_date_due,
			'product_uom_id': self.product_uom.id,
			'product_id': self.product_id.id,
			'price_unit': self.price_unit,
			'quantity': qty,
			'partner_id': move.partner_id.id,
			'analytic_account_id': self.account_analytic_id.id,
			'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
			'tax_ids': [(6, 0, self.taxes_id.ids)],
			'display_type': self.display_type,
		}

	def prepare_products(self):
		domain = [('purchase_ok','=',True)]
		if self.categ_ids:
			domain.append(('categ_id', 'child_of', self.categ_ids.ids))
		if self.oper_type == 'add':
			config = self.env['res.config.settings'].search([('company_id','=',self.env.user.company_id.id)])
			product_line = []
			if config:
				if config[-1].module_product_expiry:
					lot = self.env['stock.production.lot'].search([('removal_date', '>', fields.Datetime.now())])
					domain.append(('id', 'not in', [r.product_id.id for r in lot]))
			product_obj = self.env['product.product'].search(domain)
			for product in product_obj:
				quantity =  0.0
				quantity = sum(r.quantity - r.reserved_quantity for r in self.env['stock.quant'].search([
								('product_id','=', product.id),
								('location_id.usage', '=', 'internal'),('location_id', '!=', 64)]))


				product_line.append((0,0,{
					'order_id': self.id,
					'name': product.name,
					'product_id': product.id,
					'product_uom': product.uom_po_id.id,
					'date_planned': datetime.now(),
					'onhand_qty': quantity,
					'forecast_qty': self.compute_forcase_qty(product),
					'sold_qty': self.compute_sold_qty(product,self.date_sales_from,self.date_sales_to),
					'sold_count': self.compute_sold_count(product,self.date_sales_from,self.date_sales_to),
					'product_qty': 0.0 ,
					'price_unit': 0.0,
					}))

			self.order_line = product_line
		elif self.oper_type == 'clean':
			self.update({
					'order_line': [(5, _, _)],
					})
		else:
			for rec in self.order_line:
				if not rec.price_subtotal:
					self._cr.execute("DELETE FROM purchase_order_line where id = %s;" ,[rec.id])
					#self.write({'order_line':[(2,rec.id,_)]})

	def action_confirm(self):
		for line in self.order_line:
			if not line.price_subtotal:
				raise UserError(_("Product '%s' price subtotal must be != 0.0 click remove 0 line if want !!")% line.product_id.name)
		if not all(obj.order_line for obj in self):
			raise UserError(_("Please insert at least one product !!"))
		self.write({'state': 'confirm'})

	def button_confirm(self):
		for order in self:
			if order.state not in ['confirm', 'sent']:
				continue
			order._add_supplier_to_product()
			# Deal with double validation process
			if order.company_id.po_double_validation == 'one_step'\
					or (order.company_id.po_double_validation == 'two_step'\
						and order.amount_total < self.env.company.currency_id._convert(
							order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
					or order.user_has_groups('purchase_custome.group_purchase_department_manage'):
				order.button_approve()
			else:
				order.write({'state': 'to approve'})
		return super(PurchaseOrder, self).button_confirm()

	# @api.depends('order_line.qty_received')
	# def action_done_po():
	#   if all(r.qty_received != 0.0 for r in self.order_line):
	#       self.write({'state':'done_po'})

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'


	#user_qty = fields.Float(string='User Measure', default=0.0)
	onhand_qty = fields.Float('On hand Quantity', readonly=True,store=True)
	forecast_qty = fields.Float('Forcast Quantity' , readonly=True, store=True)
	sold_qty = fields.Float('Sold Quantity', readonly=True, store=True)
	sold_count = fields.Integer('Order Count', readonly=True, store=True)
	default_code = fields.Char('Code', related="product_id.default_code")


	# @api.onchange('user_qty')
	# def onchange_user_qty(self):
	# 	# Conversion and Upper Rounding
	# 	for rec in self:
	# 		if rec.user_qty > 0.0:
	# 			if rec.product_uom and rec.product_uom.always_round_up:
	# 				# Getting UoM Quantity Conversion with Round Up
	# 				qty = 0.0
	# 				if rec.product_uom.uom_type == 'bigger':
	# 					qty = rec.user_qty / rec.product_uom.factor_inv
	# 				elif rec.product_uom.uom_type == 'smaller':
	# 					qty = rec.user_qty / rec.product_uom.factor
	# 				print (qty,"---------............................>>>>>>>qty")
	# 				rounded_qty = float_utils.float_round(
	# 					qty,
	# 					precision_digits=None,
	# 					precision_rounding=1,
	# 					rounding_method='UP')

	# 				rec.product_qty = rounded_qty
	# 		else:
	# 			rec.product_qty = 0.0
				

			

	# @api.onchange('product_id',  'user_qty')
	def _onchange_product_id(self):
		quant = self.env['stock.quant']
		qty = 0.0
		if self.order_id.picking_type_id and self.product_id:
			qty = sum(r.quantity - r.reserved_quantity for r in quant.search([
				('product_id','=', self.product_id.id),
				('location_id.usage', '=', 'internal'),('location_id', '!=', 64)]))
		self.onhand_qty = qty
		self.forecast_qty = self.compute_forcase_qty()
		self.sold_qty = self.compute_sold_qty()
		self.sold_count = self.compute_sold_count()


	def _suggest_quantity(self):
		res = super(PurchaseOrderLine, self)._suggest_quantity()
		self.product_qty = 0.0
		return res


	def compute_forcase_qty(self):
		po_line = self.env['purchase.order.line'].search([('product_id','=',self.product_id.id),('order_id.check_fully_delivery','=',False),('order_id.check_partially_delivery','=',False),('order_id.state','in',('purchase','confirm'))])
		forecast_qty = 0.0
		for rec in po_line:
			for picking in rec.order_id.picking_ids:
				if picking != 'done':
					forecast_qty += rec.product_qty
		return forecast_qty

	def compute_sold_qty(self):
		domain = [('product_id','=',self.product_id.id),('order_id.child_order_id','=',False),('order_id.state','in',('sale','done','delivery_done'))]
		if self.order_id.date_sales_from :
			domain += [('order_id.date_order','>=',self.order_id.date_sales_from)]
		if self.order_id.date_sales_to :
			domain += [('order_id.date_order','<=',self.order_id.date_sales_to)]
		so_line = self.env['sale.order.line'].search(domain)
		sold_qty = 0.0
		for rec in so_line:
			sold_qty += rec.product_uom_qty

		return sold_qty

	def compute_sold_count(self):
		domain = [('product_uom_qty','!=',0.0),('product_id','=',self.product_id.id),('order_id.child_order_id','=',False),('order_id.state','in',('sale','done','delivery_done'))]
		if self.order_id.date_sales_from :
			domain += [('order_id.date_order','>=',self.order_id.date_sales_from)]
		if self.order_id.date_sales_to :
			domain += [('order_id.date_order','<=',self.order_id.date_sales_to)]
		so_line = self.env['sale.order.line'].search(domain)
		sold_count = 0
		for rec in so_line:
			sold_count += 1
		return sold_count