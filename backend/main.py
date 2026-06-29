from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    from services.detector import PipelineDefectDetector
    from services.llm_provider import LLMProvider
    from services.knowledge_base import StandardKnowledgeBase

    app.state.detector = PipelineDefectDetector(
        model_path=app.settings.detector_model_path
    )
    app.state.llm_provider = LLMProvider(app.settings.llm_config)
    app.state.kb = StandardKnowledgeBase(app.settings.kb_path)

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
