from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class CreditScoreRequest(BaseModel):
    use_blockchain: bool = True
    data_sources: Dict[str, bool] = {"manual": True} # {"bank_data": True, "bki": True, etc}

class CreditScoreResponse(BaseModel):
    id: int
    score: int
    score_category: str
    reputation_score: float
    blockchain_hash: Optional[str] = None
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
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

class CreditRequestResponse(BaseModel):
    id: int
    status: str
    blockchain_recorded: bool
    created_at: datetime

    class Config:
        from_attributes = True