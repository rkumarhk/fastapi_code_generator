from fastapi import FastAPI
app = FastAPI()

from app.routers import dashboard, lms, pods

app.include_router(dashboard.router)
app.include_router(lms.router)
app.include_router(pods.router)