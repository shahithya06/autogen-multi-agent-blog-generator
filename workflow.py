from agents import create_agents


async def run_blog_workflow(user_topic: str):

    trend_agent, blog_agent, seo_agent = create_agents()

    # STEP 1: Scrape trends
    trend_result = await trend_agent.run(
        task=f"Find trending topics about {user_topic}"
    )

    trends = trend_result.messages[-1].content

    # STEP 2: Generate blog
    blog_result = await blog_agent.run(
        task=f"Write a blog using these trends:\n{trends}"
    )

    blog = blog_result.messages[-1].content

    # STEP 3: Generate SEO
    seo_result = await seo_agent.run(
        task=f"Generate SEO for this blog:\n{blog}"
    )

    final_output = seo_result.messages[-1].content

    return final_output