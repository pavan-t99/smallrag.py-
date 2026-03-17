import streamlit as st
from Rag_pipeline import get_answer
# def get_answer(question):
#     answer = Rag_pipeline(question)
#     return answer

st.title("Ayushman Bharath Registration chatbot")
st.write("Welcome to Ayushman bharath")
#st.header("Header Example")
if "messages" not in st.session_state:
    st.session_state.messages = []
    

english_answer=[]
hindi_answer=[]
selected=None
if st.button("ENGILSH"):
    selected="ENGILSH"
    st.write("ENGILSH SELECTED!")
if st.button("Hindi"):
    st.write("HINDI SELECTED!")
    selected="Hindi"
user_input = st.chat_input("Ask your question")
if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        recent_history=st.session_state.messages[-12:]
        with st.spinner("Searching Ayushman Bharat documents..."):
            if selected=="Hindi":
                hindi_answer[1]= get_answer(user_input,recent_history)
                answer=hindi_answer[1]
            #if selected=="ENGILSH":
            english_answer[0]= get_answer(user_input,recent_history)
            answer=english_answer[0]
        st.session_state.messages.append({"role":"chat_bot","content":answer})
   
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # st.chat_message(msg["reply"])
        # st.write(msg["content_by_bot"])