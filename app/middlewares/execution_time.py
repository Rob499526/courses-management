import os
import time
import asyncio
from fastapi import Request, HTTPException

TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", 5))

def add_execution_time_middleware(app):
    @app.middleware("http")
    async def execution_time_middleware(request: Request, call_next):
        start_time = time.time()
        try:
            response = await asyncio.wait_for(call_next(request), timeout=TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Request took too long to process.")
        duration = time.time() - start_time
        response.headers["X-Execution-Time"] = str(duration)
        return response
