# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'POS Customer screen (Enterprise)',
    'version': '1.0',
    'category': 'Point of Sale',
    'website': 'http://www.acespritech.com',
    'price': 40.0,
    'currency': 'EUR',
    'summary': "Allows Seller's to promote there new products and customers can also see there products.",
    'description': "Allows Seller's to promote there new products and customers can also see there products.",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'depends': ['point_of_sale','bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_display.xml',
        'views/templates.xml',
        'views/pos_config_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
