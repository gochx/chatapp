#pip install streamlit faiss-cpu llama-cpp-python ctransformers chromadb transformers

import ollama

def generate_response(prompt):
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


# Classifier
from transformers import pipeline

classifier = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")

def is_sensitive(text):
    result = classifier(text)[0]
    return result["label"] in ["hate_speech", "offensive"]


# Wissensdatenbank (Vektorsearch):
import chromadb

chroma_client = chromadb.PersistentClient(path="db/")
collection = chroma_client.get_or_create_collection(name="knowledge")

def add_knowledge(text):
    collection.add(
        documents=[text],
        metadatas=[{"source": "manual"}],
        ids=[str(len(collection.get()["documents"]))]
    )

def search_knowledge(query):
    results = collection.query(query_texts=[query], n_results=1)
    return results["documents"][0] if results["documents"] else None

# Frontend mit Streamlit
import streamlit as st

st.title("🧠 Lokaler AI-Chatbot mit Wissenserweiterung")

user_input = st.text_input("Gib eine Frage ein:")

if user_input:
    if is_sensitive(user_input):
        st.error("⚠️ Diese Anfrage enthält sensible Inhalte und kann nicht beantwortet werden.")
    else:
        extra_info = search_knowledge(user_input)
        prompt = f"{user_input}\n\nZusätzliche Informationen:\n{extra_info}" if extra_info else user_input
        response = generate_response(prompt)
        st.write("🤖:", response)
