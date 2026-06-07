import requests
import json
import os
from datetime import datetime
import sys
# Allow importing from storage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.db import save_post

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "phi4-mini"  # As requested

def generate_social_content(topic, platform, style):
    prompt = f"""
You are Vaurdin Content AI, the internal content engine for Vaurdin, an innovative tech company.
Write a {platform} post about "{topic}".
Style/Theme: {style}
Brand tone: professional, modern, human, founder style, innovative.
Avoid: generic motivational content, cringe startup phrases.

Platform Rules:
"""
    if platform == "Instagram":
        prompt += "- Short, high energy, hook first\n- Format: HOOK, value, CTA, hashtags\n- Length: 80 to 180 words\n"
    elif platform == "LinkedIn":
        prompt += "- Founder style, professional, storytelling allowed\n- Length: 150 to 350 words\n"
    elif platform == "X":
        prompt += "- Short, punchy, thread capable\n- Length: Under platform limits\n"
    elif platform == "Facebook":
        prompt += "- Engaging, community focused\n- Length: 100 to 250 words\n"
        
    prompt += "\nOutput JSON format ONLY: {\"type\": \"social\", \"topic\": \""+topic+"\", \"platform\": \""+platform+"\", \"caption\": \"...\", \"hashtags\": [\"#Vaurdin\", \"...\"]}"

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "num_ctx": 1024,
            "temperature": 0.8
        }
    }
    
    try:
        response = requests.post(OLLAMA_API, json=payload)
        if response.status_code == 200:
            result = response.json()
            content = result.get('response', '{}')
            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if model didn't return pure JSON
                parsed_content = {
                    "type": "social",
                    "topic": topic,
                    "platform": platform,
                    "caption": content,
                    "hashtags": ["#Vaurdin"]
                }
            
            # Save to SQLite
            save_post(topic, platform, json.dumps(parsed_content))
            
            # Save to JSON file
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}-{topic.replace(' ', '-').lower()}-{platform.lower()}.json"
            filepath = os.path.join(os.path.dirname(__file__), '..', 'storage', 'posts', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_content, f, indent=4)
                
            return parsed_content
        else:
            print(f"Error from Ollama: {response.text}")
            return None
    except Exception as e:
        print(f"Connection error to Ollama: {e}")
        return None

if __name__ == "__main__":
    print(generate_social_content("AI in Automation", "Instagram", "AI"))
