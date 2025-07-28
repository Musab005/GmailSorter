#  The entry point for the Streamlit web application.

# main_app.py

import streamlit as st
from cognitive_inbox.agent import conversational_agent

st.set_page_config(page_title="Cognitive Inbox", layout="wide")

st.title("🧠 Cognitive Inbox")
st.subheader("Have a conversation with your email history.")


@st.cache_resource
def load_agent():
    """
    Load the conversational agent. The cache prevents reloading the models on every interaction.
    """
    return conversational_agent.create_conversational_agent()


# Load the agent once and cache it
try:
    agent = load_agent()
    st.success("Your conversational email agent is ready.")
except Exception as e:
    st.error(f"Failed to initialize the agent. Please check your configuration and logs. Error: {e}")
    st.stop()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you search your emails today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about your emails..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Invoke the RAG chain to get a response
            response = agent.invoke(prompt)
            st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
