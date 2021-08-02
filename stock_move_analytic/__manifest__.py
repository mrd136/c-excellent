# -*- coding: utf-8 -*-
{
    'name': "stock_move_analytic",
    'summary': """Stock Move Analytic """,
    'description': """ Add analytic account in ..........  """,
    'author': "CubicIt Egypt",
    'category': 'Uncategorized',
    'version': '13.0.0.1',
    'depends': ['base','account', 'sale', 'product', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_setting.xml',
        'views/warehouse.xml',
    ],

}
