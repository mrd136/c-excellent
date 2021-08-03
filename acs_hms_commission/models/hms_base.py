# -*- coding: utf-8 -*-

from odoo import fields, models, api, SUPERUSER_ID

class ResPartner(models.Model):
    _inherit = "res.partner"

    commission_role_id = fields.Many2one('acs.commission.role', string='Role')
    commission_ids = fields.One2many('acs.hms.commission', 'partner_id', 'Business Commission')
    provide_commission = fields.Boolean('Give Commission')
    commission_percentage = fields.Float('Commission Percentage')
    commission_rule_ids = fields.One2many("acs.commission.rule", "partner_id", string="Commission Rules")
    
    #ACSNOTE: Remove in v14 later we did schema changes so added it
    def __init__(self, pool, cr):
        """ Override of __init__ to add fields."""
        try:
            env = api.Environment(cr, SUPERUSER_ID, {})
            cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='res_partner' and column_name='commission_role_id'")
            commission_role_id = cr.dictfetchone()
            if not commission_role_id:
                cr.execute(
                    "ALTER TABLE res_partner ADD COLUMN commission_role_id INTEGER"
                )

        except:
            pass
        return super(ResPartner, self).__init__(pool, cr)

    def commission_action(self):
        action = self.env.ref('acs_hms_commission.acs_hms_commission_action').read()[0]
        action['domain'] = [('partner_id','=',self.id)]
        action['context'] = {'default_partner_id': self.id, 'search_default_not_invoiced': 1}
        return action


class Physician(models.Model):
    _inherit = "hms.physician"

    def commission_action(self):
        action = self.env.ref('acs_hms_commission.acs_hms_commission_action').read()[0]
        action['domain'] = [('partner_id','=',self.partner_id.id)]
        action['context'] = {'default_partner_id': self.partner_id.id, 'search_default_not_invoiced': 1}
        return action


class Appointment(models.Model):
    _inherit = "hms.appointment"

    def create_invoice(self):
        res = super(Appointment, self).create_invoice()
        for rec in self:
            rec.invoice_id.onchange_total_amount()
            rec.invoice_id.onchange_ref_physician()
            rec.invoice_id.onchange_physician()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: