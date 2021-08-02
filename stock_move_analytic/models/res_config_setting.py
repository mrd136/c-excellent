from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Res Config Settings'

    is_analytic = fields.Boolean(string="Enable Stock Move Analytic", config_parameter='base_setup.is_analytic')

