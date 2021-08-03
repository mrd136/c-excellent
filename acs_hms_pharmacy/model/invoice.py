# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError, RedirectWarning, Warning

class AccountMove(models.Model):
    _inherit = "account.move"

    patient_id = fields.Many2one('hms.patient',string="Patient")
    pharmacy_invoice = fields.Boolean("Pharmacy Invoice", copy=False)
    prescription_id = fields.Many2one('prescription.order',  string='Prescription')

    @api.model
    def assign_invoice_lots(self, picking):
        MoveLine = self.env['stock.move.line']
        for line in self.invoice_line_ids:
            quantity = line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id)
            if line.batch_no:
                move_line_id = MoveLine.search([('product_id', '=', line.product_id.id),('picking_id','=',picking.id),('qty_done','=',quantity),('lot_id','=',False)],limit=1)
                if move_line_id:
                    move_line_id.lot_id = line.batch_no.id
                    move_line_id.quantity_done = quantity

    def get_scan_line_data(self, product, lot=False):
        res = super(AccountMove, self).get_scan_line_data(product, lot)
        res['batch_no'] = lot and lot.id or False
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_id = fields.Many2one(domain=[('sale_ok', '=', True),('hospital_product_type', '=', 'medicament')])
    batch_no = fields.Many2one("stock.production.lot", domain=[('locked', '=', False)], string="Batch Number")
    exp_date = fields.Datetime(string="Expiry Date")

    @api.onchange('quantity', 'batch_no')
    def onchange_batch(self):
        if self.batch_no and self.move_id.type=='out_invoice':
            if self.batch_no.product_qty < self.quantity:
                batch_product_qty = self.batch_no.product_qty
                self.batch_no = False
                warning = {
                    'title': "Warning",
                    'message': _("Selected Lot do not have enough qty. %s qty needed and lot have only %s" %(self.quantity,batch_product_qty)),
                }
                return {'warning': warning}

            self.exp_date = self.batch_no.use_date
            if self.batch_no.mrp:
                self.price_unit = self.batch_no.mrp

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        if self.move_id and self.product_id and self.move_id.type =='in_invoice':
            self.product_uom_id = self.product_id.uom_po_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: