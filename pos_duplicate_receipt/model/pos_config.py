# -*- coding: utf-8 -*-
# This module open source
# Design and development by: TL Technology (thanhchatvn@gmail.com)

from odoo import api, fields, models, _

class pos_config(models.Model):
    _inherit = "pos.config"

    duplicate_receipt = fields.Boolean('Duplicate Receipt')
    print_number = fields.Integer('Print number', help='How many number receipt need to print at printer ?', default=2)
