from odoo import fields, models

class PeAIConversation(models.Model):
    _name = "pe.ai.conversation"
    _description = "Pe AI Conversation"
    _order = "write_date desc"

    name = fields.Char(required=True)
    channel = fields.Selection(
        [("telegram", "Telegram"), ("ui", "Odoo UI"), ("other", "Other")],
        default="telegram",
        required=True,
    )
    external_chat_id = fields.Char(index=True)
    message_ids = fields.One2many("pe.ai.message", "conversation_id")
    active = fields.Boolean(default=True)

class PeAIMessage(models.Model):
    _name = "pe.ai.message"
    _description = "Pe AI Message"
    _order = "create_date asc"

    conversation_id = fields.Many2one("pe.ai.conversation", required=True, ondelete="cascade")
    role = fields.Selection(
        [("user", "User"), ("assistant", "Pe AI"), ("system", "System")],
        required=True,
    )
    body = fields.Text(required=True)
    external_message_id = fields.Char(index=True)
    metadata_json = fields.Text()

    def _cron_cleanup(self):
        return True
