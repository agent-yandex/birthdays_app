"""
This script initializes a FastAPI application and includes routers.

It sets up endpoints under the '/api' prefix for each module.
"""

from fastapi import FastAPI

from app.routers import profile, reglog, subscriptions

app = FastAPI()

app.include_router(reglog.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
