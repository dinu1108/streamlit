import os
import streamlit as st
import requests
from datetime import date

# ── 설정 ──────────────────────────────────────────────────────────────────────
# 우선순위: 환경변수(Render) → Streamlit secrets → 로컬 기본값
API_BASE = (
    os.environ.get("API_BASE_URL")
    or st.secrets.get("API_BASE_URL", "http://localhost:8000")
)

st.set_page_config(
    page_title="🎬 영화 리뷰 서비스",
    page_icon="🎬",
    layout="wide",
)

# ── 세션 초기화 ───────────────────────────────────────────────────────────────
if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None

# ── API 헬퍼 ──────────────────────────────────────────────────────────────────

# ngrok 무료 플랜의 브라우저 경고 페이지를 우회하는 헤더
_HEADERS = {"ngrok-skip-browser-warning": "true"}


def api_get(path: str, params: dict = None):
    try:
        res = requests.get(f"{API_BASE}{path}", params=params, headers=_HEADERS, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error("백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return None
    except Exception as e:
        st.error(f"API 오류: {e}")
        return None


def api_post(path: str, payload: dict):
    try:
        res = requests.post(f"{API_BASE}{path}", json=payload, headers=_HEADERS, timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error("백엔드 서버에 연결할 수 없습니다.")
        return None
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        st.error(f"오류: {detail}")
        return None
    except Exception as e:
        st.error(f"요청 실패: {e}")
        return None


def api_delete(path: str) -> bool:
    try:
        res = requests.delete(f"{API_BASE}{path}", headers=_HEADERS, timeout=10)
        res.raise_for_status()
        return True
    except Exception as e:
        st.error(f"삭제 실패: {e}")
        return False


# ── 유틸 ──────────────────────────────────────────────────────────────────────

def score_to_stars(avg: float) -> float:
    """감성 점수(0~1) → 별점(1~5)"""
    return round(1 + avg * 4, 1)


def stars_display(stars: float) -> str:
    full = int(stars)
    half = 1 if (stars - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty


def sentiment_badge(label: str) -> str:
    return "😊 긍정" if label == "positive" else "😞 부정"


# ── 페이지: 영화 목록 ─────────────────────────────────────────────────────────

def page_movie_list():
    st.title("🎬 영화 목록")
    movies = api_get("/movies/")
    if not movies:
        st.info("등록된 영화가 없습니다. '영화 추가' 메뉴에서 영화를 추가해보세요.")
        return

    cols_per_row = 3
    for i in range(0, len(movies), cols_per_row):
        row = st.columns(cols_per_row)
        for j, movie in enumerate(movies[i : i + cols_per_row]):
            with row[j]:
                _render_movie_card(movie)


def _render_movie_card(movie: dict):
    with st.container(border=True):
        if movie.get("poster_url"):
            st.image(movie["poster_url"], use_container_width=True)
        else:
            st.markdown("### 🎬")

        st.markdown(f"**{movie['title']}**")
        st.caption(f"{movie['release_date']} | {movie['director']} | {movie['genre']}")

        avg = movie.get("average_rating")
        if avg is not None:
            stars = score_to_stars(avg)
            st.markdown(f"{stars_display(stars)} **{stars}점** / 5점")
        else:
            st.caption("리뷰 없음")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("리뷰 보기", key=f"view_{movie['id']}", use_container_width=True):
                st.session_state.selected_movie_id = movie["id"]
                st.rerun()
        with col_b:
            if st.button("삭제", key=f"del_{movie['id']}", use_container_width=True):
                if api_delete(f"/movies/{movie['id']}"):
                    st.success("삭제되었습니다.")
                    st.rerun()


# ── 페이지: 영화 상세 (전체 리뷰) ────────────────────────────────────────────

def page_movie_detail():
    movie_id = st.session_state.selected_movie_id
    movie = api_get(f"/movies/{movie_id}")
    if not movie:
        st.session_state.selected_movie_id = None
        st.rerun()
        return

    if st.button("← 목록으로 돌아가기"):
        st.session_state.selected_movie_id = None
        st.rerun()

    st.divider()

    # 영화 정보
    col_img, col_info = st.columns([1, 2])
    with col_img:
        if movie.get("poster_url"):
            st.image(movie["poster_url"], use_container_width=True)
        else:
            st.markdown("## 🎬")

    with col_info:
        st.title(movie["title"])
        st.markdown(f"**감독:** {movie['director']}")
        st.markdown(f"**장르:** {movie['genre']}")
        st.markdown(f"**개봉일:** {movie['release_date']}")

        avg = movie.get("average_rating")
        if avg is not None:
            stars = score_to_stars(avg)
            st.markdown(f"### {stars_display(stars)} {stars}점 / 5점")
        else:
            st.markdown("*아직 리뷰가 없습니다.*")

    st.divider()

    # 전체 리뷰
    reviews = api_get(f"/movies/{movie_id}/reviews")
    review_count = len(reviews) if reviews else 0
    st.subheader(f"리뷰 ({review_count}개)")

    if not reviews:
        st.info("이 영화의 리뷰가 없습니다. 리뷰 작성 메뉴에서 첫 리뷰를 남겨보세요!")
        return

    for review in sorted(reviews, key=lambda r: r["created_at"], reverse=True):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 2, 5, 1])
            c1.markdown(f"**{review['author']}**")
            c2.caption(review["created_at"][:10])
            c3.write(review["content"])
            badge = "😊 긍정" if review["sentiment_label"] == "positive" else "😞 부정"
            c4.markdown(badge)

            if st.button("삭제", key=f"del_review_{review['id']}"):
                if api_delete(f"/reviews/{review['id']}"):
                    st.success("삭제되었습니다.")
                    st.rerun()


# ── 페이지: 영화 추가 ─────────────────────────────────────────────────────────

def page_add_movie():
    st.title("➕ 영화 추가")
    with st.form("add_movie_form"):
        title = st.text_input("제목 *")
        release_date = st.date_input("개봉일 *", value=date.today())
        director = st.text_input("감독 *")
        genre = st.text_input("장르 *", placeholder="예: 액션, 드라마, 로맨스")
        poster_url = st.text_input("포스터 URL", placeholder="https://...")
        submitted = st.form_submit_button("등록", type="primary")

    if not submitted:
        return

    if not all([title, director, genre]):
        st.warning("필수 항목(*)을 모두 입력해주세요.")
        return

    payload = {
        "title": title,
        "release_date": str(release_date),
        "director": director,
        "genre": genre,
        "poster_url": poster_url or None,
    }
    result = api_post("/movies/", payload)
    if result:
        st.success(f"'{result['title']}' 영화가 등록되었습니다!")
        st.balloons()


# ── 페이지: 리뷰 작성 ─────────────────────────────────────────────────────────

def page_write_review():
    st.title("✍️ 리뷰 작성")
    movies = api_get("/movies/")
    if not movies:
        st.info("먼저 영화를 등록해주세요.")
        return

    movie_options = {m["title"]: m["id"] for m in movies}

    with st.form("write_review_form"):
        selected_title = st.selectbox("영화 선택 *", options=list(movie_options.keys()))
        author = st.text_input("작성자 이름 *")
        content = st.text_area("리뷰 내용 *", height=150, placeholder="영화에 대한 리뷰를 작성해주세요...")
        submitted = st.form_submit_button("리뷰 등록 & 감성 분석", type="primary")

    if not submitted:
        return

    if not all([author, content]):
        st.warning("작성자 이름과 리뷰 내용을 입력해주세요.")
        return

    with st.spinner("감성 분석 중... (최초 실행 시 모델 로딩으로 시간이 걸릴 수 있습니다)"):
        payload = {"movie_id": movie_options[selected_title], "author": author, "content": content}
        result = api_post("/reviews/", payload)

    if not result:
        return

    st.success("리뷰가 등록되었습니다!")
    st.divider()
    st.subheader("감성 분석 결과")

    col1, col2 = st.columns(2)
    label_kr = "긍정" if result["sentiment_label"] == "positive" else "부정"
    emoji = "😊" if result["sentiment_label"] == "positive" else "😞"
    col1.metric("감성", f"{emoji} {label_kr}")
    col2.metric("감성 점수 (별점 환산)", f"{score_to_stars(result['sentiment_score'])}점 / 5점")
    st.info(f"리뷰 내용: {result['content']}")


# ── 페이지: 최근 리뷰 ─────────────────────────────────────────────────────────

def page_recent_reviews():
    st.title("📋 최근 리뷰 (최대 10개)")
    reviews = api_get("/reviews/", params={"limit": 10})
    if not reviews:
        st.info("등록된 리뷰가 없습니다.")
        return

    movies = api_get("/movies/") or []
    movie_map = {m["id"]: m["title"] for m in movies}

    for review in reviews:
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 4, 1])
            movie_title = movie_map.get(review['movie_id'], f"ID:{review['movie_id']}")
            c1.markdown(f"**{movie_title}**")
            c2.write(review["author"])
            c3.caption(review["created_at"][:10])
            c4.write(review["content"])
            badge = "😊 긍정" if review["sentiment_label"] == "positive" else "😞 부정"
            c5.markdown(badge)


# ── 사이드바 & 라우팅 ─────────────────────────────────────────────────────────

PAGES = {
    "🎬 영화 목록": "movie_list",
    "➕ 영화 추가": "add_movie",
    "✍️ 리뷰 작성": "write_review",
    "📋 최근 리뷰": "recent_reviews",
}

with st.sidebar:
    st.title("영화 리뷰 서비스")
    st.caption(f"Backend: `{API_BASE}`")
    st.divider()
    selected_label = st.radio("메뉴", list(PAGES.keys()), label_visibility="collapsed")
    selected_page = PAGES[selected_label]

    # 다른 메뉴 클릭 시 상세 페이지 초기화
    if selected_page != "movie_list":
        st.session_state.selected_movie_id = None

# 라우팅
if selected_page == "movie_list":
    if st.session_state.selected_movie_id is not None:
        page_movie_detail()
    else:
        page_movie_list()
elif selected_page == "add_movie":
    page_add_movie()
elif selected_page == "write_review":
    page_write_review()
elif selected_page == "recent_reviews":
    page_recent_reviews()
