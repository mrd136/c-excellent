# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import Warning
from odoo import models, fields, api, _

class Product(models.Model):
    _inherit = "product.product"

    @api.depends('name')
    def _make_sku_sequence(self):
        config_id = self.env['product.setting.sku'].search([], limit=1, order="id desc")
        if not config_id:
            self.default_code = False
            return
        else:
            self.default_code = False
        for product in self:
            string = ''
            temp = ''
            if config_id.product == 'two':
                count = 2
            elif config_id.product == 'three':
                count = 3
            elif config_id.product == 'four':
                count = 4
            else:
                raise Warning('Please Select Correct One')
            string+=product.name[0:count] + "-"
            if config_id.use_attribute:
                if product.product_template_attribute_value_ids:
                    for att in product.product_template_attribute_value_ids:
                        if config_id.attribute == 'two':
                            count = 2
                        elif config_id.attribute == 'three':
                            count = 3
                        elif config_id.attribute == 'four':
                            count = 4
                        else:
                            raise Warning('Please Select Correct One')

                        string+=att.name[0:count] + "-"
            if config_id.use_category:
                if config_id.category == 'two':
                    count = 2
                elif config_id.category == 'three':
                    count = 3
                elif config_id.category == 'four':
                    count = 4
                else:
                    raise Warning('Please Select Correct One')

                string += product.categ_id.name[0:count] + "-"
            for a in range(int(float(config_id.pattern))):
                temp += "0"
            string += temp + str(product.id)

            if not config_id.hyphens_opt:
                string = str(string)
                string = string.replace('-', '')
            if string:
                product.default_code = string
                product.write({'default_code1' : string})

    default_code = fields.Char('Internal Reference', index=True, compute='_make_sku_sequence', store=True)
    default_code1 = fields.Char('code', index=True)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_code1 = fields.Char('code', index=True)


