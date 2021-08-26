# -*- coding: utf-8 -*-
{
    'name': "POS Analytic Account",
    'summary': """
       Use analytic account defined on POS configuration for POS orders and in Journal Entry""",

    'description': """
        Use analytic account defined on POS configuration for POS orders and in Journal Entry
    """,
    'author': 'A&L',
    'images': ['static/description/icon.png'],
    'category': 'Sales/Point of Sale',
    'depends': [
        'point_of_sale',
        'account',
        'analytic'
    ],
    'data': [
        'views/pos_config.xml',
        'views/pos_order.xml',
    ],
    'installable': True,
}
