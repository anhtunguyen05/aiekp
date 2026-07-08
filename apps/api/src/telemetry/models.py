import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

class Trace(Base):
    __tablename__ = "traces"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), index=True, nullable=True)
    query = Column(String, nullable=False)
    timestamp = Column(DateTime, default=get_utc_now)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    metadata_ = Column("metadata", JSON, nullable=True)
    
    spans = relationship("TraceSpan", back_populates="trace", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="trace", cascade="all, delete-orphan")


class TraceSpan(Base):
    __tablename__ = "trace_spans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String(36), ForeignKey("traces.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    start_time = Column(DateTime, default=get_utc_now)
    end_time = Column(DateTime, nullable=True)
    inputs = Column(JSON, nullable=True)
    outputs = Column(JSON, nullable=True)
    
    trace = relationship("Trace", back_populates="spans")


class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String(36), ForeignKey("traces.id"), index=True, nullable=False)
    score = Column(Integer, nullable=False)  # 1 (Thumbs Up), -1 (Thumbs Down), or 1-5
    comment = Column(String, nullable=True)
    timestamp = Column(DateTime, default=get_utc_now)
    
    trace = relationship("Trace", back_populates="feedbacks")
