# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Appointment(models.Model):
    _inherit = 'hms.appointment'
    _description = "Appointment"

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting', 'Waiting'),
        ('in_consultation', 'In consultation'),
        ('referral', 'Referral'),
        ('pause', 'Pause'),
        ('to_invoice', 'To Invoice'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='State', default='draft', required=True, copy=False, tracking=True,
        states=READONLY_STATES)
    is_referral = fields.Boolean(string='Referral ?', states=READONLY_STATES)

    def action_new_referral(self):
        action = self.env.ref('ce_referral_hms.action_new_referral').read()[0]
        action['context'] = {
            'default_weight': self.weight,
            'default_height': self.height,
            'default_patient_id': self.patient_id.id,
            'default_appointment_id': self.id,
            'default_temp': self.temp,
            'default_hr': self.hr,
            'default_rr': self.rr,
            'default_bp': self.bp,
            'default_spo2': self.spo2,
            'default_differencial_diagnosis': self.differencial_diagnosis,
            'default_present_illness': self.present_illness,
            'default_lab_report': self.lab_report,
            'default_radiological_report': self.radiological_report,
            'default_past_history': self.past_history,
            'default_urgency': self.urgency,
            'default_diseas_id': self.diseas_id.id,
            'default_responsible_id': self.responsible_id.id,
        }
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: