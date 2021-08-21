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
        survy_id = self.env['survey.survey'].search([], limit=1)
        url = survy_id.public_url or ''
        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.partner',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_patient_id': self.patient_id.id,
                            'default_message': url,
                            'default_message_type': 'url_link',
                            'format_invisible': True},
                }