# -*- coding: utf-8 -*-
# This module open source
# Design and development by: TL Technology (thanhchatvn@gmail.com)
{
    'name': "POS Duplicate Receipt",
    'version': '1.0.0',
    'category': 'Point of Sale',
    'author': 'A&L.',
    'images': ['static/description/icon.png'],
    'sequence': 0,
    'depends': [
        'point_of_sale'
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/parameter_data.xml',
        'template/import_library.xml',
        'views/pos_config.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    'images': ['static/description/icon.png'],
    'support': 'thanhchatvn@gmail.com',
    'installable': True,
    'application': True,
    'post_init_hook': 'auto_action_after_install',
}
