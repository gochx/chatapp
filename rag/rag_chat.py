import streamlit as st
from google import genai
from google.genai import types
from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool
import vertexai

ragpaths = ["gs://rac_bucket/Blaustern-Kohlenstoff-Formel.txt"]  

# Initialize Vertex AI Client
def initialize_client():
    client = genai.Client(
        vertexai=True,
        project="vertex2025",  # Dein Google Cloud Projekt
        location="us-central1"
    )
    return client

# Initialize Vertex AI for RAC
def initialize_rac():
    vertexai.init(project="vertex2025", location="us-central1")
    display_name = "test_corpus"
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )

    # Lade oder erstelle das Corpus
    rag_corpus = rag.create_corpus(
        display_name=display_name,
        embedding_model_config=embedding_model_config,
    )
    
    # Import Files to the RagCorpus
    rag.import_files(
        rag_corpus.name,
        ragpaths,
        chunk_size=512,  # Optional
        chunk_overlap=100,  # Optional
        max_embedding_requests_per_min=900,  # Optional
    )

    # Tool für RAC erstellen
    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(rag_corpus=rag_corpus.name)
                ],
                similarity_top_k=3,
                vector_distance_threshold=0.5,
            ),
        )
    )

    # Generatives Modell mit RAC-Tool
    rag_model = GenerativeModel(
        model_name="gemini-1.5-flash-001",
        tools=[rag_retrieval_tool]
    )
    return rag_model

# Generiere Antworten basierend auf generativem oder RAC-Modell
def generate_response(client, rag_model, user_input):
    # Führe eine RAC-Abfrage aus, wenn es nach spezifischem Wissen klingt
    if "Was" in user_input or "Erkläre" in user_input:
        response = rag_model.generate_content(user_input)
        return response.text
    else:
        # Generatives Modell verwenden
        model = "gemini-2.0-flash-exp"
        contents = [user_input]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            max_output_tokens=1024,
            response_modalities=["TEXT"],
        )

        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response += chunk.text
        return response

# Callback-Funktion für den Button
def handle_user_input(client, rag_model):
    user_input = st.session_state.input_box
    if user_input.strip():
        response = generate_response(client, rag_model, user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})
        st.session_state.messages.append({"role": "bot", "text": response})
        st.session_state.input_box = ""  # Eingabe zurücksetzen

# Streamlit App
def main():
    st.set_page_config(page_title="Vertex AI Chatbot mit RAC", layout="wide")
    st.title("Vertex AI Chatbot mit RAC")
    st.write("Ein intelligenter Chatbot, der auf generative Modelle und RAC zugreift!")

    # Initialisierung der Clients
    client = initialize_client()
    rag_model = initialize_rac()

    # Chat-Historie
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Eingabefeld unten
    st.markdown("---")
    st.text_input(
        "Deine Nachricht:",
        key="input_box",
        on_change=handle_user_input,  # Callback-Funktion
        args=(client, rag_model)  # Übergib die benötigten Argumente
    )

    # Chat-Ausgabe oben
    with st.container():
        for message in st.session_state["messages"]:
            if message["role"] == "user":
                st.markdown(f"**Du:** {message['text']}")
            else:
                st.markdown(f"**Bot:** {message['text']}")

if __name__ == "__main__":
    main()
