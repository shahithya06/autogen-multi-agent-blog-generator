from autogen_agentchat.agents import AssistantAgent
from config import get_model_client
from tools import scrape_trending_topics


def create_agents():

    model_client = get_model_client()

    trend_agent = AssistantAgent(
        name="TrendScraperAgent",
        model_client=model_client,
        tools=[scrape_trending_topics],
        system_message="""
You are a research agent.

Your task:
1. Use the scraping tool
2. Find 5 trending topics based on the user input
3. Return only the topics
""",
    )

    blog_agent = AssistantAgent(
        name="BlogWriterAgent",
        model_client=model_client,
        system_message="""
You are a professional blog writer.

Input: trending topics

Generate a blog with:

Title
Introduction
3 sections
Conclusion
""",
    )

    seo_agent = AssistantAgent(
        name="SEOAgent",
        model_client=model_client,
        system_message="""
You are an SEO expert.

Given a blog, generate:

SEO Title
Meta description
10 Keywords
URL Slug
5 Hashtags

Return blog + SEO details.
""",
    )

    return trend_agent, blog_agent, seo_agent