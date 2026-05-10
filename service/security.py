"""Security utilities for BTP Engine HTTP Service."""

import os
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """
    Verify the bearer token.
    
    If BTP_ENGINE_TOKEN is not set, no authentication is required.
    If BTP_ENGINE_TOKEN is set, the request must provide a valid bearer token.
    """
    expected_token = os.getenv("BTP_ENGINE_TOKEN")
    
    # If no token is configured, allow all requests
    if not expected_token:
        return True
    
    # If token is configured but not provided
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization token required"
        )
    
    # Verify token
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid authorization token"
        )
    
    return True
