import torch
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSequenceClassification

MODEL_NAME = "snunlp/KR-FinBert-SC"
LABEL_MAP = {0: "negative", 1: "positive"}


class SentimentAnalyzer:
    """싱글톤 패턴 + ONNX Runtime으로 경량화된 감성 분석기.

    기존 동적 양자화(INT8) 대비:
    - 추론 속도 2~5배 향상 (PyTorch 런타임 오버헤드 제거)
    - PyTorch를 추론 엔진 대신 ONNX Runtime 사용
    - export=True: 최초 실행 시 자동 ONNX 변환 후 캐시
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._load_model()
        self._initialized = True

    def _load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = ORTModelForSequenceClassification.from_pretrained(
            MODEL_NAME, export=True
        )

    def analyze(self, text: str) -> dict:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )

        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        predicted_class = int(probs.argmax().item())
        label = LABEL_MAP.get(predicted_class, "negative")

        # 긍정 클래스 확률(0.0~1.0)을 그대로 score로 사용
        # → 별점이 1점/5점 극단값이 아닌 연속적인 값으로 표시됨
        positive_prob = float(probs[0][1].item())

        return {"label": label, "score": positive_prob}


def get_analyzer() -> SentimentAnalyzer:
    return SentimentAnalyzer()
