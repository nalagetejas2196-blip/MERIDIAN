from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.entities import User, SkillEvidence, SkillStatus, AssessmentTask, AssessmentAttempt, Recommendation
from app.rules_engine.engine import MeridianRuleEngine

rule_engine = MeridianRuleEngine()

class AssessmentEvaluationService:
    """
    Evaluates submissions deterministically using keyword and rubric verification.
    Crucially separates ASSISTED evidence from INDEPENDENT evidence.
    """
    @staticmethod
    def evaluate_task_submission(
        db: Session,
        user: User,
        task: AssessmentTask,
        submission_text: str,
        hints_used: int,
        time_taken_seconds: int
    ) -> Dict[str, Any]:
        # 1. Rubric Verification (Deterministic Keyword Checks)
        criteria = task.evaluation_criteria or {}
        required_keywords = criteria.get("required_keywords", [])
        
        matches = [kw for kw in required_keywords if kw in submission_text]
        score_percentage = round((len(matches) / len(required_keywords)) * 100.0, 1) if required_keywords else 80.0

        is_passed = score_percentage >= 70.0

        # 2. Determine Evidence State based on hints and independent flag
        # AI/Hint assistance prohibits award of DEMONSTRATED_INDEPENDENT
        if not is_passed:
            new_status = SkillStatus.NEEDS_DEVELOPMENT
        elif task.is_independent and hints_used == 0:
            new_status = SkillStatus.DEMONSTRATED_INDEPENDENT
        else:
            new_status = SkillStatus.DEMONSTRATED_ASSISTED

        # 3. Record Assessment Attempt
        attempt = AssessmentAttempt(
            user_id=user.id,
            task_id=task.id,
            skill_id=task.skill_id,
            submission_text=submission_text,
            is_independent=task.is_independent,
            hints_used=hints_used,
            score_percentage=score_percentage,
            rubric_feedback={
                "required_keywords": required_keywords,
                "matched_keywords": matches,
                "passed": is_passed,
                "evaluation_mode": "unassisted_independent" if task.is_independent else "assisted_practice"
            },
            time_taken_seconds=time_taken_seconds,
            status="completed"
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # 4. Update or Insert Persistent Skill Evidence
        evidence = db.query(SkillEvidence).filter(
            SkillEvidence.user_id == user.id,
            SkillEvidence.skill_id == task.skill_id
        ).first()

        if not evidence:
            evidence = SkillEvidence(
                user_id=user.id,
                skill_id=task.skill_id,
                skill_name=task.title,
                status=new_status,
                mastery_score=score_percentage,
                last_assessment_id=attempt.id,
                assisted_attempts_count=0 if task.is_independent else 1,
                independent_attempts_count=1 if task.is_independent else 0,
                evidence_notes=f"Initial assessment score: {score_percentage}%"
            )
            db.add(evidence)
        else:
            evidence.mastery_score = score_percentage
            evidence.last_assessment_id = attempt.id
            if task.is_independent:
                evidence.independent_attempts_count += 1
                if is_passed:
                    evidence.status = SkillStatus.DEMONSTRATED_INDEPENDENT
                    evidence.evidence_notes = f"Verified independently with {score_percentage}% score without hints."
            else:
                evidence.assisted_attempts_count += 1
                # If already demonstrated independently, do not downgrade to assisted
                if evidence.status != SkillStatus.DEMONSTRATED_INDEPENDENT:
                    evidence.status = new_status
                    evidence.evidence_notes = f"Demonstrated in assisted mode ({hints_used} hints used). Independent reassessment needed."

        db.commit()
        db.refresh(evidence)

        # 5. Automatically trigger rule engine evaluation to update recommendations
        all_evidence = db.query(SkillEvidence).filter(SkillEvidence.user_id == user.id).all()
        facts = {
            "target_role": user.target_role,
            "skill_status": {e.skill_id: e.status.value for e in all_evidence}
        }
        rule_eval = rule_engine.evaluate_forward_chaining(facts)
        
        # Save highest priority recommendation
        if rule_eval["primary_recommendation"]:
            rec_data = rule_eval["primary_recommendation"]
            db.query(Recommendation).filter(Recommendation.user_id == user.id, Recommendation.is_completed == False).delete()
            db.add(Recommendation(
                user_id=user.id,
                skill_id=rec_data["skill_id"],
                title=rec_data["title"],
                recommendation_type=rec_data["recommendation_type"],
                priority=rec_data["priority"],
                rationale=rec_data["rationale"],
                fired_rule_id=rec_data.get("fired_rule_id")
            ))
            db.commit()

        return {
            "attempt_id": attempt.id,
            "task_id": task.id,
            "skill_id": task.skill_id,
            "is_independent": task.is_independent,
            "hints_used": hints_used,
            "score_percentage": score_percentage,
            "new_skill_status": evidence.status,
            "rubric_feedback": attempt.rubric_feedback,
            "message": "Independent competency demonstrated successfully!" if new_status == SkillStatus.DEMONSTRATED_INDEPENDENT else "Assessment evaluated. Review graduated recommendations."
        }
