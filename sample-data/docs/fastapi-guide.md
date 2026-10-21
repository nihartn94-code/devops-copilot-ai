# FastAPI Production Architecture Guide

Source: https://fastapi.tiangolo.com/tutorial/

## Core Architecture Principles
1. **Pydantic Schemas**: Use strict input and output validation with Pydantic v2 `BaseModel`.
2. **CORS Handling**: Configure `CORSMiddleware` with explicit allowed origins, methods, and headers.
3. **Async Endpoints**: Use `async def` for I/O bound endpoints (database, external HTTP/AWS calls).
4. **Structured Error Handling**: Throw `HTTPException(status_code=..., detail=...)` with readable error messages.
5. **Background Tasks**: Use `BackgroundTasks` for asynchronous work that does not block response delivery.

## Security Best Practices
- Never log raw passwords, access tokens, or sensitive user headers.
- Restrict file upload endpoints with maximum size limits.
- Validate paths using `Path.resolve()` to prevent directory traversal (`../`).
