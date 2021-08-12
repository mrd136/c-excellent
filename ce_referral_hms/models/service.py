from odoo import api, fields, models, _


class Referral(models.Model):
    _name = 'hms.referral.service'
    _description = "Service"

    name = fields.Char('Service', required=1)
    code = fields.Char('Code')
