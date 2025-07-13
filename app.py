import streamlit as st
import requests
import json
from datetime import datetime
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Any
import os
from dotenv import load_dotenv

load_dotenv()

class E2ELLM(LLM):
    """Custom LLM wrapper for E2E Networks endpoint"""
    
    endpoint_url: str = ""
    api_key: str = ""
    model_name: str = "e2e-llm"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint_url = os.getenv("E2E_ENDPOINT_URL", "")
        self.api_key = os.getenv("E2E_API_KEY", "")
    
    @property
    def _llm_type(self) -> str:
        return "e2e_llm"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the E2E LLM endpoint"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stop": stop
        }
        
        try:
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", result.get("text", "No response received"))
            
        except requests.exceptions.RequestException as e:
            return f"Error calling E2E LLM: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Error parsing response: {str(e)}"

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm" not in st.session_state:
        st.session_state.llm = E2ELLM()

def display_chat_messages():
    """Display chat messages from session state"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(f"*{message['timestamp']}*")

def get_llm_response(prompt: str) -> str:
    """Get response from LLM"""
    try:
        response = st.session_state.llm._call(prompt)
        return response
    except Exception as e:
        return f"Error getting response: {str(e)}"

def main():
    st.set_page_config(
        page_title="E2E LLM Chatbot",
        page_icon="🤖",
        layout="centered"
    )
    
    st.title("🤖 E2E LLM Chatbot")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Configuration
        endpoint_url = st.text_input(
            "E2E Endpoint URL", 
            value=os.getenv("E2E_ENDPOINT_URL", ""),
            type="password"
        )
        api_key = st.text_input(
            "API Key", 
            value=os.getenv("E2E_API_KEY", ""),
            type="password"
        )
        
        # Model Parameters
        st.subheader("Model Parameters")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.slider("Max Tokens", 100, 2000, 1000, 100)
        
        # Update LLM configuration
        if st.button("Update Configuration"):
            st.session_state.llm.endpoint_url = endpoint_url
            st.session_state.llm.api_key = api_key
            st.session_state.llm.temperature = temperature
            st.session_state.llm.max_tokens = max_tokens
            st.success("Configuration updated!")
        
        # Clear chat history
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Chat statistics
        st.subheader("📊 Chat Stats")
        st.metric("Total Messages", len(st.session_state.messages))
        
        if st.session_state.messages:
            user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
            assistant_messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
            st.metric("User Messages", len(user_messages))
            st.metric("Bot Responses", len(assistant_messages))
    
    # Initialize session state
    initialize_session_state()
    
    # Main chat interface
    st.subheader("💬 Chat Interface")
    
    # Display existing messages
    display_chat_messages()
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to session state
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"*{timestamp}*")
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_llm_response(prompt)
            
            st.markdown(response)
            response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"*{response_timestamp}*")
            
            # Add assistant response to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": response_timestamp
            })
    
    # Information section
    with st.expander("ℹ️ About this Chatbot"):
        st.markdown("""
        This chatbot is built using:
        - **Streamlit** for the user interface
        - **LangChain** for LLM integration
        - **E2E Networks** LLM endpoint for AI responses
        
        **Features:**
        - Real-time chat interface
        - Configurable model parameters
        - Chat history with timestamps
        - Session persistence
        - Error handling and status indicators
        
        **Usage:**
        1. Configure your E2E endpoint URL and API key in the sidebar
        2. Adjust model parameters as needed
        3. Start chatting!
        """)

if __name__ == "__main__":
    main()