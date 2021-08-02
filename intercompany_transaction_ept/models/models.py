# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class StockLocation(models.Model):
    _inherit = "stock.location"

    code = fields.Char('Code')
    owner_ids = fields.Many2many('res.partner', string='Owner')
    is_transfer_location = fields.Boolean('Is Transit Transfer Location?')
    account_id = fields.Many2one('account.account', string='Account')
    customer_valuation_account_id = fields.Many2one('account.account', string='Customer Valuation Account')
    # vendor_valuation_account_id = fields.Many2one('account.account', string='Vendor Valuation Account')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')


class StockMove(models.Model):
    _inherit = "stock.move"

    transfer_line_id = fields.Many2one('transfer.request.line', 'Transfer Line', index=True)
    deliver_type = fields.Selection([('deliver', 'Deliver'), ('receipt', 'Receipt')])

    # def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
    #                               cost):
    #     self.ensure_one()
    #     AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
    #     # new_move_lines = []
    #     move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
    #     if move_lines:
    #         move_exist = False
    #         date = self._context.get('force_period_date', fields.Date.context_today(self))
    #         # picking_id = self.env['stock.picking'].search([('id','=',self.picking_id.id)])
    #         # inventory_id = self.env['stock.inventory'].search([('id','=',self.reference.replace('INV:', ''))])
    #
    #         if self.picking_id:
    #             move_exist = self.env['account.move'].search([('picking_id', '=', self.picking_id.id)])
    #         if self.inventory_id:
    #             move_exist = self.env['account.move'].search([('stock_inventory_id', '=', self.inventory_id.id)])
    #
    #         if not move_exist:
    #             new_account_move = AccountMove.sudo().create({
    #                 'journal_id': journal_id,
    #                 'line_ids': move_lines,
    #                 'date': date,
    #                 'ref': description,
    #                 'stock_move_id': self.id,
    #                 'stock_valuation_layer_ids': [(6, None, [svl_id])],
    #                 'type': 'entry',
    #                 'picking_id': self.picking_id.id,
    #                 'stock_inventory_id': self.inventory_id.id
    #             })
    #
    #             self.write({'account_move_ids': [(4, new_account_move.id)]})
    #         else:
    #             move_exist.write({'line_ids': move_lines})
    #             self.write({'account_move_ids': [(4, move_exist.id)]})


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')


