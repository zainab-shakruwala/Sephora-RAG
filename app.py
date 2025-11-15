from llm_generation import *
import streamlit as st
from dotenv import load_dotenv

st.set_page_config(page_title="Sephora Beauty Assistant", page_icon="💄")

st.title("💄 Sephora Beauty Assistant")
st.markdown("Ask me anything about beauty products!")

with st.sidebar:
    user_api_key = st.text_input("Optional: Your Gemini API Key (if default limit exceeded)", 
              type="password", 
              key="user_api_key")
    "[Get a Gemini API key](https://aistudio.google.com)"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What beauty product are you looking for?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Searching products..."):
            result = rag_chatbot(prompt, top_k = 3, user_api_key=user_api_key)
            response = result['response']
            st.markdown(response)
            
            # Show products
            if result.get('retrieved_products'):
                with st.expander("View recommended products"):
                    for p in result['retrieved_products']:
                        st.write(f"**{p.get('name', 'Unknown')}** by {p.get('brand', 'Unknown')}")
                        st.write(f"Price: ${p.get('price', 'N/A')} | Rating: {p.get('rating', 'N/A')}/5")
                        st.divider()
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})