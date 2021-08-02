# -*- coding: utf-8 -*-
{
    'name': "Documents",

    'summary': "Document management",

    'description': """
        App to upload and manage your documents.
    """,

    'author': "Mounir Lahsini",
    'version': '1.0',
    'application': True,
    'website': 'https://github.com/mounirlahsini',

    'depends': ['base', 'mail', 'web'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cortex_documents_data.xml',
        'data/files_data.xml',
        'views/assets.xml',
        'views/cortex_documents_views.xml', 
        'wizard/upload_document_views.xml',
    ],

    'qweb': [
        "static/src/xml/*.xml",
    ],

    'demo': [
    ],
}