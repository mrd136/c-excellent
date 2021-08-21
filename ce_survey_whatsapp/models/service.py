from odoo import api, fields, models, _


class Service(models.Model):
    _inherit = 'hms.referral.service'
    _description = "Service"

    survey_id = fields.Many2one('survey.survey', string='Survey')
