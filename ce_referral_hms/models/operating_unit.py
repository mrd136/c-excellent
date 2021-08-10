# Copyright 2015-TODAY ForgeFlow
# - Jordi Ballester Alomar
# Copyright 2015-TODAY Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class OperatingUnit(models.Model):

    _inherit = "operating.unit"
    _description = "Operating Unit"

    referral_user_ids = fields.Many2many("res.users", "referral_users_rel", "operating_unit_id", "user_id",
                                         "Users responsible for referral")
