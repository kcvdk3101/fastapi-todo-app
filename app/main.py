from fastapi import FastAPI
from app.routers import router

app = FastAPI(title="Todo API")

app.include_router(router)