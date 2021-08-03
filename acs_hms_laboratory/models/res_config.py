# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class ResCompany(models.Model):
    _inherit = "res.company"

    #ACSNOTE: Remove in v14 later we did schema changes so added it
    def __init__(self, pool, cr):
        """ Override of __init__ to add fields."""
        try:
            env = api.Environment(cr, SUPERUSER_ID, {})
            cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='res_company' and column_name='laboratory_usage_location'")
            usage_location = cr.dictfetchone()
            if not usage_location:
                cr.execute(
                    "ALTER TABLE res_company ADD COLUMN laboratory_usage_location INTEGER"
                )

            cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='res_company' and column_name='laboratory_stock_location'")
            stock_location = cr.dictfetchone()
            if not stock_location:
                cr.execute(
                    "ALTER TABLE res_company ADD COLUMN laboratory_stock_location INTEGER"
                )
        except:
            pass
        return super(ResCompany, self).__init__(pool, cr)

    laboratory_usage_location = fields.Many2one('stock.location', 
        string='Usage Location for Consumed Laboratory Test Material.')
    laboratory_stock_location = fields.Many2one('stock.location', 
        string='Stock Location for Consumed Laboratory Test Material')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    laboratory_usage_location = fields.Many2one('stock.location', 
        related='company_id.laboratory_usage_location',
        domain=[('usage','=','customer')],
        string='Usage Location for Consumed Laboratory Test Material', readonly=False)
    laboratory_stock_location = fields.Many2one('stock.location', 
        related='company_id.laboratory_stock_location',
        domain=[('usage','=','internal')],
        string='Stock Location for Consumed Laboratory Test Material', readonly=False)