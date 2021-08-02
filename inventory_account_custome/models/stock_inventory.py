# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Inventory(models.Model):
    _inherit = "stock.inventory"

    account_move_ids = fields.One2many('account.move', 'stock_inventory_id', string="Inventory")

    def _compute_has_account_moves(self):
        for inventory in self:
            if inventory.state == 'done' and inventory.move_ids:
                account_move = self.env['account.move'].search_count([
                    ('stock_inventory_id', '=', inventory.id)
                ])
                inventory.has_account_moves = account_move > 0
            else:
                inventory.has_account_moves = False

    def action_get_account_moves(self):
        self.ensure_one()
        action_ref = self.env.ref('account.action_move_journal_line')
        if not action_ref:
            return False
        action_data = action_ref.read()[0]
        action_data['domain'] = [('stock_inventory_id', '=', self.id)]
        action_data['context'] = dict(self._context, create=False)
        return action_data

    def _create_account_move(self):
        entry_lines = []
        for line in self.move_ids:
            credit_account = line.location_id.account_id or False
            debit_account = line.location_dest_id.account_id or False
            if not credit_account:
                raise UserError(_("Please define stock  '%s' account !!") % line.location_id.name)
            if not debit_account:
                raise UserError(_("Please define stock  '%s' account !!") % line.location_id.name)

            for move in line.account_move_ids:
                for move_line in move.line_ids:
                    if credit_account and debit_account:
                        if move_line.credit and not move_line.debit:
                            credit_entry_line = {
                                'account_id': credit_account.id,
                                'name': move_line.name,
                                'debit': 0.0,
                                'credit': move_line.credit,
                                'company_id': move_line.company_id.id,
                                'company_currency_id': move_line.company_id.currency_id.id,
                            }

                            move_line.update(credit_entry_line)
                            entry_lines.append((0, 0, credit_entry_line))
                        if move_line.debit and not move_line.credit:
                            debit_entry_line = {
                                'account_id': debit_account.id,
                                'name': move_line.name,
                                'debit': move_line.debit,
                                'credit': 0.0,
                                'company_id': move_line.company_id.id,
                                'company_currency_id': move_line.company_id.currency_id.id,
                            }
                            move_line.update(debit_entry_line)
                            entry_lines.append((0, 0, debit_entry_line))
                #move.sudo().state = 'draft'
                #move.sudo().with_context({'force_delete': True}).unlink()

        return entry_lines 

    def action_validate(self):
        res = super(Inventory, self).action_validate()
        if self.account_move_ids :
            for move in self.account_move_ids:
                move.post()

        return res
