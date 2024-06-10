from pydantic import BaseModel, EmailStr, PositiveInt, root_validator


class LoginEmail(BaseModel):
    login: EmailStr
