from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)


class TicketStatusUpdate(BaseModel):
    status: Literal["open", "in_progress", "resolved"]


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    priority: str
    summary: Optional[str] = None
    suggested_reply: Optional[str] = None
    ai_generated: bool
    status: str
    created_at: datetime
