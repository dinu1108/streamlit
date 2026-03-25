POSITIVE_WORDS = [
    "좋", "훌륭", "최고", "재미", "추천", "감동", "완벽", "만족", "기대",
    "멋", "대단", "신선", "박력", "압권", "완성도", "탄탄", "즐거", "행복",
    "최애", "걸작", "수작", "경이", "통쾌", "생생", "웅장", "스릴", "박진",
    "매력", "훌륭", "몰입", "완벽", "아름", "감탄", "뛰어", "인상",
]

NEGATIVE_WORDS = [
    "나쁘", "실망", "아쉽", "지루", "평범", "실패", "최악", "별로",
    "단조", "약하", "부족", "심심", "복잡", "갑작스", "늘어지", "예상 가능",
    "기억에 남는 장면도 없", "그냥 그런", "노잼", "재미없", "별로",
    "졸리", "후회", "돈 아깝", "시간 낭비", "구리", "별점 1", "최악",
    "형편없", "억지", "어색", "지겹", "식상", "클리셰",
]


def _keyword_score(text: str) -> float:
    pos = sum(1 for w in POSITIVE_WORDS if w in text)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text)
    total = pos + neg
    if total == 0:
        return 0.4  # 매칭 없으면 약한 부정으로 처리
    return pos / total


def get_analyzer():
    return SentimentAnalyzer()


class SentimentAnalyzer:
    def analyze(self, text: str) -> dict:
        score = _keyword_score(text)
        label = "positive" if score >= 0.5 else "negative"
        return {"label": label, "score": round(score, 4)}
