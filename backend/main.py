from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import engine, Base
from routers import movies_router, reviews_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Review API",
    description="""
## 영화 리뷰 및 감성 분석 API

### 주요 기능
- **영화 관리**: 영화 등록, 전체/특정 영화 조회, 삭제
- **리뷰 관리**: 리뷰 등록(자동 감성 분석), 전체/특정 리뷰 조회, 삭제
- **평점 조회**: 리뷰 감성 분석 점수 평균 조회
- **감성 분석**: 한국어 키워드 기반 감성 분석 (긍정/부정 판별)
    """,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router, prefix="/movies", tags=["Movies"])
app.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Movie Review API", "docs": "/docs"}
