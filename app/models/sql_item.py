# Standard library imports
from datetime import datetime
from typing import Optional

# Third-party imports
from pydantic import BaseModel, Field


class SqlItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")


class SqlItemCreate(SqlItemBase):
    pass


class SqlItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class SqlItemResponse(SqlItemBase):
    id: str
    created_at: datetime
    updated_at: datetime


class PaginatedSqlItems(BaseModel):
    items: list[SqlItemResponse]
    total_count: int
    page: int
    size: int
    total_pages: int
