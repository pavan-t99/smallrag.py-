import streamlit as st
from Rag_pipeline import get_answer
# def get_answer(question):
#     answer = Rag_pipeline(question)
#     return answer

st.title("Ayushman Bharath Registration chatbot")
st.write("Welcome to Ayushman bharath")
#st.header("Header Example")
if "selected" not in st.session_state:
    st.session_state.selected = None

if st.button("ENGLISH"):
    st.session_state.selected = "ENGLISH"
    st.write("ENGLISH SELECTED!")

if st.button("Hindi"):
    st.session_state.selected = "Hindi"
    st.write("HINDI SELECTED!")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask your question")
if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        recent_history=st.session_state.messages[-12:]
        with st.spinner("Searching Ayushman Bharat documents..."):
            answers= get_answer(user_input,recent_history)
            print(answers)
            answer=answers[1]
            if st.session_state.selected=="Hindi":
                hindi_answer=answers[1]
                answer=hindi_answer
            if st.session_state.selected=="ENGILSH":
                english_answer= answers[0].summary
                answer=english_answer

        st.session_state.messages.append({"role":"assistent","content":answer})
   
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        