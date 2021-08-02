# -*- coding:utf-8 -*-
from odoo import api, fields, models, tools


class TransferRequestReport(models.Model):
	_name = 'transfer.request.report'
	_description = 'Transfer Request Report'
	_auto = False
	_order = 'date desc'

	date = fields.Date(string="Date", readonly=True)
	request_id = fields.Many2one('transfer.request')
	user_id = fields.Many2one('res.users', 'Representative', readonly=True)
	location_from_id = fields.Many2one('stock.location','Location From',readonly=True)
	location_to_id = fields.Many2one('stock.location', 'Location To',readonly=True)
	product_id = fields.Many2one('product.product', 'Product', domain="[('type', 'in', ['product', 'consu'])]", index=True, required=True)	
	product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
	product_qty = fields.Float(string="Quantity", required=True, default=0.0)
	deliver_qty = fields.Float('Delivered', compute='_compute_qty_delivered', store=True , readonly=True)
	receipt_qty = fields.Float('Receipted', compute='_compute_qty_delivered', store=True, readonly=True)
	onhand_src_qty = fields.Float('Qty From' , store=True)
	onhand_dest_qty = fields.Float('Qty To' , store=True)
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



	def init(self):
		# self._table = transfer_request_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s FROM ( %s ) %s )""" % (self._table, self._select(), self._from(), self._group_by()))

	def _select(self):
		select_str = """
			SELECT
				min(l.id) as id,
				tr.id as request_id,
				tr.location_main_id as location_from_id,
				tr.location_branch_id as location_to_id,
				tr.date_request as date,
				tr.user_id as user_id,
				l.product_id as product_id,
				l.product_uom as product_uom,
				l.product_qty as product_qty,
				l.deliver_qty as deliver_qty,
				l.receipt_qty as receipt_qty,
				l.onhand_src_qty as onhand_src_qty,
				l.onhand_dest_qty as onhand_dest_qty,
				tr.type as type,
				tr.state as state

		""" 
		return select_str

	def _from(self):
		from_str = """
			transfer_request_line l
				join transfer_request tr on (l.request_id=tr.id)
		"""
		return from_str

	def _group_by(self):
		group_by_str = """
			GROUP BY
				l.product_id ,
				l.product_uom ,
				l.product_qty ,
				l.deliver_qty ,
				l.receipt_qty ,
				l.onhand_src_qty ,
				l.onhand_dest_qty,
				tr.date_request ,
				tr.type ,
				tr.state ,
				tr.id ,
				tr.location_main_id ,
				tr.location_branch_id ,
				tr.user_id
		"""
		return group_by_str
