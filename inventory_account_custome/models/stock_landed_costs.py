# -*- coding: utf-8 -*-


from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    location_id = fields.Many2one('stock.location', 'Location', domain="[('usage','=','internal')]")

    def action_account_move(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['context'] = {'default_type': 'entry'}
        action['view_mode'] = 'tree'
        action['domain'] = [('id', '=', self.account_move_id.id)]
        return action

    def button_validate(self):
        res = super(LandedCost, self).button_validate()
        if self.location_id:
            if not self.location_id.account_id:
                raise UserError(_('Please define location (%s) account !!') % self.location_id.name)
        account_list = []
        for picking in self.picking_ids:
            for move in picking.move_ids_without_package:
                accounts = move.product_id.product_tmpl_id.get_product_accounts()
                account_list.append(accounts.get('stock_valuation') and accounts['stock_valuation'].id or False)

        for rec in self.account_move_id.line_ids:
            if rec.account_id.id in account_list:
                rec.write({'account_id': self.location_id.account_id.id})

        return res
