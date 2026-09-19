import json
import urllib.request
import urllib.error

from odoo import api, models
from odoo.exceptions import UserError

class PeAIService(models.AbstractModel):
    _name = "pe.ai.service"
    _description = "Pe AI Service"

    @api.model
    def _get_param(self, key, default=None):
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    @api.model
    def _call_openai(self, messages):
        api_key = self._get_param("pe_ai_core.api_key")
        model = self._get_param("pe_ai_core.model", "gpt-5.6-luna")
        system_prompt = self._get_param(
            "pe_ai_core.system_prompt",
            "Bạn là Pe AI của Pe Guppy Farm. Trả lời bằng tiếng Việt và không bịa dữ liệu.",
        )
        if not api_key:
            raise UserError("Pe AI chưa được cấu hình OpenAI API Key.")

        input_items = [{"role": "system", "content": system_prompt}]
        for msg in messages[-20:]:
            input_items.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"],
            })

        payload = json.dumps({
            "model": model,
            "input": input_items,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=payload,
            headers={
                "Authorization": "Bearer %s" % api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise UserError("OpenAI API error %s: %s" % (exc.code, body))
        except Exception as exc:
            raise UserError("Không thể gọi OpenAI: %s" % exc)

        text = data.get("output_text")
        if text:
            return text.strip()

        # Fallback parser for Responses API output items.
        parts = []
        for item in data.get("output", []) or []:
            if item.get("type") != "message":
                continue
            for content in item.get("content", []) or []:
                if content.get("type") in ("output_text", "text"):
                    value = content.get("text")
                    if value:
                        parts.append(value)
        if parts:
            return "".join(parts).strip()

        raise UserError("OpenAI trả về kết quả nhưng Pe AI không đọc được nội dung.")

    @api.model
    def build_context(self, query):
        # Intentionally excludes product/price/stock data.
        knowledge = self.env["pe.ai.knowledge"].sudo().search_relevant(query, limit=6)
        return [
            {"name": rec.name, "content": rec.content, "category": rec.category or ""}
            for rec in knowledge
        ]

    @api.model
    def process_owner_message(self, conversation, text):
        context = self.build_context(text)
        history = []
        for msg in conversation.message_ids[-20:]:
            history.append({"role": msg.role, "content": msg.body})

        if context:
            knowledge_text = "\n\n".join(
                "[Knowledge: %s]\n%s" % (item["name"], item["content"])
                for item in context
            )
            history.append({
                "role": "user",
                "content": (
                    "Dưới đây là Knowledge nội bộ liên quan. Chỉ sử dụng nếu phù hợp:\n"
                    + knowledge_text
                ),
            })

        history.append({"role": "user", "content": text})
        return self._call_openai(history)
