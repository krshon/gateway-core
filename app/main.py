from fastapi import FastAPI, Request, HTTPException
import time
from app.auth import verify_token

# Create the FastAPI app FIRST
app = FastAPI(title="API Gateway")

# ---------------- Gateway Middleware ----------------
@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    start_time = time.time()
    path = request.url.path

    print(f"Incoming request: {request.method} {path}")

    # Public routes (no auth required)
    if path in ["/", "/login", "/docs", "/openapi.json"]:
        response = await call_next(request)
    else:
        # Expect Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        # Support: Bearer <token>
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Attach user info to request (optional, but realistic)
        request.state.user = payload.get("sub")

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
