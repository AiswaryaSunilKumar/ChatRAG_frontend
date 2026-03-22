import streamlit as st
import requests
import os
from langchain_community.document_loaders import PyPDFLoader

st.set_page_config(page_title="PDF Chatbot", page_icon="🤖", layout="wide")
st.title("📄 Chat with your PDF!")

# --- Sidebar for PDF upload ---
st.sidebar.header("Upload PDF")

uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

# API endpoints (adjust if running elsewhere)
VECTOR_API_URL =  "https://chatrag-backend-3.onrender.com/vector/vector"
QUERY_API_URL =  "https://chatrag-backend-3.onrender.com/query/query"

# --- Session state for table_path and chat history ---
if "table_path" not in st.session_state:
    st.session_state["table_path"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "vector_store_created" not in st.session_state:
    st.session_state["vector_store_created"] = False

# --- Handle PDF upload ---
if uploaded_file:
    temp_dir = "./uploaded_pdfs"
    # os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded_file.name)
    # with open(file_path, "wb") as f:
    #     f.write(uploaded_file.getbuffer())


    loader = PyPDFLoader(uploaded_file)
    docs = loader.load()




    # If new file or file changed, reset state
    if st.session_state.get("table_path") != file_path:
        st.session_state["chat_history"] = []
        st.session_state["vector_store_created"] = False
        st.session_state["table_path"] = file_path
    # Only create vector store if not already created
    if not st.session_state.get("vector_store_created"):
        with st.spinner("Processing PDF and creating vector store..."):
            resp = requests.post(VECTOR_API_URL, json={"table_path": file_path,"docs" : docs})
            if resp.status_code == 200:
                st.success("Vector store created! You can now chat with your PDF.")
                st.session_state["vector_store_created"] = True
            else:
                st.error(f"Failed to create vector store: {resp.text}")
                st.session_state["vector_store_created"] = False

# --- Chatbot UI ---
st.subheader("Chat with your PDF")

# Chat input
if st.session_state["table_path"]:
    user_input = st.chat_input("Ask a question about your PDF...")
    if user_input:
        # Call query endpoint
        with st.spinner("Getting answer..."):
            payload = {"query": user_input, "table_path": st.session_state["table_path"]}
            resp = requests.post(QUERY_API_URL, json=payload)
            if resp.status_code == 200 and "answer" in resp.json():
                answer = resp.json()["answer"]
                st.session_state["chat_history"].append(("user", user_input))
                st.session_state["chat_history"].append(("assistant", answer))
            else:
                error_msg = f"Error: {resp.text}"
                st.session_state["chat_history"].append(("user", user_input))
                st.session_state["chat_history"].append(("assistant", error_msg))
    # Display chat history
    for role, message in st.session_state["chat_history"]:
        with st.chat_message(role):
            st.markdown(message)
else:
    st.info("Upload a PDF to get started.")
