import json
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.schemas import (
    HealthResponse,
    StrategyRecord,
    RetrievalRequest,
    RetrievalResponse,
    InterventionRequest,
    InterventionResponse,
    StoryRecord,
    StoryRecommendationRequest,
    StoryRecommendationResponse,
    PlanRebalanceRequest,
    PlanRebalanceResponse
)
from app.services.rag_engine import rag_engine
from app.services.gemini_service import gemini_service
from app.services.planner import adaptive_planner

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Adaptive Task-Initiation & Student Productivity Companion Backend API"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
def get_health():
    """Returns server health, Gemini SDK configuration status, and version. Never exposes API keys."""
    return HealthResponse(
        status="ok",
        gemini_configured=gemini_service.is_configured(),
        gemini_model=settings.GEMINI_MODEL,
        version=settings.VERSION
    )

@app.get("/api/strategies", response_model=List[StrategyRecord])
def get_all_strategies():
    """Returns curated local RAG strategies."""
    return rag_engine.get_all_strategies()

@app.get("/api/stories", response_model=List[StoryRecord])
def get_all_stories():
    """Returns curated original motivational stories."""
    if not settings.STORIES_FILE.exists():
        raise HTTPException(status_code=404, detail="Story library not found.")
    with open(settings.STORIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [StoryRecord(**item) for item in data]

@app.post("/api/retrieve", response_model=RetrievalResponse)
def retrieve_strategies(req: RetrievalRequest):
    """Retrieves top matching strategies based on deterministic keyword and tag matching."""
    matched = rag_engine.retrieve(
        difficulty=req.difficulty,
        description=req.description or "",
        limit=req.limit or 3
    )
    return RetrievalResponse(
        difficulty=req.difficulty,
        retrieved_count=len(matched),
        strategies=matched
    )

@app.post("/api/intervention", response_model=InterventionResponse)
def generate_intervention(req: InterventionRequest):
    """
    RAG-grounded intervention engine.
    Retrieves strategy excerpts and generates compassionate, structured action guidance
    via Gemini Developer API (or instant deterministic fallback if no key is supplied).
    """
    retrieved = rag_engine.retrieve(
        difficulty=req.difficulty,
        description=req.description or "",
        limit=3
    )
    intervention = gemini_service.generate_intervention(
        request=req,
        retrieved_strategies=retrieved
    )
    return intervention

@app.post("/api/story-recommendation", response_model=StoryRecommendationResponse)
def recommend_story(req: StoryRecommendationRequest):
    """
    Recommends a story based on the student's selected difficulty.
    Deterministic mapping prioritizes:
    - beginning / overwhelm -> 'story_seed_rock' or 'story_one_stone'
    - ineffective_approach -> 'story_river_route'
    - perfectionism / distraction -> 'story_smallest_tree'
    - low_energy / break -> 'story_flower_rain'
    """
    raw_diff = (req.difficulty or "").lower()
    
    if any(k in raw_diff for k in ["ineffective", "approach", "method", "stuck"]):
        story_id = "story_river_route"
        title = "The River That Took Another Route"
        reason = "Recommended because changing your method is a valid way to move forward when an existing approach stalls."
    elif any(k in raw_diff for k in ["perfection", "behind", "compare", "wrong"]):
        story_id = "story_smallest_tree"
        title = "The Smallest Tree"
        reason = "Recommended to remind you that your pace and deep rooting are valid, independent of external comparison."
    elif any(k in raw_diff for k in ["energy", "tired", "break", "exhausted", "rest"]):
        story_id = "story_flower_rain"
        title = "The Flower After the Rain"
        reason = "Recommended because stepping into quiet rest is an active part of growth, not lost time."
    elif any(k in raw_diff for k in ["begin", "start", "blank", "first"]):
        story_id = "story_one_stone"
        title = "One Stone at a Time"
        reason = "Recommended because stepping onto just the single visible stone in front of you unlocks the next horizon."
    else:
        story_id = "story_seed_rock"
        title = "The Seed and the Rock"
        reason = "Recommended to illustrate finding a sideways sunlit path when upward progress meets an obstacle."

    return StoryRecommendationResponse(
        recommended_story_id=story_id,
        title=title,
        selection_reason=reason,
        selection_source="deterministic_mapping"
    )

@app.post("/api/rebalance-plan", response_model=PlanRebalanceResponse)
def rebalance_plan(req: PlanRebalanceRequest):
    """
    Deterministic adaptive planning engine endpoint.
    Respects energy, deadlines, and time constraints without deleting or silently modifying tasks.
    """
    return adaptive_planner.rebalance(
        tasks=req.tasks,
        energy=req.energy,
        available_minutes=req.available_minutes or 180
    )
