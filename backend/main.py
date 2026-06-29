import sys
import os
import yaml
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "backend" / "config" / "settings.yaml", "r", encoding="utf-8") as f:
    settings = yaml.safe_load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from services.detector import PipelineDefectDetector
    from services.llm_provider import LLMProvider
    from services.knowledge_base import StandardKnowledgeBase

    detector_config = settings["detector"]
    llm_config = settings["llm"]
    kb_config = settings["knowledge_base"]

    app.state.detector = PipelineDefectDetector(
        model_path=str(BASE_DIR / detector_config["model_path"]),
        device=detector_config.get("device", "cuda:0"),
    )
    app.state.llm_provider = LLMProvider({
        "model_name": llm_config["default_model"],
        "base_url": next(
            (p["base_url"] for p in llm_config.get("presets", [])
             if p["model_name"] == llm_config["default_model"]),
            "",
        ),
        "temperature": llm_config.get("temperature", 0.1),
        "max_tokens": llm_config.get("max_tokens", 4096),
    })
    app.state.kb = StandardKnowledgeBase(
        str(BASE_DIR / kb_config["standard_file"])
    )

    yield

    app.state.detector.close()


app = FastAPI(title="PipeAI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import chat_router, batch_router, report_router, config_router

app.include_router(chat_router, prefix="/api")
app.include_router(batch_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(config_router, prefix="/api")
