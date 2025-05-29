# app.py  ─ Safe-Steward Utility Framework (툴팁 + Expander 버전)
# ──────────────────────────────────────────────────────────
import streamlit as st
import plotly.express as px
from framework import (
    CRITERIA,
    gate_human_limit,
    gate_irreversible,
    weighted_score,
    final_status,
)

# ─────────────────── 기본 설정 ───────────────────
st.set_page_config(
    page_title="Safe-Steward Utility Framework",
    page_icon="⚖️",
    layout="centered",
)
st.title("⚖️ Safe-Steward Utility Framework")
st.caption("생명공학 기술 허용 여부를 단계별로 평가·시각화하는 의사결정 도구입니다.")

# 단계 추적용 세션 변수
if "step" not in st.session_state:
    st.session_state.step = 1

# ─────────────────── 1단계 ───────────────────
if st.session_state.step == 1:
    st.header("1️⃣ Human-Limit Trigger")
    st.caption("인간적 방법·자원으로 문제를 해결하려는 시도가 충분했는지 점검합니다.")
    tried = st.radio(
        "인간적 방법을 충분히 시도했습니까?",
        ("아직 충분하지 않음", "예, 충분히 시도함"),
        key="tried",
    )

    col_spacer, col_next = st.columns([5, 1])
    if col_next.button("다음"):
        st.session_state.gate1 = gate_human_limit(tried.startswith("예"))
        if st.session_state.gate1 != "Pass":
            st.error("추가 연구·자원 투입 후 재평가가 필요합니다.")
            st.stop()
        st.session_state.step = 2
        st.rerun()

# ─────────────────── 2단계 ───────────────────
if st.session_state.step == 2:
    st.header("2️⃣ Irreversible-Harm Gate")
    st.caption("발생 가능한 위험에 대해 점검합니다.")

    controllable = st.radio(
        "위험이 통제 가능하거나 가역적입니까?",
        ("아니오, 치명적·비가역적", "예, 통제/가역 가능"),
        key="controllable",
    )

    col_prev, col_next = st.columns(2)
    if col_prev.button("이전"):
        st.session_state.step = 1
        st.rerun()

    if col_next.button("다음"):
        st.session_state.gate2 = gate_irreversible(controllable.startswith("예"))
        if st.session_state.gate2 != "Pass":
            st.error("치명적·비가역 위험이 있는 기술은 즉시 기각됩니다.")
            st.stop()
        st.session_state.step = 3
        st.rerun()

# ─────────────────── 3단계 ───────────────────
if st.session_state.step == 3:
    st.header("3️⃣ Multi-Criteria Scoring (0-100)")
    st.caption(
        "각 평가 항목을 0 ~ 100 점으로 매겨 주세요. "
        "각 평가항목을 더 자세히 보려면 ▶ 아이콘을 눌러 펼쳐보기가 가능합니다."
    )

    # ⇣ 항목별 설명 (툴팁 & Expander 내용) ⇣
    EXPLAIN = {
        "Majority Benefit": """
            해당 기술이 사회·경제·건강 측면에서 순행복(총 편익 − 총 비용)을
            얼마나 증가시키는지 평가합니다.
            - 0점 : 순행복 감소 (피해가 편익보다 큼)
            - 50점 : 편익 ≈ 피해
            - 100점 : 순행복 대폭 증가
        """,
        "Non-Human Welfare": """
            AI·동물·생태계 등 비인간 주체에 미치는 긍·부정적 영향을 평가합니다.
            - 0점 : 심각한 피해
            - 50점 : 경미/중립
            - 100점 : 순이익 발생
        """,
        "Necessity Beyond Human": """
            인간 능력만으로 해결할 수 없거나 극도로 비효율일 때 높은 점수를 줍니다.
            - 0점 : 사람만으로 충분히 해결 가능
            - 100점 : 비인간 자원(로봇·AI 등) 없이는 불가능
        """,
        "Reversibility & Control": """
            실패 시 가역성(되돌림)·차단·모니터링이 가능한지 평가합니다.
            - 0점 : 통제 불가, 비가역
            - 100점 : 실시간 차단·완전 회수 가능
        """,
        "Justice & Equity": """
            취약집단 손익·격차 변화를 평가합니다.
            - 0점 : 불평등 심화, 취약층 손실
            - 100점 : 형평성 개선, 취약층 순이익
        """,
        "Virtue Alignment": """
            4대 윤리 덕목(자율·정의·선행·무해) 충족 정도를 평가합니다.
            - 0점 : 대부분 위반
            - 100점 : 모두 증진
        """,
    }

    raw_scores = []
    for idx, (crit, _) in enumerate(CRITERIA):
        # 펼쳐보기 Expander
        with st.expander(f"➤ {crit} 설명", expanded=False):
            st.markdown(EXPLAIN[crit])

        # 슬라이더 + 툴팁
        score = st.slider(
            crit,
            0, 100, 50, 5,
            key=f"score_{idx}",
            help=EXPLAIN[crit].strip().split("\n")[0]  # 첫 줄을 툴팁으로
        )
        raw_scores.append(score)

    col_prev, col_calc = st.columns(2)

    if col_prev.button("이전"):
        st.session_state.step = 2
        st.rerun()

    if col_calc.button("결과 확인"):
        total = weighted_score(raw_scores)
        decision = final_status(
            st.session_state.gate1,
            st.session_state.gate2,
            total,
            min(raw_scores),
        )

        # ─ 결과 요약 패널 ─
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Weighted Total", f"{total:.1f} / 100")
            st.metric("Decision", decision)
        with col2:
            fig = px.line_polar(
                r=raw_scores,
                theta=[c for c, _ in CRITERIA],
                line_close=True,
                range_r=[0, 100],
            )
            fig.update_traces(fill="toself")
            st.plotly_chart(fig, use_container_width=True)

        # 세부 점수 표
        st.write("### 세부 점수")
        st.table({c: [s] for (c, _), s in zip(CRITERIA, raw_scores)})

        # 처음으로 돌아가기 버튼
        if st.button("처음으로"):
            st.session_state.clear()
            st.session_state.step = 1
            st.rerun()
