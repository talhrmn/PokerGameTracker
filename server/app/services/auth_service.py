from datetime import timedelta

from app.core.security import create_access_token
from app.schemas.auth import LoginResponse
from app.schemas.py_object_id import PyObjectId


class AuthService:

    def __init__(self, token_exp):
        self.token_exp = token_exp

    def _create_access_token(self, user_id: PyObjectId):
        access_token_expires = timedelta(minutes=self.token_exp)
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=access_token_expires
        )
        return access_token

    def login_user(self, user_id: PyObjectId) -> LoginResponse:
        access_token = self._create_access_token(user_id)
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
        )
