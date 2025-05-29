# framework.py  ─ Safe-Steward Utility Framework 로직 모듈
# (2025-05-29, 한글 결과 라벨 버전)
# ─────────────────────────────────────────────────────────
import numpy as np

# ✔️  평가 기준과 가중치
CRITERIA = [
    ("Majority Benefit",       0.25),
    ("Non-Human Welfare",      0.20),
    ("Necessity Beyond Human", 0.15),
    ("Reversibility & Control",0.15),
    ("Justice & Equity",       0.15),
    ("Virtue Alignment",       0.10),
]
WEIGHTS = np.array([w for _, w in CRITERIA])

# ───────── Gate 함수들 ─────────
def gate_human_limit(attempted: bool) -> str:
    """1단계: 인간 한계 내 해결 시도 여부"""
    return "Pass" if attempted else "Re-evaluate"

def gate_irreversible(risk_controllable: bool) -> str:
    """2단계: 통제·가역성 여부"""
    return "Pass" if risk_controllable else "Reject"

# ───────── 점수 계산 ─────────
def weighted_score(raw_scores: list[float]) -> float:
    """가중 합계 (0~100)"""
    return float(np.dot(raw_scores, WEIGHTS))

# ───────── 최종 판정 ─────────
def final_status(g1: str, g2: str, total: float, min_single: float) -> str:
    """
    Gate1·Gate2 결과, 가중 총점, 단일 항목 최소값을 종합해
    한글 라벨로 최종 판정 반환
    """
    if g1 == "Pass" and g2 == "Pass" and total >= 60 and min_single >= 25:
        return "✅ 기술 사용 허용"
    return "🔄 기술 사용 재검토"
