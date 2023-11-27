import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_router import router
from app.db.base import Base
from app.db.base import engine
from app.core.config import settings
from app.core.manage_websocket import connection_manager

Base.metadata.create_all(bind=engine)

def get_application() -> FastAPI:
    application = FastAPI()
    application.include_router(router, prefix=settings.API_PREFIX)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return application

app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=True)
