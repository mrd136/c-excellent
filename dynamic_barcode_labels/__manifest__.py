# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

{
    'name': 'Print Dynamic Barcode Labels',
    "version": "12.0.1",
    'author': 'TidyWay',
    'category': 'product',
    'website': 'http://www.tidyway.in',
    'description': '''Print Dynamic Barcode Labels''',
    'depends': ['stock'],
    'data': [
             'data/barcode_config.xml',
             'security/barcode_label_security.xml',
             'security/ir.model.access.csv',
             'wizard/barcode_labels.xml',
             'views/barcode_config_view.xml',
             'report/barcode_labels_report.xml',
             'report/barcode_labels.xml',
             'views/menu_view.xml'
             ],
    'price': 99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['images/label.jpg'],
    'live_test_url': 'https://youtu.be/SPQZ8p7ATN4'
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
