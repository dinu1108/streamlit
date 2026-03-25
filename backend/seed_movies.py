"""2025년 인기 영화 시드 데이터 삽입 스크립트"""
import requests

API_BASE = "https://movie-review-api-g9bd.onrender.com"

MOVIES = [
    {
        "title": "미키 17",
        "release_date": "2025-02-28",
        "director": "봉준호",
        "genre": "SF/스릴러",
        "poster_url": "https://i.namu.wiki/i/aW4LCnah5HbuoxwERx3aQ1B-bjHEOIFjhFQ6tGvMIZFBTR6XY3bVPG9PiTSrpgS26rDywd1wTV_rA94sPt2TNnVpvImg4eN_BWcX7aBKW1RK_kujWSRU60uws_9x0Qb7MqYO8wnpKU_zpgOCIP5rHg.webp",
    },
    {
        "title": "캡틴 아메리카: 브레이브 뉴 월드",
        "release_date": "2025-02-12",
        "director": "줄리어스 오나",
        "genre": "액션/히어로",
        "poster_url": "https://i.namu.wiki/i/xnlEQPGLC2Pm-W3Yr9Y2Xc9lc41eo2LN9Cc1znw41J8ac2kJuf9x6SlVd8QNAs4T-N8QAIdXNS2tvXL0Ehj1lfgd9fjGPPbFYLTkZHhA7cZedpaisafXynBB9Wq_CUEfe2G274CcZKA5y4nCNqBz9A.webp",
    },
    {
        "title": "마인크래프트 무비",
        "release_date": "2025-04-02",
        "director": "재러드 헤스",
        "genre": "어드벤처/코미디",
        "poster_url": "https://i.namu.wiki/i/1heZfdOwNPlFyDFy4BzpZsiJqOMJxpBg_NuM7C2YD8zFS-n1Kf6qPnIndve1QcxXGbgFGbvfv03KKogFfiAu696w77Xq7rCrTTtA_CHdHTac7BIT-tbmF_NwsDm87rthwWNl6lOuxreuBArHk_xxBA.webp",
    },
    {
        "title": "미션 임파서블: 파이널 레코닝",
        "release_date": "2025-05-21",
        "director": "크리스토퍼 맥쿼리",
        "genre": "액션/스파이",
        "poster_url": "https://i.namu.wiki/i/V66b2PpkgziEPK9vynyNhzCG7pv4GCcfR5FBXbUPBH36wnvFw9xAfOBtqOxpAI1TDuY4YGDMxUqDK2jK5dNVt89FA-zUc3q2BcKbRf5StG00ffBEFmLoJY8X3-RzOQ5qotSvrVKzT9V1UFskAb6Bcw.webp",
    },
    {
        "title": "쥬라기 월드: 리버스",
        "release_date": "2025-07-02",
        "director": "가레스 에드워즈",
        "genre": "SF/어드벤처",
        "poster_url": "https://i.namu.wiki/i/APWZplQ4rxNIrqzIdPa-mwcD3HZAt4CZ4tqWcGuzrc8HiNISmt0srCu7z2hHkvKSAoG383IfnKaggvghytqy7BXg51fAGkCYvbW67NoxHwVmKany4M89cRGeg6RrT2m5vR2y98Pa6lFhIP_60G7aBw.webp",
    },
    {
        "title": "썬더볼츠",
        "release_date": "2025-04-30",
        "director": "제이크 슈라이어",
        "genre": "액션/히어로",
        "poster_url": "https://i.namu.wiki/i/OfX4zfJNfmOfCIAi-v_CFfPulqz8i4bBpq2lfUY0RrmACkBsbFb4U5HzKde9MmAMa2XC0nKsoEl6J8ttYfxI8gJ3HOzulVhWBYyTLtwZMU8e91NDS8E_PBZycomkiCmowGkQxY4IOCrAEfm0oz_EBw.webp",
    },
    {
        "title": "하울링",
        "release_date": "2025-01-22",
        "director": "류승완",
        "genre": "액션/범죄",
        "poster_url": None,
    },
    {
        "title": "노킹 온 헤븐스 도어",
        "release_date": "2025-03-19",
        "director": "이정범",
        "genre": "드라마/범죄",
        "poster_url": "https://i.namu.wiki/i/ZV-7j0E0yvNq2UQq7JyHPIu-4VNabSPVVDm3_l0vqAPeK5obcIL2wKN2r_qIWlw4wctjo4MWp2KdYOkoT9G3zkWdQrB3Rj72D6YnWlA217iEFeVxTpD8jetCFVFjJ7awZcXuPMoJZtgVoHtzzq-nPA.webp",
    },
    {
        "title": "F1",
        "release_date": "2025-06-25",
        "director": "조셉 코신스키",
        "genre": "액션/스포츠",
        "poster_url": "https://i.namu.wiki/i/Bl6gg915y5g2zoMBf3QfoOcv7ZnsBAwgY_Gapq8CVDz8wTqwW90EfmXsGUW-p8K9GrsNJMUhoGZgiNddpU6iN2HGTE0fB0IVlURT7VXbZKZYYEJzSGF7n4J-bhtZ-_qmWsrWVFLtuQXicFAKHFkSyw.webp",
    },
    {
        "title": "스파이더맨: 브랜드 뉴 데이",
        "release_date": "2025-07-23",
        "director": "데스틴 다니엘 크레튼",
        "genre": "액션/히어로",
        "poster_url": "https://i.namu.wiki/i/KRVW78ht5H8elbMeR7dfKfh1h_F9EGehGtxyZ2cGSQK5BQCdVl9Kk5ezwvNLfb4RGwLWIN6K211ZoRJlfeuIH14BmXPbuMPtMatb7DVyGPrFm0Fr7iljis4X2si8Gpw2uGHenwXMVAAMG4TEKWi-Hg.webp",
    },
]


def seed():
    print("영화 데이터 삽입 시작...\n")
    success = 0
    for movie in MOVIES:
        try:
            res = requests.post(f"{API_BASE}/movies/", json=movie, timeout=60)
            res.raise_for_status()
            data = res.json()
            print(f"[OK] [{data['id']}] {data['title']} ({data['release_date']})")
            success += 1
        except Exception as e:
            print(f"[FAIL] {movie['title']} 실패: {e}")

    print(f"\n완료: {success}/{len(MOVIES)}개 삽입")


if __name__ == "__main__":
    seed()
