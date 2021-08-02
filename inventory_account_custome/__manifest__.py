# -*- coding: utf-8 -*-
{
    'name': "Inventory Account Custome",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Muram Makkawy Mubarak",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',


    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'stock',
        'stock_account',
        'purchase_stock',
        'sale_stock',
        'inventory_material_request',
        'inventory_custome',
        'stock_move_custome',
        'stock_landed_costs'],

    # always loaded
    'data': [
        'views/stock_picking_views.xml',
        'views/hr_department_views.xml',
        'views/stock_landed_costs_views.xml',
    ],
    # only loaded in demonstration mode

}