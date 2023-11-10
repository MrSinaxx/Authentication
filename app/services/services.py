from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from app.schema.schemas import UserProfileResponse
from motor.motor_asyncio import AsyncIOMotorClient as Client
from app.schema.schemas import UserResponse
from tempfile import NamedTemporaryFile
from bson import ObjectId
import qrcode
from pyotp import TOTP
import pyotp


def sess_collection():
    db = Client().get_database("rss-feed")
    account_collection = db["users"]
    yield account_collection


def get_user_service(collection=Depends(sess_collection)):
    return UserService(collection)


class UserService:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, collection):
        self.collection = collection

    def get_hashed_password(self, password: str) -> str:
        return self.password_context.hash(password)

    def verify_password(self, password: str, hashed_pass: str) -> bool:
        return self.password_context.verify(password, hashed_pass)

    def generate_totp_secret(self) -> str:
        return pyotp.random_base32()

    def generate_totp_uri(self, username: str, secret: str) -> str:
        totp = TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name="YourIssuer")
        img = qrcode.make(provisioning_url)

    def verify_totp_code(self, secret: str, code: str) -> bool:
        totp = TOTP(secret)
        return totp.verify(code)

    async def get_user(self, username: str, password: str):
        user_dict = await self.collection.find_one({"username": username})
        if user_dict is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User was not found"
            )

        result = self.verify_password(password, user_dict["password"])
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password"
            )

        return user_dict

    async def authenticate(self, username, password, totp_code):
        user = await self.get_user(username, password)
        totp_secret = user.get("totp_secret")

        if totp_secret and not self.verify_totp_code(totp_secret, totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code"
            )

        return user

    async def create_user(self, user):
        check_user = await self.collection.find_one({"username": user.username})
        if check_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists",
            )

        hashed_password = self.get_hashed_password(user.password)
        totp_secret = self.generate_totp_secret()

        provisioning_url = self.generate_totp_uri(user.username, totp_secret)
        img = qrcode.make(provisioning_url)

        with NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            img.save(temp_file)
            temp_file_path = temp_file.name

        data = {
            "username": user.username,
            "password": hashed_password,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "totp_secret": totp_secret,
            "totp_qr_code": temp_file_path,
        }

        await self.collection.insert_one(data)
        return data

    async def get_user_profile(self, user_id: str):
        user_profile = await self.collection.find_one({"_id": ObjectId(user_id)})

        if user_profile:
            return UserProfileResponse(**user_profile)

        return None
