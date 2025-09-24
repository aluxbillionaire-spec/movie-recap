"""
API Router v1

Main router that includes all API endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, uploads, jobs, outputs, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(outputs.router, prefix="/outputs", tags=["outputs"])
api_router.include_router(users.router, prefix="/users", tags=["users"])