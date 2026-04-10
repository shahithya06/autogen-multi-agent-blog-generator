"""
Multi-Agent Blog Generator
--------------------------
Built with Microsoft AutoGen 0.4 (autogen-agentchat + autogen-ext)

Reflection pattern:
  Writer → [SEO Reviewer | Legal Reviewer | Ethics Reviewer] → Meta Reviewer → Writer (revised)

Install:
    pip install -r requirements.txt

Run:
    python blog_generator.py
"""

import asyncio
import json
import os
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


# ── Model Clients ─────────────────────────────────────────────────────────────

def get_creative_client() -> OpenAIChatCompletionClient:
    """Higher temperature for the Writer — more expressive output."""
    return OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )

def get_precise_client() -> OpenAIChatCompletionClient:
    """Lower temperature for reviewers — consistent, structured critique."""
    return OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.2,
    )


# ── Agent Factory ─────────────────────────────────────────────────────────────

def make_writer() -> AssistantAgent:
    return AssistantAgent(
        name="Writer",
        model_client=get_creative_client(),
        system_message="""You are a professional blog writer. Write clear, engaging, 
well-structured blog posts (maximum 3 paragraphs).

When writing:
- Start with a compelling hook
- Use simple, direct language — avoid jargon  
- End with a clear takeaway or call to action
- Structure: Introduction | Main Body | Conclusion

When you receive feedback, revise your post to address every point raised.
Output ONLY the blog post text — no meta-commentary or explanations.""",
    )


def make_seo_reviewer() -> AssistantAgent:
    return AssistantAgent(
        name="SEO_Reviewer",
        model_client=get_precise_client(),
        system_message="""You are an SEO specialist. Review blog posts for search engine optimisation.

Check for:
- Target keyword presence and density
- Heading structure implied in the text
- Readability (short sentences, active voice)
- Meta description potential (first 160 chars)
- Link opportunities or calls to action

Respond ONLY with a valid JSON object — no other text:
{
  "role": "SEO",
  "score": <1-10>,
  "strengths": ["..."],
  "issues": ["..."],
  "recommendations": ["..."]
}""",
    )


def make_legal_reviewer() -> AssistantAgent:
    return AssistantAgent(
        name="Legal_Reviewer",
        model_client=get_precise_client(),
        system_message="""You are a legal and factual accuracy reviewer.

Check for:
- Unverified or overstated factual claims
- Legally risky absolute statements or guarantees
- Missing disclaimers where needed
- Misleading statistics or unsourced data

Respond ONLY with a valid JSON object — no other text:
{
  "role": "Legal",
  "score": <1-10>,
  "strengths": ["..."],
  "issues": ["..."],
  "recommendations": ["..."]
}""",
    )


def make_ethics_reviewer() -> AssistantAgent:
    return AssistantAgent(
        name="Ethics_Reviewer",
        model_client=get_precise_client(),
        system_message="""You are an ethics and tone reviewer.

Check for:
- Unconscious bias or stereotyping
- Inclusive language usage
- Balanced, non-manipulative framing
- Respectful handling of sensitive topics

Respond ONLY with a valid JSON object — no other text:
{
  "role": "Ethics",
  "score": <1-10>,
  "strengths": ["..."],
  "issues": ["..."],
  "recommendations": ["..."]
}""",
    )


