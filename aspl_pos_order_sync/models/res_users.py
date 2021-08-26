from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
from pytz import timezone
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_is_zero

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    # pos_user_type = fields.Selection(related='user_id.pos_user_type', store=1)
    pos_user_type = fields.Selection([('cashier', 'Cashier'), ('salesman', 'Sales Person')], string="POS User Type",
                                     default='salesman')
    can_give_discount = fields.Boolean("Can Give Discount")
    can_change_price = fields.Boolean("Can Change Price")
    discount_limit = fields.Float("Discount Limit")
    # based_on = fields.Selection([('pin', 'Pin'), ('barcode', 'Barcode')],
    #                             default='barcode', string="Authenticaion Based On")
    sales_persons = fields.Many2many('hr.employee', 'sales_person_rel', 'sales_person_id', 'employee_id',
                                     string='Sales Person')
    # barcode = fields.Char(help="Use a barcode to identify this contact from the Point of Sale.", copy=False)

# class HrEmployeePublic(models.Model):
#     _inherit = "hr.employee.public"
#
#     pos_user_type = fields.Selection(related='user_id.pos_user_type', store=1)
#
# class HrEmployee(models.Model):
#     _inherit = "hr.employee"
#
#     pos_user_type = fields.Selection(related='user_id.pos_user_type', store=1)



# class ResUsers(models.Model):
#     _inherit = "res.users"
#
#     pos_security_pin = fields.Char(string='Security PIN', size=32,
#                                    help='A Security PIN used to protect sensible functionality in the Point of Sale')
#
#     @api.constrains('pos_security_pin')
#     def _check_pin(self):
#         if self.pos_security_pin and not self.pos_security_pin.isdigit():
#             raise UserError(_("Security PIN can only contain digits"))
#
#     barcode = fields.Char(help="Use a barcode to identify this contact from the Point of Sale.", copy=False)