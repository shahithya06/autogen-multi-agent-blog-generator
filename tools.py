import requests
from bs4 import BeautifulSoup


def scrape_trending_topics(keyword: str) -> str:
    """
    Scrapes trending topics from Google News.
    """

    url = f"https://news.google.com/search?q={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    headlines = []

    for item in soup.select("article h3")[:5]:
        headlines.append(item.text)

    if not headlines:
        return "No trends found."

    return "\n".join(headlines)