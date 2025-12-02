from fastapi import APIRouter, HTTPException, Header
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import uuid
from models import ChatRequest, ChatResponse, ChatMessage
from services.chat_service import chat_service
from config import get_settings

settings = get_settings()
client = MongoClient(settings.MONGODB_URL)
db = client["fast"]

router = APIRouter(prefix="/api/chat", tags=["chat"])

businesses_collection = db["businesses"]
chatbots_collection = db["chatbots"]
chat_sessions_collection = db["chat_sessions"]


@router.post("/{chatbot_id}", response_model=ChatResponse)
def chat(chatbot_id: str, request: ChatRequest, x_api_key: str = Header(None)):
    """
    Public endpoint for widget to send chat messages
    Requires API key in X-API-Key header
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Verify API key and get business
    business = businesses_collection.find_one({"api_key": x_api_key})
    if not business:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Get chatbot
    chatbot = chatbots_collection.find_one({
        "_id": ObjectId(chatbot_id),
        "business_id": str(business["_id"])
    })
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    if not chatbot.get("config", {}).get("enabled", True):
        raise HTTPException(status_code=403, detail="Chatbot is disabled")
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get conversation history
    session = chat_sessions_collection.find_one({"session_id": session_id})
    conversation_history = []
    if session:
        conversation_history = [
            ChatMessage(**msg) for msg in session.get("messages", [])
        ]
    
    # Get chatbot config
    from models import ChatbotConfig
    config = ChatbotConfig(**chatbot["config"])
    
    # Get response from LangChain
    response_text = chat_service.chat(
        user_message=request.message,
        chatbot_config=config,
        session_id=session_id,
        conversation_history=conversation_history
    )
    
    # Save messages to session
    new_messages = conversation_history + [
        ChatMessage(role="user", content=request.message, timestamp=datetime.utcnow()),
        ChatMessage(role="assistant", content=response_text, timestamp=datetime.utcnow())
    ]
    
    chat_sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "chatbot_id": chatbot_id,
                "messages": [msg.model_dump() for msg in new_messages],
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "session_id": session_id,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return ChatResponse(message=response_text, session_id=session_id)

