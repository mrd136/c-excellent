# -*- coding: utf-8 -*-
{
    'name': "Electronic invoice KSA - Base",
    'description': """
       Electronic invoice KSA - Base
    """,
    'author': "Era group",
    'email': "aqlan@era.net.sa ",
    'website': "https://era.net.sa",
    'category': 'accounting',
    'version': '0.1',
    #'price': 0,  
    #'currency': 'EUR',
    'license': 'AGPL-3',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'account', 'sale', 'purchase'],
    'data': [
        'views/partner.xml',
        'reports/invoice_inherit_report.xml',
    ],
}
