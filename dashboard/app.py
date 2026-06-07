from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import zipfile
from io import BytesIO

# Allow importing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.db import get_history, init_db
from scheduler.daily import daily_workflow
from research.rss import collect_topics
from generator.social import generate_social_content
from generator.blog import generate_blog

app = Flask(__name__)

# Initialize DB on startup
init_db()

import json

@app.route('/')
def index():
    raw_history = get_history(limit=10)
    history = []
    for item in raw_history:
        parsed_content = item["content"]
        try:
            parsed_data = json.loads(item["content"])
            # Create a case-insensitive dictionary wrapper for extraction
            lower_keys_data = {k.lower(): v for k, v in parsed_data.items()}
            
            # Extract main text body based on the type
            if item["type"].lower() == "blog":
                parsed_content = lower_keys_data.get("markdown", item["content"])
            else:
                parsed_content = lower_keys_data.get("caption", item["content"])
        except Exception:
            pass # keep raw if it fails
            
        history.append({
            "id": item["id"],
            "topic": item["topic"],
            "type": item["type"],
            "content": parsed_content
        })
        
    return render_template('index.html', history=history)

@app.route('/api/generate-today', methods=['POST'])
def api_generate_today():
    try:
        daily_workflow()
        return jsonify({"status": "success", "message": "Daily workflow executed successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate-blog', methods=['POST'])
def api_generate_blog():
    try:
        topics = collect_topics()
        target_topic = topics[0] if topics else "AI workflows"
        result = generate_blog(target_topic, "AI") # Default to AI style for manual
        if not result:
            return jsonify({"status": "error", "message": "Failed to connect to LLM (Ollama). Check logs."}), 500
        return jsonify({"status": "success", "message": f"Blog generated for: {target_topic}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate-social', methods=['POST'])
def api_generate_social():
    try:
        topics = collect_topics()
        target_topic = topics[0] if topics else "startup growth"
        result = generate_social_content(target_topic, "X", "startup")
        if not result:
            return jsonify({"status": "error", "message": "Failed to connect to LLM (Ollama). Check logs."}), 500
        return jsonify({"status": "success", "message": f"Social post generated for: {target_topic}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/regenerate', methods=['POST'])
def api_regenerate():
    data = request.get_json()
    topic = data.get('topic')
    item_type = data.get('type')
    
    if not topic or not item_type:
        return jsonify({"status": "error", "message": "Missing topic or type"}), 400
        
    try:
        if item_type.lower() == "blog":
            result = generate_blog(topic, "AI") # default style
        else:
            result = generate_social_content(topic, item_type, "startup") # default style
            
        if not result:
            return jsonify({"status": "error", "message": "Failed to connect to LLM (Ollama). Check logs."}), 500
            
        return jsonify({"status": "success", "message": f"Regenerated {item_type} for: {topic}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_content():
    storage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(storage_path):
            for file in files:
                if file.endswith('.json') or file == 'db.sqlite':
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, storage_path)
                    zf.write(filepath, arcname)
                    
    memory_file.seek(0)
    return send_file(memory_file, download_name='vaurdin_export.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
