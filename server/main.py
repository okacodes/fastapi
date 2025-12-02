from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import jwt
from jwt import DecodeError
from fastapi import Depends, HTTPException, Cookie
from config import get_settings
from routers import business, chat

app = FastAPI(title="Chatbot Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*", "Content-Type", "Authorization", "X-API-Key"],
    expose_headers=["*"]
)

# Include routers
app.include_router(business.router)
app.include_router(chat.router)


# User model
class User(BaseModel):
    username: str
    password: str

# Helpers
def generate_token(username: str):
    payload = {"username": username}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

# Connect to MongoDB
client = MongoClient(get_settings().MONGODB_URL)
db = client["fast"]
users_collection = db["users"]
JWT_SECRET_KEY = get_settings().JWT_SECRET_KEY

if client:
    print("MongoDB client connected")


@app.get("/")
async def homepage():
    return {"message": "Welcome to the homepage"}


@app.post("/login")
def login(user: User, response: Response):
    user_data = users_collection.find_one(
        {"user": user.username, "password": user.password}
    )
    if user_data:
        # generate a token
        token = generate_token(user.username)
        # convert objectId to string
        user_data["_id"] = str(user_data["_id"])
        # Set HTTPOnly cookie
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=86400  # 24 hours
        )
        # Don't return token in response body
        user_data.pop("token", None)
        return user_data
    raise HTTPException(status_code=401, detail="Username or password is incorrect.")


@app.post("/register")
def register(user: User, response: Response):
    # Check if user user exists
    existing_user = users_collection.find_one(
        {"user": user.username}
    )
    if existing_user:
        return {"message": "This username is unavailable."}
    user_dict = {"user": user.username, "password": user.password}
    users_collection.insert_one(user_dict)
    token = generate_token(user.username)
    user_dict["_id"] = str(user_dict["_id"])
    # Set HTTPOnly cookie
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400  # 24 hours
    )
    # Don't return token in response body
    user_dict.pop("token", None)
    return user_dict


def get_current_user(token: str = Cookie(None)):
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

@app.get("/api/user")
def get_user(username: str = Depends(get_current_user)):
    user_data = users_collection.find_one({"user": username})
    if user_data:
        # Convert to dict and remove password
        user_dict = dict(user_data)
        user_dict["_id"] = str(user_dict["_id"])
        user_dict.pop("password", None)
        return user_dict
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="token")
    return {"message": "Logged out successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
