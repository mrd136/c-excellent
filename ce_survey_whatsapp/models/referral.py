# -*- coding: utf-8 -*-

# import logging
from odoo import models, fields, api, _


# _logger = logging.getLogger(__name__)


class Referral(models.Model):
    _inherit = 'hms.referral'

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
    ], default='without_sending')

    def send_whatsapp_step(self):
        domain = []
        if self.service_id.survey_id:
            domain = [('id', '=', self.service_id.survey_id.id)]
        survy_id = self.env['survey.survey'].search([domain], limit=1)
        url = survy_id.public_url or ''
        action = self.env.ref('gtica_whatsapp_integration_partner.send_whatsapp_partner_action').read()[0]
        action['context'] = {'default_patient_id': self.patient_id.id,
                             'default_mobile': self.patient_id.mobile,
                             'default_message': url,
                             'default_message_type': 'url_link',
                             'format_invisible': True}
        return action
