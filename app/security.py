"""Authentication dependencies shared by protected API routes."""

import os
import secrets

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str = Header(None)):
    """Validate the operator key without exposing its configured value."""
    expected = os.getenv("PUBLISH_API_KEY") or os.getenv("API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Publicacao indisponivel: autenticacao nao configurada")
    if not isinstance(x_api_key, str) or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
