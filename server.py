"""
Flask backend server replacing the Streamlit UI.
Provides REST API endpoints consumed by the HTML/CSS/JS frontend.
API keys are loaded from the .env file – no client input required.
"""

import os
<<<<<<< HEAD
from dotenv import load_dotenv
=======
#from dotenv import load_dotenv
>>>>>>> 1c6fc7870aa3a19e2c2fc4efe88feabd82aa7f78
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from src.langgraph_agentic_ai.LLMs.groqllm import GroqLLM
from src.langgraph_agentic_ai.graph.graph_builder import GraphBuilder
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Load .env from the project root (one level up from Agentic-Chatbot/)
<<<<<<< HEAD
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
=======
#load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
>>>>>>> 1c6fc7870aa3a19e2c2fc4efe88feabd82aa7f78

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# ── Config ────────────────────────────────────────────────────────────────────
LLM_OPTIONS = ["Groq"]
USECASE_OPTIONS = ["Basic Chatbot", "Chatbot with WebSearch", "AI News"]
GROQ_MODEL_OPTIONS = [
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
]
PAGE_TITLE = "LangGraph: Build stateful Agentic AI"


# ── Static frontend ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── Config endpoint ────────────────────────────────────────────────────────────
@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(
        {
            "page_title": PAGE_TITLE,
            "llm_options": LLM_OPTIONS,
            "usecase_options": USECASE_OPTIONS,
            "groq_model_options": GROQ_MODEL_OPTIONS,
        }
    )


# ── Chat endpoint ──────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    selected_groq_model = data.get("selected_groq_model", "")
    selected_usecase    = data.get("selected_usecase", "")
    user_message        = data.get("user_message", "").strip()

    # Read keys from environment (loaded from .env)
    groq_api_key  = os.environ.get("GROQ_API_KEY", "").strip()
    tavily_api_key = (
        os.environ.get("TAVILY_SEARCH_API", "").strip()
        or os.environ.get("TAVILY_API_KEY", "").strip()
    )

    # Validation
    if not groq_api_key:
        return jsonify({"error": "GROQ_API_KEY is not set in the .env file."}), 500
    if not selected_usecase:
        return jsonify({"error": "No use case selected."}), 400
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400
    if selected_usecase in ["Chatbot with WebSearch", "AI News"] and not tavily_api_key:
        return (
            jsonify(
                {"error": "Tavily key is not set in .env (use TAVILY_SEARCH_API or TAVILY_API_KEY)."}
            ),
            500,
        )

    # Ensure the Tavily key is available under common variable names.
    if tavily_api_key:
        os.environ["TAVILY_API_KEY"] = tavily_api_key
        os.environ["TAVILY_SEARCH_API"] = tavily_api_key

    try:
        # Build LLM
        user_controls = {
            "GROQ_API_KEY": groq_api_key,
            "selected_groq_model": selected_groq_model,
        }
        llm_config = GroqLLM(user_controls_input=user_controls)
        model = llm_config.get_llm_model()

        # Build graph
        graph_builder = GraphBuilder(model)
        graph = graph_builder.setup_graph(selected_usecase)

        # ── Basic Chatbot ──────────────────────────────────────────────────────
        if selected_usecase == "Basic Chatbot":
            messages = []
            for event in graph.stream({"messages": ("user", user_message)}):
                for value in event.values():
                    messages.append(
                        {"role": "assistant", "content": value["messages"].content}
                    )
            return jsonify({"usecase": selected_usecase, "messages": messages})

        # ── Chatbot with WebSearch ─────────────────────────────────────────────
        elif selected_usecase == "Chatbot with WebSearch":
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state)
            out_messages = []
            for msg in res["messages"]:
                if isinstance(msg, HumanMessage):
                    out_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, ToolMessage):
                    out_messages.append({"role": "tool", "content": msg.content})
                elif isinstance(msg, AIMessage) and msg.content:
                    out_messages.append({"role": "assistant", "content": msg.content})
            return jsonify({"usecase": selected_usecase, "messages": out_messages})

        # ── AI News ───────────────────────────────────────────────────────────
        elif selected_usecase == "AI News":
            frequency = user_message  # e.g. "daily" / "weekly" / "monthly"
            result = graph.invoke({"messages": frequency})
<<<<<<< HEAD
            md_content = result.get("markdown", "").strip()
            if not md_content:
                return jsonify({"error": "Failed to generate AI news summary."}), 500
            return jsonify(
                {"usecase": selected_usecase, "markdown": md_content, "frequency": frequency}
            )
=======
            ai_news_path = f"./AINews/{frequency.lower()}_summary.md"
            try:
                with open(ai_news_path, "r") as f:
                    md_content = f.read()
                return jsonify(
                    {"usecase": selected_usecase, "markdown": md_content, "frequency": frequency}
                )
            except FileNotFoundError:
                return (
                    jsonify(
                        {"error": f"News file not found: {ai_news_path}. Generation may have failed."}
                    ),
                    404,
                )
>>>>>>> 1c6fc7870aa3a19e2c2fc4efe88feabd82aa7f78

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)
