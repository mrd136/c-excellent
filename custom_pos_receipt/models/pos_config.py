from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.http import request
from odoo.addons.ehcs_qr_code_base.models.qr_code_base import generate_qr_code

class PosOrder(models.Model):
    _inherit = 'pos.order'

    qr_image = fields.Binary("QR Code", compute='_generate_qr_code')

    def _generate_qr_code(self):
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        text = "Price: 13.00 \n Reference: 00001"
        self.qr_image = generate_qr_code(text)

    @api.model
    def generate_qrcode(self, text):
        return generate_qr_code(text)

    def unlink(self):
        for pos_order in self.filtered(lambda pos_order: pos_order.state not in ['draft', 'cancel']):
            raise UserError(_('In order to delete a sale, it must be new or cancelled.'))
        if self.state == 'draft':
            for payment in self.payment_ids:
                payment.unlink()
        return super(PosOrder, self).unlink()

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = []
        for order in orders:
            existing_order = False
            if 'server_id' in order['data']:
                existing_order = self.env['pos.order'].search(
                    ['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])],
                    limit=1)
            if (existing_order and existing_order.state == 'draft') or not existing_order:
                order_ids.append(self._process_order(order, draft, existing_order))
            if existing_order and existing_order.state != 'draft':
                order['data']['name'] = order['data']['name'] + '-Duplicated'
                existing_order = False
                order_ids.append(self._process_order(order, draft, existing_order))

        return self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)], fields=['id', 'pos_reference'])


class PosSession(models.Model):

    _inherit = 'pos.session'

    total_return = fields.Float(string='Total Return', compute='_get_total_return')

    def _get_total_return(self):
        for r in self:
            self.env.cr.execute("""
                        SELECT
                        sum(amount_total) as total
                        FROM pos_order
                        WHERE session_id = %s
                        AND amount_total < 0
                    """, (r.id,))
            for res in self.env.cr.dictfetchall():
                r.total_return = res['total']

    def action_pos_session_close(self):
        # Session without cash payment method will not have a cash register.
        # However, there could be other payment methods, thus, session still
        # needs to be validated.
        if not self.cash_register_id:
            return self._validate_session()

        if self.cash_control and abs(self.cash_register_difference) > self.config_id.amount_authorized_diff:
            # Only pos manager can close statements with cash_register_difference greater than amount_authorized_diff.
            if not self.user_has_groups("point_of_sale.group_pos_manager"):
                # raise UserError(_(
                #     "Your ending balance is too different from the theoretical cash closing (%.2f), "
                #     "the maximum allowed is: %.2f. You can contact your manager to force it."
                # ) % (self.cash_register_difference, self.config_id.amount_authorized_diff))
                raise UserError(_(
                    "Your ending balance is too different from the theoretical cash closing "
                    "You can contact your manager to force it."
                ))
            else:
                return self._warning_balance_closing()
        else:
            return self._validate_session()

    def _validate_session(self):
        self.ensure_one()
        self._check_if_no_draft_orders()
        # Users without any accounting rights won't be able to create the journal entry. If this
        # case, switch to sudo for creation and posting.
        sudo = False
        if (
            not self.env['account.move'].check_access_rights('create', raise_exception=False)
            and self.user_has_groups('point_of_sale.group_pos_user')
        ):
            sudo = True
            self.sudo()._create_account_move()
        else:
            self._create_account_move()
        if self.move_id.line_ids:
            self.move_id.post() if not sudo else self.move_id.sudo().post()
            # Set the uninvoiced orders' state to 'done'
            self.env['pos.order'].search([('session_id', '=', self.id), ('state', '=', 'paid')]).write({'state': 'done'})
        else:
            # The cash register needs to be confirmed for cash diffs
            # made thru cash in/out when sesion is in cash_control.
            if self.config_id.cash_control:
                self.cash_register_id.button_confirm_bank()
            self.move_id.unlink()
        self.write({'state': 'closed'})
        # return {
        #     'type': 'ir.actions.client',
        #     'name': 'Point of Sale Menu',
        #     'tag': 'reload',
        #     'params': {'menu_id': self.env.ref('point_of_sale.menu_point_root').id},
        # }


class Configuration(models.Model):

    _inherit = 'pos.config'

    exepted_products = fields.Many2many('product.product',string='Excluded products',help="Selected products will never shows in this POS.",domain=[('available_in_pos','=',True)])
    neighborhood_ids = fields.One2many('pos.neighborhood', 'pos_config_id', string='Delivery Neighborhoods', domain="[('pos_config_id', '=?', id)]")
    receipt_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Receipt Operation Type',
        domain="[('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)]",
        ondelete='restrict')


