import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class SkillStatus(str, enum.Enum):
    UNASSESSED = "unassessed"
    NEEDS_DEVELOPMENT = "needs_development"
    DEVELOPING = "developing"
    DEMONSTRATED_ASSISTED = "demonstrated_assisted"
    DEMONSTRATED_INDEPENDENT = "demonstrated_independently"

class RoleType(str, enum.Enum):
    JAVA_DEV = "Junior Java Developer"
    PYTHON_DEV = "Junior Python Developer"
    WEB_DEV = "Entry-Level Web Developer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_instructor = Column(Boolean, default=False)
    target_role = Column(String(100), default=RoleType.PYTHON_DEV.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessments = relationship("AssessmentAttempt", back_populates="user", cascade="all, delete-orphan")
    skill_evidence = relationship("SkillEvidence", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    learning_plans = relationship("LearningPlan", back_populates="user", cascade="all, delete-orphan")

class RoleCompetency(Base):
    __tablename__ = "role_competencies"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), index=True, nullable=False)
    skill_id = Column(String(100), index=True, nullable=False)
    skill_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    prerequisites = Column(JSON, default=list) # List of prerequisite skill_ids
    description = Column(Text, nullable=True)
    priority_weight = Column(Float, default=1.0)

class AssessmentTask(Base):
    __tablename__ = "assessment_tasks"

    id = Column(String(100), primary_key=True, index=True)
    role_name = Column(String(100), index=True, nullable=False)
    skill_id = Column(String(100), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    task_type = Column(String(50), default="baseline") # "baseline", "assisted", "independent"
    prompt = Column(Text, nullable=False)
    instructions = Column(Text, nullable=True)
    initial_code_or_template = Column(Text, nullable=True)
    expected_output_or_answer = Column(Text, nullable=True)
    evaluation_criteria = Column(JSON, default=dict) # Rubric breakdown & test patterns
    hints_available = Column(JSON, default=list) # Graduated hints 1 to 4
    is_independent = Column(Boolean, default=False)

class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String(100), ForeignKey("assessment_tasks.id"), nullable=False)
    skill_id = Column(String(100), nullable=False)
    submission_text = Column(Text, nullable=False)
    is_independent = Column(Boolean, default=False)
    hints_used = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    rubric_feedback = Column(JSON, default=dict)
    time_taken_seconds = Column(Integer, default=0)
    status = Column(String(50), default="completed") # "submitted", "evaluated"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="assessments")
    task = relationship("AssessmentTask")

class SkillEvidence(Base):
    __tablename__ = "skill_evidence"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(String(100), index=True, nullable=False)
    skill_name = Column(String(255), nullable=False)
    status = Column(Enum(SkillStatus), default=SkillStatus.UNASSESSED)
    mastery_score = Column(Float, default=0.0)
    last_assessment_id = Column(Integer, ForeignKey("assessment_attempts.id"), nullable=True)
    assisted_attempts_count = Column(Integer, default=0)
    independent_attempts_count = Column(Integer, default=0)
    evidence_notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="skill_evidence")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    recommendation_type = Column(String(50), default="practice")
    priority = Column(String(50), default="medium") # "critical", "high", "medium", "low"
    rationale = Column(Text, nullable=False)
    fired_rule_id = Column(String(100), nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")

class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String(100), nullable=False)
    plan_steps = Column(JSON, default=list) # ordered sequence of recommended milestones
    total_hours_estimated = Column(Float, default=10.0)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="learning_plans")

class AgentRunLog(Base):
    __tablename__ = "agent_run_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(String(255), nullable=False)
    state_history = Column(JSON, default=list) # Trace of steps, decisions, tool calls
    status = Column(String(50), default="completed") # "running", "completed", "failed"
    final_output = Column(JSON, default=dict)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
