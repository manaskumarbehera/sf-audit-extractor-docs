"""
TrackForcePro — Adaptive Quiz Engine (FastAPI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Features:
  - Spaced repetition: tracks which topics/questions each player struggles with
  - Adaptive difficulty: starts easy, scales based on rolling accuracy
  - Weakness targeting: prioritizes topics with lowest historical accuracy
  - XP & leveling system: XP per question, level thresholds, streak bonuses
  - Session memory: remembers questions already asked in the current session

Endpoints:
  GET  /api/quiz/next         — get the next adaptive question
  POST /api/quiz/answer       — submit an answer, get feedback + XP
  GET  /api/quiz/profile/{id} — player stats, weak topics, XP, level
  GET  /api/quiz/topics       — list all topics with player accuracy
  POST /api/quiz/reset/{id}   — reset a player's adaptive state
  GET  /api/quiz/health       — health check
"""

import json
import math
import os
import random
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from question_bank import QUESTIONS, TOPICS, get_question_by_id

# ──────────────────────────────────────────────
#  App Setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="TrackForcePro Adaptive Quiz API",
    version="1.0.0",
    description="Spaced-repetition powered quiz engine for TrackForcePro",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
#  Data Storage (file-based for simplicity)
# ──────────────────────────────────────────────
DATA_DIR = Path(os.environ.get("TFP_DATA_DIR", Path(__file__).parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_FILE = DATA_DIR / "player_profiles.json"


def _load_profiles() -> dict:
    if PROFILES_FILE.exists():
        try:
            return json.loads(PROFILES_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_profiles(profiles: dict):
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2))


# ──────────────────────────────────────────────
#  XP & Level System
# ──────────────────────────────────────────────
XP_PER_CORRECT = {1: 10, 2: 20, 3: 35}  # by difficulty
XP_STREAK_BONUS = 5  # extra XP per streak count
XP_SPEED_BONUS = 15  # bonus for answering fast (< 5s)


def xp_for_level(level: int) -> int:
    """XP needed to reach a given level (exponential curve)."""
    return int(100 * (level ** 1.5))


def level_from_xp(total_xp: int) -> int:
    """Calculate level from total XP."""
    level = 1
    while xp_for_level(level + 1) <= total_xp:
        level += 1
    return level


# ──────────────────────────────────────────────
#  Spaced Repetition Engine
# ──────────────────────────────────────────────
# Each question has a "memory strength" per player:
#   - correct answers increase interval (2x)
#   - wrong answers reset interval to minimum
# Items due for review (interval elapsed) are prioritized.

DEFAULT_INTERVAL = 60  # seconds — first review after 1 minute
MAX_INTERVAL = 86400 * 7  # cap at 7 days


def _get_or_create_profile(player_id: str) -> dict:
    profiles = _load_profiles()
    if player_id not in profiles:
        profiles[player_id] = {
            "player_id": player_id,
            "total_xp": 0,
            "level": 1,
            "total_correct": 0,
            "total_answered": 0,
            "current_streak": 0,
            "best_streak": 0,
            "topic_stats": {},      # topic -> {correct, total, last_accuracy}
            "question_memory": {},   # question_id -> {interval, next_due, ease, times_correct, times_wrong}
            "session_asked": [],     # question IDs asked in current session
            "last_difficulty": 1,
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        _save_profiles(profiles)
    return profiles[player_id]


def _save_profile(profile: dict):
    profiles = _load_profiles()
    profiles[profile["player_id"]] = profile
    _save_profiles(profiles)


def _calculate_adaptive_difficulty(profile: dict) -> int:
    """Determine difficulty based on rolling accuracy."""
    total = profile.get("total_answered", 0)
    if total < 5:
        return 1  # Start easy

    correct = profile.get("total_correct", 0)
    accuracy = correct / total if total > 0 else 0

    if accuracy >= 0.85:
        return 3  # Hard
    elif accuracy >= 0.65:
        return 2  # Medium
    else:
        return 1  # Easy


def _get_weakest_topics(profile: dict, n: int = 3) -> list[str]:
    """Get the N topics with lowest accuracy."""
    topic_stats = profile.get("topic_stats", {})
    if not topic_stats:
        return list(TOPICS.keys())[:n]

    scored = []
    for topic, stats in topic_stats.items():
        total = stats.get("total", 0)
        if total == 0:
            scored.append((topic, 0.0))  # Never attempted = weakest
        else:
            accuracy = stats.get("correct", 0) / total
            scored.append((topic, accuracy))

    # Also add topics never attempted
    for topic in TOPICS:
        if topic not in topic_stats:
            scored.append((topic, -1.0))  # Never seen = highest priority

    scored.sort(key=lambda x: x[1])
    return [t[0] for t in scored[:n]]


def _select_next_question(
    profile: dict,
    mode: Optional[str] = None,
    topic: Optional[str] = None,
) -> Optional[dict]:
    """
    Select the best next question using spaced repetition + weakness targeting.

    Priority:
    1. Questions that are DUE for review (spaced repetition)
    2. Questions from weak topics not yet asked this session
    3. Unseen questions at the adaptive difficulty
    4. Random fallback
    """
    now = time.time()
    session_asked = set(profile.get("session_asked", []))
    memory = profile.get("question_memory", {})
    adaptive_diff = _calculate_adaptive_difficulty(profile)
    weak_topics = _get_weakest_topics(profile)

    # Filter by mode/topic if specified
    pool = QUESTIONS
    if mode:
        pool = [q for q in pool if mode in q["mode"]]
    if topic:
        pool = [q for q in pool if q["topic"] == topic]

    # Exclude questions asked this session
    available = [q for q in pool if q["id"] not in session_asked]

    if not available:
        # Session exhausted — reset session and re-select
        profile["session_asked"] = []
        _save_profile(profile)
        available = pool

    if not available:
        return None

    # ── Priority 1: Due for review (spaced repetition) ──
    due_questions = []
    for q in available:
        mem = memory.get(q["id"])
        if mem and mem.get("next_due", 0) <= now and mem.get("times_wrong", 0) > 0:
            due_questions.append(q)

    if due_questions:
        # Pick the most overdue
        due_questions.sort(
            key=lambda q: memory.get(q["id"], {}).get("next_due", 0)
        )
        return due_questions[0]

    # ── Priority 2: Weak topic questions ──
    weak_pool = [q for q in available if q["topic"] in weak_topics]
    if weak_pool:
        # Prefer questions at adaptive difficulty
        diff_match = [q for q in weak_pool if q["difficulty"] == adaptive_diff]
        if diff_match:
            return random.choice(diff_match)
        return random.choice(weak_pool)

    # ── Priority 3: Unseen questions at adaptive difficulty ──
    unseen = [q for q in available if q["id"] not in memory]
    if unseen:
        diff_match = [q for q in unseen if q["difficulty"] == adaptive_diff]
        if diff_match:
            return random.choice(diff_match)
        return random.choice(unseen)

    # ── Priority 4: Random from available ──
    diff_match = [q for q in available if q["difficulty"] == adaptive_diff]
    if diff_match:
        return random.choice(diff_match)
    return random.choice(available)


# ──────────────────────────────────────────────
#  Pydantic Models
# ──────────────────────────────────────────────
class AnswerRequest(BaseModel):
    player_id: str
    question_id: str
    selected: int  # index of selected answer
    time_taken: float = 0  # seconds taken to answer


class AnswerResponse(BaseModel):
    correct: bool
    correct_answer: int
    explanation: str
    xp_earned: int
    streak: int
    total_xp: int
    level: int
    level_up: bool
    accuracy_pct: float
    weak_topics: list[str]


class NextQuestionResponse(BaseModel):
    id: str
    topic: str
    topic_label: str
    difficulty: int
    q: str
    opts: list[str]
    session_progress: int  # how many asked this session
    adaptive_difficulty: int
    player_level: int
    player_xp: int


class PlayerProfile(BaseModel):
    player_id: str
    total_xp: int
    level: int
    xp_to_next_level: int
    total_correct: int
    total_answered: int
    accuracy_pct: float
    current_streak: int
    best_streak: int
    topic_accuracies: dict  # topic -> accuracy%


# ──────────────────────────────────────────────
#  API Endpoints
# ──────────────────────────────────────────────
@app.get("/api/quiz/health")
def health_check():
    return {
        "status": "ok",
        "questions": len(QUESTIONS),
        "topics": len(TOPICS),
        "version": "1.0.0",
    }


@app.get("/api/quiz/topics")
def list_topics(player_id: Optional[str] = None):
    result = []
    profile = _get_or_create_profile(player_id) if player_id else None

    for key, label in TOPICS.items():
        count = len([q for q in QUESTIONS if q["topic"] == key])
        entry = {"topic": key, "label": label, "question_count": count}

        if profile:
            stats = profile.get("topic_stats", {}).get(key, {})
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            entry["accuracy_pct"] = round((correct / total) * 100, 1) if total > 0 else None
            entry["attempted"] = total
        result.append(entry)

    return {"topics": result}


@app.get("/api/quiz/next", response_model=NextQuestionResponse)
def get_next_question(
    player_id: str,
    mode: Optional[str] = Query(None, description="Filter by game mode"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
):
    profile = _get_or_create_profile(player_id)
    question = _select_next_question(profile, mode=mode, topic=topic)

    if not question:
        raise HTTPException(404, detail="No questions available for the given filters")

    # Track in session
    profile.setdefault("session_asked", []).append(question["id"])
    _save_profile(profile)

    return NextQuestionResponse(
        id=question["id"],
        topic=question["topic"],
        topic_label=TOPICS.get(question["topic"], question["topic"]),
        difficulty=question["difficulty"],
        q=question["q"],
        opts=question["opts"],
        session_progress=len(profile["session_asked"]),
        adaptive_difficulty=_calculate_adaptive_difficulty(profile),
        player_level=profile.get("level", 1),
        player_xp=profile.get("total_xp", 0),
    )


@app.post("/api/quiz/answer", response_model=AnswerResponse)
def submit_answer(req: AnswerRequest):
    question = get_question_by_id(req.question_id)
    if not question:
        raise HTTPException(404, detail=f"Question {req.question_id} not found")

    profile = _get_or_create_profile(req.player_id)
    now = time.time()
    is_correct = req.selected == question["answer"]

    # ── Update totals ──
    profile["total_answered"] = profile.get("total_answered", 0) + 1
    if is_correct:
        profile["total_correct"] = profile.get("total_correct", 0) + 1

    # ── Update streak ──
    if is_correct:
        profile["current_streak"] = profile.get("current_streak", 0) + 1
        if profile["current_streak"] > profile.get("best_streak", 0):
            profile["best_streak"] = profile["current_streak"]
    else:
        profile["current_streak"] = 0

    # ── Update topic stats ──
    topic = question["topic"]
    topic_stats = profile.setdefault("topic_stats", {})
    if topic not in topic_stats:
        topic_stats[topic] = {"correct": 0, "total": 0}
    topic_stats[topic]["total"] += 1
    if is_correct:
        topic_stats[topic]["correct"] += 1

    # ── Spaced repetition update ──
    memory = profile.setdefault("question_memory", {})
    qid = req.question_id
    if qid not in memory:
        memory[qid] = {
            "interval": DEFAULT_INTERVAL,
            "next_due": now + DEFAULT_INTERVAL,
            "ease": 2.5,
            "times_correct": 0,
            "times_wrong": 0,
        }

    mem = memory[qid]
    if is_correct:
        mem["times_correct"] += 1
        # Increase interval (SM-2 inspired)
        mem["ease"] = max(1.3, mem["ease"] + 0.1)
        mem["interval"] = min(mem["interval"] * mem["ease"], MAX_INTERVAL)
        mem["next_due"] = now + mem["interval"]
    else:
        mem["times_wrong"] += 1
        # Reset to short interval for review
        mem["ease"] = max(1.3, mem["ease"] - 0.2)
        mem["interval"] = DEFAULT_INTERVAL
        mem["next_due"] = now + DEFAULT_INTERVAL

    # ── Calculate XP ──
    xp_earned = 0
    if is_correct:
        diff = question["difficulty"]
        xp_earned = XP_PER_CORRECT.get(diff, 10)
        # Streak bonus
        streak = profile["current_streak"]
        if streak > 1:
            xp_earned += XP_STREAK_BONUS * min(streak, 10)
        # Speed bonus
        if req.time_taken > 0 and req.time_taken < 5:
            xp_earned += XP_SPEED_BONUS

    old_level = profile.get("level", 1)
    profile["total_xp"] = profile.get("total_xp", 0) + xp_earned
    new_level = level_from_xp(profile["total_xp"])
    profile["level"] = new_level
    profile["updated_at"] = now

    _save_profile(profile)

    # ── Build response ──
    total_answered = profile["total_answered"]
    total_correct = profile["total_correct"]
    accuracy = round((total_correct / total_answered) * 100, 1) if total_answered > 0 else 0

    return AnswerResponse(
        correct=is_correct,
        correct_answer=question["answer"],
        explanation=question["explanation"],
        xp_earned=xp_earned,
        streak=profile["current_streak"],
        total_xp=profile["total_xp"],
        level=new_level,
        level_up=new_level > old_level,
        accuracy_pct=accuracy,
        weak_topics=_get_weakest_topics(profile, n=3),
    )


@app.get("/api/quiz/profile/{player_id}", response_model=PlayerProfile)
def get_profile(player_id: str):
    profile = _get_or_create_profile(player_id)

    total = profile.get("total_answered", 0)
    correct = profile.get("total_correct", 0)
    level = profile.get("level", 1)
    total_xp = profile.get("total_xp", 0)

    topic_accuracies = {}
    for topic_key in TOPICS:
        stats = profile.get("topic_stats", {}).get(topic_key, {})
        t = stats.get("total", 0)
        c = stats.get("correct", 0)
        topic_accuracies[topic_key] = round((c / t) * 100, 1) if t > 0 else 0.0

    return PlayerProfile(
        player_id=player_id,
        total_xp=total_xp,
        level=level,
        xp_to_next_level=xp_for_level(level + 1) - total_xp,
        total_correct=correct,
        total_answered=total,
        accuracy_pct=round((correct / total) * 100, 1) if total > 0 else 0.0,
        current_streak=profile.get("current_streak", 0),
        best_streak=profile.get("best_streak", 0),
        topic_accuracies=topic_accuracies,
    )


@app.post("/api/quiz/reset/{player_id}")
def reset_profile(player_id: str):
    profiles = _load_profiles()
    if player_id in profiles:
        del profiles[player_id]
        _save_profiles(profiles)
    return {"ok": True, "message": f"Profile {player_id} reset"}


# ──────────────────────────────────────────────
#  Run
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
