# Standard library imports

# Third-party imports
from fastapi import FastAPI

# Local imports
from app.routes import (
    root,
    items,
)
from app.core import config

# API Documentation
description = """
### Root
- Root endpoint of the API. Just a welcome message.
- Health-check endpoint.

### Items
- CRUD operations for items (in-memory storage).
- Pagination support for listing items.
- Search functionality by name.
"""

# Initialize FastAPI application
app = FastAPI(
    title="FastAPI starter",
    description=description,
    summary="FastAPI starter documentation",
    version=config.VERSION,
)

@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup.
    
    This function is called before the FastAPI app starts serving requests.
    It performs necessary initialization tasks like setting up database indexes.
    """
    # Initialize MongoDB indexes (unique for serialNumber)
    # mongo_utils.init_indexes()

# Register API routes
app.include_router(root.router, prefix="", tags=["root"])
app.include_router(items.router, prefix="/items", tags=["items"])
