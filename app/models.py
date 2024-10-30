from sqlalchemy import Column, Integer, String, LargeBinary
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class ProcessedImage(Base):
    __tablename__ = 'processed_images'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filter_type = Column(String)
    image_data = Column(LargeBinary)
    status = Column(String)
