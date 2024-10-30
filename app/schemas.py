from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class ProcessedImage(BaseModel):
    id: int
    user_id: int

    class Config:
        orm_mode = True
