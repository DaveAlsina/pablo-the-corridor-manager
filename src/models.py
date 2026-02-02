"""Database models using SQLAlchemy ORM."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime, Date, 
    ForeignKey, Numeric, UniqueConstraint, BIGINT, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy.sql import func

Base = declarative_base()


class Person(Base):
    """Corridor residents."""
    
    __tablename__ = "people"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=True)
    joined_date = Column(Date, default=func.current_date())
    active = Column(Boolean, default=True)
    
    # Relationships
    task_completions = relationship("TaskInstance", back_populates="completer", foreign_keys="TaskInstance.completed_by")
    opt_outs = relationship("TaskOptOut", back_populates="person", cascade="all, delete-orphan")
    penalties = relationship("Penalty", back_populates="person", cascade="all, delete-orphan")
    completion_logs = relationship("CompletionLog", back_populates="person")
    
    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.name}', telegram_id={self.telegram_id})>"


class TaskType(Base):
    """Task type definitions (e.g., 'Toilet 1', 'Kitchen A')."""
    
    __tablename__ = "task_types"
    
    id                          = Column(Integer, primary_key=True)
    name                        = Column(String(100), nullable=False, unique=True)
    category                    = Column(String(50), nullable=True)  # toilet, shower, kitchen, common
    description                 = Column(Text, nullable=True)
    instructions                = Column(Text, nullable=True)
    media_file_id               = Column(String(200), nullable=True)  # Telegram file_id
    frequency                   = Column(String(20), default="weekly")
    estimated_duration_minutes  = Column(Integer, nullable=True)
    location                    = Column(String(255), nullable=True)  # Increased from 100 to 255
    
    # Relationships
    opt_outs = relationship("TaskOptOut", back_populates="task_type", cascade="all, delete-orphan")
    instances = relationship("TaskInstance", back_populates="task_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TaskType(id={self.id}, name='{self.name}', category='{self.category}')>"


class TaskOptOut(Base):
    """People who opt out of specific tasks."""
    
    __tablename__ = "task_opt_outs"
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    task_type_id = Column(Integer, ForeignKey("task_types.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("person_id", "task_type_id", name="uq_person_task_optout"),
    )
    
    # Relationships
    person = relationship("Person", back_populates="opt_outs")
    task_type = relationship("TaskType", back_populates="opt_outs")
    
    def __repr__(self):
        return f"<TaskOptOut(person_id={self.person_id}, task_type_id={self.task_type_id})>"


class Week(Base):
    """Weekly cycles with deadlines."""
    
    __tablename__ = "weeks"
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)  # ISO week number
    start_date = Column(Date, nullable=False)
    deadline = Column(DateTime, nullable=False)
    closed = Column(Boolean, default=False)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("year", "week_number", name="uq_year_week"),
    )
    
    # Relationships
    task_instances = relationship("TaskInstance", back_populates="week", cascade="all, delete-orphan")
    penalties = relationship("Penalty", back_populates="week", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Week(id={self.id}, year={self.year}, week={self.week_number}, closed={self.closed})>"


class TaskInstance(Base):
    """Specific task instances for each week."""
    
    __tablename__ = "task_instances"
    
    id = Column(Integer, primary_key=True)
    week_id = Column(Integer, ForeignKey("weeks.id", ondelete="CASCADE"), nullable=False)
    task_type_id = Column(Integer, ForeignKey("task_types.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, skipped
    completed_by = Column(Integer, ForeignKey("people.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("week_id", "task_type_id", name="uq_week_task"),
        CheckConstraint("status IN ('pending', 'completed', 'skipped')", name="check_status"),
    )
    
    # Relationships
    week = relationship("Week", back_populates="task_instances")
    task_type = relationship("TaskType", back_populates="instances")
    completer = relationship("Person", back_populates="task_completions", foreign_keys=[completed_by])
    completion_logs = relationship("CompletionLog", back_populates="task_instance", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TaskInstance(id={self.id}, week_id={self.week_id}, status='{self.status}')>"


class CompletionLog(Base):
    """Audit trail for task completions."""
    
    __tablename__ = "completion_log"
    
    id = Column(Integer, primary_key=True)
    task_instance_id = Column(Integer, ForeignKey("task_instances.id", ondelete="CASCADE"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(20), nullable=False)  # completed, claimed, disputed, unclaimed
    timestamp = Column(DateTime, default=func.now())
    message_id = Column(BIGINT, nullable=True)  # Telegram message ID for audit
    
    # Relationships
    task_instance = relationship("TaskInstance", back_populates="completion_logs")
    person = relationship("Person", back_populates="completion_logs")
    
    def __repr__(self):
        return f"<CompletionLog(id={self.id}, action='{self.action}', timestamp={self.timestamp})>"


class Penalty(Base):
    """Penalty tracking for missed tasks."""
    
    __tablename__ = "penalties"
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    week_id = Column(Integer, ForeignKey("weeks.id", ondelete="CASCADE"), nullable=False)
    amount_eur = Column(Numeric(5, 2), nullable=False)
    penalty_type = Column(String(50), nullable=False)  # missed_task, late_completion
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    paid_via = Column(String(50), nullable=True)  # money, cooking, transferred
    
    # Relationships
    person = relationship("Person", back_populates="penalties")
    week = relationship("Week", back_populates="penalties")
    
    def __repr__(self):
        return f"<Penalty(id={self.id}, person_id={self.person_id}, amount={self.amount_eur}, paid={self.paid})>"