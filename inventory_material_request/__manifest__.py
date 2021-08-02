# -*- coding: utf-8 -*-
{
    'name': "Inventory Material Request",

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
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','sale','hr','hr_expense','stock_move_custome','warehouse_stock_restrictions'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/inventory_material_request_data.xml',

        'report/material_request_report_views.xml',
        
        'views/inventoy_material_request_views.xml',
        'views/res_users_views.xml',
        'views/view_picking_type.xml'
    ],
    # only loaded in demonstration mode
    
}