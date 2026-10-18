from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, oauth2_scheme
from app.core.config import settings
from jose import jwt, JWTError
from app.models.entities import User, RoleCompetency, AssessmentTask, SkillEvidence, Recommendation, LearningPlan, AgentRunLog, SkillStatus
from app.schemas.api_schemas import (
    UserCreate, UserLogin, UserOut, Token, RoleCompetencyOut, SkillEvidenceOut,
    AssessmentTaskOut, AssessmentSubmission, AssessmentResultOut, RecommendationOut,
    LearningPlanOut, ChatQueryRequest, ChatResponse, AgentRunRequest, AgentRunOut
)
from app.rules_engine.engine import MeridianRuleEngine
from app.rag.pipeline import rag_pipeline
from app.agent.workflow import BoundedLearningAgent
from app.services.assessment_service import AssessmentEvaluationService
from app.algorithms.practicals import (
    run_simple_reflex_agent, run_model_based_agent, run_astar_8puzzle,
    run_alphabeta_pruning, run_tower_of_hanoi, run_sudoku_solver, run_tsp_local_beam_search,
    run_bfs_planning, run_dfs_problem_solving, run_eight_queens, run_rule_based_chatbot,
    run_number_guessing_agent, run_goal_stack_planning, run_minimax_tictactoe,
    run_medical_diagnosis_expert_system, run_rule_based_recommendation_system
)

router = APIRouter()
rule_engine = MeridianRuleEngine()
bounded_agent = BoundedLearningAgent(rule_engine)

# Auth Dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter((User.username == username) | (User.email == username)).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ENDPOINTS ---
@router.post("/auth/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == user_in.email) | (User.username == user_in.username)).first():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    from app.core.security import get_password_hash
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        target_role=user_in.target_role or "Junior Python Developer"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/auth/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == login_data.username_or_email) | (User.email == login_data.username_or_email)
    ).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/auth/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/auth/target-role", response_model=UserOut)
