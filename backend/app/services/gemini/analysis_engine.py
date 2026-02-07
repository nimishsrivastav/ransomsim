"""
Analysis Engine - Generates post-negotiation feedback
"""
from typing import List, Dict, Optional
import logging
from datetime import datetime
import json

from app.services.gemini.client import get_gemini_service
from app.models.schemas.negotiation import Message
from app.models.schemas.analysis import (
    Analysis,
    TacticalInsight,
    Mistake,
    Success,
    Recommendation,
    BenchmarkData,
)
from app.prompts.analysis_prompts import ANALYSIS_PROMPT_TEMPLATE
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """Generates comprehensive negotiation analysis"""
    
    def __init__(self):
        self.gemini_service = get_gemini_service()
        self.analyses_cache: Dict[str, Analysis] = {}
    
    async def analyze_negotiation(
        self,
        session_id: str,
        messages: List[Message],
        session_metadata: Dict,
    ) -> Analysis:
        """
        Analyze completed negotiation
        
        Args:
            session_id: Session identifier
            messages: Full conversation history
            session_metadata: Session metadata (outcome, timing, etc.)
            
        Returns:
            Comprehensive analysis
        """
        try:
            logger.info(f"Analyzing negotiation for session {session_id}")
            
            # Build conversation transcript
            transcript = self._build_transcript(messages)
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(
                transcript=transcript,
                metadata=session_metadata,
            )
            
            # Generate analysis
            analysis_data = await self.gemini_service.generate_structured_content(
                prompt=prompt,
                response_schema=self._get_analysis_schema(),
                temperature=0.7,
            )
            
            # Parse and create analysis object
            analysis = self._parse_analysis(
                session_id=session_id,
                analysis_data=analysis_data,
                messages=messages,
                metadata=session_metadata,
            )
            
            # Cache analysis
            self.analyses_cache[session_id] = analysis
            
            logger.info(f"Analysis completed for session {session_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing negotiation: {e}")
            raise GeminiAPIError(f"Analysis failed: {str(e)}")
    
    async def get_analysis(self, session_id: str) -> Optional[Analysis]:
        """Get cached analysis"""
        return self.analyses_cache.get(session_id)
    
    def _build_transcript(self, messages: List[Message]) -> str:
        """Build formatted transcript"""
        transcript = "NEGOTIATION TRANSCRIPT:\n"
        transcript += "=" * 80 + "\n\n"
        
        for i, msg in enumerate(messages, 1):
            sender = "VICTIM" if msg.sender == "user" else "THREAT ACTOR"
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            transcript += f"[{i}] {sender} ({timestamp}):\n"
            transcript += f"{msg.content}\n\n"
        
        transcript += "=" * 80 + "\n"
        return transcript
    
    def _build_analysis_prompt(
        self,
        transcript: str,
        metadata: Dict,
    ) -> str:
        """Build analysis generation prompt"""
        
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            transcript=transcript,
            total_messages=metadata.get('total_messages', 0),
            duration_minutes=metadata.get('duration_minutes', 0),
            outcome=metadata.get('outcome', 'Unknown'),
        )
        
        return prompt
    
    def _get_analysis_schema(self) -> Dict:
        """Get expected analysis schema"""
        return {
            "performance_score": "number (0-10)",
            "outcome_summary": "string",
            "key_mistakes": [
                {
                    "description": "string",
                    "severity": "low/medium/high",
                    "consequence": "string",
                    "better_approach": "string",
                }
            ],
            "successful_tactics": [
                {
                    "description": "string",
                    "impact": "string",
                }
            ],
            "tactical_insights": [
                {
                    "message_number": "number",
                    "insight_type": "mistake/success/opportunity",
                    "analysis": "string",
                    "improvement": "string (optional)",
                }
            ],
            "recommendations": [
                {
                    "skill": "string",
                    "description": "string",
                    "priority": "low/medium/high",
                }
            ],
            "benchmark_comparison": {
                "estimated_avg_payment_percent": "number",
                "estimated_avg_time_minutes": "number",
            },
        }
    
    def _parse_analysis(
        self,
        session_id: str,
        analysis_data: Dict,
        messages: List[Message],
        metadata: Dict,
    ) -> Analysis:
        """Parse analysis data into Analysis object"""
        
        # Parse mistakes
        mistakes = [
            Mistake(
                description=m["description"],
                severity=m["severity"],
                consequence=m["consequence"],
                better_approach=m["better_approach"],
            )
            for m in analysis_data.get("key_mistakes", [])
        ]
        
        # Parse successes
        successes = [
            Success(
                description=s["description"],
                impact=s["impact"],
                message_ref=f"Message {i+1}",
            )
            for i, s in enumerate(analysis_data.get("successful_tactics", []))
        ]
        
        # Parse tactical insights
        tactical_breakdown = [
            TacticalInsight(
                id=f"insight_{i}",
                message_ref=f"Message {t.get('message_number', i+1)}",
                insight_type=t["insight_type"],
                analysis=t["analysis"],
                improvement=t.get("improvement"),
            )
            for i, t in enumerate(analysis_data.get("tactical_insights", []))
        ]
        
        # Parse recommendations
        recommendations = [
            Recommendation(
                skill=r["skill"],
                description=r["description"],
                priority=r["priority"],
            )
            for r in analysis_data.get("recommendations", [])
        ]
        
        # Create benchmark data (simplified for MVP)
        benchmark_data = analysis_data.get("benchmark_comparison", {})
        benchmarks = BenchmarkData(
            user_payment=metadata.get('final_payment', 0),
            avg_payment=metadata.get('initial_ransom', 0) * 
                       benchmark_data.get('estimated_avg_payment_percent', 70) / 100,
            user_time=metadata.get('duration_minutes', 0),
            avg_time=benchmark_data.get('estimated_avg_time_minutes', 45),
            user_concessions=metadata.get('concessions_made', 0),
            avg_concessions=3,
        )
        
        # Create analysis
        analysis = Analysis(
            session_id=session_id,
            performance_score=float(analysis_data.get("performance_score", 5.0)),
            outcome=analysis_data.get("outcome_summary", "Negotiation completed"),
            time_to_resolution=metadata.get('duration_minutes', 0),
            message_count=len(messages),
            concessions_made=metadata.get('concessions_made', 0),
            tactical_breakdown=tactical_breakdown,
            mistakes=mistakes,
            successes=successes,
            recommendations=recommendations,
            benchmarks=benchmarks,
            generated_at=datetime.now(),
        )
        
        return analysis


def get_analysis_engine() -> AnalysisEngine:
    """Get analysis engine instance"""
    return AnalysisEngine()