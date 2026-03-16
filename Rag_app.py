import os
import json
import traceback
from flask import Flask, request, render_template, jsonify,session
from langchain import hub
from req_res import Request, Response
from models import load_index, init_llm_model,eng_tel

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise Exception("Please set the GEMINI_API_KEY environment variable")

model = init_llm_model(API_KEY)

INDEX_FILE = "./data/vector_store.pkl"

server = Flask(__name__)
server.secret_key = os.urandom(24)
prompt = hub.pull("rlm/rag-prompt")


def do_rag_generation(search_request: Request) -> Response:
    query = search_request.query
    history = session.get("chat_history", [])
    recent_history = history[-8:]  
    history_text = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in recent_history])
    # 1. Retrieve docs
    context_docs = vector_store.similarity_search(query, k=5)
    docs_content = "\n\n".join(doc.page_content for doc in context_docs)
    final_context = f"Conversation History:\n{history_text}\n\nKnowledge Base:\n{docs_content}"
    # 2. Create prompt
    message = prompt.invoke({
        "question": query,
        "context": final_context
    })

    final_prompt = message.to_messages()[0].content

    # 3. Call Gemini correctly
    llm_response = model.models.generate_content(model="gemini-2.5-flash",contents=final_prompt)

    # 4. Build response
    response = Response(request=search_request)
    response.summary = getattr(llm_response, "text", str(llm_response))
    response.sources = [
        doc.page_content + "\t" + json.dumps(doc.metadata)
        for doc in context_docs
    ]
    
    return response

@server.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")


@server.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        query = data["message"]

        search_request = Request(query)
        response_obj = do_rag_generation(search_request)
        history = session.get("chat_history", [])
        history.append({"user": query, "bot": response_obj.summary})
        session["chat_history"] = history[-8:]
        print("User Query:", query)
        print("Response:", response_obj.summary)
        response_eng_tel=eng_tel(response_obj.summary)
        return jsonify({"response": response_eng_tel})

    except Exception as e:
        traceback.print_exc()   # shows REAL error in terminal
        return jsonify({"error": str(e)}), 500


print("Loading index...")
force_rebuild_index = os.getenv("FORCE_REBUILD_INDEX", "False") == "True"
print("Force Rebuilt Index:", force_rebuild_index)

vector_store = load_index(
    INDEX_FILE, force_rebuild_index=force_rebuild_index
)

print("Ready to serve...")

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000, debug=True)