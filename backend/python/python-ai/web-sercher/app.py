from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
from config import Config
from crewai_agent import CrewAIAgent

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

crewai_agent = CrewAIAgent()

@app.route("/")
def index():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html", chat_history=session["history"])

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    # Save user's message to session history
    history = session.get("history", [])
    history.append({"role": "user", "message": user_msg})
    session["history"] = history

    # Get AI response
    ai_reply, tool_used = crewai_agent.get_response(user_msg, history)
    history.append({"role": "ai", "message": ai_reply, "tool": tool_used})
    session["history"] = history

    return jsonify({
        "reply": ai_reply, 
        "tool": tool_used, 
        "history": history
    })

@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    return jsonify({"message": "Chat history reset"})

if __name__ == "__main__":
    app.run(debug=True)