def update_target_role(role_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.target_role = role_name
    db.commit()
    db.refresh(current_user)
    return current_user

# --- ROLE COMPETENCIES & EVIDENCE ---
@router.get("/roles/competencies", response_model=List[RoleCompetencyOut])
def get_role_competencies(role_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(RoleCompetency)
    if role_name:
        query = query.filter(RoleCompetency.role_name == role_name)
    return query.all()

@router.get("/skills/evidence", response_model=List[SkillEvidenceOut])
def get_skill_evidence(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SkillEvidence).filter(SkillEvidence.user_id == current_user.id).all()

# --- ASSESSMENTS ---
@router.get("/assessments/tasks", response_model=List[AssessmentTaskOut])
def get_assessment_tasks(skill_id: Optional[str] = None, role_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AssessmentTask)
    if skill_id:
        query = query.filter(AssessmentTask.skill_id == skill_id)
    if role_name:
        query = query.filter(AssessmentTask.role_name == role_name)
    return query.all()

@router.post("/assessments/submit", response_model=AssessmentResultOut)
def submit_assessment(
    submission: AssessmentSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(AssessmentTask).filter(AssessmentTask.id == submission.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Assessment task not found")
    result = AssessmentEvaluationService.evaluate_task_submission(
        db=db,
        user=current_user,
        task=task,
        submission_text=submission.submission_text,
        hints_used=submission.hints_used,
        time_taken_seconds=submission.time_taken_seconds
    )
    return result

# --- RECOMMENDATIONS & LEARNING PLAN ---
@router.get("/recommendations", response_model=List[RecommendationOut])
def get_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Recommendation).filter(Recommendation.user_id == current_user.id).all()

@router.get("/rules/explore")
def explore_rules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_evidence = db.query(SkillEvidence).filter(SkillEvidence.user_id == current_user.id).all()
    facts = {
        "target_role": current_user.target_role,
        "skill_status": {e.skill_id: e.status.value for e in all_evidence}
    }
    evaluation = rule_engine.evaluate_forward_chaining(facts)
    return evaluation

@router.get("/rules/verify-goal")
def verify_goal_backward_chaining(goal_skill: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_evidence = db.query(SkillEvidence).filter(SkillEvidence.user_id == current_user.id).all()
    facts = {
        "target_role": current_user.target_role,
        "skill_status": {e.skill_id: e.status.value for e in all_evidence}
    }
    return rule_engine.backward_chain_goal_verification(goal_skill, facts)

# --- AI ASSISTANT & RAG ---
@router.post("/chat/query", response_model=ChatResponse)
async def chat_assistant(req: ChatQueryRequest):
    res = await rag_pipeline.generate_response(
        query=req.message,
        skill_context=req.skill_context,
        hint_step=req.hint_step
    )
    return res

@router.get("/rag/inspect")
def inspect_rag(query: str = "FastAPI"):
    retrieved = rag_pipeline.retrieve(query, top_k=5)
    return {
        "query": query,
        "retrieved_chunks_count": len(retrieved),
        "total_documents_indexed": len(rag_pipeline.documents),
        "results": retrieved
    }

# --- BOUNDED AGENT RUN ---
@router.post("/agent/run", response_model=AgentRunOut)
def run_agent_workflow(
    req: AgentRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    all_evidence = db.query(SkillEvidence).filter(SkillEvidence.user_id == current_user.id).all()
    facts = {
        "target_role": current_user.target_role,
        "skill_status": {e.skill_id: e.status.value for e in all_evidence}
    }
    result = bounded_agent.execute_workflow(facts)
    
    # Save trace log to database
    run_log = AgentRunLog(
        user_id=current_user.id,
        goal=req.goal or "Optimize Next Skill Milestone",
        state_history=result["state_history"],
        status=result["status"],
        final_output=result["final_output"],
        execution_time_ms=result["execution_time_ms"]
    )
    db.add(run_log)
    db.commit()
    db.refresh(run_log)

    return {
        "run_id": run_log.id,
        "goal": run_log.goal,
        "status": run_log.status,
        "state_history": run_log.state_history,
        "final_output": run_log.final_output,
        "execution_time_ms": run_log.execution_time_ms
    }

# --- 16 ALGORITHM LAB PRACTICAL RUNNERS ---
@router.get("/algorithms/practical/{practical_id}")
def execute_syllabus_practical(practical_id: int, param: Optional[str] = None):
    if practical_id == 1:
        return run_simple_reflex_agent({"A": "Dirty", "B": "Dirty"})
    elif practical_id == 2:
        return run_model_based_agent({"A": "Dirty", "B": "Clean"})
    elif practical_id == 3:
        return run_astar_8puzzle()
    elif practical_id == 4:
        return run_alphabeta_pruning()
    elif practical_id == 5:
        disks = int(param) if param and param.isdigit() else 3
        return run_tower_of_hanoi(disks)
    elif practical_id == 6:
        return run_sudoku_solver()
    elif practical_id == 7:
        k = int(param) if param and param.isdigit() else 3
        return run_tsp_local_beam_search(k)
    elif practical_id == 8:
        return run_bfs_planning()
    elif practical_id == 9:
        return run_dfs_problem_solving()
    elif practical_id == 10:
        n = int(param) if param and param.isdigit() else 8
        return run_eight_queens(n)
    elif practical_id == 11:
        msg = param or "What is RAG in AI?"
        return run_rule_based_chatbot(msg)
    elif practical_id == 12:
        secret = int(param) if param and param.isdigit() else 42
        return run_number_guessing_agent(secret)
    elif practical_id == 13:
        return run_goal_stack_planning()
    elif practical_id == 14:
        return run_minimax_tictactoe()
    elif practical_id == 15:
        symptoms = [s.strip() for s in (param or "cough, runny_nose, sneezing").split(",")]
        return run_medical_diagnosis_expert_system(symptoms)
    elif practical_id == 16:
        return run_rule_based_recommendation_system({
            "target_role": "Junior Python Developer",
            "weekly_hours": 8,
            "weaknesses": ["python_basics"]
        })
    else:
        raise HTTPException(status_code=404, detail="Practical not found (valid range 1-16)")
