from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class HealthResponse(BaseModel):
    status: str
    gemini_configured: bool
    gemini_model: str
    version: str

class StrategyRecord(BaseModel):
    id: str
    title: str
    difficulty_tags: List[str]
    keywords: List[str]
    explanation: str
    suggested_action: str
    safety_note: Optional[str] = None
    score: Optional[float] = None

class RetrievalRequest(BaseModel):
    difficulty: str
    description: Optional[str] = ""
    limit: Optional[int] = 3

class RetrievalResponse(BaseModel):
    difficulty: str
    retrieved_count: int
    strategies: List[StrategyRecord]

class TaskItem(BaseModel):
    id: str
    title: str
    subject: str = "General"
    description: Optional[str] = ""
    deadline: Optional[str] = None
    estimated_duration: int = Field(default=30, ge=1) # in minutes
    priority: str = Field(default="normal") # low, normal, high
    status: str = Field(default="not_started") # not_started, in_progress, completed
    scheduled_order: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class InterventionRequest(BaseModel):
    difficulty: str
    energy: str = "medium" # low, medium, high
    task_title: Optional[str] = None
    task_subject: Optional[str] = None
    description: Optional[str] = ""
    previous_feedback: Optional[List[Dict[str, Any]]] = None

class InterventionResponse(BaseModel):
    acknowledgement: str
    action_title: str
    action_steps: List[str]
    why_this_fits: str
    strategy_ids: List[str]
    generation_source: str # "gemini" or "local_fallback"
    fallback_reason: Optional[str] = None
    retrieved_strategies: Optional[List[StrategyRecord]] = None

class StoryScene(BaseModel):
    scene_number: int
    title: str
    description: str
    narration_text: str
    visual_key: str

class StoryRecord(BaseModel):
    id: str
    title: str
    difficulty_tags: List[str]
    summary: str
    takeaway: str
    reflection_question: str
    suggested_next_actions: List[str]
    narration_language: str = "en-US"
    estimated_reading_time_minutes: int = 2
    scenes: List[StoryScene]

class StoryRecommendationRequest(BaseModel):
    difficulty: str
    energy: Optional[str] = "medium"

class StoryRecommendationResponse(BaseModel):
    recommended_story_id: str
    title: str
    selection_reason: str
    selection_source: str # "gemini" or "deterministic_mapping"

class PlanRebalanceRequest(BaseModel):
    tasks: List[TaskItem]
    energy: str = "medium" # low, medium, high
    available_minutes: Optional[int] = 180

class ScheduleConflict(BaseModel):
    task_id: str
    title: str
    message: str

class PlanRebalanceResponse(BaseModel):
    ordered_tasks: List[TaskItem]
    recommended_next_task_id: Optional[str] = None
    recommendation_reason: str
    total_planned_minutes: int
    available_minutes: int
    has_time_conflict: bool
    conflicts: List[ScheduleConflict]
    energy_adaptation_note: str
