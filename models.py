import os
import pickle
import subprocess
from req_res import Request, Response
#import google.generativeai as genai
from google import genai
from langchain_community.vectorstores import FAISS
#from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
translation_model = None
translation_tokenizer = None

def load_translation_model():
    global translation_model, translation_tokenizer

    if translation_model is None:
        from transformers import MarianMTModel, MarianTokenizer

        model_name = "Helsinki-NLP/opus-mt-en-hi"

        translation_tokenizer = MarianTokenizer.from_pretrained(model_name)
        translation_model = MarianMTModel.from_pretrained(model_name)

    return translation_tokenizer, translation_model 
# ##

# response = model.models.generate_content(
#     model="gemini-1.5-flash",
#     contents=message.to_messages()[0].content,
# )

# return response.text
# ###
# def init_llm_model(api_key=None):
#     if api_key is None:
#         raise ValueError("API Key is required")

#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     return model

def init_llm_model(api_key=None):
    if api_key is None:
            raise ValueError("API Key is required")

    client = genai.Client(api_key=api_key)
    return client

def embedding_model():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
  
def eng_hindi(text):
    tokenizer, model = load_translation_model()
    tokens = tokenizer(text, return_tensors="pt", padding=True)                 
    translated = model.generate(**tokens)
    output = tokenizer.decode(translated[0], skip_special_tokens=True)

    return output

def load_index(filename, force_rebuild_index=False):
    if force_rebuild_index or not os.path.exists(filename):
        print("Force Rebuilding Index...")
        cmd = "python build_index.py"
        subprocess.call(cmd, shell=True)

    with open(filename, "rb") as f:
        vector_store = pickle.load(f)

    return vector_store