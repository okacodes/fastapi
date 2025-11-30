from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import jwt
from jwt import encode as jwt_encode
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from bson import ObjectId
from config import get_settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# User model
class User(BaseModel):
    username: str
    password: str


# Connect to MongoDB
client = MongoClient(get_settings().MONGODB_URL)
db = client("fast")
users_collection = db["users"]
JWT_SECRET_KEY = get_settings().JWT_SECRET_KEY
security = HTTPBearer()

if client:
    print("Client connected", client)


@app.get("/")
async def homepage():
    return {"message:" "Welcome to the homepage"}


@app.post("/login")
def login(user: User):
    user_data = users_collection.find_one(
        {"user": user.username, "password": user.password}
    )
    if user_data:
        # generate a token
        token = generate_token(user.username)
    # convert objectId to string
        user_data["_id"] = str(user_data["_id"])
        user_data["token"] = token
        return user_data
    return {"message": "Username or password is incorrect."}


@app.register("/register")
def register(user: User):
    # Check if user user exists
    existing_user = users.usercollection.find_one(
        {"user": user.username}
    )
    if existing_user:
        return {"message": "This username is unavailable."}
