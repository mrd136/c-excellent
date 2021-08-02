# -*- coding: utf-8 -*-
{
    'name': "Inventory Custome",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Muram Makkawy Mubarak",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'stock',
        'sale',
        'purchase_stock',
        'sales_team',
        'hr',
        'hr_expense',
        'stock_move_custome',
        'warehouse_stock_restrictions'
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'data/transfer_request_data.xml',

        'report/transfer_request_report_views.xml',

        'views/transfer_request_views.xml',
        'views/stock_location_views.xml',
        'views/product_category_views.xml',
        # 'views/stock_picking_views.xml',

        'wizard/update_picking_views.xml',
    ],
    
}