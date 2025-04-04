# app/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .presentation.api.routes.healthcheck_router import router as healthcheck_router
from .presentation.api.routes.doc_generation_router import router as doc_generation_router

def create_app() -> FastAPI:
    app = FastAPI()

    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclusion des différents routers
    app.include_router(healthcheck_router, prefix="/api")
    app.include_router(doc_generation_router, prefix="/api")

    return app

app = create_app()

if __name__ == "__main__":
    # Pour exécuter en local :  python -m app.main
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
