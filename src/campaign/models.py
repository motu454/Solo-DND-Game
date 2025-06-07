"""
Data models for The Fey Bargain campaign system
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
from pathlib import Path


class TrustLevel(Enum):
    """NPC trust levels matching your campaign system"""
    MAX_ALLIANCE = 5  # ⭐⭐⭐⭐⭐
    STRONG_ALLIANCE = 4  # ⭐⭐⭐⭐
    MODERATE_ALLIANCE = 3  # ⭐⭐⭐
    BASIC_ALLIANCE = 2  # ⭐⭐
    NEUTRAL = 1  # ⭐
    UNFRIENDLY = -1
    HOSTILE = -2
    ENEMY = -3
    COMPROMISED = -4  # Like Councilor Blackwood
    PRIMARY_THREAT = -5


class NPC(BaseModel):
    """NPC data model matching your directory structure"""
    name: str
    role: str
    relationship: str  # We'll parse the star rating later
    trust_level: Optional[int] = None
    capabilities: List[str] = Field(default_factory=list)
    current_status: str = ""
    intelligence_value: str = ""
    notes: str = ""


class Location(BaseModel):
    """Location data model"""
    name: str
    type: str = ""
    control_level: str = ""
    overview: str = ""
    key_features: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)


class Mission(BaseModel):
    """Mission/objective tracking"""
    title: str
    status: str = ""
    priority: int = 1
    deadline: Optional[str] = None
    objectives: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)


class CharacterStats(BaseModel):
    """Character sheet data"""
    name: str = "Motu of House Grant"
    level: int = 3
    hit_points: int = 27
    max_hit_points: int = 27
    armor_class: int = 13
    abilities: Dict[str, int] = Field(default_factory=dict)
    skills: Dict[str, int] = Field(default_factory=dict)
    equipment: List[str] = Field(default_factory=list)
    wealth: Dict[str, int] = Field(default_factory=dict)


class CampaignFile(BaseModel):
    """Represents a single campaign file"""
    filename: str
    content: str
    parsed_data: Optional[Any] = None
    last_modified: Optional[datetime] = None
    file_type: str = "markdown"