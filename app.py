"""
ESG Copilot - AI-Powered Sustainability Assistant for Small Businesses
=====================================================================

A Streamlit mock-up that helps small businesses understand and improve their
sustainability performance through:
  - A guided ESG questionnaire
  - A Sustainability Score (overall + Environmental / Social / Governance)
  - AI-powered, prioritized improvement recommendations (OpenAI)
  - Industry benchmark comparison
  - Session-based progress tracking

Deploy on Streamlit Community Cloud: set OPENAI_API_KEY in the app's Secrets.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from esg_copilot.questions import INDUSTRIES, QUESTIONNAIRE, total_question_count
from esg_copilot.recommendations import api_key_available, generate_recommendations
from esg_copilot.scoring import benchmark_for, compute_scores, weakest_areas

# ---------------------------------------------------------------------------
# Page configuration & theme tokens
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ESG Copilot - Sustainability Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Color palette (eco theme)
GREEN = "#2e7d4f"
GREEN_LIGHT = "#5ca97a"
AMBER = "#d99a2b"
RED = "#c0563f"
INK = "#1b2a22"
MUTED = "#6b7b72"

CUSTOM_CSS = f"""
<style>
    .main .block-container {{ padding-top: 2rem; max-width: 1200px; }}
    .hero {{
        background: linear-gradient(135deg, {GREEN} 0%, {GREEN_LIGHT} 100%);
        color: #ffffff; padding: 2rem 2.25rem; border-radius: 16px; margin-bottom: 1.5rem;
    }}
    .hero h1 {{ color: #ffffff; margin: 0 0 .35rem 0; font-size: 2rem; }}
    .hero p {{ color: #eaf5ee; margin: 0; font-size: 1.05rem; }}
    .metric-card {{
        background: #f1f6f1; border: 1px solid #e0ebe3; border-radius: 14px;
        padding: 1.1rem 1.25rem; height: 100%;
    }}
    .metric-card h3 {{ margin: 0; font-size: .85rem; color: {MUTED}; font-weight: 600;
        text-transform: uppercase; letter-spacing: .04em; }}
    .metric-card .value {{ font-size: 2rem; font-weight: 700; color: {INK}; }}
    .rec-card {{
        background: #ffffff; border: 1px solid #e0ebe3; border-left: 5px solid {GREEN};
        border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: .85rem;
    }}
    .rec-card.high {{ border-left-color: {RED}; }}
    .rec-card.medium {{ border-left-color: {AMBER}; }}
    .rec-card.low {{ border-left-color: {GREEN}; }}
    .pill {{ display:inline-block; padding: .15rem .6rem; border-radius: 999px;
        font-size: .72rem; font-weight: 700; letter-spacing: .03em; }}
    .pill.high {{ background: #f7e0da; color: {RED}; }}
    .pill.medium {{ background: #f6ecd5; color: {AMBER}; }}
    .pill.low {{ background: #dcefe3; color: {GREEN}; }}
    .pill.pillar {{ background: #e7f0ea; color: {GREEN}; margin-left:.4rem; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
def _init_state() -> None:
    st.session_state.setdefault("results", None)
    st.session_state.setdefault("history", [])  # list of past assessments


_init_state()


def _score_color(score: float) -> str:
    if score >= 70:
        return GREEN
    if score >= 50:
        return AMBER
    return RED


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌱 ESG Copilot")
    st.caption("AI-Powered Sustainability Assistant for Small Businesses")
    st.divider()

    if api_key_available():
        st.success("AI recommendations: **Enabled**", icon="✅")
    else:
        st.warning(
            "AI recommendations: **rule-based fallback**.\n\n"
            "Add `OPENAI_API_KEY` in app Secrets to enable tailored AI advice.",
            icon="ℹ️",
        )

    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        "1. Tell us about your business\n"
        "2. Answer a short ESG questionnaire\n"
        "3. Get your Sustainability Score\n"
        "4. Review AI recommendations\n"
        "5. Track progress over time"
    )
    st.divider()
    if st.session_state["history"]:
        st.metric("Assessments completed", len(st.session_state["history"]))


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>ESG Copilot</h1>
        <p>Understand your sustainability performance and get practical, AI-powered
        recommendations built for small businesses.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_assess, tab_results, tab_progress = st.tabs(
    ["📝 Assessment", "📊 Results & Recommendations", "📈 Progress"]
)


# ---------------------------------------------------------------------------
# Tab 1: Assessment
# ---------------------------------------------------------------------------
with tab_assess:
    st.subheader("Tell us about your business")
    col1, col2 = st.columns(2)
    with col1:
        business_name = st.text_input("Business name", placeholder="e.g. Green Leaf Cafe")
    with col2:
        industry = st.selectbox("Industry", INDUSTRIES, index=0)

    st.divider()
    st.subheader("Sustainability questionnaire")
    st.caption(
        f"Answer all {total_question_count()} questions across the three ESG pillars. "
        "Pick the option that best matches your business today."
    )

    with st.form("assessment_form"):
        answers: Dict[str, float] = {}
        for pillar, questions in QUESTIONNAIRE.items():
            st.markdown(f"#### {pillar}")
            for q in questions:
                labels = [opt["label"] for opt in q["options"]]
                choice = st.radio(
                    q["text"],
                    options=range(len(labels)),
                    format_func=lambda i, labels=labels: labels[i],
                    help=q["help"],
                    key=f"q_{q['key']}",
                )
                answers[q["key"]] = q["options"][choice]["score"]
            st.divider()

        submitted = st.form_submit_button(
            "Calculate my Sustainability Score", type="primary", use_container_width=True
        )

    if submitted:
        scores = compute_scores(answers)
        weak = weakest_areas(answers, limit=5)
        with st.spinner("Generating your AI-powered recommendations..."):
            recs = generate_recommendations(business_name, industry, scores, weak)

        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "business_name": business_name or "Your business",
            "industry": industry,
            "answers": answers,
            "scores": scores,
            "weak_areas": weak,
            "recommendations": recs,
        }
        st.session_state["results"] = result
        st.session_state["history"].append(
            {
                "timestamp": result["timestamp"],
                "overall": scores["overall"],
                **scores["pillar_scores"],
            }
        )
        st.success(
            "Your assessment is ready! Open the **Results & Recommendations** tab.",
            icon="✅",
        )


# ---------------------------------------------------------------------------
# Tab 2: Results & Recommendations
# ---------------------------------------------------------------------------
def _gauge(score: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"font": {"size": 40, "color": INK}, "suffix": ""},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": MUTED},
                "bar": {"color": _score_color(score)},
                "bgcolor": "#ffffff",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "#f7e0da"},
                    {"range": [40, 55], "color": "#f6ecd5"},
                    {"range": [55, 70], "color": "#eaf3e0"},
                    {"range": [70, 100], "color": "#dcefe3"},
                ],
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=10))
    return fig


def _benchmark_chart(pillar_scores: Dict[str, float], bench: Dict[str, float]) -> go.Figure:
    pillars = list(pillar_scores.keys())
    fig = go.Figure()
    fig.add_bar(
        name="Your business",
        x=pillars,
        y=[pillar_scores[p] for p in pillars],
        marker_color=GREEN,
    )
    fig.add_bar(
        name="Industry average",
        x=pillars,
        y=[bench[p] for p in pillars],
        marker_color=GREEN_LIGHT,
        opacity=0.6,
    )
    fig.update_layout(
        barmode="group",
        height=340,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        yaxis=dict(range=[0, 100], title="Score"),
        plot_bgcolor="#ffffff",
    )
    return fig


with tab_results:
    result = st.session_state["results"]
    if not result:
        st.info("Complete the assessment first to see your results here.", icon="📝")
    else:
        scores = result["scores"]
        st.subheader(f"Results for {result['business_name']}")
        st.caption(f"Industry: {result['industry']} · Assessed {result['timestamp']}")

        # Top metrics
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("**Overall Sustainability Score**")
            st.plotly_chart(_gauge(scores["overall"]), use_container_width=True)
            st.markdown(
                f"<div class='metric-card'><h3>Rating</h3>"
                f"<div class='value'>{scores['letter']} · {scores['label']}</div></div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown("**Pillar breakdown**")
            pc = scores["pillar_scores"]
            mc1, mc2, mc3 = st.columns(3)
            for col, pillar in zip((mc1, mc2, mc3), pc.keys()):
                with col:
                    st.markdown(
                        f"<div class='metric-card'><h3>{pillar}</h3>"
                        f"<div class='value' style='color:{_score_color(pc[pillar])}'>"
                        f"{pc[pillar]}</div></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Benchmark vs. industry average**")
            bench = benchmark_for(result["industry"])
            st.plotly_chart(
                _benchmark_chart(pc, bench), use_container_width=True
            )

        st.divider()

        # Recommendations
        recs = result["recommendations"]
        st.subheader("AI-powered recommendations")
        if recs.get("source") == "ai":
            st.caption("Generated by OpenAI, tailored to your business.")
        else:
            st.caption("Rule-based recommendations (add an OpenAI API key for tailored AI advice).")
            if recs.get("error"):
                with st.expander("Why am I seeing fallback recommendations?"):
                    st.code(recs["error"])

        if recs.get("summary"):
            st.markdown(f"> {recs['summary']}")

        for rec in recs.get("recommendations", []):
            priority = str(rec.get("priority", "Medium")).lower()
            actions_html = "".join(f"<li>{a}</li>" for a in rec.get("actions", []))
            st.markdown(
                f"""
                <div class="rec-card {priority}">
                    <span class="pill {priority}">{rec.get('priority', 'Medium')} priority</span>
                    <span class="pill pillar">{rec.get('pillar', '')}</span>
                    <h4 style="margin:.5rem 0 .35rem 0;">{rec.get('area', '')}</h4>
                    <ul style="margin:0; padding-left:1.1rem;">{actions_html}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Tab 3: Progress
# ---------------------------------------------------------------------------
with tab_progress:
    st.subheader("Progress over time")
    history = st.session_state["history"]
    if len(history) == 0:
        st.info("Your completed assessments will appear here so you can track improvement.", icon="📈")
    else:
        df = pd.DataFrame(history)
        st.caption("Each assessment you complete this session is recorded below.")

        fig = go.Figure()
        for col, color in [
            ("overall", INK),
            ("Environmental", GREEN),
            ("Social", GREEN_LIGHT),
            ("Governance", AMBER),
        ]:
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df[col],
                        mode="lines+markers",
                        name=col.capitalize(),
                        line=dict(color=color, width=3 if col == "overall" else 2),
                    )
                )
        fig.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=30, b=10),
            yaxis=dict(range=[0, 100], title="Score"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            plot_bgcolor="#ffffff",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Assessment history**")
        st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)

        if st.button("Clear history"):
            st.session_state["history"] = []
            st.rerun()
