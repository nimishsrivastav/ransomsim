"""
Scenario Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrganizationSize(str, Enum):
    """Organization size categories"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class DataSensitivity(str, Enum):
    """Data sensitivity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OrganizationProfile(BaseModel):
    """Organization profile for scenario generation"""
    size: OrganizationSize = Field(..., description="Organization size category")
    industry: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Industry sector (e.g., Healthcare, Finance, Manufacturing)"
    )
    data_sensitivity: DataSensitivity = Field(..., description="Sensitivity level of data handled")

    class Config:
        json_schema_extra = {
            "example": {
                "size": "medium",
                "industry": "Healthcare",
                "data_sensitivity": "critical"
            }
        }


class ScenarioCreate(BaseModel):
    """Request to generate a new ransomware scenario"""
    organization: OrganizationProfile = Field(..., description="Target organization profile")
    persona_type: str = Field(
        ...,
        pattern="^(professional|opportunist|script_kiddie)$",
        description="Threat actor type: professional (sophisticated), opportunist (money-focused), or script_kiddie (amateur)"
    )
    difficulty: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Difficulty level 1-10 (1=easy, 5=realistic, 10=expert)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "organization": {
                    "size": "medium",
                    "industry": "Healthcare",
                    "data_sensitivity": "critical"
                },
                "persona_type": "professional",
                "difficulty": 7
            }
        }


class Scenario(BaseModel):
    """Generated scenario"""
    id: str
    organization: OrganizationProfile
    narrative: str
    entry_vector: str
    timeline: str
    systems_affected: List[str]
    data_at_risk: List[str]
    ransom_amount: float
    ransom_currency: str = "USD"
    deadline: datetime
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "scenario_abc123",
                "organization": {
                    "size": "medium",
                    "industry": "Healthcare",
                    "data_sensitivity": "critical"
                },
                "narrative": "On January 15, attackers gained access via...",
                "entry_vector": "Phishing email with malicious attachment",
                "timeline": "Discovery: Jan 20, Encryption: Jan 18",
                "systems_affected": ["EMR systems", "Patient databases", "Backup servers"],
                "data_at_risk": ["Patient records", "Medical histories", "Billing information"],
                "ransom_amount": 2500000,
                "ransom_currency": "USD",
                "deadline": "2026-02-10T12:00:00Z",
                "created_at": "2026-02-05T10:30:00Z"
            }
        }