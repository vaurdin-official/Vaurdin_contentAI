# pyrefly: ignore [missing-import]
import feedparser
import json
import os
from datetime import datetime

FEEDS = [
    "https://techcrunch.com/feed/",
    "https://hnrss.org/frontpage"
]

def collect_topics():
    topics = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # Get top 5 from each
                title = entry.get('title', '')
                if title:
                    topics.append(title)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    # Filter or refine topics based on some logic if needed, here we just return a limited set to keep it simple
    return topics[:10]

if __name__ == "__main__":
    t = collect_topics()
    print("Collected topics:", t)
