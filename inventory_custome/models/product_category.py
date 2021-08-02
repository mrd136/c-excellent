# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_round

class ProductCategory(models.Model):
	_inherit = 'product.category'

	code = fields.Char('Code')
		