# -*- coding: utf-8 -*-
{
    'name': 'QR Code Invoice',
    'version': '13.0.1.0.0',
    'category': 'Accounting',
    'author': 'A&L.',
    'images': ['static/description/icon.png'],
    'summary': 'Generate QR Code for Invoice',
    'description': """""",
    'depends': [
        'ehcs_qr_code_base',
        'account',
    ],
    'data': [
        'report/account_invoice_report_template.xml',
        'views/qr_code_invoice_view.xml',
    ],
    'installable': True,
}
