# See LICENSE file for full copyright and licensing details.

from odoo import api,fields,models

def is_module_installed(env, module_name):
    """ Check if an Odoo addon is installed.

    :param module_name: name of the addon
    """
    # the registry maintains a set of fully loaded modules so we can
    # lookup for our module there
    return module_name in env.registry._init_modules

class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _default_is_pos_restaurant(self):
        return is_module_installed(self.env, 'pos_restaurant')

    
    def _is_pos_restaurant(self):
        self.is_pos_restaurant = is_module_installed(self.env, 'pos_restaurant')

    is_pos_restaurant = fields.Boolean(compute='_is_pos_restaurant', string='Is Pos Restaurant', default= _default_is_pos_restaurant)
    orderline_note = fields.Boolean('Orderline Note', default=True, help='Allow custom notes on Orderlines',domain=[()])
    order_remark = fields.Boolean('Order Remark', default=False, help='Allow custom Remark on Order')
    print_orderline_note = fields.Boolean('Print Orderline Note', default=True, help='Prints order line notes on POS receipt',domain=[()])
    print_order_remark = fields.Boolean('Print Order Remark', default=True, help='Prints order line notes on POS receipt')

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    note = fields.Text("Notes")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_remark = fields.Text("Order Notes")

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['order_remark'] = ui_order.get('order_remark', '')
        return order_fields
