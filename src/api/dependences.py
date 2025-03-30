from fastapi import HTTPException, Request
from sqlmodel import select
from .database import Domains, SessionDep

def validate_source_ip(request: Request, session: SessionDep):
    """
    Dependency that validates the source IP address.
    Only allows access from localhost (127.0.0.1) or specified web endpoints.
    """
    # Get the client's IP address
    client_ip = request.client.host
    
    print(request.headers.get("host"))
    print(request.headers.get("host").split(":")[0])

    # Check if the request is from localhost
    if client_ip == "127.0.0.1":
        return True  # Allow all endpoints from localhost
    
    # Check if the request is from a whitelisted domain
    request_domain = request.headers.get("host").split(":")[0]
    client_domain = session.exec(select(Domains).where(Domains.domain == request_domain)).first()
    
    if not client_domain:
        raise HTTPException(
            status_code=403,
            detail="Domain not whitelisted."
        )
    
    if client_domain.status == "disabled":
        raise HTTPException(
            status_code=403,
            detail="Domain is disabled."
        )
    
    # Get the path from the request
    path = request.url.path
    
    # List of public endpoints (add more as needed)
    public_endpoints = [
        "/local/printers/",  # Get public printers
        "/local/print/json/",  # Print JSON data
        "/local/print/text/",  # Print text data
        "/local/print/pdf/",  # Print PDF data
        "/local/print/ticket/"  # Print ticket data
    ]
    
    # Check if the path is in the public endpoints list
    if path not in public_endpoints:
        raise HTTPException(
            status_code=403,
            detail="Endpoint not accessible from external sources."
        )
    
    return True
