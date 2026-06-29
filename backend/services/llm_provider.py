from openai import OpenAI
from typing import Optional
import base64


class LLMProvider:
    PRESETS = {
        "qwen-vl-max": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "supports_vision": True,
            "max_context": 32000,
        },
        "qwen-vl-plus": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "supports_vision": True,
            "max_context": 32000,
        },
        "gpt-4o": {
            "base_url": "https://api.openai.com/v1",
            "supports_vision": True,
            "max_context": 128000,
        },
        "qwen3-vl-8b-local": {
            "base_url": "http://localhost:8000/v1",
            "supports_vision": True,
            "max_context": 8192,
        },
    }

    _instance = None
    _config = None

    def __init__(self, config: dict = None):
        if config is None:
            config = self._config or {
                "model_name": "qwen-vl-max",
                "base_url": self.PRESETS["qwen-vl-max"]["base_url"],
                "api_key": "",
                "temperature": 0.1,
                "max_tokens": 4096,
            }

        self.model_name = config["model_name"]
        self.base_url = config.get(
            "base_url", self.PRESETS.get(self.model_name, {}).get("base_url", "")
        )
        self.api_key = config.get("api_key", "")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 4096)

        self.client = OpenAI(
            api_key=self.api_key or "not-needed",
            base_url=self.base_url,
        )

    @classmethod
    def update_global_config(cls, config):
        cls._config = {
            "model_name": config.model_name,
            "base_url": config.base_url,
            "api_key": config.api_key,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }

    def chat_with_image(
        self,
        system_prompt: str,
        user_text: str,
        image_path: str = None,
        image_base64: str = None,
    ) -> str:
        messages = [{"role": "system", "content": system_prompt}]

        user_content = []
        if image_path or image_base64:
            if image_path:
                with open(image_path, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode()
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            })
        user_content.append({"type": "text", "text": user_text})

        messages.append({"role": "user", "content": user_content})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def chat_text_only(self, system_prompt: str, messages: list) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=full_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def get_langchain_llm(self):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key or "not-needed",
            base_url=self.base_url,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
