# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.env['ir.config_parameter'].sudo().get_param('base_setup.is_analytic') == "True":
            if self.picking_type_id.code == 'outgoing':
                for ln in self.move_ids_without_package:
                    move_id = self.env['account.move'].search([('ref', '=', ln.product_id.display_name)], limit=1, order="id desc")
                    # print(self.picking_type_id, ">>>>>>>>>1 ", move_id )
                    for line in move_id.line_ids:
                        if line.debit > 0:
                            line.analytic_account_id = self.location_id.analytic_account_id.id
                    # move_line_id = self.env['account.move.line'].search([
                    #     ('product_id', '=', ln.product_id.id),
                    #     ('debit', '>', 0),
                    # ],order="id desc", limit=1)
                    # move_line_id.analytic_account_id = self.location_id.analytic_account_id.id
            elif self.picking_type_id.code == 'incoming':
                for ln in self.move_ids_without_package:
                    move_id = self.env['account.move'].search([('ref', '=', ln.product_id.display_name)], limit=1, order="id desc")
                    # print(self.picking_type_id, ">>>>>>>>>2 ", move_id )
                    for line in move_id.line_ids:
                        # print(">>>>>>>>>>>>. ", line.credit)
                        if line.credit > 0:
                            line.analytic_account_id = self.location_dest_id.analytic_account_id.id
                    # move_line_id = self.env['account.move.line'].search([
                    #     ('product_id', '=', ln.product_id.id),
                    #     ('credit', '>', 0),
                    # ],order="id desc", limit=1)
                    # move_line_id.analytic_account_id = self.location_id.analytic_account_id.id
            elif self.picking_type_id.code == 'internal':
                if len(self.move_ids_without_package.ids)>0:
                    for ln in self.move_ids_without_package:
                        move_id = self.env['account.move'].create({
                            'journal_id': self.move_ids_without_package[0].product_id.categ_id.property_stock_journal.id,
                            'partner_id': self.partner_id.id,
                            'ref': "Internal Transfer , " + self.name,
                        })
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id': move_id.id,
                            'name': ln.product_id.name,
                            'analytic_account_id': self.location_id.analytic_account_id.id,
                            'account_id': ln.product_id.categ_id.property_stock_valuation_account_id.id,
                            'credit': ln.product_id.standard_price * ln.product_uom_qty,
                            'debit': 0.0,
                        })
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id': move_id.id,
                            'analytic_account_id': self.location_dest_id.analytic_account_id.id,
                            'name': ln.product_id.name,
                            'account_id': ln.product_id.categ_id.property_stock_valuation_account_id.id,
                            'debit': ln.product_id.standard_price * ln.product_uom_qty,
                            'credit': 0.0,
                        })
                        move_id.post()
        return res



class StockMove(models.Model):
    _inherit="stock.move"

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        res = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description)
        for line in res:
            product_id = self.env['product.product'].browse(int(res[line]['product_id']))
            if product_id.categ_id.property_stock_valuation_account_id.id == res[line]['account_id'] and res[line]['debit'] > 0:
                res[line].update({
                    'analytic_account_id': self.location_dest_id.analytic_account_id.id
                })
            if product_id.categ_id.property_stock_valuation_account_id.id == res[line]['account_id'] and res[line]['credit'] > 0:
                res[line].update({
                    'analytic_account_id': self.location_id.analytic_account_id.id
                })
        return res

