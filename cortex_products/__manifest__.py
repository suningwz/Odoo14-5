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

    'depends': ['base', 'mail', 'product', 'cortex_documents', 'mrp', 'sale', 'contacts'],

    'data': [
        'security/ir.model.access.csv',
        'data/machine_center_data.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/res_partner_views.xml',
        'views/mail_compose_message_views.xml',
        'views/installed_part_views.xml',
        'views/machine_center_views.xml',
    ],

    'demo': [
    ],
    
    'application': False,
}
