from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class LLMConfig(BaseModel):
    provider: str
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4096


class DetectorConfig(BaseModel):
    model_path: str = "models/detector/best.pt"
    confidence_threshold: float = 0.5
    device: str = "cuda:0"


@router.post("/config/llm")
async def update_llm_config(config: LLMConfig):
    from services.llm_provider import LLMProvider

    LLMProvider.update_global_config(config)
    return {"status": "ok", "provider": config.provider, "model": config.model_name}


@router.get("/config/llm/presets")
async def get_llm_presets():
    return [
        {
            "name": "通义千问-VL-Max (云端)",
            "provider": "cloud",
            "model_name": "qwen-vl-max",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        },
        {
            "name": "通义千问-VL-Plus (云端)",
            "provider": "cloud",
            "model_name": "qwen-vl-plus",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        },
        {
            "name": "GPT-4o (云端)",
            "provider": "cloud",
            "model_name": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
        },
        {
            "name": "本地模型 (vLLM)",
            "provider": "local",
            "model_name": "qwen3-vl-8b-local",
            "base_url": "http://localhost:8000/v1",
        },
    ]
