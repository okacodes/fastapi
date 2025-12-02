from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from pymongo import MongoClient
from bson import ObjectId
import secrets
from datetime import datetime
import jwt
from jwt import DecodeError
from models import Business, Chatbot, ChatbotConfig
from config import get_settings

settings = get_settings()
client = MongoClient(settings.MONGODB_URL)
db = client["fast"]
JWT_SECRET_KEY = settings.JWT_SECRET_KEY

router = APIRouter(prefix="/api/business", tags=["business"])

businesses_collection = db["businesses"]
chatbots_collection = db["chatbots"]


def generate_token(username: str):
    """Generate JWT token"""
    payload = {"username": username}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def get_current_user(token: str = Cookie(None)):
    """Get current authenticated user"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


def generate_api_key() -> str:
    """Generate a unique API key for widget embedding"""
    return f"sk_{secrets.token_urlsafe(32)}"


@router.post("/register")
def register_business(business: Business, response: Response):
    """Register a new business"""
    # Check if business exists
    existing = businesses_collection.find_one({
        "$or": [
            {"username": business.username},
            {"email": business.email}
        ]
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Generate API key
    api_key = generate_api_key()
    
    # Create business document
    business_dict = {
        "name": business.name,
        "email": business.email,
        "username": business.username,
        "password": business.password,  # In production, hash this!
        "api_key": api_key,
        "created_at": datetime.utcnow()
    }
    
    result = businesses_collection.insert_one(business_dict)
    business_dict["_id"] = str(result.inserted_id)
    
    # Generate token and set cookie
    token = generate_token(business.username)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400
    )
    
    # Don't return password
    business_dict.pop("password", None)
    return business_dict


@router.post("/login")
def login_business(business: Business, response: Response):
    """Login for business"""
    business_data = businesses_collection.find_one({
        "username": business.username,
        "password": business.password  # In production, verify hashed password
    })
    
    if not business_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token and set cookie
    token = generate_token(business.username)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400
    )
    
    business_dict = dict(business_data)
    business_dict["_id"] = str(business_dict["_id"])
    business_dict.pop("password", None)
    return business_dict


@router.get("/me")
def get_current_business(username: str = Depends(get_current_user)):
    """Get current business info"""
    business = businesses_collection.find_one({"username": username})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_dict = dict(business)
    business_dict["_id"] = str(business_dict["_id"])
    business_dict.pop("password", None)
    return business_dict


@router.get("/chatbots")
def get_chatbots(username: str = Depends(get_current_user)):
    """Get all chatbots for current business"""
    business = businesses_collection.find_one({"username": username})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    chatbots = list(chatbots_collection.find({"business_id": str(business["_id"])}))
    
    for chatbot in chatbots:
        chatbot["_id"] = str(chatbot["_id"])
        chatbot["business_id"] = str(chatbot["business_id"])
    
    return chatbots


@router.post("/chatbots")
def create_chatbot(chatbot_config: ChatbotConfig, username: str = Depends(get_current_user)):
    """Create a new chatbot"""
    business = businesses_collection.find_one({"username": username})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    chatbot_dict = {
        "business_id": str(business["_id"]),
        "config": chatbot_config.model_dump(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = chatbots_collection.insert_one(chatbot_dict)
    chatbot_dict["_id"] = str(result.inserted_id)
    chatbot_dict["business_id"] = str(chatbot_dict["business_id"])
    
    return chatbot_dict


@router.get("/chatbots/{chatbot_id}")
def get_chatbot(chatbot_id: str, username: str = Depends(get_current_user)):
    """Get a specific chatbot"""
    business = businesses_collection.find_one({"username": username})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    chatbot = chatbots_collection.find_one({
        "_id": ObjectId(chatbot_id),
        "business_id": str(business["_id"])
    })
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    chatbot["_id"] = str(chatbot["_id"])
    chatbot["business_id"] = str(chatbot["business_id"])
    return chatbot


@router.put("/chatbots/{chatbot_id}")
def update_chatbot(chatbot_id: str, chatbot_config: ChatbotConfig, username: str = Depends(get_current_user)):
    """Update a chatbot"""
    business = businesses_collection.find_one({"username": username})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    chatbot = chatbots_collection.find_one({
        "_id": ObjectId(chatbot_id),
        "business_id": str(business["_id"])
    })
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    chatbots_collection.update_one(
        {"_id": ObjectId(chatbot_id)},
        {
            "$set": {
                "config": chatbot_config.model_dump(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    updated = chatbots_collection.find_one({"_id": ObjectId(chatbot_id)})
    updated["_id"] = str(updated["_id"])
    updated["business_id"] = str(updated["business_id"])
    return updated

