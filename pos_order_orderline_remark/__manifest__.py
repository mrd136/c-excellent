# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Order Orderline Remark',
    'version': '12.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Point of Sale',
    'summary': """
    Make order and line notes in POS.
    """,
    'description': """
    pos remarks on order
    pos order remarks
    order remarks on product
    pos product line remarks
    restaurant customer remarks
    restaurant order remarks
    pos order note
    product note on restaurant
    """,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_orderline_remark_views.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/pos_order_orderline_remark.xml'],
    'images': ['static/description/pos_order_orderline_remark.png'],
    'installable': True,
    'auto_install': False,
    'sequence': 8,
    'application': True,
    'price': 12,
    'currency': 'EUR',
}
