from typing import Any, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Natural language question for the database"
    )


# ============================================================
# SUCCESS / AGENT RESPONSE
# ============================================================

class AgentResponse(BaseModel):

    success: bool

    question: Optional[str] = None

    sql: Optional[str] = None

    results: Optional[List[List[Any]]] = None

    answer: Optional[str] = None

    attempts: Optional[int] = None

    error_type: Optional[str] = None

    error: Optional[str] = None


# ============================================================
# API ERROR RESPONSE
# ============================================================

class ErrorResponse(BaseModel):

    success: bool = False

    error_type: str

    message: str

    details: Optional[Any] = None