from fastapi import FastAPI, Request, HTTPException
import time
import uuid
from app.auth import verify_token
from app.rate_limiter import is_allowed
from app.logger import log_event

# Create the FastAPI app FIRST
app = FastAPI(title="API Gateway")

# ---------------- Gateway Middleware ----------------
@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    request_id = str(uuid.uuid4())

    # Attach request ID
    request.state.request_id = request_id

    try:
        # Public routes (no auth, no rate limiting)
        if path in ["/", "/login", "/docs", "/openapi.json"]:
            response = await call_next(request)
            status_code = response.status_code

        else:
            # ----- AUTHENTICATION -----
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Authorization header missing")

            token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
            payload = verify_token(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            user_id = payload.get("sub")
            request.state.user = user_id

            # ----- RATE LIMITING -----
            if not is_allowed(user_id):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests, please try again later"
                )

            response = await call_next(request)
            status_code = response.status_code

    except HTTPException as exc:
        # ----- ERROR LOG -----
        log_event({
            "request_id": request_id,
            "method": request.method,
            "path": path,
            "status": exc.status_code,
            "error": exc.detail
        })
        raise exc

    process_time = round((time.time() - start_time) * 1000, 2)

    # ----- SUCCESS LOG -----
    log_event({
        "request_id": request_id,
        "method": request.method,
        "path": path,
        "user": getattr(request.state, "user", None),
        "status": status_code,
        "latency_ms": process_time
    })

    # ----- RESPONSE HEADERS -----
    response.headers["X-Process-Time"] = f"{process_time}ms"
    response.headers["X-Request-ID"] = request_id

    return response


# ---------------- Routes ----------------
from app.routes import test, auth

app.include_router(auth.router)
app.include_router(test.router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "API Gateway running"}
