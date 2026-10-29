import pytest
from datetime import datetime, timedelta
from app.main import (
    get_health,
    get_all_strategies,
    get_all_stories,
    retrieve_strategies,
    generate_intervention,
    recommend_story,
    rebalance_plan
)
from app.schemas import (
    RetrievalRequest,
    InterventionRequest,
    StoryRecommendationRequest,
    PlanRebalanceRequest,
    TaskItem
)
from app.services.rag_engine import rag_engine
from app.services.planner import adaptive_planner
from app.observer.stuck_radar import stuck_radar_engine

def test_health_endpoint():
    res = get_health()
    assert res.status == "ok"
    assert hasattr(res, "gemini_configured")
    assert res.gemini_model == "gemini-3.5-flash-lite"
    assert res.version == "1.0.0"
    dump = res.model_dump()
    assert "api_key" not in dump
    assert "GEMINI_API_KEY" not in dump

def test_strategies_endpoint():
    strategies = get_all_strategies()
    assert len(strategies) >= 12
    for s in strategies:
        assert s.id.startswith("strat_")
        assert len(s.title) > 0
        assert len(s.difficulty_tags) > 0
        assert len(s.explanation) > 0
        assert len(s.suggested_action) > 0

def test_stories_endpoint():
    stories = get_all_stories()
    assert len(stories) == 5
    ids = [s.id for s in stories]
    assert "story_seed_rock" in ids
    assert "story_river_route" in ids
    assert "story_smallest_tree" in ids
    assert "story_flower_rain" in ids
    assert "story_one_stone" in ids

    for s in stories:
        assert len(s.scenes) >= 3
        assert len(s.takeaway) > 0
        assert len(s.reflection_question) > 0
        assert len(s.suggested_next_actions) > 0

def test_rag_retrieval_across_difficulties():
    difficulties = [
        "beginning",
        "overwhelm",
        "perfectionism",
        "distraction",
        "low_energy",
        "ineffective_approach"
    ]
    for diff in difficulties:
        req = RetrievalRequest(difficulty=diff, limit=3)
        res = retrieve_strategies(req)
        assert res.retrieved_count >= 1
        assert len(res.strategies) >= 1
        top_strat = res.strategies[0]
        assert top_strat.id.startswith("strat_")

def test_intervention_no_key_mode_fallback():
    req = InterventionRequest(
        difficulty="beginning",
        energy="low",
        task_title="Wireless & Mobile Communication",
        task_subject="Engineering",
        description="I have been staring at the empty document for 20 minutes."
    )
    res = generate_intervention(req)
    assert res.generation_source in ["local_fallback", "gemini"]
    assert len(res.action_steps) >= 2
    assert len(res.acknowledgement) > 0
    assert len(res.action_title) > 0
    assert len(res.why_this_fits) > 0
    assert len(res.strategy_ids) > 0
    assert res.retrieved_strategies is not None
    assert len(res.retrieved_strategies) > 0

def test_story_recommendation():
    # Ineffective approach maps to river route
    res = recommend_story(StoryRecommendationRequest(difficulty="ineffective_approach"))
    assert res.recommended_story_id == "story_river_route"
    assert "River" in res.title

    # Low energy maps to flower rain
    res2 = recommend_story(StoryRecommendationRequest(difficulty="low_energy"))
    assert res2.recommended_story_id == "story_flower_rain"
    assert "Flower" in res2.title

    # Beginning maps to one stone
    res3 = recommend_story(StoryRecommendationRequest(difficulty="beginning"))
    assert res3.recommended_story_id == "story_one_stone"

def test_adaptive_planner_logic():
    tasks = [
        TaskItem(id="t1", title="Task 1 Long", estimated_duration=90, priority="high", status="not_started", deadline="2026-11-01"),
        TaskItem(id="t2", title="Task 2 Short", estimated_duration=20, priority="normal", status="not_started", deadline="2026-11-02"),
        TaskItem(id="t3", title="Task 3 Completed", estimated_duration=45, priority="normal", status="completed"),
    ]

    req = PlanRebalanceRequest(tasks=tasks, energy="low", available_minutes=120)
    result_low = rebalance_plan(req)
    assert result_low.recommended_next_task_id is not None
    
    # Completed task must stay completed and preserved
    completed_in_plan = [t for t in result_low.ordered_tasks if t.status == "completed"]
    assert len(completed_in_plan) == 1
    assert completed_in_plan[0].id == "t3"

    # Test time conflict detection
    heavy_tasks = [
        TaskItem(id="h1", title="Heavy 1", estimated_duration=120, priority="high"),
        TaskItem(id="h2", title="Heavy 2", estimated_duration=120, priority="high"),
    ]
    req_heavy = PlanRebalanceRequest(tasks=heavy_tasks, energy="medium", available_minutes=120)
    result_heavy = rebalance_plan(req_heavy)
    assert result_heavy.has_time_conflict is True
    assert len(result_heavy.conflicts) > 0

def test_stuck_radar_evaluation():
    engine = stuck_radar_engine

    # Inactivity trigger
    inactive_check = engine.evaluate(
        seconds_inactive=130,
        request_timestamps=[],
        dismissal_timestamps=[],
        is_session_active=True
    )
    assert inactive_check.should_prompt is True
    assert inactive_check.trigger_reason == "inactivity"

    # Inactive when session is NOT active -> should not prompt
    inactive_idle = engine.evaluate(
        seconds_inactive=150,
        request_timestamps=[],
        dismissal_timestamps=[],
        is_session_active=False
    )
    assert inactive_idle.should_prompt is False

    # Cooldown check
    now = datetime.now()
    cooldown_check = engine.evaluate(
        seconds_inactive=150,
        request_timestamps=[],
        dismissal_timestamps=[],
        last_prompt_dismissed_at=now - timedelta(seconds=60),
        is_session_active=True
    )
    assert cooldown_check.should_prompt is False
