from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class CreditScoreRequest(BaseModel):
    data_sources: Dict[str, bool]  # {"bank_data": True, "bki": True, etc}

class CreditScoreResponse(BaseModel):
    score: int
    score_category: str
    factors: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class ParserJobResponse(BaseModel):
    id: int
    status: str
    data_sources: Dict[str, bool]
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True