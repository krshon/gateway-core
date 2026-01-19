from fastapi import FastAPI, Request, HTTPException
import time
import uuid
from app.auth import verify_token
from app.rate_limiter import is_allowed
from app.logger import log_event
from fastapi.responses import JSONResponse

from app.metrics import inc, snapshot

app = FastAPI(title="API Gateway")

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    request_id = str(uuid.uuid4())

    inc("total_requests")
    request.state.request_id = request_id

    try:
        # Public routes
        if path in ["/", "/login", "/docs", "/openapi.json", "/metrics"]:
            response = await call_next(request)
            inc("success")

        else:
            # ----- AUTH -----
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                inc("unauthorized")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authorization header missing"}
                )

            token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
            payload = verify_token(token)
            if not payload:
                inc("unauthorized")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"}
                )

            user_id = payload.get("sub")
            request.state.user = user_id

            # ----- RATE LIMIT -----
            if not is_allowed(user_id):
                inc("rate_limited")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests, please try again later"}
                )

            response = await call_next(request)
            inc("success")

    except Exception as exc:
        log_event({
            "request_id": request_id,
            "method": request.method,
            "path": path,
            "status": 500,
            "error": str(exc)
        })
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    process_time = round((time.time() - start_time) * 1000, 2)

    log_event({
        "request_id": request_id,
        "method": request.method,
        "path": path,
        "user": getattr(request.state, "user", None),
        "status": response.status_code,
        "latency_ms": process_time
    })

    response.headers["X-Process-Time"] = f"{process_time}ms"
    response.headers["X-Request-ID"] = request_id

    return response

# ---------------- Routes ----------------
from app.routes import test, auth

app.include_router(auth.router)
app.include_router(test.router)

@app.get("/")
def root():
    return {"message": "API Gateway running"}

@app.get("/metrics")
def metrics():
    return snapshot()
