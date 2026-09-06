from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database: str

class ReadinessResponse(BaseModel):
    status: str
    database: str