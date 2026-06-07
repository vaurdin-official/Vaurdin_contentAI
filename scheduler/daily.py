import schedule
import time
import os
import sys
from datetime import datetime

# Allow importing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.rss import collect_topics
from generator.social import generate_social_content
from generator.blog import generate_blog
from storage.db import init_db

STYLE_ENGINE = {
    0: "startup",      # Monday
    1: "AI",           # Tuesday
    2: "automation",   # Wednesday
    3: "case study",   # Thursday
    4: "innovation",   # Friday
    5: "startup",      # Saturday (fallback)
    6: "founder insights" # Sunday
}

def daily_workflow():
    print(f"[{datetime.now()}] Starting daily workflow...")
    
    # 1. Collect Topics
    topics = collect_topics()
    if not topics:
        print("No topics found from RSS. Using evergreen topics.")
        topics = ["automation", "AI workflows", "startup growth", "agent workflows"]
        
    print(f"Collected topics: {topics}")
    
    # 2. Determine Style
    day_of_week = datetime.now().weekday()
    style = STYLE_ENGINE.get(day_of_week, "startup")
    
    # 3. Generate Content
    # We will pick the top topic for blog and another for social, or just use the top topic for everything for simplicity
    target_topic = topics[0]
    
    print(f"Generating for topic: {target_topic} with style: {style}")
    
    # Generate Social
    platforms = ["Instagram", "LinkedIn", "X"]
    for platform in platforms:
        print(f"Generating {platform} post...")
        result = generate_social_content(target_topic, platform, style)
        if not result:
            raise Exception(f"Failed to connect to LLM (Ollama) while generating {platform} post. Check logs.")
        
    # Generate Blog
    print("Generating Blog post...")
    result = generate_blog(target_topic, style)
    if not result:
        raise Exception("Failed to connect to LLM (Ollama) while generating blog post. Check logs.")
    
    print("Daily workflow completed successfully.")

def start_scheduler():
    init_db()
    # 6 AM daily execution
    schedule.every().day.at("06:00").do(daily_workflow)
    
    print("Scheduler running... Waiting for 06:00 AM")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # If run directly, execute the workflow once for testing
    init_db()
    daily_workflow()
