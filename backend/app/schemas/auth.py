from pydantic import BaseModel

from app.schemas.user import UserResponse


class RegistrationResponse(BaseModel):
    message: str
    user: UserResponse