"""
ThreatGraph API entrypoint.

Wires up CORS, driver lifecycle, routers, and two exception handlers
that turn internal failures into clean, typed HTTP responses instead of
leaking stack traces (or connection strings) to the client.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db import DatabaseUnavailableError, close_driver, init_driver
from app.routes import entities, health, investigations, search, stats
from app.services.exceptions import EntityNotFoundError

logging.basicConfig(level=get_settings().log_level)
logger = logging.getLogger("threatgraph.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_driver()
    yield
    close_driver()


app = FastAPI(
    title="ThreatGraph API",
    description="Read-only cybersecurity threat-intelligence graph explorer, backed by CognoDB.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(stats.router)
app.include_router(entities.router)
app.include_router(search.router)
app.include_router(investigations.router)


@app.exception_handler(DatabaseUnavailableError)
async def database_unavailable_handler(request: Request, exc: DatabaseUnavailableError) -> JSONResponse:
    logger.error("Database unavailable while handling %s: %s", request.url.path, exc)
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
