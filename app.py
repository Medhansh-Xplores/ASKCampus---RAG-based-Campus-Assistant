import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from rag import CampusRAG

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

rag = CampusRAG()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    history = payload.get("history") or []

    if len(question) < 2:
        return jsonify({"error": "Please enter a question."}), 400
    if len(question) > 1500:
        return jsonify({"error": "Please keep your question under 1,500 characters."}), 400

    try:
        result = rag.ask(question, history)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({"error": "The assistant could not complete this request. Check the server configuration and try again."}), 500


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "knowledge_base_loaded": rag.is_ready})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)),
            debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
