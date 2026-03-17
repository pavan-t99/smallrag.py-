import os
import json
import traceback
from req_res import Request, Response
from models import load_index, init_llm_model,eng_hindi
from langchain import hub
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise Exception("Please set the GEMINI_API_KEY environment variable")

model = init_llm_model(API_KEY)

INDEX_FILE = "./data/vector_store.pkl"
prompt = hub.pull("rlm/rag-prompt")
def do_rag_generation(search_request: Request,history) -> Response:
    query = search_request.query
    
    # 1. Retrieve docs
    context_docs = vector_store.similarity_search(query, k=5)
    docs_content = "\n\n".join(doc.page_content for doc in context_docs)
    final_context = f"Conversation History:\n{history}\n\nKnowledge Base:\n{docs_content}"
    # 2. Create prompt
    message = prompt.invoke({
        "question": query,
        "context": final_context
    })

    system_message = """
    You are AI Assistant for helping users with registration in Ayushman Bharath.

    Rules:
    - Answer in simple English
    - Give answers in bullet points
    - Use short explanations
    - Only use the provided context 
    - If the answer is not in the context, say "I don't know"
    - If a website link appears in the answer, format it as a clickable hyperlink using proper HTML or Markdown with target="_blank" rel="noopener noreferrer" so that users can opens in new tab the website when they click it.
        """
    final_prompt = system_message + "\n\n" + message.to_messages()[0].content

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

print("Loading index...")
force_rebuild_index = os.getenv("FORCE_REBUILD_INDEX", "False") == "True"
print("Force Rebuilt Index:", force_rebuild_index)

vector_store = load_index(
    INDEX_FILE, force_rebuild_index=force_rebuild_index
)

print("Ready to serve...")

def get_answer(question,history):
    search_request = Request(question)
    answer = do_rag_generation(search_request,history)
    response_eng_hin=eng_hindi(answer.summary)
    return answer,response_eng_hin
