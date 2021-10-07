# -*- coding: utf-8 -*-
{
    'name': "Cortex Links",

    'summary': "Customization for Purchase, Sale, Manufacturing, Project, Stock and Account",

    'description': """
        App to add additional feature to Purchase, Sale, Manufacturing, Project, Stock and Account.
    """,

    'author': "Mounir Lahsini",
    'version': '1.0',
    'installable': True,
    'website': 'https://github.com/mounirlahsini',

    'depends': ['base', 'mail', 'mrp', 'sale', 'project', 'account', 'stock', 'purchase', 'sale_project'],

    'data': [
        'views/cortex_products_assets.xml',
        'views/account_payment_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/mrp_production_views.xml',
        'views/project_views.xml',
        'views/stock_move_views.xml',
    ],

    'demo': [
    ],
    
    'application': False,
}
