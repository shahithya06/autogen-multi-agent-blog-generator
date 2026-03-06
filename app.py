import streamlit as st
import asyncio
from workflow import run_blog_workflow

st.set_page_config(page_title="AutoGen Blog Generator", layout="wide")

st.title("🤖 AutoGen Multi-Agent Blog Generator")

st.write("""
This system uses **3 AI agents**:

1️⃣ Trend Scraper Agent  
2️⃣ Blog Writer Agent  
3️⃣ SEO Optimizer Agent  
""")

topic = st.text_input("Enter a blog topic")

generate_button = st.button("Generate Blog")

if generate_button:

    if not topic:
        st.warning("Please enter a topic.")
    else:

        with st.spinner("Agents working..."):

            try:
                result = asyncio.run(run_blog_workflow(topic))

                st.success("Blog generated successfully!")

                st.markdown(result)

            except Exception as e:

                st.error("Error occurred")
                st.text(str(e))