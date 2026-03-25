from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models import Movie, Review
from schemas import MovieCreate, MovieResponse, RatingResponse, ReviewResponse

router = APIRouter()


def _build_movie_response(movie: Movie, db: Session) -> MovieResponse:
    avg = db.query(func.avg(Review.sentiment_score)).filter(Review.movie_id == movie.id).scalar()
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        release_date=movie.release_date,
        director=movie.director,
        genre=movie.genre,
        poster_url=movie.poster_url,
        created_at=movie.created_at,
        average_rating=round(avg, 4) if avg is not None else None,
    )


@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(payload: MovieCreate, db: Session = Depends(get_db)):
    movie = Movie(**payload.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return _build_movie_response(movie, db)


@router.get("/", response_model=List[MovieResponse])
def list_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).order_by(Movie.created_at.desc()).all()
    return [_build_movie_response(m, db) for m in movies]


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    return _build_movie_response(movie, db)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    db.delete(movie)
    db.commit()


@router.get("/{movie_id}/rating", response_model=RatingResponse)
def get_movie_rating(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")

    result = (
        db.query(func.avg(Review.sentiment_score), func.count(Review.id))
        .filter(Review.movie_id == movie_id)
        .first()
    )
    avg_score, count = result
    return RatingResponse(
        movie_id=movie_id,
        average_rating=round(avg_score, 4) if avg_score is not None else 0.0,
        review_count=count or 0,
    )


@router.get("/{movie_id}/reviews", response_model=List[ReviewResponse])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    return (
        db.query(Review)
        .filter(Review.movie_id == movie_id)
        .order_by(Review.created_at.desc())
        .all()
    )
