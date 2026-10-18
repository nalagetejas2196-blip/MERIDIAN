import pytest
from app.rules_engine.engine import MeridianRuleEngine
from app.models.entities import SkillStatus
from app.algorithms.practicals import (
    run_simple_reflex_agent, run_model_based_agent, run_astar_8puzzle,
    run_alphabeta_pruning, run_tower_of_hanoi, run_sudoku_solver,
    run_tsp_local_beam_search, run_bfs_planning, run_dfs_problem_solving,
    run_eight_queens, run_rule_based_chatbot, run_number_guessing_agent,
    run_goal_stack_planning, run_minimax_tictactoe, run_medical_diagnosis_expert_system,
    run_rule_based_recommendation_system
)
from app.rag.pipeline import rag_pipeline
from app.agent.workflow import BoundedLearningAgent

def test_rule_engine_forward_chaining():
    engine = MeridianRuleEngine()
    facts = {
        "target_role": "Junior Python Developer",
        "skill_status": {
            "python_basics": SkillStatus.DEMONSTRATED_INDEPENDENT.value,
            "python_oop": SkillStatus.NEEDS_DEVELOPMENT.value
        }
    }
    result = engine.evaluate_forward_chaining(facts)
    assert result["primary_recommendation"] is not None
    assert result["primary_recommendation"]["skill_id"] == "python_oop"
    assert result["primary_recommendation"]["priority"] == "critical"

def test_rule_engine_backward_chaining():
    engine = MeridianRuleEngine()
    facts = {
        "skill_status": {
            "python_basics": SkillStatus.DEMONSTRATED_INDEPENDENT.value,
            "python_oop": SkillStatus.DEMONSTRATED_INDEPENDENT.value
        }
    }
    proof = engine.backward_chain_goal_verification("python_oop", facts)
    assert proof["verified"] is True

def test_rag_retrieval_and_citations():
    # Query knowledge base
    retrieved = rag_pipeline.retrieve("classes and inheritance in Python", top_k=2)
    assert len(retrieved) > 0
    assert "source" in retrieved[0]
    assert "similarity_score" in retrieved[0]
    assert retrieved[0]["similarity_score"] > 0.0

def test_bounded_agent_workflow():
    engine = MeridianRuleEngine()
    agent = BoundedLearningAgent(engine)
    facts = {
        "target_role": "Junior Python Developer",
        "skill_status": {
            "python_basics": SkillStatus.DEMONSTRATED_INDEPENDENT.value,
            "python_oop": SkillStatus.DEMONSTRATED_ASSISTED.value
        }
    }
    result = agent.execute_workflow(facts)
    assert result["status"] == "completed"
    assert result["steps_executed"] == 8
    assert len(result["state_history"]) == 8

# Test All 16 AI Practicals
def test_all_16_syllabus_practicals():
    # Part A
    p1 = run_simple_reflex_agent({"A": "Dirty", "B": "Clean"})
    assert p1["steps_count"] > 0

    p2 = run_model_based_agent({"A": "Dirty", "B": "Dirty"})
    assert p2["steps_count"] > 0

    p3 = run_astar_8puzzle()
    assert p3["solution_steps"] >= 0

    p4 = run_alphabeta_pruning()
    assert "optimal_minimax_value" in p4

    p5 = run_tower_of_hanoi(3)
    assert p5["moves_generated"] == 7

    p6 = run_sudoku_solver()
    assert p6["solved"] is True

    p7 = run_tsp_local_beam_search(3)
    assert p7["best_distance"] > 0

    # Part B
    p8 = run_bfs_planning("A", "G")
    assert "G" in p8["shortest_path"]

    p9 = run_dfs_problem_solving("A", "G")
    assert "G" in p9["path_found"]

    p10 = run_eight_queens(4)
    assert p10["total_solutions_found"] == 2

    p11 = run_rule_based_chatbot("hello there")
    assert "deterministic" in p11["agent_response"].lower()

    p12 = run_number_guessing_agent(42, 1, 100)
    assert p12["total_attempts"] <= 7

    p13 = run_goal_stack_planning()
    assert p13["plan_length"] == 10

    p14 = run_minimax_tictactoe()
    assert p14["recommended_ai_move"] >= 0

    # Part C
    p15 = run_medical_diagnosis_expert_system(["cough", "runny_nose", "sneezing"])
    assert len(p15["matched_inferences"]) > 0

    p16 = run_rule_based_recommendation_system({
        "target_role": "Junior Python Developer",
        "weaknesses": ["python_basics"]
    })
    assert p16["rules_fired_count"] > 0
