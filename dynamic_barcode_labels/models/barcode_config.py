# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models, api, fields


class BarcodeConfiguration(models.Model):
    _name = 'barcode.configuration'

    @api.model
    def _get_barcode_field(self):
        field_list = []
        ir_model_id = self.env['ir.model'].search([('model', '=', 'product.product')])
        if ir_model_id:
            for field in self.env['ir.model.fields'].search([
                     ('field_description', '!=', 'unknown'),
                     ('readonly', '=', False),
                     ('model_id', '=', ir_model_id.id),
                     ('ttype', '=', 'char')]):
                field_list.append((field.name, field.field_description))
        return field_list

    label_width = fields.Integer(
         'Label Width(MM)',
         required=True,
         help="Page Width"
         )
    label_height = fields.Integer(
         'Label Height(MM)',
         required=True,
         help="Page Height"
         )
    margin_top = fields.Integer(string="Margin(Top)", required=True)
    margin_bottom = fields.Integer(string="Margin(Bottom)", required=True)
    margin_left = fields.Integer(string="Margin(Left)", required=True)
    margin_right = fields.Integer(string="Margin(Right)", required=True)
    dpi = fields.Integer(string="DPI", required=True)
    header_spacing = fields.Integer(string="Header Spacing", required=True)
    currency = fields.Many2one(
           'res.currency',
           string="Currency",
           default=lambda self: self.env.user.company_id.currency_id
           )
    currency_position = fields.Selection([
          ('after', 'After Amount'),
          ('before', 'Before Amount')],
         'Symbol Position',
         help="Determines where the currency symbol"
         " should be placed after or before the amount.",
         default='before')
    barcode_height = fields.Integer(string="Height",  help="Height of barcode.")
    barcode_width = fields.Integer(string="Width",  help="Width of barcode.")
    barcode_field = fields.Selection('_get_barcode_field', string="Barcode Field")
    display_height = fields.Integer(
        string="Display Height (px)",
        help="This height will required for display barcode in label.")
    display_width = fields.Integer(
       string="Display Width (px)",
       help="This width will required for display barcode in label.")
    humanreadable = fields.Boolean()
    product_name = fields.Boolean('Product Name')
    product_variant = fields.Boolean('Attributes')
    lot = fields.Boolean('Production Lot')
    price_display = fields.Boolean('Price')
    product_code = fields.Boolean('Product Default Code')
    barcode = fields.Boolean('Barcode Label')
    description = fields.Boolean('Description')
    quantity = fields.Boolean('Quantity')

    @api.onchange('dpi')
    def onchange_dpi(self):
        if self.dpi < 80:
            self.dpi = 80

    #@api.multi
    def apply(self):
        return True

    @api.model
    def get_config(self):
        return self.env.ref('dynamic_barcode_labels.default_barcode_configuration')
