# -*- coding: utf-8 -*-
from odoo import api, models

class ReportSession(models.AbstractModel):
    _name = 'report.techno_pos_session_report.report_pos_session_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        session_report = self.env['ir.actions.report']._get_report_from_name('techno_pos_session_report.report_pos_session_pdf')
        session_id = self.env['pos.session'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': session_report.model,
            'docs': session_id,
        }
