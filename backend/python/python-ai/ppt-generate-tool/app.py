import os
from flask import Flask, render_template, request, session, jsonify, send_file
from flask_session import Session
from config import Config
from crewai_workflow import (
    llm_chat_step,
    first_search_step,
    confirm_and_summarize_step,
    generate_ppt_step,
)

app = Flask(__name__)
app.config.from_object(Config)
Session(app)


@app.route("/")
def index():
    if "history" not in session:
        session["history"] = []
    if "state" not in session:
        session["state"] = "idle"
    return render_template("index.html", chat_history=session["history"])


@app.route("/chat", methods=["POST"])
def chat():
    user_msg = (request.json.get("message") or "").strip()
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    history = session.get("history", [])
    history.append({"role": "user", "message": user_msg})
    session["history"] = history

    # Step 1: LLM handles the message (chat-first)
    llm_reply_text = llm_chat_step(user_msg)

    # If LLM indicates a search is needed, it should include 'search:' followed by query
    if "search:" in llm_reply_text.lower():
        # extract after 'search:'
        try:
            query = llm_reply_text.split("search:", 1)[1].strip() or user_msg
        except Exception:
            query = user_msg

        session["state"] = "searching"
        session["last_query"] = query

        result = first_search_step(query)
        session["last_search_results"] = result["results"]
        session["state"] = "await_confirm"

        history.append({"role": "ai", "message": result["message"], "tool": "Search"})
        session["history"] = history

        return jsonify({
            "reply": result["message"],
            "step": "await_confirm",
            "options": ["OK to confirm", "Or type a new query to search again"],
            "ppt_path": None
        })

    # Otherwise: normal chat reply
    history.append({"role": "ai", "message": llm_reply_text, "tool": "LLM"})
    session["history"] = history

    return jsonify({
        "reply": llm_reply_text,
        "step": "idle",
        "options": ["Ask me something", "Or request a search"],
        "ppt_path": None
    })


@app.route("/confirm_search", methods=["POST"])
def confirm_search():
    action = (request.json.get("action") or "").strip().lower()
    new_query = (request.json.get("new_query") or "").strip()

    if action not in {"ok", "search_again"}:
        return jsonify({"error": "action must be 'ok' or 'search_again'"}), 400

    if action == "search_again":
        query = new_query or session.get("last_query", "")
        if not query:
            return jsonify({"error": "No previous query and no new_query provided."}), 400

        history = session.get("history", [])
        history.append({"role": "user", "message": new_query or "[search again]"})
        session["history"] = history

        res = first_search_step(query)
        session["last_query"] = query
        session["last_search_results"] = res["results"]
        session["state"] = "await_confirm"

        history.append({"role": "ai", "message": res["message"], "tool": "Search"})
        session["history"] = history

        return jsonify({
            "reply": res["message"],
            "step": "await_confirm",
            "options": ["OK to confirm", "Or type a new query to search again"],
            "ppt_path": None
        })

    # action == "ok"
    results = session.get("last_search_results", [])
    query = session.get("last_query", "")
    if not results or not query:
        return jsonify({"error": "Nothing to confirm. Start with a /chat search."}), 400

    out = confirm_and_summarize_step(query, results)
    session["last_summary"] = out["summary"]
    session["state"] = "summarized"

    history = session.get("history", [])
    history.append({"role": "ai", "message": out["message"], "tool": "Summarizer"})
    session["history"] = history

    return jsonify({
        "reply": out["message"],
        "step": "summarized",
        "options": ["Generate PPT"],
        "ppt_path": None
    })


@app.route("/generate_ppt", methods=["POST"])
def generate_ppt():
    summary = session.get("last_summary", "")
    if not summary:
        return jsonify({"error": "No summary available. Confirm search first."}), 400

    res = generate_ppt_step(summary)
    ppt_path = res["ppt_path"]

    history = session.get("history", [])
    history.append({"role": "ai", "message": f"PPT generated: {ppt_path}", "tool": "PPT"})
    session["history"] = history

    return jsonify({
        "reply": "PPT generated. You can download it now.",
        "ppt_path": ppt_path
    })


@app.route("/download_ppt")
def download_ppt():
    ppt_file = "outputs/presentation.pptx"
    if os.path.exists(ppt_file):
        return send_file(ppt_file, as_attachment=True)
    else:
        return "PPT file not found", 404


@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    session["state"] = "idle"
    session["last_query"] = ""
    session["last_search_results"] = []
    session["last_summary"] = ""
    return jsonify({"message": "Reset done"})


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    app.run(debug=True)
