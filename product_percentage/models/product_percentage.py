# See LICENSE file for full copyright and licensing details.

from odoo import api,fields,models,_
from odoo.exceptions import UserError, ValidationError


class ProductPercentage(models.Model):
    _inherit = 'product.template'
    _description = 'Percent value to compute sales price'

    value_amount = fields.Float(string='Value', digits='Product Price',
         help="For percent enter a ratio between 0-100.")
    is_percent = fields.Boolean(string="Percent")
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.")


    @api.onchange('value_amount')
    def onchange_percent(self):
        for rec in self:
            percent = (rec.value_amount/100)*rec.standard_price + rec.standard_price
            rec.list_price = percent


    @api.constrains('value')
    def _check_percent(self):
        for prod in self:
            if prod.value_amount < 0.0 or prod.value_amount > 100.0:
                raise ValidationError(_('Percentages on the product must be between 0 and 100.'))
