from fastapi import APIRouter
from app.routers import health, todos, users, companies, auth

router = APIRouter()
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(companies.router)
router.include_router(todos.router)
router.include_router(health.router)