import os
import json
import traceback
from req_res import Request, Response
from models import load_index, init_llm_model, HyDERetriever#,eng_hindi
from langchain import hub
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise Exception("Please set the GEMINI_API_KEY environment variable")

API_KEY2 = os.environ.get("CHATTING_GEMINI_API_KEY")
if not API_KEY2:
    raise Exception("Please set the CHATTING_GEMINI_API_KEY environment variable")

model = init_llm_model(API_KEY)

hyde_ret = HyDERetriever(API_KEY2)
INDEX_FILE = "./data/vector_store.pkl"
prompt = hub.pull("rlm/rag-prompt")
def do_rag_generation(search_request: Request,history) -> Response:
    query = search_request.query
    context_docs, hypothetical_doc = hyde_ret.retrieve(query)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    print("hypothetical_doc=    ",hypothetical_doc)

    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # 1. Retrieve docs
    #context_docs = vector_store.similarity_search_with_relevance_scores(query, k=5)
    print("score=",context_docs[0][1])
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    print(context_docs)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%/n")
    # relevant_count = 0

    # for doc, score in context_docs:
    #     text = doc.page_content.lower()
    #     if any(word in text for word in query.lower().split()):
    #         relevant_count += 1
    # precision_at_k = relevant_count / len(context_docs)

    # print("Precision@k:", precision_at_k)
    if len(context_docs) == 0 or context_docs[0][1] < 0.5:
        print("unable to find matching results.:(")
        return
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(context_docs)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%/n")
    docs_content = "\n\n".join(doc.page_content for doc,score in context_docs)
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
    #llm_response = model.models.generate_content(model="gemini-2.5-flash",contents=final_prompt)
    llm_response = model.generate_content(final_prompt)
    # 4. Build response
    response = Response(request=search_request)
    response.summary = getattr(llm_response, "text", str(llm_response))
    response.sources = [
        doc.page_content + "\t" + json.dumps(doc.metadata)
        for doc,score in context_docs
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
    return answer