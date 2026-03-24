"""
Production server startup script
"""
import uvicorn
import multiprocessing
from app.config import settings

def calculate_workers():
    """Calculate optimal worker count: 2 * CPU cores + 1"""
    cpu_count = multiprocessing.cpu_count()
    return (2 * cpu_count) + 1

if __name__ == "__main__":
    workers = calculate_workers()
    print(f"Starting production server with {workers} workers...")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=workers,
        log_level="warning",
        access_log=True,
        timeout_graceful_shutdown=30
    )
