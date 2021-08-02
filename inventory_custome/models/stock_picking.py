# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_round


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	transfer_id = fields.Many2one('transfer.request')
	deliver_type = fields.Selection([('deliver','Deliver'),('receipt','Recipt')])


	def _prepare_sp_lines(self, location_src, location_dest):
		picking_lines = []
		adj_line_vals = []
		picking_type_id = self.env['stock.picking.type'].sudo().search([
								('code', 'ilike', 'outgoing'),
								('default_location_src_id', '=', location_src.id),
								('default_location_dest_id', '=', location_dest.id)
								],limit=1)
		for rec in self:
			if rec.move_ids_without_package:
				for line in rec.move_ids_without_package:
					qty_request = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id, rounding_method='HALF-UP')
					picking_lines.append((0, 0, {
								'name': _('Product ')+line.product_id.name,
								'product_uom': line.product_uom.id,
								'product_id': line.product_id.id,
								'product_uom_qty': line.quantity_done,
								'reserved_availability': line.quantity_done,
								'qty_request':str(line.product_qty) + ' (' + line.product_uom.name + ')',
								'date_expected': datetime.now().date(),
								'picking_type_id': picking_type_id.id,
								'location_id': location_src.id,
								'location_dest_id': location_dest.id,
								'transfer_line_id':line.transfer_line_id.id,
								'deliver_type':'receipt'
								}))
					
		return picking_lines


	def done_all(self):
		active_ids = self._context.get('active_ids')
		pikings = self.env['stock.picking'].search([('id', 'in', active_ids)])
		for rec in pikings:
			for line in rec.move_line_ids_without_package:
				line.qty_done = line.product_uom_qty
			if rec.state != 'done':
				rec.button_validate()


		
	def action_done(self):
		res = super(StockPicking, self).action_done()

		location_src  = None
		location_dest = None
		if self.transfer_id.type == 'internal':
			location_src = self.transfer_id.location_transit_id
			location_dest = self.transfer_id.location_main_id
			dest_name = self.transfer_id.location_branch_id.name
		else:
			location_src = self.transfer_id.location_transit_id
			location_dest = self.transfer_id.location_branch_id
			dest_name = self.transfer_id.location_main_id.name


		if location_src and location_dest and not self.transfer_id.picking_receipt_id:
			picking_type_id = self.env['stock.picking.type'].sudo().search([
									('code', 'ilike', 'incoming'),
									('default_location_src_id', '=',location_src.id),
									('default_location_dest_id', '=', location_dest.id)
									],limit=1)
			if not picking_type_id:
				raise UserError(_("You have not receipt operation main location (%s/%s) and main transit location (%s/%s) !!") % (
					location_dest.location_id.name, location_dest.name,
					location_src.location_id.name,location_src.name))

			sp_lines = self._prepare_sp_lines(location_src=location_src, location_dest=location_dest)
			sp = self.env['stock.picking'].sudo().create({
								'origin': self.transfer_id.name +' -- ('+dest_name+')',
								'location_id': location_src.id,
								'location_dest_id': location_dest.id,
								'picking_type_id': picking_type_id.id,
								'move_ids_without_package': sp_lines,
								'transfer_id':self.transfer_id.id,
								'deliver_type':'receipt'

								})
			sp.action_assign()
			self.transfer_id.picking_receipt_id = sp
			
		if self.transfer_id.state == 'receipt':
			self.transfer_id.action_done()

		else:
			self.transfer_id.action_receipt()

		return res 


