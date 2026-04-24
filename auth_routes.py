from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from models.user import User
from auth.hash_password import hash_password, verify_password
from auth.jwt_handler import create_access_token


auth_router = APIRouter()


class TokenResponse(BaseModel):
    username: str
    access_token: str


class UserSignup(BaseModel):
    username: str
    password: str


@auth_router.post("/signup", status_code=201)
async def sign_user_up(user: UserSignup):

    existing_user = await User.find_one(User.username == user.username)

    if user.username == "" or user.password == "":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or password cannot be blank",
        )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    new_user = User(
        username=user.username, hashed_password=hash_password(user.password)
    )

    await new_user.insert()

    return {"message": "User successfully created"}


@auth_router.post("/sign-in", response_model=TokenResponse)
async def sign_user_in(user: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    db_user = await User.find_one(User.username == user.username)

    if db_user:
        if verify_password(user.password, db_user.hashed_password):
            access_token = create_access_token({"username": db_user.username})

            return TokenResponse(
                username=db_user.username,
                access_token=access_token,
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid details passed."
    )
