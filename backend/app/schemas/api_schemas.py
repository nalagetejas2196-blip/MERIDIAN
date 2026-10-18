from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.entities import SkillStatus

# --- User & Auth Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    target_role: Optional[str] = "Junior Python Developer"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    is_instructor: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# --- Competency & Skill Schemas ---
class RoleCompetencyOut(BaseModel):
    id: int
    role_name: str
    skill_id: str
    skill_name: str
    category: str
    prerequisites: List[str]
    description: Optional[str] = None
    priority_weight: float
    class Config:
        from_attributes = True

class SkillEvidenceOut(BaseModel):
    id: int
    skill_id: str
    skill_name: str
    status: SkillStatus
    mastery_score: float
    assisted_attempts_count: int
    independent_attempts_count: int
    evidence_notes: Optional[str] = None
    updated_at: datetime
    class Config:
        from_attributes = True

# --- Assessment Schemas ---
class AssessmentTaskOut(BaseModel):
    id: str
    role_name: str
    skill_id: str
    title: str
    task_type: str
    prompt: str
    instructions: Optional[str] = None
    initial_code_or_template: Optional[str] = None
    is_independent: bool
    hints_available: List[str]
    class Config:
        from_attributes = True

class AssessmentSubmission(BaseModel):
    task_id: str
    submission_text: str
    hints_used: int = 0
    time_taken_seconds: int = 0

class AssessmentResultOut(BaseModel):
    attempt_id: int
    task_id: str
    skill_id: str
    is_independent: bool
    hints_used: int
    score_percentage: float
    new_skill_status: SkillStatus
    rubric_feedback: Dict[str, Any]
    message: str

# --- Recommendation Schemas ---
class RecommendationOut(BaseModel):
    id: int
    skill_id: str
    title: str
    recommendation_type: str
    priority: str
    rationale: str
    fired_rule_id: Optional[str] = None
    is_completed: bool
    created_at: datetime
    class Config:
        from_attributes = True

class LearningPlanOut(BaseModel):
    id: int
    target_role: str
    plan_steps: List[Dict[str, Any]]
    total_hours_estimated: float
    explanation: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

# --- AI & RAG Schemas ---
class ChatMessage(BaseModel):
    role: str # "user" | "assistant" | "system"
    content: str

class ChatQueryRequest(BaseModel):
    message: str
    skill_context: Optional[str] = None
    task_context_id: Optional[str] = None
    hint_step: Optional[int] = None # 1=Conceptual, 2=Specific, 3=Guided Reasoning, 4=Worked Example

class ChatResponse(BaseModel):
    reply: str
    is_fallback: bool
    source_citations: List[Dict[str, Any]]
    retrieved_passages: List[Dict[str, Any]]
    model_used: str

# --- Agent Run Schemas ---
class AgentRunRequest(BaseModel):
    goal: Optional[str] = "Formulate optimal next learning milestone based on skill gaps"

class AgentRunOut(BaseModel):
    run_id: int
    goal: str
    status: str
    state_history: List[Dict[str, Any]]
    final_output: Dict[str, Any]
    execution_time_ms: float