class AccountMove(models.Model):
    _inherit = "account.move"

    picking_id = fields.Many2one('stock.picking', 'Stock Picking')
    stock_inventory_id = fields.Many2one('stock.inventory', string='Stock inventory', index=True)


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

        return entry_lines

    def action_validate(self):
        res = super(Inventory, self).action_validate()
        if self.account_move_ids:
            for move in self.account_move_ids:
                move.post()

        return res


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


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    is_return = fields.Boolean('Is Return', default=False)

    def action_account_move(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['context'] = {'default_type': 'entry'}
        action['view_mode'] = 'tree'
        action['domain'] = [('picking_id', 'in', self.ids)]
        return action

    def action_view_return(self):
        stock_move = self.env['stock.move'].search([('origin_returned_move_id.picking_id', 'in', self.ids)]).picking_id
        picking_return = self.env['stock.picking'].search([('id', '=', stock_move.ids)])
        return {
            'name': _('Return'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree',
            'view_id': self.env.ref('stock.vpicktree').id,
            'domain': [('id', 'in', picking_return.ids)]
        }

    def _calculate_account_move(self, debit_account, credit_account):
        entry_lines = []
        move = self.move_ids_without_package.filtered(lambda r: r.account_move_ids)
        if move:
            for line in self.move_ids_without_package:
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
                                if move.picking_id.inter_company_transfer_id.type == 'pos' and move.picking_id.picking_type_id.code == 'incoming':
                                    account_analytic_id = move.picking_id.inter_company_transfer_id.pos_config.account_analytic_id
                                    debit_entry_line = {
                                        'account_id': debit_account.id,
                                        'name': move_line.name,
                                        'debit': move_line.debit,
                                        'credit': 0.0,
                                        'analytic_account_id': account_analytic_id.id,
                                        'company_id': move_line.company_id.id,
                                        'company_currency_id': move_line.company_id.currency_id.id,
                                    }
                                move_line.update(debit_entry_line)
                                entry_lines.append((0, 0, debit_entry_line))
                    move.sudo().button_draft()
        else:
            for move in self.move_ids_without_package:
                if move.product_id.type == 'product':
                    if credit_account and debit_account:
                        debit_amount = credit_amount = (move.product_id.standard_price * move.product_uom_qty) or 0.0
                        if move.purchase_line_id:
                            debit_amount = credit_amount = (move.purchase_line_id.price_unit * move.product_uom_qty) or 0.0
                        if move.sale_line_id:
                            debit_amount = credit_amount = (move.sale_line_id.price_unit * move.product_uom_qty) or 0.0
                        credit_entry_line = {
                            'account_id': credit_account.id,
                            'name': move.name + ' - ' + move.product_id.name,
                            'debit': 0.0,
                            'credit': credit_amount,
                            'company_id': self.company_id.id,
                            'company_currency_id': self.company_id.currency_id.id,
                        }
                        entry_lines.append((0, 0, credit_entry_line))
                        debit_entry_line = {
                            'account_id': debit_account.id,
                            'name': move.name + ' - ' + move.product_id.name,
                            'debit': debit_amount,
                            'credit': 0.0,
                            'company_id': self.company_id.id,
                            'company_currency_id': self.company_id.currency_id.id,
                        }
                        if move.picking_id.inter_company_transfer_id.type == 'pos' and move.picking_id.picking_type_id.code == 'incoming':
                            account_analytic_id = move.picking_id.inter_company_transfer_id.pos_config.account_analytic_id
                            if account_analytic_id:
                                debit_entry_line = {
                                    'account_id': debit_account.id,
                                    'name': move.name + ' - ' + move.product_id.name,
                                    'debit': debit_amount,
                                    'credit': 0.0,
                                    'analytic_account_id': account_analytic_id.id,
                                    'company_id': self.company_id.id,
                                    'company_currency_id': self.company_id.currency_id.id,
                                }
                        entry_lines.append((0, 0, debit_entry_line))
            for move in self.move_ids_without_package:
                journal_id = move.product_id.categ_id.property_stock_journal
                if not journal_id:
                    raise UserError(
                        _("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
            val = {
                'ref': self.name,
                'line_ids': entry_lines,
                'picking_id': self.id,
                'journal_id': journal_id.id,
                'state': 'draft',
            }
            if move.product_id.categ_id.property_valuation != 'real_time':
                move = False
            elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'service':
                move = False
            elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'product':
                move = self.env['account.move'].sudo().create(val)
            elif move.product_id.categ_id.property_valuation == 'real_time' and move.product_id.type == 'consu':
                move = False

        return move

    def _material_account_moves(self, is_return):
        entry_lines = []
        res = False
        pos_analytic_account = False
        for move in self.move_ids_without_package:
            if move.product_id.type == 'product' and move.product_id.categ_id.property_valuation == 'real_time':
                # # Get debit and credit accounts, throw validation error if not found
                if not is_return:
                    credit_account = self.location_id.account_id or False
                    debit_account = move.product_id.categ_id.property_stock_account_input_categ_id or False
                    if self.inter_company_transfer_id:
                        if self.inter_company_transfer_id.type == 'internal':
                            credit_account = self.location_id.account_id
                            debit_account = self.location_dest_id.account_id
                            if not credit_account:
                                raise UserError(_("Please define stock ( %s/%s ) account !!") % (
                                    self.location_id.location_id.name, self.location_id.name))
                            if not debit_account:
                                raise UserError(_("Please define stock ( %s/%s ) account !!") % (
                                    self.location_dest_id.location_id.name, self.location_dest_id.name))
                        if self.inter_company_transfer_id.type == 'pos':
                            if self.inter_company_transfer_id.source_company_id == self.inter_company_transfer_id.destination_company_id:
                                pos_analytic_account = self.inter_company_transfer_id.pos_config.account_analytic_id
                                credit_account = self.location_id.account_id
                                debit_account = self.location_dest_id.account_id
                                if not credit_account:
                                    raise UserError(_("Please define stock ( %s/%s ) account !!") % (
                                        self.location_id.location_id.name, self.location_id.name))
                                if not debit_account:
                                    raise UserError(_("Please define stock ( %s/%s ) account !!") % (
                                        self.location_dest_id.location_id.name, self.location_dest_id.name))
                            else:
                                if self.purchase_id:
                                    credit_account = move.product_id.categ_id.property_stock_account_input_categ_id
                                    debit_account = self.location_dest_id.account_id or False
                                    if not debit_account:
                                        raise UserError(
                                            _("Please define Account in location : %s") % self.location_dest_id.name)
                                elif self.sale_id:
                                    credit_account = self.location_id.account_id or False
                                    debit_account = self.location_id.customer_valuation_account_id
                                    if not credit_account:
                                        raise UserError(
                                            _("Please define Account in location : %s") % self.location_id.name)
                                    if not debit_account:
                                        raise UserError(
                                            _("Please define Customer Valuation Account in location : %s") % self.location_id.name)

                        if self.inter_company_transfer_id.type == 'ict':
                            if self.purchase_id:
                                credit_account = move.product_id.categ_id.property_stock_account_input_categ_id
                                debit_account = self.location_dest_id.account_id or False
                                if not debit_account:
                                    raise UserError(_("Please define Account in location : %s") % self.location_dest_id.name)
                            elif self.sale_id:
                                credit_account = self.location_id.account_id or False
                                debit_account = self.location_id.customer_valuation_account_id
                                if not credit_account:
                                    raise UserError(_("Please define stock ( %s/%s ) account !!") % (
                                        self.location_id.location_id.name, self.location_id.name))
                                if not debit_account:
                                    raise UserError(_("Please define Customer Valuation Account in location : %s") % self.location_id.name)
                    else:
                        if self.sale_id:
                            credit_account = self.location_id.account_id or False
                            debit_account = self.location_id.customer_valuation_account_id
                            if not debit_account:
                                raise UserError(
                                    _("Please define Customer Valuation Account in location : %s") % self.location_id.name)
                        if self.purchase_id:
                            credit_account = move.product_id.categ_id.property_stock_account_input_categ_id
                            debit_account = self.location_dest_id.account_id
                            if not debit_account:
                                raise UserError(
                                    _("Please define Account in location : %s") % self.location_dest_id.name)

                    analytic_account = False
                    if self.picking_type_code == 'incoming' and self.inter_company_transfer_id.type == 'pos':
                        pos_analytic_account = self.inter_company_transfer_id.pos_config.account_analytic_id
                        if pos_analytic_account:
                            analytic_account = pos_analytic_account.id
                    else:
                        analytic_account = False
                    debit_amount = credit_amount = (move.product_id.standard_price * move.product_uom_qty) or 0.0

                    if self.purchase_id:
                        if move.purchase_line_id:
                            debit_amount = credit_amount = (move.purchase_line_id.price_unit * move.product_uom_qty) or 0.0

                    credit_entry_line = {
                        'account_id': credit_account.id,
                        'name': 'Material Deliver / ' + move.product_id.name,
                        'debit': 0.0,
                        'credit': credit_amount,
                        'company_id': self.company_id.id,
                        'company_currency_id': self.company_id.currency_id.id
                    }
                    entry_lines.append((0, 0, credit_entry_line))
                    debit_entry_line = {
                        'account_id': debit_account.id,
                        'name': 'Material Deliver / ' + move.product_id.name,
                        'debit': debit_amount,
                        'credit': 0.0,
                        'company_id': self.company_id.id,
                        'company_currency_id': self.company_id.currency_id.id,
                        'analytic_account_id': analytic_account
                    }
                    entry_lines.append((0, 0, debit_entry_line))

                else:
                    debit_account = move.product_id.categ_id.property_stock_account_input_categ_id
                    credit_account = self.location_dest_id.account_id or False
                    analytic_account = self.env.user.department_id.analytic_account_id

                    debit_amount = credit_amount = (move.product_id.standard_price * move.product_uom_qty) or 0.0

                    credit_entry_line = {
                        'account_id': credit_account.id,
                        'name': 'Material Deliver / ' + move.product_id.name,
                        'debit': 0.0,
                        'credit': credit_amount,
                        'company_id': self.company_id.id,
                        'company_currency_id': self.company_id.currency_id.id,
                        'analytic_account_id': analytic_account.id

                    }
                    entry_lines.append((0, 0, credit_entry_line))
                    debit_entry_line = {
                        'account_id': debit_account.id,
                        'name': 'Material Deliver / ' + move.product_id.name,
                        'debit': debit_amount,
                        'credit': 0.0,
                        'company_id': self.company_id.id,
                        'company_currency_id': self.company_id.currency_id.id,
                    }
                    entry_lines.append((0, 0, debit_entry_line))

        for move in self.move_ids_without_package:
            journal_id = move.product_id.categ_id.property_stock_journal
            if not journal_id:
                raise UserError(
                    _("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
        val = {
            'ref': self.name,
            'line_ids': entry_lines,
            'picking_id': self.id,
            'journal_id': journal_id.id,
            'state': 'draft',
        }

        if len(entry_lines) > 0:
            res = self.env['account.move'].sudo().create(val)
        return res

    def action_done(self):
        res = super(StockPicking, self).action_done()
        is_return = False
        picking_id = None
        for rec in self.move_ids_without_package:
            if rec.origin_returned_move_id:
                is_return = True
                picking_id = rec.origin_returned_move_id.picking_id
            if self.sale_id and self.picking_type_id.code == 'incoming':
                picking_id = self
                is_return = True

                break

        if not is_return:
            new_move = self._material_account_moves(is_return)
            if new_move:
                for move in self.move_ids_without_package:
                    journal_id = move.product_id.categ_id.property_stock_journal
                    if not journal_id:
                        raise UserError(
                            _("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
                val = {
                    'ref': self.name,
                    # 'line_ids':lines,
                    'picking_id': self.id,
                    'journal_id': journal_id.id,
                    # 'state':'draft',
                }
                new_move.write(val)
                if new_move.state == 'draft':
                    new_move.post()

        else:
            if not picking_id.inter_company_transfer_id:
                if self.picking_type_id:
                    try:
                        if self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_dest_id:
                            credit_account = self.location_id.account_id or False
                            debit_account = self.location_dest_id.account_id or False
                            if credit_account and debit_account:
                                name = str(self.origin)
                                op_type = ""
                                if picking_id.sale_id:
                                    op_type = 'Sale'
                                    credit_account = self.picking_type_id.default_location_dest_id.account_id or False
                                    debit_account = self.env['stock.location'].sudo().search(
                                        [('usage', '=', 'customer')],
                                        limit=1).account_id  # .sale_id.team_id.cost_account_id
                                if picking_id.purchase_id:
                                    op_type = 'Purchase'

                                    debit_account = self.picking_type_id.default_location_src_id.account_id or False
                                    credit_account = self.picking_type_id.default_location_dest_id.account_id  # self.env['stock.location'].sudo().search([('usage', '=', 'supplier')],limit=1).account_id  # self.picking_type_id.default_location_src_id.account_id or False
                                if picking_id.transfer_id:
                                    op_type = picking_id.transfer_id.type
                                new_move = self._calculate_account_move(credit_account, debit_account)
                                for move in self.move_ids_without_package:
                                    journal_id = move.product_id.categ_id.property_stock_journal
                                    if not journal_id:
                                        raise UserError(
                                            _("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)

                                val = {
                                    'ref': self.name,
                                    # 'line_ids':lines,
                                    'picking_id': self.id,
                                    'journal_id': journal_id.id,
                                    # 'state':'draft',
                                }
                                new_move.write(val)
                                if new_move.state == 'draft':
                                    # account_move = self.env['account.move'].sudo().create(val)
                                    new_move.post()



                            # else:
                            #     if not credit_account:
                            #         raise ValidationError(_("7Please define stock (%s/%s) account !!") % (
                            #             self.picking_type_id.default_location_src_id.location_id.name,
                            #             self.picking_type_id.default_location_src_id.name))
                            #     if not debit_account:
                            #         raise ValidationError(_("8Please define stock (%s/%s) account !!") % (
                            #             self.picking_type_id.default_location_dest_id.location_id.name,
                            #             self.picking_type_id.default_location_dest_id.name))

                    except ValueError:
                        raise ValidationError(_("Please check sourse and destination location of picking!!"))


            else:
                new_move = self._material_account_moves(is_return)
                name = 'Matrial Request'

                for move in self.move_ids_without_package:
                    journal_id = move.product_id.categ_id.property_stock_journal
                    if not journal_id:
                        raise UserError(
                            _("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)
                val = {
                    'ref': self.name,
                    # 'line_ids':lines,
                    'picking_id': self.id,
                    'journal_id': journal_id.id,
                    # 'state':'draft',
                }
                new_move.write(val)
                if new_move.state == 'draft':
                    # account_move = self.env['account.move'].sudo().create(val)
                    new_move.post()
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        if self.inter_company_transfer_id.type == 'pos':
            if not self.inter_company_transfer_id.destination_company_id.pos_location_id:
                raise UserError(_("Please select Pos Location for this company %s") % self.inter_company_transfer_id.destination_company_id.name)
            if not self.inter_company_transfer_id.source_company_id.pos_other_transit_location_id:
                raise UserError(_("Please select Pos Other Company Transit Location for this company %s") % self.inter_company_transfer_id.source_company_id.name)
            return {
                'picking_type_id': self.picking_type_id.id,
                'partner_id': self.partner_id.id,
                'user_id': False,
                'date': self.date_order,
                'origin': self.name,
                'location_dest_id': self.inter_company_transfer_id.destination_company_id.pos_location_id.id,
                'location_id': self.inter_company_transfer_id.source_company_id.pos_other_transit_location_id.id,
                'company_id': self.company_id.id,
                'inter_company_transfer_id': self.inter_company_transfer_id.id
            }
        else:
            return {
                'picking_type_id': self.picking_type_id.id,
                'partner_id': self.partner_id.id,
                'user_id': False,
                'date': self.date_order,
                'origin': self.name,
                'location_dest_id': self._get_destination_location(),
                'location_id': self.partner_id.property_stock_supplier.id,
                'company_id': self.company_id.id,
                'inter_company_transfer_id': self.inter_company_transfer_id.id
            }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env['stock.move']
        incoming_moves = self.env['stock.move']

        for move in self.move_ids.filtered(lambda r: r.state != 'cancel' and not r.scrapped and self.product_id == r.product_id):
            if move.location_dest_id.usage == "supplier" and move.to_refund:
                outgoing_moves |= move
            elif move.location_dest_id.usage != "supplier":
                if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                    incoming_moves |= move

        return outgoing_moves, incoming_moves

    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        for move in incoming_moves:
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        description_picking = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)._get_description(self.order_id.picking_type_id)
        if self.order_id.inter_company_transfer_id.type == 'pos':
            template = {
                # truncate to 2000 to avoid triggering index limit error
                # TODO: remove index in master?
                'name': (self.name or '')[:2000],
                'product_id': self.product_id.id,
                'product_uom': self.product_uom.id,
                'date': self.order_id.date_order,
                'date_expected': self.date_planned,
                'location_id': self.order_id.inter_company_transfer_id.source_company_id.pos_other_transit_location_id.id,
                'location_dest_id': self.order_id.inter_company_transfer_id.destination_company_id.pos_location_id.id,
                'picking_id': picking.id,
                'partner_id': self.order_id.dest_address_id.id,
                'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
                'state': 'draft',
                'purchase_line_id': self.id,
                'company_id': self.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': self.order_id.picking_type_id.id,
                'group_id': self.order_id.group_id.id,
                'origin': self.order_id.name,
                'propagate_date': self.propagate_date,
                'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
                'description_picking': description_picking,
                'propagate_cancel': self.propagate_cancel,
                'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            }
        else:
            template = {
                # truncate to 2000 to avoid triggering index limit error
                # TODO: remove index in master?
                'name': (self.name or '')[:2000],
                'product_id': self.product_id.id,
                'product_uom': self.product_uom.id,
                'date': self.order_id.date_order,
                'date_expected': self.date_planned,
                'location_id': self.order_id.partner_id.property_stock_supplier.id,
                'location_dest_id': self.order_id._get_destination_location(),
                'picking_id': picking.id,
                'partner_id': self.order_id.dest_address_id.id,
                'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
                'state': 'draft',
                'purchase_line_id': self.id,
                'company_id': self.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': self.order_id.picking_type_id.id,
                'group_id': self.order_id.group_id.id,
                'origin': self.order_id.name,
                'propagate_date': self.propagate_date,
                'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
                'description_picking': description_picking,
                'propagate_cancel': self.propagate_cancel,
                'route_ids': self.order_id.picking_type_id.warehouse_id and [
                    (6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            po_line_uom = self.product_uom
            quant_uom = self.product_id.uom_id
            product_uom_qty, product_uom = po_line_uom._adjust_uom_quantities(diff_quantity, quant_uom)
            template['product_uom_qty'] = product_uom_qty
            template['product_uom'] = product_uom.id
            res.append(template)
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            if line.order_id.inter_company_transfer_id.type == 'pos':
                procurements.append(self.env['procurement.group'].Procurement(
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.inter_company_transfer_id.destination_company_id.pos_other_transit_location_id,
                    line.name, line.order_id.name, line.order_id.company_id, values))
            else:
                procurements.append(self.env['procurement.group'].Procurement(
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name, line.order_id.name, line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)
        return True