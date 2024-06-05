from fastapi import FastAPI

from app.routers import (
    reglog,
    subscriptions,
    profile,
)

app = FastAPI()
app.include_router(reglog.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
