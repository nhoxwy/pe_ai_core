from odoo import api, fields, models

class PeAIKnowledge(models.Model):
    _name = "pe.ai.knowledge"
    _description = "Pe AI Knowledge"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "write_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    content = fields.Text(required=True, tracking=True)
    category = fields.Char(tracking=True)
    status = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
        default="active",
        required=True,
        tracking=True,
    )
    visibility = fields.Selection(
        [("internal", "Internal"), ("public", "Public")],
        default="internal",
        required=True,
    )
    source = fields.Selection(
        [("owner_telegram", "Owner Telegram"), ("ui", "Odoo UI"), ("system", "System")],
        default="ui",
        required=True,
    )
    source_ref = fields.Char()
    version = fields.Integer(default=1, required=True)
    active = fields.Boolean(default=True)

    def action_archive(self):
        self.write({"status": "archived", "active": False})

    def action_activate(self):
        self.write({"status": "active", "active": True})

    @api.model
    def search_relevant(self, query, limit=8):
        if not query:
            return self.browse()

        tokens = [
            x.strip()
            for x in query.split()
            if len(x.strip()) >= 2
        ][:8]

        domain = [
            ("active", "=", True),
            ("status", "=", "active"),
        ]

        if tokens:
            conditions = []
            for token in tokens:
                conditions.extend([
                    ("name", "ilike", token),
                    ("content", "ilike", token),
                ])

            # OR all conditions together.
            # Odoo prefix notation requires N-1 "|" operators
            # for N OR conditions.
            search_domain = ["|"] * (len(conditions) - 1)
            search_domain.extend(conditions)

            domain += search_domain

        return self.search(domain, limit=limit)
