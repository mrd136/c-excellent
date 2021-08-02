# -*- coding:utf-8 -*-
from odoo import api, fields, models, tools


class MaterialRequestReport(models.Model):
	_name = 'material.request.report'
	_description = 'material Request Report'
	_auto = False
	_order = 'date desc'

	date = fields.Date(string="Date", readonly=True)
	request_id = fields.Many2one('transfer.request')
	user_id = fields.Many2one('res.users', 'Representative', readonly=True)
	location_id = fields.Many2one('stock.location', 'Location',readonly=True)
	product_id = fields.Many2one('product.product', 'Product', domain="[('type', 'in', ['product', 'consu'])]", index=True, required=True)	
	product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
	onhand_qty = fields.Float('On hand Quantity', readonly=True,store=True)
	product_qty = fields.Float(string="Quantity", required=True, default=0.0)
	deliver_qty = fields.Float('Delivered' , readonly=True)
	state = fields.Selection([
		('draft','Draft'),
		('confirm','Confirm'),
		('deliver','Deliver'),
		('receipt','Ready to Receipt'),
		('in process','In Process'),
		('done','Done'),
		('cancel','Cancel')], string='Status', copy=False, index=True, readonly=True, tracking=True, default='draft')



	def init(self):
		# self._table = material_request_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s FROM ( %s ) %s )""" % (self._table, self._select(), self._from(), self._group_by()))

	def _select(self):
		select_str = """
			SELECT
				min(l.id) as id,
				tr.id as request_id,
				tr.location_id as location_id,
				tr.date_request as date,
				tr.user_id as user_id,
				l.product_id as product_id,
				l.product_uom as product_uom,
				l.product_qty as product_qty,
				l.deliver_qty as deliver_qty,
				l.onhand_qty as onhand_qty,
				tr.state as state

		""" 
		return select_str

	def _from(self):
		from_str = """
			material_request_line l
				join material_request tr on (l.request_id=tr.id)
		"""
		return from_str

	def _group_by(self):
		group_by_str = """
			GROUP BY
				l.product_id ,
				l.product_uom ,
				l.product_qty ,
				l.deliver_qty ,
				l.onhand_qty ,
				tr.date_request ,
				tr.state ,
				tr.id ,
				tr.location_id ,
				tr.user_id
		"""
		return group_by_str
