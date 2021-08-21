from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"
    _description = "Operating Unit"

    # referral_user_ids = fields.Many2many("res.users", "referral_users_rel", "operating_unit_id", "user_id",
    #                                      "Users responsible for receive referral")
    referral_coordinator_ids = fields.Many2many("res.users", "referral_coordinator_rel", "operating_unit_id", "user_id",
                                                "Users Coordinator referral")
