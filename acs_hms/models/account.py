# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    patient_id = fields.Many2one('hms.patient',  string='Patient', index=True, readonly=True, states={'draft': [('readonly', False)]})
    physician_id = fields.Many2one('hms.physician', string='Physician', readonly=True, states={'draft': [('readonly', False)]}) 
    ref_physician_id = fields.Many2one('res.partner', ondelete='restrict', string='Referring Physician', 
        index=True, help='Referring Physician', readonly=True, states={'draft': [('readonly', False)]})
    appointment_id = fields.Many2one('hms.appointment',  string='Appointment', readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('patient_id')
    def onchange_patient(self):
        if self.patient_id and not self.partner_id:
        	self.partner_id = self.patient_id.partner_id.id