def make_meta_reviewer() -> AssistantAgent:
    return AssistantAgent(
        name="Meta_Reviewer",
        model_client=get_creative_client(),
        system_message="""You are the Meta Reviewer. You receive structured JSON feedback 
from three specialist reviewers (SEO, Legal, Ethics) and synthesise it into one 
clear, prioritised revision brief for the Writer.

Your output must be a single actionable paragraph (max 150 words) that:
1. Acknowledges what works well (1-2 sentences)
2. Lists the top 3-5 most important changes needed, in priority order
3. Ends with an encouraging instruction to revise

Be specific — reference actual phrases from the blog post where possible.
Output ONLY the revision brief — no JSON, no headers, no preamble.""",
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_review(raw: str) -> str:
    """Extract and format a reviewer's JSON output for the Meta Reviewer."""
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(raw[start:end])
            return (
                f"[{data['role']} Reviewer — Score: {data.get('score', '?')}/10]\n"
                f"Strengths: {'; '.join(data.get('strengths', []))}\n"
                f"Issues: {'; '.join(data.get('issues', []))}\n"
                f"Recommendations: {'; '.join(data.get('recommendations', []))}"
            )
    except (json.JSONDecodeError, KeyError):
        pass
    return raw  # Fallback: pass raw text if JSON parsing fails


async def run_agent(agent: AssistantAgent, message: str) -> str:
    """Send a single message to an agent and return its text response."""
    token = CancellationToken()
    response = await agent.on_messages(
        [TextMessage(content=message, source="user")],
        cancellation_token=token,
    )
    return response.chat_message.content


# ── Core Pipeline ─────────────────────────────────────────────────────────────

async def run_review_loop(draft: str) -> str:
    """
    Run the three specialist reviewers in parallel, then synthesise
    via the Meta Reviewer. Returns the consolidated revision brief.
    """
    print("\n" + "=" * 60)
    print("  INNER REVIEW LOOP")
    print("=" * 60)

    # Run all three reviewers concurrently
    print("\n→ Running SEO, Legal, and Ethics reviewers in parallel...")
    seo_task    = run_agent(make_seo_reviewer(),    f"Review this blog post:\n\n{draft}")
    legal_task  = run_agent(make_legal_reviewer(),  f"Review this blog post:\n\n{draft}")
    ethics_task = run_agent(make_ethics_reviewer(), f"Review this blog post:\n\n{draft}")

    seo_out, legal_out, ethics_out = await asyncio.gather(seo_task, legal_task, ethics_task)

    print("  ✓ SEO Reviewer done")
    print("  ✓ Legal Reviewer done")
    print("  ✓ Ethics Reviewer done")

    # Parse and combine
    combined = "\n\n".join([
        parse_review(seo_out),
        parse_review(legal_out),
        parse_review(ethics_out),
    ])

    # Meta Reviewer synthesises
    print("\n→ Meta Reviewer synthesising feedback...")
    brief = await run_agent(
        make_meta_reviewer(),
        f"Here is structured feedback from three specialist reviewers:\n\n{combined}"
        f"\n\nSynthesise this into a prioritised revision brief for the Writer.",
    )
    print("  ✓ Meta Reviewer done")
    print("=" * 60)

    return brief


async def generate_blog(topic: str) -> str:
    """
    Full pipeline:
      1. Writer produces initial draft
      2. Parallel review (SEO + Legal + Ethics) → Meta Reviewer synthesises
      3. Writer revises based on the consolidated brief
    """
    print("\n" + "=" * 60)
    print("  MULTI-AGENT BLOG GENERATOR  (AutoGen 0.4)")
    print(f"  Topic: {topic}")
    print("=" * 60)

    writer = make_writer()

    # Step 1 — Initial draft
    print("\n[Step 1]  Writer generating initial draft...")
    draft = await run_agent(writer, f"Write a blog post about: {topic}")

    print("\n── INITIAL DRAFT " + "─" * 43)
    print(draft)

    # Step 2 — Nested review loop
    print("\n[Step 2]  Running nested review loop...")
    revision_brief = await run_review_loop(draft)

    print("\n── REVISION BRIEF " + "─" * 41)
    print(revision_brief)

    # Step 3 — Writer revises
    print("\n[Step 3]  Writer producing final revised post...")
    final = await run_agent(
        writer,
        f"Revise the blog post based on this feedback:\n\n{revision_brief}"
        f"\n\nOriginal post:\n\n{draft}",
    )

    print("\n── FINAL REVISED POST " + "─" * 37)
    print(final)
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)

    return final


# ── Entry Point ───────────────────────────────────────────────────────────────

async def main():
    topic = input("\nEnter blog topic: ").strip()
    if not topic:
        topic = "How AI agents are transforming e-commerce in 2025"

    result = await generate_blog(topic)

    output_file = "output_blog.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Topic: {topic}\n\n{result}")

    print(f"\n✓ Final blog saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
