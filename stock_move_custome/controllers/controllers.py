# -*- coding: utf-8 -*-
from odoo import http

# class StockPickingCustome(http.Controller):
#     @http.route('/stock_picking_custome/stock_picking_custome/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_picking_custome/stock_picking_custome/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_picking_custome.listing', {
#             'root': '/stock_picking_custome/stock_picking_custome',
#             'objects': http.request.env['stock_picking_custome.stock_picking_custome'].search([]),
#         })

#     @http.route('/stock_picking_custome/stock_picking_custome/objects/<model("stock_picking_custome.stock_picking_custome"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_picking_custome.object', {
#             'object': obj
#         })