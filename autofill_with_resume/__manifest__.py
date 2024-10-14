{
    'name': 'AutoFill With Resume',
    'version': '17.0.0.1',
    'category': 'Project',
    'author': 'Ahex Technologies',
    'summary': 'AutoFill With Resume',
    'website': '',
    'sequence': '10',
    'description': """
    AutoFill With Resume
    """,
    'depends': ['base', 'web', 'website', 'hr_recruitment'],
    'images': [
        'static/description/banner.png',
        ],
    'data': [

        'security/ir.model.access.csv',
        "views/resume_entity_extraction.xml",
        "wizard/pop_up_entity.xml",
        "views/openai_key.xml",
    ],
    'license': 'OPL-1',
    'application': True,
    'installable': True,
}
