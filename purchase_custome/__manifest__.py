# -*- coding: utf-8 -*-
{
    'name': "Purchase Custome",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Custom purchase module
    """,

    'author': "Muram Makkawy Mubarak",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase','stock', 'sale','purchase_stock', 'inventory_custome'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/purchase_security.xml',
        'views/purchase_views.xml',
        'report/purchase_order_templates.xml',
        'report/purchase_quotation_templates.xml'

    ],

}