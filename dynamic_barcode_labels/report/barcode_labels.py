# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

import base64
import time
from odoo import models, api, _
from reportlab.graphics import barcode
from base64 import b64encode
from reportlab.graphics.barcode import createBarcodeDrawing


class ReportBarcodeLabels(models.AbstractModel):
    _name = 'report.dynamic_barcode_labels.report_barcode_labels'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        product_obj = self.env["product.product"]
        record_ids = []
        for rec in data['form']['product_ids']:
            for loop in range(0, int(rec['qty'])):
                record_ids.append((
                       product_obj.browse(int(rec['product_id'])),
                       rec['lot_number']
                       ))
        return {
            'doc_ids': data['form']['product_ids'],
            'doc_model': 'product.product',
            'data': data,
            'docs': record_ids,
            'get_barcode_value': self.get_barcode_value,
            'is_humanreadable': self.is_humanreadable,
            'barcode': self.barcode,
            'time': time,
        }

    def is_humanreadable(self, data):
        return data['form']['humanreadable'] and 1 or 0

    def get_barcode_value(self, product, data):
        barcode_value = product[str(data['form']['barcode_field'])]
        return barcode_value


    def barcode(self, type, value, width, height, humanreadable, product):
        barcode_obj = createBarcodeDrawing(
            type, value=value, format='png', width=width, height=height,
            humanReadable = humanreadable
        )
        attachment = self.env['ir.attachment'].search([('res_id','=', product.id)], limit=1)
        if not attachment:
            attachment_id = self.env['ir.attachment'].create({
                        'name': product.name,
                        'res_model': 'product.product',
                        'res_id': product.id or False,
                        'datas_fname': str(product.name) + '_' + 'attachment'
                    })
        else:
            attachment_id = attachment
        file_data = base64.encodestring(barcode_obj.asString('png'))
        attachment_id.update({'datas':file_data})
        return attachment_id