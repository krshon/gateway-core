from fastapi import FastAPI, Request
import time

# Create the FastAPI app FIRST
app = FastAPI(title="API Gateway")

# Middleware
@app.middleware("http")
async def base_middleware(request: Request, call_next):
    start_time = time.time()

    print(f"Incoming request: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    print(f"Completed in {process_time:.4f}s")

    return response

# Import routes AFTER app is created
from app.routes import test

# Register routes
app.include_router(test.router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "API Gateway running"}
