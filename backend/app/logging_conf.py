import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("joke_api")

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request timing and status.
    Essential for monitoring API performance in production.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"Path: {request.url.path} | "
                f"Method: {request.method} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.2f}ms"
            )
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Path: {request.url.path} | "
                f"Method: {request.method} | "
                f"failed after {process_time:.2f}ms | "
                f"Error: {str(e)}"
            )
            raise e
