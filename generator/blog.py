import requests
import json
import os
from datetime import datetime
import sys
# Allow importing from storage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.db import save_post

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "phi4-mini"

def generate_blog(topic, style):
    prompt = f"""
You are Vaurdin Content AI, the internal content engine for Vaurdin, an innovative tech company.
Write a blog post about "{topic}".
Theme: {style}
Brand tone: professional, modern, human, founder style, innovative.
Avoid: generic motivational content, cringe startup phrases.

Blog Rules:
- Markdown output
- SEO optimized
- Sections required: Title, Intro, Problem, Solution, Insights, Future, Conclusion
- Length: 700 to 1200 words

Output JSON format ONLY: {{"title": "...", "slug": "...", "category": "...", "markdown": "..."}}
"""
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
                # Fallback
                parsed_content = {
                    "title": topic,
                    "slug": topic.replace(' ', '-').lower(),
                    "category": style,
                    "markdown": content
                }
            
            # Save to SQLite
            save_post(topic, "blog", json.dumps(parsed_content))
            
            # Save to JSON file
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}-{topic.replace(' ', '-').lower()}-blog.json"
            if os.environ.get('VERCEL') == '1':
                filepath = os.path.join('/tmp', 'blogs', filename)
            else:
                filepath = os.path.join(os.path.dirname(__file__), '..', 'storage', 'blogs', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_content, f, indent=4)
                
            return parsed_content
        else:
            print(f"Error from Ollama: {response.text}")
            return None
    except Exception as e:
        print(f"Connection error to Ollama: {e}")
        if os.environ.get('VERCEL') == '1':
            parsed_content = {
                "title": f"The Future of {topic}",
                "slug": topic.replace(' ', '-').lower(),
                "category": style,
                "markdown": f"# The Future of {topic}\n\nThis is a mock blog post because Vercel cannot reach your local Ollama instance at `localhost:11434`.\n\n## Next Steps\nTo get real AI content, update `OLLAMA_API` in `generator/blog.py` to point to a public LLM provider like OpenAI or Groq."
            }
            save_post(topic, "blog", json.dumps(parsed_content))
            return parsed_content
        return None

if __name__ == "__main__":
    print(generate_blog("AI in Automation", "AI"))
