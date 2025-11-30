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
print(client)
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


@app.post("/register")
def register(user: User):
    # Check if user user exists
    existing_user = users.usercollection.find_one(
        {"user": user.username}
    )
    if existing_user:
        return {"message": "This username is unavailable."}
    user_dict = user_dict()
    users_collection.insert_one(user_dict)
    token = generate_token(user.username)
    user_dict["_id"] = str(user_dict["_id"])
    user_dict["token"] = token
    return user_dict


@app.get("/api/user")
def get_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = {
        "username": "test1",
        "password": "test1"
    }
    if user_data["username"] and user_data["email"]:
        return user_data


raise HTTPException(status_code=401, detail="Invalid token")


def generate_token(email: str) -> str:
    payload = {"email": email}
    token = jwt_encode(payload, SECRET_KEY, algorithm="HS256")
    return token


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
