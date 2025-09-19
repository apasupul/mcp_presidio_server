import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.routes import anonymize as anonymize_route
from .api.routes import deanonymize as deanonymize_route

logging.config.fileConfig("app/core/logging.conf", disable_existing_loggers=False)

app = FastAPI(title="Presidio Anonymize/Deanonymize API (No DB)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(anonymize_route.router)
app.include_router(deanonymize_route.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
