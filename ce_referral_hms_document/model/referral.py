# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Referral(models.Model):
    _inherit = "hms.referral"

    def _acs_get_attachemnts(self):
        AttachmentObj = self.env['ir.attachment']
        attachments = AttachmentObj.search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)])
        # attachments += self.mapped('attachment_ids')
        return attachments

    def _acs_attachemnt_count(self):
        # AttachmentObj = self.env['ir.attachment']
        for rec in self:
            attachments = rec._acs_get_attachemnts()
            rec.attach_count = len(attachments)
            rec.attachment_ids = [(6,0,attachments.ids)]

    attach_count = fields.Integer(compute="_acs_attachemnt_count", readonly=True, string="Documents")
    attachment_ids = fields.Many2many('ir.attachment', 'attachment_referral_rel', 'referral_id', 'attachment_id', compute="_acs_attachemnt_count", string="Attachments")

    def action_view_attachments(self):
        self.ensure_one()
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('id', 'in', self.attachment_ids.ids)]
        action['context'] = {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_is_document': True}
        return action
