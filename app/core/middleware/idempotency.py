"""
MediKiosk — Idempotency Middleware (B5)
Prevents duplicate encounters, audio turns, and document uploads from mobile retries.
Caches responses for mutating requests bearing an 'Idempotency-Key' header.
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.database import get_db

logger = logging.getLogger("medikiosk.middleware.idempotency")


class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        idempotency_key = request.headers.get("Idempotency-Key") or request.headers.get("idempotency-key")

        if not idempotency_key or request.method not in ("POST", "PATCH", "PUT"):
            return await call_next(request)

        idempotency_key = idempotency_key.strip()
        try:
            db = await get_db()
            cursor = await db.execute(
                "SELECT response_json, status_code FROM idempotency_keys WHERE key = ?",
                (idempotency_key,)
            )
            cached = await cursor.fetchone()
            if cached:
                logger.info(f"Idempotency cache hit for key: {idempotency_key}")
                return Response(
                    content=cached["response_json"],
                    status_code=cached["status_code"],
                    media_type="application/json",
                    headers={"X-Cache": "HIT-IDEMPOTENCY"}
                )
        except Exception as e:
            logger.warning(f"Error checking idempotency cache: {e}")

        # Execute request
        response = await call_next(request)

        # Cache successful mutating responses (status < 400)
        if response.status_code < 400:
            try:
                body_bytes = b""
                async for chunk in response.body_iterator:
                    body_bytes += chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")

                body_text = body_bytes.decode("utf-8", errors="replace")

                # Cache in SQLite
                db = await get_db()
                await db.execute(
                    """
                    INSERT OR REPLACE INTO idempotency_keys (key, response_json, status_code)
                    VALUES (?, ?, ?)
                    """,
                    (idempotency_key, body_text, response.status_code)
                )
                await db.commit()
                logger.info(f"Cached idempotency response for key: {idempotency_key}")

                headers = dict(response.headers)
                headers["X-Cache"] = "STORE-IDEMPOTENCY"
                return Response(
                    content=body_bytes,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type
                )
            except Exception as e:
                logger.warning(f"Error saving idempotency response: {e}")

        return response
