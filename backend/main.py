from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import movies, reviews
from sentiment import get_analyzer

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 모델 프리로드 (첫 요청 타임아웃 방지)
    get_analyzer()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Movie Review API",
    description="""
## 영화 리뷰 및 감성 분석 API

### 주요 기능
- **영화 관리**: 영화 등록, 전체/특정 영화 조회, 삭제
- **리뷰 관리**: 리뷰 등록(자동 감성 분석), 전체/특정 리뷰 조회, 삭제
- **평점 조회**: 리뷰 감성 분석 점수 평균 조회
- **감성 분석**: KR-FinBert-SC 모델 (동적 양자화 INT8 경량화 적용)
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

app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Movie Review API", "docs": "/docs"}
