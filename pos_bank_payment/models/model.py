from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, UserError, ValidationError
# from datetime import datetime
# import odoo.addons.decimal_precision as dp
# from odoo.tools.float_utils import float_round, float_compare

#################################################################################################################
# inherit the pos.payment.method model
#################################################################################################################

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_bank = fields.Boolean('Bank Payment')
    bk_journal_id = fields.Many2one('account.journal', string='Bank Journal')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', required=True, readonly=False,
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")

    @api.onchange('is_bank')
    def _onchange_is_bank(self):
        # super(PosPaymentMethod, self)._onchange_is_cash_count()
        if not self.is_bank:
            self.bk_journal_id = False
            self.payment_method_id = False
            self.is_bank = False
        # if self.is_bank and self.is_cash_count:
        #     self.is_cash_count = False

#################################################################################################################
# inherit the pos.payment model
#################################################################################################################

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment'

    bk_payment_id = fields.Many2one('account.payment', 'Bank Payment Linked')

#################################################################################################################
# inherit the pos.session model
#################################################################################################################

class PosSession(models.Model):
    _inherit = 'pos.session'

    def action_pos_session_closing_control(self):
        super(PosSession, self).action_pos_session_closing_control()
        for rec in self:
            pos_payment_method_ids = self.env['pos.payment.method'].sudo().search([('is_bank', '=', True), ('id', 'in', rec.config_id.payment_method_ids.ids or [])])
            for pos_method in pos_payment_method_ids:
                payment_ids = self.env['pos.payment'].sudo().search([('session_id.id', '=', rec.id), ('payment_method_id.id', '=', pos_method.id), ('bk_payment_id', '=', False)])
                pay_amount = sum(payment.amount for payment in payment_ids if payment_ids) or 0
                if payment_ids and pay_amount > 0 and pos_method.bk_journal_id and pos_method.payment_method_id:
                    payment_created = self.env['account.payment'].sudo().create({
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'communication': rec.name,
                        'journal_id': pos_method.bk_journal_id.id,
                        'payment_method_id': pos_method.payment_method_id.id,
                        'destination_account_id': pos_method.receivable_account_id.id,
                        #'doc_branch_id': rec.app_branch_id.id,
                        'amount': pay_amount
                    })
                    if payment_created:
                        payment_created.write({'destination_account_id': pos_method.receivable_account_id.id})
                        payment_created.post()
                        account_move_lines_to_reconcile = self.env['account.move.line']
                        # + rec.move_id.line_ids
                        for line in payment_created.move_line_ids + rec.move_id.line_ids:
                            if line.account_id.id == pos_method.receivable_account_id.id and line.account_id.reconcile:
                                account_move_lines_to_reconcile |= line
                        account_move_lines_to_reconcile.reconcile()
                        payment_ids.write({'bk_payment_id': payment_created.id})
         #   rec.move_id.doc_branch_id = rec.app_branch_id.id