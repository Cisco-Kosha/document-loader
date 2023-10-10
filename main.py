from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_v1_router

from app.core.config import settings, logger

app = FastAPI(
    title="Document Loader Connector", openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

logger.info("Starting document-loader-connector app")


app.include_router(api_v1_router, prefix=settings.API_V1_STR)

