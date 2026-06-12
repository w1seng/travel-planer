from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import projects_router, places_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="travel planner",
    lifespan=lifespan,
)


# Router
app.include_router(projects_router, prefix="/api/v1")
app.include_router(places_router,   prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}