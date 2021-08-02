# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    enable_analytic = fields.Boolean(string='Enable analytic', compute="_enable_analytic")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.depends('name')
    def _enable_analytic(self):
        for rec in self:
            if rec.env['ir.config_parameter'].sudo().get_param('base_setup.is_analytic') == "True":
                rec.enable_analytic = True
            else:
                rec.enable_analytic = False

    @api.model
    def create(self, vals):
        res = super(StockWarehouse, self).create(vals)
        location_ids = self.env['stock.location'].search([('location_id.name', '=', vals['code'])])
        for location in location_ids:
            location.analytic_account_id = res.analytic_account_id.id
        return res

    def write(self, vals):
        res = super(StockWarehouse, self).write(vals)
        if 'analytic_account_id' in vals:
            location_ids = self.env['stock.location'].search(['|',
                ('location_id', '=', self.lot_stock_id.location_id.id),
                ('name', '=', self.lot_stock_id.location_id.name),
            ])
            for location in location_ids:
                location.analytic_account_id = vals['analytic_account_id']
        return res


class StockLocations(models.Model):
    _inherit = 'stock.location'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    enable_analytic = fields.Boolean(string='Enable analytic', compute="_enable_analytic")

    @api.depends('name')
    def _enable_analytic(self):
        for rec in self:
            if rec.env['ir.config_parameter'].sudo().get_param('base_setup.is_analytic') == "True":
                rec.enable_analytic = True
            else:
                rec.enable_analytic = False