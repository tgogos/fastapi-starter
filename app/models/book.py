"""Pydantic schemas for books API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=200)
    year: Optional[int] = Field(None, ge=0, le=9999)
    notes: Optional[str] = Field(None, max_length=2000)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    year: Optional[int] = Field(None, ge=0, le=9999)
    notes: Optional[str] = Field(None, max_length=2000)


class BookResponse(BookBase):
    id: str
    created_at: datetime
    updated_at: datetime


class PaginatedBooks(BaseModel):
    items: list[BookResponse]
    total_count: int
    page: int
    size: int
    total_pages: int
