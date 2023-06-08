from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow())
