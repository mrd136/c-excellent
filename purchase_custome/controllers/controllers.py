# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseCustome(http.Controller):
#     @http.route('/purchase_custome/purchase_custome/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_custome/purchase_custome/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_custome.listing', {
#             'root': '/purchase_custome/purchase_custome',
#             'objects': http.request.env['purchase_custome.purchase_custome'].search([]),
#         })

#     @http.route('/purchase_custome/purchase_custome/objects/<model("purchase_custome.purchase_custome"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_custome.object', {
#             'object': obj
#         })