class PosCity(models.Model):
    _name = 'pos.neighborhood'

    pos_config_id = fields.Many2one('pos.config', string='Point Of Sale', required=True)
    country = fields.Many2one('res.country', string='Country', default=lambda self: self.env.user.company_id.country_id, required=True)
    state = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=?', country)]", required=True)
    name = fields.Char(string='Name', required=True)
    delivery_fees = fields.Float(string='Delivery Fees', required=True)

    @api.onchange('delivery_fees')
    def change_delivery_fees(self):
        for r in self:
            if r.delivery_fees <= 0:
                raise ValidationError("Delivery Fees should be greater than zero")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    neighborhood_id = fields.Many2one('pos.neighborhood', string='Neighborhood', domain="[('state', '=?', state_id)]")
    delivery_fees = fields.Float(string='Delivery Fees', related='neighborhood_id.delivery_fees')
    is_pos_partner = fields.Boolean(string='Is Pos Partner?')

    @api.model
    def create_from_ui(self, partner):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """
        # image is a dataurl, get the data after the comma
        if partner.get('image_1920'):
            partner['image_1920'] = partner['image_1920'].split(',')[1]
        partner_id = partner.pop('id', False)
        if partner_id:  # Modifying existing partner
            self.browse(partner_id).write(partner)
        else:
            partner['lang'] = self.env.user.lang
            #partner['is_pos_partner'] = True
            partner_id = self.create(partner).id
        return partner_id


class Product(models.Model):
    _inherit = 'product.product'

    def _get_ar_trans(self):
        for rec in self:
            rec.ar_trans = False
            trans = self.env['ir.translation'].search([('name', '=', 'product.template,name'),
                                                       ('type', '=', 'model'),
                                                       ('lang', '=', 'ar_001'),
                                                       ('res_id', '=', rec.product_tmpl_id.id)], limit=1)
            if trans:
                rec.write({'ar_trans': trans.value})

    def _get_en_trans(self):
        for rec in self:
            rec.en_trans = False
            trans = self.env['ir.translation'].search([('name', '=', 'product.template,name'),
                                                       ('type', '=', 'model'),
                                                       ('lang', '=', 'en_US'),
                                                       ('res_id', '=', rec.product_tmpl_id.id)], limit=1)
            if trans:
                rec.write({'en_trans': trans.value})

    ar_trans = fields.Char(string='arabic translation', compute='_get_ar_trans', store=True)
    en_trans = fields.Char(string='english translation', compute='_get_en_trans', store=True)

    @api.depends('name')
    def _get_arabic_translate(self):
        for rec in self:
            rec.ar_trans = False
            rec.en_trans = False
            trans = self.env['ir.translation'].search([('name','=','product.template,name'),
                                                          ('type','=','model'),
                                                          ('res_id','=',rec.product_tmpl_id.id)])
            if trans:
                for r in trans:
                    if r.lang == 'ar_001':
                        rec.write({'ar_trans': r.value})
                    if r.lang == 'en_US':
                        rec.write({'en_trans': r.value})

    @api.model
    def create(self, values):
        product = super(Product, self).create(values)
        product._get_en_trans()
        product._get_ar_trans()
        return product


class Translation(models.Model):
    _inherit = 'ir.translation'

    def write(self, values):
        translation = super(Translation, self).write(values)
        for r in self:
            if r.name == 'product.template,name' and r.type == 'model':
                product_id = self.env['product.product'].search([('product_tmpl_id', '=', r.res_id)])
                if product_id:
                    if r.lang == 'ar_001':
                        product_id.write({'ar_trans': r.value})
                    if r.lang == 'en_US':
                        product_id.write({'en_trans': r.value})


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_hour = fields.Char(string='Order Hour')

    def _calculate_order_hour(self):
        for r in self:
            if not r.order_hour:
                order_datetime = datetime.strptime(str(r.date_order),DEFAULT_SERVER_DATETIME_FORMAT)
                new_hour_datetime = str(order_datetime.year)+'-'+ str(order_datetime.month) +'-'+ str(order_datetime.day) +' '+str(order_datetime.hour) +':00:00'
                r.order_hour = datetime.strptime(str(new_hour_datetime), DEFAULT_SERVER_DATETIME_FORMAT)


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    order_hour = fields.Char(string='Order Hour')

    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                COUNT(*) AS nbr_lines,
                s.date_order AS date,
                s.order_hour AS order_hour,
                SUM(l.qty) AS product_qty,
                SUM(l.qty * l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_sub_total,
                SUM((l.qty * l.price_unit) * (100 - l.discount) / 100 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_total,
                SUM((l.qty * l.price_unit) * (l.discount / 100) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS total_discount,
                (SUM(l.qty*l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)/SUM(l.qty * u.factor))::decimal AS average_price,
                SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                s.id as order_id,
                s.partner_id AS partner_id,
                s.state AS state,
                s.user_id AS user_id,
                s.location_id AS location_id,
                s.company_id AS company_id,
                s.sale_journal AS journal_id,
                l.product_id AS product_id,
                pt.categ_id AS product_categ_id,
                p.product_tmpl_id,
                ps.config_id,
                pt.pos_categ_id,
                s.pricelist_id,
                s.session_id,
                s.account_move IS NOT NULL AS invoiced
        """

    def _group_by(self):
        return """
            GROUP BY
                s.id, s.date_order, s.partner_id,s.state, pt.categ_id,s.order_hour,
                s.user_id, s.location_id, s.company_id, s.sale_journal,
                s.pricelist_id, s.account_move, s.create_date, s.session_id,
                l.product_id,
                pt.categ_id, pt.pos_categ_id,
                p.product_tmpl_id,
                ps.config_id
        """


class ProductPricelistCustom(models.Model):
    _inherit = 'product.pricelist'

    pricelist_type = fields.Selection([('normal', 'Normal'), ('employee', 'Employee Price list')], string='Price list type', default='normal', required=True)

