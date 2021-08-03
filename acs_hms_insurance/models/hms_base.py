# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError, RedirectWarning, Warning

import odoo.modules as addons
loaded_modules = addons.module.loaded

class ACSPatient(models.Model):
    _inherit = 'hms.patient'

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.claim_count = len(rec.claim_ids)

    claim_ids = fields.One2many('hms.insurance.claim', 'patient_id',string='Claims')
    claim_count = fields.Integer(compute='_rec_count', string='# Claims')
    insurance_ids = fields.One2many('hms.patient.insurance', 'patient_id', string='Insurance')

    def action_insurance_policy(self):
        action = self.env.ref('acs_hms_insurance.action_hms_patient_insurance').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id,
        }
        return action

    def action_claim_view(self):
        action = self.env.ref('acs_hms_insurance.action_insurance_claim').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id,
        }
        return action


class ACSAppointment(models.Model):
    _inherit = 'hms.appointment'

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    insurance_id = fields.Many2one('hms.patient.insurance', string='Insurance Policy', states=READONLY_STATES)
    claim_id = fields.Many2one('hms.insurance.claim', string='Claim', states=READONLY_STATES)
    insurance_company_id = fields.Many2one('hms.insurance.company', related='insurance_id.insurance_company_id', string='Insurance Company', readonly=True)
    app_insurance_percentage = fields.Float(related='insurance_id.app_insurance_percentage', string="Insured Percentage", readonly=True)

    def create_invoice(self):
        res = super(ACSAppointment, self).create_invoice()
        if self.invoice_id and self.insurance_id and (self.insurance_id.app_insurance_limit >= self.invoice_id.amount_total or self.insurance_id.app_insurance_limit==0) and "acs_invoice_split" in loaded_modules:
            split_context = {'active_model':'account.move', 'active_id': self.invoice_id.id, 'insurance_id': self.insurance_id.id}
            wiz_id = self.env['split.invoice.wizard'].with_context(split_context).create({
                'split_selection': 'invoice',
                'percentage': self.app_insurance_percentage,
                'partner_id': self.insurance_company_id.partner_id.id if self.insurance_company_id.partner_id else self.patient_id.partner_id.id,
            })
            insurance_invoice_id = wiz_id.split_record()
            insurance_invoice_id.write({
                'appointment_id': self.id,
                'ref': self.name,
                'invoice_origin': self.name
            })

            if insurance_invoice_id and self.insurance_id.create_claim:
                claim_id = self.env['hms.insurance.claim'].create({
                    'patient_id': self.patient_id.id,
                    'insurance_id': self.insurance_id.id,
                    'claim_for': 'appointment',
                    'appointment_id': self.id,
                    'amount_requested': insurance_invoice_id.amount_total,
                })
                self.claim_id = claim_id.id
                insurance_invoice_id.claim_id = claim_id.id

    def create_consumed_prod_invoice(self):
        res = super(ACSAppointment, self).create_consumed_prod_invoice()
        if self.consumable_invoice_id and self.insurance_id and (self.insurance_id.app_insurance_limit >= self.consumable_invoice_id.amount_total or self.insurance_id.app_insurance_limit==0) and "acs_invoice_split" in loaded_modules:
            split_context = {'active_model':'account.move', 'active_id': self.consumable_invoice_id.id, 'insurance_id': self.insurance_id.id}
            wiz_id = self.env['split.invoice.wizard'].with_context(split_context).create({
                'split_selection': 'invoice',
                'percentage': self.app_insurance_percentage,
                'partner_id': self.insurance_company_id.partner_id.id if self.insurance_company_id.partner_id else self.patient_id.partner_id.id,
            })
            insurance_invoice_id = wiz_id.split_record()
            insurance_invoice_id.write({
                'appointment_id': self.id,
                'ref': self.name,
                'invoice_origin': self.name
            })

            if insurance_invoice_id and self.insurance_id.create_claim:
                if not self.claim_id:
                    claim_id = self.env['hms.insurance.claim'].create({
                        'patient_id': self.patient_id.id,
                        'insurance_id': self.insurance_id.id,
                        'claim_for': 'appointment',
                        'appointment_id': self.id,
                        'amount_requested': insurance_invoice_id.amount_total,
                    })
                    self.claim_id = claim_id.id
                insurance_invoice_id.claim_id = self.claim_id.id

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        super(ACSAppointment, self).onchange_patient_id()
        allow_appointment_insurances = self.patient_id.insurance_ids.filtered(lambda x: x.allow_appointment_insurance)
        if self.patient_id and allow_appointment_insurances:
            insurance = allow_appointment_insurances[0]
            self.insurance_id = insurance.id
            self.pricelist_id = insurance.pricelist_id and insurance.pricelist_id.id or False


class Invoice(models.Model):
    _inherit = 'account.move'

    claim_id = fields.Many2one('hms.insurance.claim', 'Claim')
    insurance_company_id = fields.Many2one('hms.insurance.company', related='claim_id.insurance_company_id', string='Insurance Company', readonly=True)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    claim_id = fields.Many2one('hms.insurance.claim', 'Claim')
    insurance_company_id = fields.Many2one('hms.insurance.company', related='claim_id.insurance_company_id', string='Insurance Company', readonly=True)


class Attachments(models.Model):
    _inherit = "ir.attachment"

    patient_id = fields.Many2one('hms.patient', 'Patient')
    hospitalization_id = fields.Many2one('acs.hospitalization', 'Hospitalization')
    claim_id = fields.Many2one('hms.insurance.claim', 'Claim')


class Hospitalization(models.Model):
    _inherit = 'acs.hospitalization'

    def _rec_count(self):
        super(Hospitalization, self)._rec_count()
        for rec in self:
            rec.claim_count = len(rec.claim_ids)

    STATES={'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    cashless = fields.Boolean(string="Cashless", default=False, states=STATES)
    package_id = fields.Many2one('hospitalization.package', string='Package', states=STATES)
    package_invoice_id = fields.Many2one('account.move', string="Package Invoice", states=STATES)
    claim_ids = fields.One2many('hms.insurance.claim','hospitalization_id', "Claims")
    claim_count = fields.Integer(compute='_rec_count', string='# Claims')

    def action_patient_doc_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('res_id', '=', self.patient_id.id), ('res_model', '=', 'hms.patient')]
        action['context'] = {
            'default_res_id': self.patient_id.id,
            'default_res_model': 'hms.patient',
            'default_patient_id': self.patient_id.id,
            'default_hospitalization_id': self.id,
            'default_is_document': True}
        return action

    def action_claim_view(self):
        action = self.env.ref('acs_hms_insurance.action_insurance_claim').read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id),('hospitalization_id','=',self.id)]
        action['context'] = {
            'default_patient_id': self.patient_id.id,
            'default_hospitalization_id': self.id
        }
        return action

    def action_create_invoice(self):
        invoice_id = super(Hospitalization, self).action_create_invoice()
        return invoice_id

    def create_package_invoice(self):
        if not self.package_id:
            raise UserError(('Please select package first.'))

        product_data = []
        for line in self.package_id.order_line:
            if line.display_type:
                product_data.append({
                    'name': line.name,
                })
            else:
                product_data.append({
                    'product_id': line.product_id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'quantity': line.product_uom_qty,
                    'discount': line.discount,
                })

        invoice = self.acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data={})
        invoice.write({
            'claim_id': self.claim_ids and self.claim_ids[0].id or False,
            'hospitalization_id': self.id
        })
        self.package_invoice_id = invoice.id
