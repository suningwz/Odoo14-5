# -*- coding: utf-8 -*-
{
    'name': "Cortex Products",

    'summary': "Products Customization",

    'description': """
        App to add additional feature to Products.
    """,

    'author': "Mounir Lahsini",
    'version': '1.0',
    'installable': True,
    'website': 'https://github.com/mounirlahsini',

    'depends': ['base', 'mail', 'product', 'cortex_documents', 'mrp', 'sale', 'contacts', 'project', 'account', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'data/machine_center_data.xml',
        'views/cortex_products_assets.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_views.xml',
        'views/mail_compose_message_views.xml',
        'views/installed_part_views.xml',
        'views/machine_center_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/mrp_production_views.xml',
        'views/project_views.xml',
        'views/stock_picking_views.xml',

    ],

    'demo': [
    ],
    
    'application': False,
}
