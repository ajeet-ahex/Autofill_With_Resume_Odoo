{
    'name': 'AutoFill With Resume',
    'version': '17.0.0.1',
    'category': 'Recruitment',
    'author': 'Ahex Technologies',
    'summary': 'AutoFill With Resume',
    'website': '',
    'sequence': '10',
    'description': """
    Ahex Resume
    """,
    'depends': ['base', 'web', 'website','hr_recruitment'],
    'data': [
        
        'security/ir.model.access.csv',
        "views/resume_entity_extraction.xml",
        "wizard/pop_up_entity.xml",
        "views/openai_key.xml",
    
    ],
  
    # 'license': 'OPL-1',
    'application': True,
    'installable': True,
    
    # 'assets':{
    #     'web.assets_backend':[

    #         '/Entity_Extraction/static/src/js/auto_refresh.js',
    #         # 'Entity_Extraction/static/src//**/*',
    #         # 'Entity_Extraction/web/static/src/css/button_position.css',
    #         # 'Entity_Extraction/web/static/src/img/spin.png',
            
    #     ],
        
    # },

}
