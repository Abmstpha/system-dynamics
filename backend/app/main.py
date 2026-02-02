"""
System Dynamics Platform - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="System Dynamics Platform",
    description="AI-Powered System Dynamics Modeling for Strategic Decision Making",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.routes import models, simulate, agent

app.include_router(models.router, prefix="/api/v1", tags=["Models"])
app.include_router(simulate.router, prefix="/api/v1", tags=["Simulation"])
app.include_router(agent.router, prefix="/api/v1", tags=["AI Agent"])

@app.get("/")
async def root():
    return {
        "message": "System Dynamics Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
