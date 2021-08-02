from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ConsumReport(models.TransientModel):
    _name = 'consum.report.wizard'
    _description = 'Consumption Wizard'

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    pos_config_id = fields.Many2one('pos.config', string="POS", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)

    # @api.onchange('start_date')
    # def _onchange_start_date(self):
    #     if self.start_date and self.end_date and self.end_date < self.start_date:
    #         self.end_date = self.start_date
    #
    # @api.onchange('end_date')
    # def _onchange_end_date(self):
    #     if self.end_date and self.end_date < self.start_date:
    #         self.start_date = self.end_date

    def generate_report(self):
        if not self.env.company.logo:
            raise UserError(_("You have to set a logo or a layout for your company."))
        elif not self.env.company.external_report_layout_id:
            raise UserError(_("You have to set your report's header and footer layout."))
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'config_id': self.pos_config_id.id,
                'product_id': self.product_id.id}
        return self.env.ref('custom_pos_receipt.consum_report').report_action([], data=data)
