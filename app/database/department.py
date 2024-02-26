from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, and_
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class Department(Base):
    __tablename__ = "department"  # Table name is typically singular
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # Name should be unique if it's used as a foreign key

    application = relationship('Application', back_populates='department')