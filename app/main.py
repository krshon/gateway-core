from fastapi import FastAPI, Request, HTTPException
import time
from app.auth import verify_token
from app.rate_limiter import is_allowed

# Create the FastAPI app FIRST
app = FastAPI(title="API Gateway")

# ---------------- Gateway Middleware ----------------
@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    start_time = time.time()
    path = request.url.path

    print(f"Incoming request: {request.method} {path}")

    # Public routes (no auth, no rate limiting)
    if path in ["/", "/login", "/docs", "/openapi.json"]:
        response = await call_next(request)

    else:
        # ----- AUTHENTICATION -----
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Attach user info
        user_id = payload.get("sub")
        request.state.user = user_id

        # ----- RATE LIMITING -----
        if not is_allowed(user_id):
            raise HTTPException(
                status_code=429,
                detail="Too many requests, please try again later"
            )

        # Forward request only if allowed
        response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    print(f"Completed in {process_time:.4f}s")
    return response


# ---------------- Routes ----------------
from app.routes import test, auth

app.include_router(auth.router)
app.include_router(test.router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "API Gateway running"}
