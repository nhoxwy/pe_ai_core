from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pe_ai_enabled = fields.Boolean(
        string="Enable Pe AI",
        config_parameter="pe_ai_core.enabled",
        default=False,
    )

    pe_ai_provider = fields.Selection(
        [("openai", "OpenAI")],
        string="LLM Provider",
        config_parameter="pe_ai_core.provider",
        default="openai",
    )

    pe_ai_api_key = fields.Char(
        string="OpenAI API Key",
        config_parameter="pe_ai_core.api_key",
        password=True,
    )

    pe_ai_model = fields.Char(
        string="Model",
        config_parameter="pe_ai_core.model",
        default="gpt-5.6-luna",
    )

    pe_ai_system_prompt = fields.Text(
        string="System Prompt",
        default=(
            "Bạn là Pe AI, trợ lý AI trung tâm của Pe Guppy Farm. "
            "Trả lời bằng tiếng Việt, ngắn gọn và rõ ràng. "
            "Không được bịa dữ liệu. Thông tin sản phẩm, giá, tồn kho, "
            "đơn hàng và các dữ liệu vận hành phải lấy từ Odoo khi được "
            "tích hợp; không tự ghi nhớ các dữ liệu động đó vào Knowledge."
        ),
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()

        default_prompt = (
            "Bạn là Pe AI, trợ lý AI trung tâm của Pe Guppy Farm. "
            "Trả lời bằng tiếng Việt, ngắn gọn và rõ ràng. "
            "Không được bịa dữ liệu. Thông tin sản phẩm, giá, tồn kho, "
            "đơn hàng và các dữ liệu vận hành phải lấy từ Odoo khi được "
            "tích hợp; không tự ghi nhớ các dữ liệu động đó vào Knowledge."
        )

        res.update(
            pe_ai_system_prompt=ICP.get_param(
                "pe_ai_core.system_prompt",
                default=default_prompt,
            )
        )
        return res

    def set_values(self):
        super().set_values()

        ICP = self.env["ir.config_parameter"].sudo()

        for record in self:
            ICP.set_param(
                "pe_ai_core.system_prompt",
                record.pe_ai_system_prompt or "",
            )
