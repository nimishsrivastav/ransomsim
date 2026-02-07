"""
Analysis Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TacticalInsight(BaseModel):
    """Single tactical insight"""
    id: str
    message_ref: str
    insight_type: str  # 'mistake', 'success', 'opportunity'
    analysis: str
    improvement: Optional[str] = None


class Mistake(BaseModel):
    """Negotiation mistake"""
    description: str
    severity: str  # 'low', 'medium', 'high'
    consequence: str
    better_approach: str


class Success(BaseModel):
    """Successful tactic"""
    description: str
    impact: str
    message_ref: str


class Recommendation(BaseModel):
    """Learning recommendation"""
    skill: str
    description: str
    priority: str  # 'low', 'medium', 'high'


class BenchmarkData(BaseModel):
    """Benchmark comparison data"""
    user_payment: float
    avg_payment: float
    user_time: int  # minutes
    avg_time: int
    user_concessions: int
    avg_concessions: int


class Analysis(BaseModel):
    """Complete negotiation analysis"""
    session_id: str
    performance_score: float = Field(..., ge=0, le=10)
    outcome: str
    time_to_resolution: int  # minutes
    message_count: int
    concessions_made: int
    tactical_breakdown: List[TacticalInsight]
    mistakes: List[Mistake]
    successes: List[Success]
    recommendations: List[Recommendation]
    benchmarks: BenchmarkData
    generated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_xyz789",
                "performance_score": 6.5,
                "outcome": "Negotiated to 60% of initial demand",
                "time_to_resolution": 23,
                "message_count": 15,
                "concessions_made": 3,
                "tactical_breakdown": [],
                "mistakes": [],
                "successes": [],
                "recommendations": [],
                "benchmarks": {
                    "user_payment": 1500000,
                    "avg_payment": 1800000,
                    "user_time": 23,
                    "avg_time": 35,
                    "user_concessions": 3,
                    "avg_concessions": 4
                },
                "generated_at": "2026-02-05T11:00:00Z"
            }
        }