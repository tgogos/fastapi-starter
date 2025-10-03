# Standard library imports
import asyncio
import time

# Third-party imports
from fastapi import APIRouter

# Local imports
# from app.utils import mongo_utils

# Capture the start time of the application
start_time = time.time()

router = APIRouter()

@router.get("/", 
    summary="Root endpoint",
    response_description="Welcome message minimal-fastapi"
)
async def root():
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        dict: Welcome message from FastAPI starter
    """
    return {"message": "Hello from FastAPI starter!"}

@router.get("/health", 
    summary="Get the service status",
    response_description="Health status..."
)
async def health():
    """
    An easy way to get back information about the status of FastAPI starter
    """
    # Perform health checks
    # db_healthy = await mongo_utils.check_database_connection()
    external_service_healthy = await check_external_service()
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)

    # Gather health information
    health_status = {
        "status": "ok",
        # "mongodb_ping": "ok" if db_healthy else "not ok",
        "external_service": "healthy" if external_service_healthy else "unhealthy",
        "uptime_seconds": uptime_seconds,
    }

    # if not db_healthy or not external_service_healthy:
    #     health_status["status"] = "unhealthy"

    return health_status

async def check_external_service():
    """
    Check the availability of external services.
    
    Returns:
        bool: True if external service is healthy, False otherwise
    """
    # Replace with actual external service check logic
    await asyncio.sleep(0.1)  # Simulate a service check delay
    return True