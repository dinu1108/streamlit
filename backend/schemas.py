from pydantic import BaseModel, HttpUrl, field_validator
from datetime import date, datetime
from typing import Optional


class MovieCreate(BaseModel):
    title: str
    release_date: date
    director: str
    genre: str
    poster_url: Optional[str] = None

    @field_validator("title", "director", "genre")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v.strip()


class MovieResponse(BaseModel):
    id: int
    title: str
    release_date: date
    director: str
    genre: str
    poster_url: Optional[str]
    created_at: datetime
    average_rating: Optional[float] = None

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    movie_id: int
    author: str
    content: str

    @field_validator("author", "content")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v.strip()


class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    author: str
    content: str
    sentiment_label: str
    sentiment_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class RatingResponse(BaseModel):
    movie_id: int
    average_rating: float
    review_count: int
