from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict
from models import ChatbotConfig, ChatMessage
import os

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class ChatService:
    """Service for handling chatbot conversations with LangChain"""
    
    def __init__(self):
        self.memories: Dict[str, List] = {}
    
    def chat(
        self,
        user_message: str,
        chatbot_config: ChatbotConfig,
        session_id: str,
        conversation_history: List[ChatMessage] = None
    ) -> str:
        """
        Process a chat message and return response
        
        Args:
            user_message: The user's message
            chatbot_config: The chatbot's configuration
            session_id: Unique session identifier
            conversation_history: Previous messages in the conversation
            
        Returns:
            Assistant's response
        """
        # Build messages with system prompt
        messages = [SystemMessage(content=chatbot_config.system_prompt)]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Create LLM with chatbot-specific config
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            temperature=chatbot_config.temperature,
            model=chatbot_config.model
        )
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        return response.content
    
    def clear_session(self, session_id: str):
        """Clear conversation memory for a session"""
        if session_id in self.memories:
            del self.memories[session_id]


chat_service = ChatService()

