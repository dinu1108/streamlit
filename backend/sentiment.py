import os
import requests

MODEL_URL = "https://router.huggingface.co/hf-inference/models/snunlp/KR-FinBert-SC"
LABEL_MAP = {"LABEL_0": "negative", "LABEL_1": "positive"}


def _get_headers() -> dict:
    token = os.environ.get("HF_API_TOKEN", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def get_analyzer():
    return SentimentAnalyzer()


class SentimentAnalyzer:
    def analyze(self, text: str) -> dict:
        try:
            response = requests.post(
                MODEL_URL,
                headers=_get_headers(),
                json={"inputs": text},
                timeout=30,
            )
            response.raise_for_status()
            results = response.json()

            if isinstance(results, list) and results:
                items = results[0] if isinstance(results[0], list) else results
                scores = {item["label"]: item["score"] for item in items}
                positive_score = scores.get("LABEL_1", 0.0)
                predicted_label = "positive" if positive_score >= 0.5 else "negative"
                return {"label": predicted_label, "score": positive_score}

        except Exception as e:
            raise RuntimeError(f"HuggingFace API 호출 실패: {e}")

        return {"label": "negative", "score": 0.0}
