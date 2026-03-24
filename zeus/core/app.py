from fastapi import FastAPI

from zeus import __version__
from zeus.core.config import settings
from zeus.core.routes import router as core_router

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Personal AI for RAG and agent orchestration",
)

app.include_router(core_router)
