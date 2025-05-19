from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(String, primary_key=True)  # UUID
    name = Column(String, nullable=False)
    ip = Column(String, nullable=True)
    status = Column(String, default='online')

    tasks = relationship('Task', back_populates='agent')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)  # UUID
    agent_id = Column(String, ForeignKey('agents.id'))
    command = Column(Text, nullable=False)
    status = Column(String, default='pending')  # pending, running, done

    agent = relationship('Agent', back_populates='tasks')
    results = relationship('Result', back_populates='task')

class Result(Base):
    __tablename__ = 'results'
    id = Column(String, primary_key=True)  # UUID
    task_id = Column(String, ForeignKey('tasks.id'))
    output = Column(Text, nullable=True)

    task = relationship('Task', back_populates='results')

class Peer(Base):
    __tablename__ = 'peers'
    id = Column(String, primary_key=True)  # Обычно agent_id
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)