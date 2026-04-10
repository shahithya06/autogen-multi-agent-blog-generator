"""
Streamlit Frontend — Multi-Agent Blog Generator
------------------------------------------------
Run: streamlit run app.py
"""

import asyncio
import json
import os
import threading
import queue
import streamlit as st
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Base */
  [data-testid="stAppViewContainer"] { background: #0f1117; }
  [data-testid="stSidebar"] { background: #161b27; border-right: 1px solid #1e2a3a; }

  /* Typography */
  h1, h2, h3 { color: #e2e8f0 !important; }
  p, li, label { color: #94a3b8; }

  /* Teal accent */
  .accent { color: #0d9488; font-weight: 600; }

  /* Agent cards */
  .agent-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-left: 3px solid #0d9488;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
  }
  .agent-card .agent-name { color: #0d9488; font-weight: 700; font-size: 14px; margin-bottom: 4px; }
  .agent-card .agent-role { color: #64748b; font-size: 12px; margin-bottom: 8px; }
  .agent-card .agent-desc { color: #94a3b8; font-size: 13px; line-height: 1.5; }

  /* Status badges */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }
  .badge-idle    { background: #1e2a3a; color: #64748b; }
  .badge-running { background: #0d948820; color: #0d9488; border: 1px solid #0d9488; }
  .badge-done    { background: #16a34a20; color: #22c55e; border: 1px solid #22c55e; }

  /* Output sections */
  .output-box {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 20px 24px;
    margin-top: 12px;
  }
  .output-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #0d9488;
    margin-bottom: 10px;
  }
  .output-text {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.8;
    white-space: pre-wrap;
  }

  /* Review JSON cards */
  .review-card {
    background: #0f1117;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
  }
  .review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  .review-role { color: #0d9488; font-weight: 700; font-size: 13px; }
  .score-pill {
    background: #0d948820;
    color: #0d9488;
    border: 1px solid #0d9488;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 700;
  }
  .review-section-label { color: #475569; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin: 8px 0 4px; }
  .review-item { color: #94a3b8; font-size: 13px; margin: 3px 0 3px 12px; }

  /* Final post */
  .final-box {
    background: #0d948808;
    border: 1px solid #0d9488;
    border-radius: 10px;
    padding: 24px 28px;
    margin-top: 12px;
  }
  .final-text {
    color: #e2e8f0;
    font-size: 15px;
    line-height: 1.9;
    white-space: pre-wrap;
  }

  /* Pipeline steps */
  .step {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 10px 0;
    border-bottom: 1px solid #1e2a3a;
  }
  .step:last-child { border-bottom: none; }
  .step-num {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: #0d9488;
    color: white;
    font-size: 12px;
    font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .step-info .step-title { color: #e2e8f0; font-size: 13px; font-weight: 600; }
  .step-info .step-sub   { color: #64748b; font-size: 12px; }

  /* Buttons */
  .stButton > button {
    background: #0d9488 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* Input */
  .stTextInput > div > div > input, .stTextArea textarea {
    background: #161b27 !important;
    border: 1px solid #1e2a3a !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
  }
  .stTextInput > div > div > input:focus, .stTextArea textarea:focus {
    border-color: #0d9488 !important;
    box-shadow: 0 0 0 1px #0d9488 !important;
  }

  /* Divider */
  hr { border-color: #1e2a3a !important; }

  /* Spinner */
  .stSpinner > div { border-top-color: #0d9488 !important; }

  /* Selectbox */
  [data-testid="stSelectbox"] > div { background: #161b27; border-color: #1e2a3a; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✍️ Blog Generator")
    st.markdown('<p style="color:#64748b;font-size:13px;margin-top:-8px;">Powered by AutoGen 0.4 · GPT-4o</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        placeholder="sk-...",
        help="Your key is never stored — used only for this session."
    )

    model = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)

    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")

    agents_info = [
        ("✍️", "Writer", "Content Creator", "Drafts & revises the blog post"),
        ("🔍", "SEO Reviewer", "Optimisation", "Keywords, headings, readability"),
        ("⚖️", "Legal Reviewer", "Risk & Accuracy", "Claims, disclaimers, risk"),
        ("🎯", "Ethics Reviewer", "Tone & Bias", "Inclusivity, balanced framing"),
        ("🧠", "Meta Reviewer", "Aggregator", "Synthesises all feedback"),
    ]

    for emoji, name, role, desc in agents_info:
        st.markdown(f"""
        <div class="agent-card">
          <div class="agent-name">{emoji} {name}</div>
          <div class="agent-role">{role}</div>
          <div class="agent-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="color:#475569;font-size:11px;text-align:center;">github.com/shahithya06</p>', unsafe_allow_html=True)


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("# Multi-Agent Blog Generator")
st.markdown('<p style="color:#64748b;margin-top:-12px;">6 specialised AI agents collaborate to write, review, and refine your blog post</p>', unsafe_allow_html=True)

# Pipeline overview
with st.expander("📐 How the pipeline works", expanded=False):
    st.markdown("""
    <div style="padding: 8px 0;">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-info">
          <div class="step-title">Writer generates initial draft</div>
          <div class="step-sub">GPT-4o with creative temperature (0.7)</div>
        </div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-info">
          <div class="step-title">SEO + Legal + Ethics reviewers run in parallel</div>
          <div class="step-sub">asyncio.gather — all three run simultaneously, each returns structured JSON</div>
        </div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-info">
          <div class="step-title">Meta Reviewer synthesises all feedback</div>
          <div class="step-sub">Produces a single prioritised revision brief</div>
        </div>
      </div>
      <div class="step">
        <div class="step-num">4</div>
        <div class="step-info">
          <div class="step-title">Writer revises based on the brief</div>
          <div class="step-sub">Final polished post incorporating all specialist feedback</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Topic input
topic = st.text_input(
    "Blog Topic",
    placeholder="e.g. How AI agents are transforming e-commerce in 2025",
    label_visibility="visible",
)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    generate_btn = st.button("Generate", use_container_width=True)

st.markdown("---")


# ── Agent Logic ───────────────────────────────────────────────────────────────

def make_client(temp: float, key: str, mdl: str) -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(model=mdl, api_key=key, temperature=temp)


async def run_agent(agent: AssistantAgent, message: str) -> str:
    response = await agent.on_messages(
        [TextMessage(content=message, source="user")],
        cancellation_token=CancellationToken(),
    )
    return response.chat_message.content


def parse_review(raw: str) -> dict:
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except (json.JSONDecodeError, KeyError):
        pass
    return {"role": "Reviewer", "score": "?", "strengths": [], "issues": [], "recommendations": [raw]}


async def full_pipeline(topic: str, api_key: str, model: str, progress_q: queue.Queue):
    """Run the full multi-agent pipeline, posting progress updates to a queue."""

    creative = make_client(0.7, api_key, model)
    precise  = make_client(0.2, api_key, model)

    writer = AssistantAgent(name="Writer", model_client=creative, system_message=
        """You are a professional blog writer. Write clear, engaging, well-structured 
blog posts (maximum 3 paragraphs).
- Start with a compelling hook
- Use simple, direct language
- End with a clear takeaway
- Output ONLY the blog post — no meta-commentary.""")

    seo_agent = AssistantAgent(name="SEO_Reviewer", model_client=precise, system_message=
        """You are an SEO specialist. Review the blog post.
Respond ONLY with valid JSON:
{"role":"SEO","score":<1-10>,"strengths":["..."],"issues":["..."],"recommendations":["..."]}""")

    legal_agent = AssistantAgent(name="Legal_Reviewer", model_client=precise, system_message=
        """You are a legal and factual accuracy reviewer.
Respond ONLY with valid JSON:
{"role":"Legal","score":<1-10>,"strengths":["..."],"issues":["..."],"recommendations":["..."]}""")

    ethics_agent = AssistantAgent(name="Ethics_Reviewer", model_client=precise, system_message=
        """You are an ethics and tone reviewer.
Respond ONLY with valid JSON:
{"role":"Ethics","score":<1-10>,"strengths":["..."],"issues":["..."],"recommendations":["..."]}""")

    meta_agent = AssistantAgent(name="Meta_Reviewer", model_client=creative, system_message=
        """You are the Meta Reviewer. Synthesise feedback from three reviewers into one 
prioritised revision brief (max 150 words). Output ONLY the brief — no headers.""")

    # Step 1 — Draft
    progress_q.put({"step": "draft_start"})
    draft = await run_agent(writer, f"Write a blog post about: {topic}")
    progress_q.put({"step": "draft_done", "draft": draft})

    # Step 2 — Parallel reviews
    progress_q.put({"step": "review_start"})
    seo_raw, legal_raw, ethics_raw = await asyncio.gather(
        run_agent(seo_agent,    f"Review this blog post:\n\n{draft}"),
        run_agent(legal_agent,  f"Review this blog post:\n\n{draft}"),
        run_agent(ethics_agent, f"Review this blog post:\n\n{draft}"),
    )
    seo_data    = parse_review(seo_raw)
    legal_data  = parse_review(legal_raw)
    ethics_data = parse_review(ethics_raw)
    progress_q.put({"step": "review_done", "seo": seo_data, "legal": legal_data, "ethics": ethics_data})

    # Step 3 — Meta synthesis
    progress_q.put({"step": "meta_start"})
    combined = "\n\n".join([
        f"[SEO — {seo_data.get('score')}/10] Issues: {'; '.join(seo_data.get('issues',[]))} | Recs: {'; '.join(seo_data.get('recommendations',[]))}",
        f"[Legal — {legal_data.get('score')}/10] Issues: {'; '.join(legal_data.get('issues',[]))} | Recs: {'; '.join(legal_data.get('recommendations',[]))}",
        f"[Ethics — {ethics_data.get('score')}/10] Issues: {'; '.join(ethics_data.get('issues',[]))} | Recs: {'; '.join(ethics_data.get('recommendations',[]))}",
    ])
    brief = await run_agent(meta_agent,
        f"Synthesise this feedback into a revision brief:\n\n{combined}")
    progress_q.put({"step": "meta_done", "brief": brief})

    # Step 4 — Revised post
    progress_q.put({"step": "revise_start"})
    final = await run_agent(writer,
        f"Revise the blog post based on this feedback:\n\n{brief}\n\nOriginal post:\n\n{draft}")
    progress_q.put({"step": "revise_done", "final": final})

    progress_q.put({"step": "complete"})


def run_pipeline_thread(topic, api_key, model, progress_q):
    asyncio.run(full_pipeline(topic, api_key, model, progress_q))


# ── Review Card Renderer ──────────────────────────────────────────────────────

def render_review_card(data: dict):
    role  = data.get("role", "Reviewer")
    score = data.get("score", "?")
    emoji = {"SEO": "🔍", "Legal": "⚖️", "Ethics": "🎯"}.get(role, "🤖")
    color = {"SEO": "#3b82f6", "Legal": "#f59e0b", "Ethics": "#a855f7"}.get(role, "#0d9488")

    strengths = data.get("strengths", [])
    issues    = data.get("issues", [])
    recs      = data.get("recommendations", [])

    items_html = ""
    if strengths:
        items_html += '<div class="review-section-label">✅ Strengths</div>'
        items_html += "".join(f'<div class="review-item">· {s}</div>' for s in strengths)
    if issues:
        items_html += '<div class="review-section-label">⚠️ Issues</div>'
        items_html += "".join(f'<div class="review-item">· {i}</div>' for i in issues)
    if recs:
        items_html += '<div class="review-section-label">💡 Recommendations</div>'
        items_html += "".join(f'<div class="review-item">· {r}</div>' for r in recs)

    st.markdown(f"""
    <div class="review-card">
      <div class="review-header">
        <span class="review-role" style="color:{color};">{emoji} {role} Reviewer</span>
        <span class="score-pill" style="color:{color};border-color:{color};background:{color}15;">
          {score}/10
        </span>
      </div>
      {items_html}
    </div>
    """, unsafe_allow_html=True)


# ── Generate Flow ─────────────────────────────────────────────────────────────

if generate_btn:
    if not topic.strip():
        st.warning("Please enter a blog topic first.")
    elif not api_key.strip():
        st.warning("Please enter your OpenAI API key in the sidebar.")
    else:
        progress_q: queue.Queue = queue.Queue()

        thread = threading.Thread(
            target=run_pipeline_thread,
            args=(topic.strip(), api_key.strip(), model, progress_q),
            daemon=True,
        )
        thread.start()

        # ── Live UI updates ───────────────────────────────────────────────────
        draft_placeholder   = st.empty()
        review_placeholder  = st.empty()
        brief_placeholder   = st.empty()
        final_placeholder   = st.empty()

        draft_text  = None
        review_data = {}
        brief_text  = None
        final_text  = None

        # State flags
        showing_draft_spinner  = False
        showing_review_spinner = False
        showing_meta_spinner   = False
        showing_revise_spinner = False

        while True:
            try:
                msg = progress_q.get(timeout=120)
            except queue.Empty:
                st.error("Pipeline timed out. Please try again.")
                break

            step = msg.get("step")

            if step == "draft_start":
                with draft_placeholder.container():
                    st.markdown("### 📝 Step 1 — Initial Draft")
                    with st.spinner("Writer agent is drafting..."):
                        showing_draft_spinner = True

            elif step == "draft_done":
                draft_text = msg["draft"]
                with draft_placeholder.container():
                    st.markdown("### 📝 Step 1 — Initial Draft")
                    st.markdown(f"""
                    <div class="output-box">
                      <div class="output-label">Initial Draft</div>
                      <div class="output-text">{draft_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

            elif step == "review_start":
                with review_placeholder.container():
                    st.markdown("### 🔬 Step 2 — Parallel Review")
                    with st.spinner("SEO · Legal · Ethics reviewers running in parallel..."):
                        pass

            elif step == "review_done":
                review_data = msg
                with review_placeholder.container():
                    st.markdown("### 🔬 Step 2 — Parallel Review")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        render_review_card(msg["seo"])
                    with c2:
                        render_review_card(msg["legal"])
                    with c3:
                        render_review_card(msg["ethics"])

            elif step == "meta_start":
                with brief_placeholder.container():
                    st.markdown("### 🧠 Step 3 — Meta Reviewer Synthesis")
                    with st.spinner("Meta Reviewer consolidating feedback..."):
                        pass

            elif step == "meta_done":
                brief_text = msg["brief"]
                with brief_placeholder.container():
                    st.markdown("### 🧠 Step 3 — Meta Reviewer Synthesis")
                    st.markdown(f"""
                    <div class="output-box">
                      <div class="output-label">Revision Brief</div>
                      <div class="output-text">{brief_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

            elif step == "revise_start":
                with final_placeholder.container():
                    st.markdown("### ✨ Step 4 — Final Revised Post")
                    with st.spinner("Writer revising based on feedback..."):
                        pass

            elif step == "revise_done":
                final_text = msg["final"]
                with final_placeholder.container():
                    st.markdown("### ✨ Step 4 — Final Revised Post")
                    st.markdown(f"""
                    <div class="final-box">
                      <div class="output-label">Final Blog Post</div>
                      <div class="final-text">{final_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.download_button(
                        label="⬇️ Download Blog Post",
                        data=f"Topic: {topic}\n\n{final_text}",
                        file_name="blog_post.txt",
                        mime="text/plain",
                    )

            elif step == "complete":
                st.success("✅ Pipeline complete! Your blog post is ready.")
                break
