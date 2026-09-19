{
    "name": "Pe AI Core",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Minimal extensible AI core for Pe Guppy Farm",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/pe_ai_knowledge_views.xml",
        "views/pe_ai_conversation_views.xml",
        "views/pe_ai_menu.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
