import streamlit as st
from google import genai
from google.genai import types

# Initialize the Vertex AI Client
def initialize_client():
    client = genai.Client(
        vertexai=True,
        project="vertex2025",  # Dein Google Cloud Projekt
        location="us-central1"
    )
    return client

# Funktion zur Generierung der Antwort
def generate_response(client, user_input):
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

# Streamlit-Frontend
def main():
    st.title("Vertex AI Chatbot")
    st.write("Chatte mit dem Chatbot, der über Vertex AI läuft!")

    # Chat-Historie
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Benutzer-Eingabe
    user_input = st.text_input("Deine Nachricht:", "")

    # Wenn der Benutzer eine Nachricht eingibt
    if st.button("Senden") and user_input.strip():
        client = initialize_client()
        response = generate_response(client, user_input)
        
        # Nachricht zur Chat-Historie hinzufügen
        st.session_state["messages"].append({"role": "user", "text": user_input})
        st.session_state["messages"].append({"role": "bot", "text": response})

    # Chat-Historie anzeigen
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.markdown(f"**Du:** {message['text']}")
        else:
            st.markdown(f"**Bot:** {message['text']}")

if __name__ == "__main__":
    main()
