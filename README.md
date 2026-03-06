# 🤖 AutoGen Multi-Agent Blog Generator

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![AutoGen](https://img.shields.io/badge/Framework-AutoGen-green)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

An **AI-powered multi-agent content generation system** built using **Microsoft AutoGen** and **Streamlit**.  
The system automatically:

1. Scrapes **trending topics from the web**
2. Generates a **structured blog article**
3. Optimizes the content with **SEO metadata**

All orchestrated through a **multi-agent pipeline**.

---

# 📑 Table of Contents

- [Overview](#overview)
- [Motivation](#motivation)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Demo](#demo)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Author](#author)
- [Acknowledgements](#acknowledgements)

---

# 🚀 Overview

This project demonstrates how to build a **multi-agent AI workflow using AutoGen**.

The system creates an **AI content generation pipeline** where multiple specialized agents collaborate:

User Input
↓
Trend Scraper Agent
↓
Blog Writer Agent
↓
SEO Optimizer Agent
↓
Final Blog Output


The entire workflow runs inside a **Streamlit web interface**.

---

# 💡 Motivation

Content creators, marketers, and startups often spend significant time:

- researching trending topics
- writing long-form blogs
- optimizing content for SEO

This project demonstrates how **AI agents can automate this workflow** using **AutoGen multi-agent orchestration**.

---

# ✨ Key Features

### 🔎 Trend Scraping Agent
Automatically scrapes **trending topics from the web** related to a user query.

### ✍️ Blog Writing Agent
Generates a **structured blog post** including:

- Title
- Introduction
- Sections
- Conclusion

### 📈 SEO Optimization Agent
Enhances the blog with:

- SEO title
- meta description
- keywords
- URL slug
- hashtags

### 🖥 Streamlit Interface
Simple UI for interacting with the agent system.

### 🔐 Secure Configuration
Uses `.env` file for API keys and configuration.

---

# 🧠 Architecture
            ┌────────────────────┐
            │     Streamlit UI    │
            └─────────┬───────────┘
                      │
                      ▼
            ┌────────────────────┐
            │ User Blog Topic     │
            └─────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │ Trend Scraper Agent    │
          │ (Web scraping tool)    │
          └─────────┬─────────────┘
                    │
                    ▼
          ┌───────────────────────┐
          │ Blog Writer Agent      │
          └─────────┬─────────────┘
                    │
                    ▼
          ┌───────────────────────┐
          │ SEO Optimizer Agent    │
          └─────────┬─────────────┘
                    │
                    ▼
            Final Blog + SEO Output

Example input:
AI in Healthcare

Example output:
Trending Topics:
AI diagnostics
AI drug discovery
Medical imaging AI

Generated Blog:
The Future of AI in Healthcare

SEO:
Meta Description
Keywords
URL Slug
Hashtags

# ⚙️ Prerequisites

- Python **3.10+**
- OpenAI API Key
- pip

Required libraries:

- autogen-agentchat
- autogen-core
- autogen-ext
- streamlit
- python-dotenv
- requests
- beautifulsoup4
- tiktoken

---

# 📦 Installation

Clone the repository

git clone https://github.com/yourusername/autogen-multi-agent-blog-generator.git
cd autogen-multi-agent-blog-generator

Create virtual environment
python -m venv venv
Activate environment

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate
Install dependencies
pip install -r requirements.txt

▶️ Usage

Run the Streamlit application
streamlit run app.py
Open the browser:
http://localhost:8501

Enter a topic like:
Artificial Intelligence in Finance

The agents will generate a blog + SEO metadata automatically.

⚙️ Configuration

Create a .env file in the project root.

OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4o-mini

The configuration loader automatically reads these variables.

📂 Project Structure
autogen_blog_team/
│
├── app.py          # Streamlit UI
├── agents.py       # Agent definitions
├── workflow.py     # Agent orchestration
├── tools.py        # Web scraping tool
├── config.py       # Environment config
├── requirements.txt
└── .env

🛣 Roadmap

Planned improvements:
Add Editor Agent for content refinement
Add LinkedIn / Medium auto publishing
Add vector database for topic memory
Add parallel research agents

🤝 Contributing
Contributions are welcome!
If you'd like to improve the project:
Fork the repo
Create a feature branch
Submit a pull request
