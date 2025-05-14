# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

Base = declarative_base()

class Case(Base):
    __tablename__ = 'cases'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    steps = relationship("Step", back_populates="case")

class Action(Base):
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    steps = relationship("Step", back_populates="action")

class Step(Base):
    __tablename__ = 'steps'
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
    case = relationship("Case", back_populates="steps")
    number = Column(Integer, nullable=False)
    image = Column(String, nullable=True)  # Save file path
    action_id = Column(Integer, ForeignKey('actions.id'), nullable=False)
    action = relationship("Action", back_populates="steps")
    detail = Column(String, nullable=True)
    thinking = Column(String, nullable=True)
    bbox_start = Column(String, nullable=True)  # Store JSON string
    bbox_end = Column(String, nullable=True)
    action_attrs = Column(Text, nullable=True)

# Setup database
engine = create_engine('sqlite:///data.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

