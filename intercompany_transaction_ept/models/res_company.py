"""
For inter_company_transfer_ept module.
"""
from odoo import fields, models


class ResCompany(models.Model):
    """
    Inherited for adding configuration for inter company transfers.
    @author: Maulik Barad on Date 24-Sep-2019.
    """
    _inherit = "res.company"

    sale_journal_id = fields.Many2one('account.journal', check_company=True,
                                      help="Sale Journal for creating invoice on.")
    purchase_journal_id = fields.Many2one('account.journal', check_company=True,
                                          help="Purchase Journal for creating vendor bill on.")
    property_stock_account_input_company_id = fields.Many2one(
        'account.account', 'Stock Input Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When doing automated inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account,
                unless there is a specific valuation account set on the source location. This is the default value for all products in this category.
                It can also directly be set on each product.""")
    property_stock_account_output_company_id = fields.Many2one(
        'account.account', 'Stock Output Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When doing automated inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account,
                    unless there is a specific valuation account set on the destination location. This is the default value for all products in this category.
                    It can also directly be set on each product.""")
    pos_warehouse_id = fields.Many2one('stock.warehouse', string="POS Warehouse")
    pos_location_id = fields.Many2one('stock.location', string="POS Location")
    pos_transit_location_id = fields.Many2one('stock.location', string="POS Transit Location")
    pos_other_transit_location_id = fields.Many2one('stock.location', string="POS Other Companies Transit Location")
