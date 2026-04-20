from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.redis import init_redis, close_redis
from app.services.whoop_scheduler import start_whoop_scheduler, stop_whoop_scheduler

app = FastAPI(
    title="HealthTrack API",
    description="Health tracking platform API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include API router
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection and start background schedulers."""
    await init_redis()
    start_whoop_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis connection and stop background schedulers."""
    stop_whoop_scheduler()
    await close_redis()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
