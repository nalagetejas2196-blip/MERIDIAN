from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from app.models.entities import SkillStatus

@dataclass
class Rule:
    rule_id: str
    description: str
    priority: int  # Higher number = higher priority
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    category: str = "curriculum"

@dataclass
class RuleExecutionRecord:
    rule_id: str
    description: str
    priority: int
    fired: bool
    reason: str
    action_result: Optional[Dict[str, Any]] = None

class MeridianRuleEngine:
    """
    Transparent, deterministic rule-based expert system implementing forward chaining,
    priority-based conflict resolution, backward goal verification, and full provenance tracing.
    """
    def __init__(self):
        self.rules: List[Rule] = []
        self._register_default_rules()

    def register_rule(self, rule: Rule):
        self.rules.append(rule)
        # Sort by priority descending for deterministic conflict resolution
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def _register_default_rules(self):
        # Rule 1: Prerequisite Check for Advanced Topics
        self.register_rule(Rule(
            rule_id="RULE-PREREQ-OOP-BEFORE-FASTAPI",
            description="IF role requires Web/API AND OOP is unassessed or needs development, THEN mandate OOP before FastAPI",
            priority=100,
            condition=lambda facts: (
                facts.get("target_role") in ["Junior Python Developer", "Entry-Level Web Developer"]
                and facts.get("skill_status", {}).get("python_oop") in [SkillStatus.UNASSESSED.value, SkillStatus.NEEDS_DEVELOPMENT.value]
                and facts.get("skill_status", {}).get("python_basics") in [SkillStatus.DEMONSTRATED_INDEPENDENT.value, SkillStatus.DEMONSTRATED_ASSISTED.value]
            ),
            action=lambda facts: {
                "recommendation_type": "prerequisite_remediation",
                "skill_id": "python_oop",
                "priority": "critical",
                "title": "Master Object-Oriented Fundamentals Before API Development",
                "rationale": "Python OOP is a mandatory prerequisite for robust FastAPI development and dependency injection.",
                "suggested_task_id": "task_python_oop_assisted"
            }
        ))

        # Rule 2: Loops & Conditionals baseline for Java
        self.register_rule(Rule(
            rule_id="RULE-JAVA-LOOP-AFTER-CONDITIONALS",
            description="IF target_role = Junior Java Developer AND conditionals demonstrated THEN prioritize loops and arrays",
            priority=90,
            condition=lambda facts: (
                facts.get("target_role") == "Junior Java Developer"
                and facts.get("skill_status", {}).get("java_loops") in [SkillStatus.UNASSESSED.value, SkillStatus.NEEDS_DEVELOPMENT.value]
                and facts.get("skill_status", {}).get("java_syntax") in [SkillStatus.DEMONSTRATED_INDEPENDENT.value, SkillStatus.DEMONSTRATED_ASSISTED.value]
            ),
            action=lambda facts: {
                "recommendation_type": "practice",
                "skill_id": "java_loops",
                "priority": "high",
                "title": "Java Iteration & Array Traversal Exercises",
                "rationale": "Conditionals are solid; mastering loop invariants and collection traversal is your next required milestone.",
                "suggested_task_id": "task_java_loops_assisted"
            }
        ))

        # Rule 3: Promote Assisted Demonstration to Independent Reassessment
        self.register_rule(Rule(
            rule_id="RULE-INDEPENDENT-VERIFICATION-PROMOTION",
            description="IF skill was demonstrated with AI assistance THEN mandate an independent unassisted verification challenge",
            priority=95,
            condition=lambda facts: any(
                status == SkillStatus.DEMONSTRATED_ASSISTED.value
                for status in facts.get("skill_status", {}).values()
            ),
            action=lambda facts: {
                "recommendation_type": "independent_assessment",
                "skill_id": [k for k, v in facts.get("skill_status", {}).items() if v == SkillStatus.DEMONSTRATED_ASSISTED.value][0],
                "priority": "critical",
                "title": "Verify Competency: Independent Assessment Challenge",
                "rationale": "You successfully solved the assisted task with hints. Complete this unassisted task to earn full independent certification.",
                "suggested_task_id": f"task_{([k for k, v in facts.get('skill_status', {}).items() if v == SkillStatus.DEMONSTRATED_ASSISTED.value][0])}_independent"
            }
        ))

        # Rule 4: Critical Foundations if Basics Need Development
        self.register_rule(Rule(
            rule_id="RULE-FOUNDATIONS-FIRST",
            description="IF core basic syntax needs development THEN block advanced tasks and schedule syntax drills",
            priority=85,
            condition=lambda facts: (
                facts.get("skill_status", {}).get("python_basics") == SkillStatus.NEEDS_DEVELOPMENT.value
                or facts.get("skill_status", {}).get("java_syntax") == SkillStatus.NEEDS_DEVELOPMENT.value
                or facts.get("skill_status", {}).get("web_html_css") == SkillStatus.NEEDS_DEVELOPMENT.value
            ),
            action=lambda facts: {
                "recommendation_type": "foundational_drill",
                "skill_id": "foundations",
                "priority": "critical",
                "title": "Strengthen Core Syntax & Control Flow Foundations",
                "rationale": "Core syntax errors were detected. Reviewing variable scoping and branching logic prevents compound difficulties later.",
                "suggested_task_id": "task_foundations_drill"
            }
        ))

        # Rule 5: Web Developer DOM & Async JavaScript
        self.register_rule(Rule(
            rule_id="RULE-WEB-JS-DOM-ASYNC",
            description="IF role = Entry-Level Web Developer AND HTML/CSS demonstrated THEN recommend Async JavaScript & DOM manipulation",
            priority=80,
            condition=lambda facts: (
                facts.get("target_role") == "Entry-Level Web Developer"
                and facts.get("skill_status", {}).get("web_js_basics") in [SkillStatus.UNASSESSED.value, SkillStatus.NEEDS_DEVELOPMENT.value]
                and facts.get("skill_status", {}).get("web_html_css") in [SkillStatus.DEMONSTRATED_INDEPENDENT.value, SkillStatus.DEMONSTRATED_ASSISTED.value]
            ),
            action=lambda facts: {
                "recommendation_type": "practice",
                "skill_id": "web_js_basics",
                "priority": "high",
                "title": "Interactive DOM Traversal and Asynchronous Fetch Practical",
                "rationale": "HTML/CSS baseline is satisfied. JavaScript event handling and promises are required for dynamic client applications.",
                "suggested_task_id": "task_web_js_assisted"
            }
        ))

        # Rule 6: General Default Continuation
        self.register_rule(Rule(
            rule_id="RULE-GENERAL-PROGRESSION",
            description="IF all evaluated prerequisites are satisfied THEN progress to next unassessed competency in role map",
            priority=10,
            condition=lambda facts: any(
                status == SkillStatus.UNASSESSED.value
                for status in facts.get("skill_status", {}).values()
            ),
            action=lambda facts: {
                "recommendation_type": "baseline_assessment",
                "skill_id": [k for k, v in facts.get("skill_status", {}).items() if v == SkillStatus.UNASSESSED.value][0],
                "priority": "medium",
                "title": "Establish Baseline in Next Role Competency",
                "rationale": "Assess your understanding of this topic to personalize subsequent learning modules.",
                "suggested_task_id": f"task_{([k for k, v in facts.get('skill_status', {}).items() if v == SkillStatus.UNASSESSED.value][0])}_baseline"
            }
        ))

    def evaluate_forward_chaining(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes forward chaining across all registered rules with fact provenance and execution audit trace.
        """
        audit_trail: List[RuleExecutionRecord] = []
        fired_recommendations: List[Dict[str, Any]] = []

        for rule in self.rules:
            try:
                matches = rule.condition(facts)
                if matches:
                    action_out = rule.action(facts)
                    action_out["fired_rule_id"] = rule.rule_id
                    fired_recommendations.append(action_out)
                    audit_trail.append(RuleExecutionRecord(
                        rule_id=rule.rule_id,
                        description=rule.description,
                        priority=rule.priority,
                        fired=True,
                        reason="Condition predicates evaluated to TRUE on current facts",
                        action_result=action_out
                    ))
                else:
                    audit_trail.append(RuleExecutionRecord(
                        rule_id=rule.rule_id,
                        description=rule.description,
                        priority=rule.priority,
                        fired=False,
                        reason="Condition predicates evaluated to FALSE on current facts"
                    ))
            except Exception as e:
                audit_trail.append(RuleExecutionRecord(
                    rule_id=rule.rule_id,
                    description=rule.description,
                    priority=rule.priority,
                    fired=False,
                    reason=f"Evaluation error: {str(e)}"
                ))

        # Conflict resolution: sort fired recommendations by priority of originating rule
        return {
            "facts_evaluated": facts,
            "fired_recommendations": fired_recommendations,
            "audit_trail": [
                {
                    "rule_id": r.rule_id,
                    "description": r.description,
                    "priority": r.priority,
                    "fired": r.fired,
                    "reason": r.reason,
                    "action_result": r.action_result
                }
                for r in audit_trail
            ],
            "primary_recommendation": fired_recommendations[0] if fired_recommendations else None
        }

    def backward_chain_goal_verification(self, target_goal_skill: str, facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Backward chaining: Given a target goal skill to certify independently,
        recursively verifies whether all dependent prerequisites and evidence are satisfied.
        """
        reasoning_tree = []
        is_verified = False
        status = facts.get("skill_status", {}).get(target_goal_skill, SkillStatus.UNASSESSED.value)

        prereq_map = {
            "python_oop": ["python_basics"],
            "python_fastapi": ["python_basics", "python_oop"],
            "java_loops": ["java_syntax"],
            "java_oop": ["java_syntax", "java_loops"],
            "web_js_basics": ["web_html_css"],
            "web_react": ["web_html_css", "web_js_basics"]
        }

        prereqs = prereq_map.get(target_goal_skill, [])
        all_prereqs_satisfied = True
        missing_prereqs = []

        for p in prereqs:
            p_status = facts.get("skill_status", {}).get(p, SkillStatus.UNASSESSED.value)
            if p_status not in [SkillStatus.DEMONSTRATED_INDEPENDENT.value, SkillStatus.DEMONSTRATED_ASSISTED.value]:
                all_prereqs_satisfied = False
                missing_prereqs.append(p)

        reasoning_tree.append({
            "target_goal": target_goal_skill,
            "current_status": status,
            "prerequisites_required": prereqs,
            "all_prereqs_satisfied": all_prereqs_satisfied,
            "missing_prereqs": missing_prereqs
        })

        if status == SkillStatus.DEMONSTRATED_INDEPENDENT.value and all_prereqs_satisfied:
            is_verified = True
            summary = f"Goal '{target_goal_skill}' is fully verified with independent demonstration and prerequisites satisfied."
        elif not all_prereqs_satisfied:
            summary = f"Goal '{target_goal_skill}' cannot be verified: prerequisites {missing_prereqs} are not yet demonstrated."
        else:
            summary = f"Goal '{target_goal_skill}' is currently in state '{status}'. Requires unassisted independent assessment."

        return {
            "goal": target_goal_skill,
            "verified": is_verified,
            "summary": summary,
            "proof_tree": reasoning_tree
        }
