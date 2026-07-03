"""
Vercel Serverless entry point for FastAPI backend.
Vercel @vercel/python builder automatically detects and serves the ASGI 'app' object.
"""
from app.main import app

__all__ = ["app"]
