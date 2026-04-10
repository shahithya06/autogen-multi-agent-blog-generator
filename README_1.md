# Multi-Agent Blog Generator

An autonomous blog generation pipeline built with **Microsoft AutoGen 0.4** (`autogen-agentchat` + `autogen-ext`), using a **reflection pattern** with 6 specialised agents running asynchronously.

Instead of a single prompt → output, this system simulates a real editorial team:  
**Writer → Parallel Review Panel → Meta Synthesis → Revised Output**

---

## Architecture

```
User Input (Topic)
       │
       ▼
  ┌─────────┐
  │  Writer  │  ← AssistantAgent — generates initial draft
  └────┬────┘
       │ draft
       ▼
  ┌────────────────────────────────────────┐
  │         PARALLEL REVIEW LOOP           │
  │                                        │
  │  ┌──────────────┐                      │
  │  │ SEO Reviewer │──┐                   │
  │  └──────────────┘  │                   │
  │  ┌───────────────┐ ├─→ asyncio.gather  │
  │  │ Legal Reviewer│─┤                   │
  │  └───────────────┘ │                   │
  │  ┌────────────────┐│                   │
  │  │ Ethics Reviewer├┘                   │
  │  └────────────────┘                    │
  │              │ JSON outputs            │
  │              ▼                         │
  │       ┌─────────────┐                 │
  │       │ Meta Reviewer│ → revision brief│
  │       └─────────────┘                 │
  └────────────────────────────────────────┘
                │
                ▼
          ┌─────────┐
          │  Writer  │  ← Revised final post
          └─────────┘
```

### Agents

| Agent | Role | Behaviour |
|-------|------|-----------|
| **Writer** | Content creator | Drafts & revises the blog post |
| **SEO Reviewer** | Optimisation | Checks keywords, readability, structure |
| **Legal Reviewer** | Risk & accuracy | Flags unverified claims, risky language |
| **Ethics Reviewer** | Tone & bias | Reviews inclusivity, balanced framing |
| **Meta Reviewer** | Aggregator | Synthesises all feedback into one brief |

### Key Design Choices

- **`asyncio.gather`** — SEO, Legal, and Ethics reviewers run in parallel, cutting review time by ~3x
- **JSON-structured outputs** — each reviewer returns structured JSON, making Meta Reviewer synthesis precise and parseable
- **Fresh agents per run** — agents are factory-created each pipeline run to avoid state bleed between topics
- **`on_messages` API** — uses AutoGen 0.4's native async message-passing (no UserProxyAgent needed)
- **Reflection pattern** — Writer receives consolidated feedback and produces a demonstrably improved final draft

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/shahithya06/autogen-multi-agent-blog-generator.git
cd autogen-multi-agent-blog-generator
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Open .env and add your OpenAI API key
```

### 5. Run
```bash
python blog_generator.py
```

Enter any topic when prompted. The pipeline runs, prints each stage, and saves the final post to `output_blog.txt`.

---

## Example Terminal Output

```
Enter blog topic: AI agents in Indian e-commerce 2025

======================================================
  MULTI-AGENT BLOG GENERATOR  (AutoGen 0.4)
  Topic: AI agents in Indian e-commerce 2025
======================================================

[Step 1]  Writer generating initial draft...

── INITIAL DRAFT ─────────────────────────────────────
...

[Step 2]  Running nested review loop...

======================================================
  INNER REVIEW LOOP
======================================================

→ Running SEO, Legal, and Ethics reviewers in parallel...
  ✓ SEO Reviewer done
  ✓ Legal Reviewer done
  ✓ Ethics Reviewer done

→ Meta Reviewer synthesising feedback...
  ✓ Meta Reviewer done

── REVISION BRIEF ────────────────────────────────────
...

[Step 3]  Writer producing final revised post...

── FINAL REVISED POST ────────────────────────────────
...

======================================================
  PIPELINE COMPLETE
======================================================

✓ Final blog saved to: output_blog.txt
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Runtime |
| `autogen-agentchat` 0.4 | Multi-agent framework |
| `autogen-ext[openai]` | OpenAI model client |
| `OpenAI GPT-4o` | LLM backbone for all agents |
| `asyncio.gather` | Parallel reviewer execution |
| `python-dotenv` | Environment management |

---

## Project Structure

```
autogen-multi-agent-blog-generator/
├── blog_generator.py     # Full pipeline — all agents and workflow
├── requirements.txt      # Dependencies
├── .env.example          # Environment variable template
├── .gitignore
└── README.md
```

---

## Why This Approach?

Single-prompt blog generation optimises for one quality dimension. This system runs **three parallel specialist critiques** simultaneously using `asyncio.gather`, synthesises them into one actionable brief via the Meta Reviewer, then feeds it back to the Writer for a demonstrably better final output — all without any human in the loop.

---

Built by [Shahithya Natarajan](https://github.com/shahithya06) — GenAI Engineer & AI Consultant, Chennai
