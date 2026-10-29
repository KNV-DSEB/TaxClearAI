from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: int
