# src/campaign/models.py
"""
Data models for the Fey Bargain Game
Think of these like Terraform resource definitions - structured, validated, and type-safe!
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class TrustLevel(Enum):
    """NPC relationship levels"""
    ENEMY = -5
    HOSTILE = -4
    UNFRIENDLY = -3
    NEUTRAL = -2
    INDIFFERENT = -1
    FRIENDLY = 1
    HELPFUL = 2
    ALLIED = 3
    DEVOTED = 4
    FANATICAL = 5


class MissionStatus(Enum):
    """Mission status tracking"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ON_HOLD = "on_hold"


class LocationType(Enum):
    """Types of locations in the campaign"""
    SETTLEMENT = "settlement"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    BUILDING = "building"
    REGION = "region"


@dataclass
class DiceRoll:
    """Represents a dice roll result"""
    dice_type: int
    num_dice: int
    modifier: int
    total: int
    rolls: List[int]
    advantage: bool = False
    disadvantage: bool = False


@dataclass
class Character:
    """Player character data model"""
    name: str
    level: int = 1
    hit_points: int = 8
    max_hit_points: int = 8
    armor_class: int = 10

    # Ability scores
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Character details
    race: str = ""
    character_class: str = ""
    background: str = ""
    alignment: str = ""

    # Skills (modifier values)
    skills: Dict[str, int] = field(default_factory=dict)

    # Equipment and inventory
    equipment: List[str] = field(default_factory=list)
    gold: int = 0

    # Character personality
    personality_traits: List[str] = field(default_factory=list)
    ideals: List[str] = field(default_factory=list)
    bonds: List[str] = field(default_factory=list)
    flaws: List[str] = field(default_factory=list)

    # Progression tracking
    experience_points: int = 0
    proficiency_bonus: int = 2

    def get_ability_modifier(self, ability_score: int) -> int:
        """Calculate ability modifier from score"""
        return (ability_score - 10) // 2

    def get_skill_modifier(self, skill_name: str) -> int:
        """Get total modifier for a skill"""
        return self.skills.get(skill_name, 0)


@dataclass
class NPC:
    """Non-player character model"""
    name: str
    role: str = ""
    location: str = ""
    relationship: TrustLevel = TrustLevel.NEUTRAL  # Use the enum
    capabilities: List[str] = field(default_factory=list)
    current_status: str = ""
    description: str = ""
    notes: str = ""

    # Trust tracking
    trust_points: int = 0
    faction_allegiance: str = ""

    # Add this compatibility property!
    @property
    def trust_level(self) -> int:
        """Compatibility property for trust_level access"""
        return self.trust_points

    def adjust_trust(self, points: int) -> None:
        """Adjust trust level with this NPC"""
        self.trust_points += points

        # Update relationship enum based on trust points
        if self.trust_points >= 20:
            self.relationship = TrustLevel.DEVOTED
        elif self.trust_points >= 15:
            self.relationship = TrustLevel.ALLIED
        elif self.trust_points >= 10:
            self.relationship = TrustLevel.HELPFUL
        elif self.trust_points >= 5:
            self.relationship = TrustLevel.FRIENDLY
        elif self.trust_points >= -5:
            self.relationship = TrustLevel.NEUTRAL
        elif self.trust_points >= -10:
            self.relationship = TrustLevel.UNFRIENDLY
        else:
            self.relationship = TrustLevel.HOSTILE


@dataclass
class Location:
    """Location data model"""
    name: str
    location_type: LocationType
    description: str = ""
    connections: List[str] = field(default_factory=list)
    npcs_present: List[str] = field(default_factory=list)
    items_available: List[str] = field(default_factory=list)
    services_available: List[str] = field(default_factory=list)
    danger_level: str = "safe"  # safe, low, medium, high, extreme
    notes: str = ""

    # Environmental details
    weather: str = ""
    lighting: str = ""
    atmosphere: str = ""


@dataclass
class Mission:
    """Mission/quest data model"""
    name: str
    status: MissionStatus = MissionStatus.NOT_STARTED
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    completed_objectives: List[str] = field(default_factory=list)
    rewards: List[str] = field(default_factory=list)

    # Mission metadata
    giver: str = ""  # NPC who gave the mission
    location: str = ""  # Where mission takes place
    deadline: Optional[str] = None
    priority: str = "medium"  # low, medium, high, urgent

    # Progress tracking
    progress_notes: List[str] = field(default_factory=list)
    related_npcs: List[str] = field(default_factory=list)
    related_locations: List[str] = field(default_factory=list)

    # Add this compatibility property!
    @property
    def title(self) -> str:
        """Compatibility property for title access"""
        return self.name

    def add_progress(self, note: str) -> None:
        """Add a progress note to the mission"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.progress_notes.append(f"[{timestamp}] {note}")

    def complete_objective(self, objective: str) -> bool:
        """Mark an objective as completed"""
        if objective in self.objectives and objective not in self.completed_objectives:
            self.completed_objectives.append(objective)
            return True
        return False

    @property
    def completion_percentage(self) -> float:
        """Calculate mission completion percentage"""
        if not self.objectives:
            return 0.0
        return (len(self.completed_objectives) / len(self.objectives)) * 100

@dataclass
class Faction:
    """Faction data model for tracking group relationships"""
    name: str
    relationship: TrustLevel = TrustLevel.NEUTRAL
    description: str = ""
    goals: List[str] = field(default_factory=list)
    members: List[str] = field(default_factory=list)  # NPC names
    territory: List[str] = field(default_factory=list)  # Location names
    resources: List[str] = field(default_factory=list)

    # Faction status
    power_level: str = "minor"  # minor, moderate, major, dominant
    activity_level: str = "active"  # dormant, active, aggressive

    def add_member(self, npc_name: str) -> None:
        """Add an NPC to this faction"""
        if npc_name not in self.members:
            self.members.append(npc_name)


@dataclass
class GameSession:
    """Represents a single game session"""
    session_id: str
    character: Character
    current_scene: str = ""
    current_location: str = ""
    session_start: datetime = field(default_factory=datetime.now)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    context_summary: str = ""

    # Session metadata
    campaign_data: Dict[str, Any] = field(default_factory=dict)
    ai_context: List[Dict[str, str]] = field(default_factory=list)

    def add_action(self, action: str, result: str = "") -> None:
        """Add an action taken during the session"""
        action_data = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result
        }
        self.actions_taken.append(action_data)

    def update_context(self, new_context: str) -> None:
        """Update the session context summary"""
        self.context_summary = new_context


@dataclass
class CampaignState:
    """Represents the overall state of a campaign"""
    campaign_name: str = ""
    current_session_id: Optional[str] = None
    total_sessions: int = 0
    active_character: Optional[str] = None
    current_location: str = ""
    campaign_status: str = "active"  # active, paused, completed
    last_session_date: Optional[str] = None
    total_playtime_minutes: int = 0

    # Campaign metadata
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"

    # Story progression
    major_events: List[str] = field(default_factory=list)
    completed_arcs: List[str] = field(default_factory=list)
    current_arc: str = ""

    def __post_init__(self):
        """Initialize derived fields"""
        if not self.campaign_name:
            self.campaign_name = "Fey Bargain Campaign"

    def update_last_session(self, session_id: str) -> None:
        """Update tracking for the most recent session"""
        self.current_session_id = session_id
        self.last_session_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        self.total_sessions += 1

    def add_major_event(self, event: str) -> None:
        """Add a major story event to the campaign"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        self.major_events.append(f"[{timestamp}] {event}")
        self.last_modified = datetime.now().isoformat()


@dataclass
class CampaignFile:
    """Represents a loaded campaign file"""
    filename: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_modified: datetime = field(default_factory=datetime.now)
    file_type: str = "markdown"

    def update_content(self, new_content: str) -> None:
        """Update file content and timestamp"""
        self.content = new_content
        self.last_modified = datetime.now()


@dataclass
class CharacterStats:
    """Character statistics parsed from character sheet"""
    name: str = ""
    level: int = 1
    hit_points: int = 8
    max_hit_points: int = 8
    armor_class: int = 10

    # Ability scores
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Character details
    race: str = ""
    character_class: str = ""
    background: str = ""
    alignment: str = ""

    # Skills and modifiers
    proficiency_bonus: int = 2
    skills: Dict[str, int] = field(default_factory=dict)

    # Resources
    spell_slots: Dict[str, int] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)

    # Experience and progression
    experience_points: int = 0

    def get_ability_modifier(self, score: int) -> int:
        """Calculate ability modifier from score"""
        return (score - 10) // 2

    def get_skill_modifier(self, skill_name: str) -> int:
        """Get total modifier for a skill"""
        base_modifier = self.skills.get(skill_name, 0)
        return base_modifier + self.proficiency_bonus

    def to_character(self) -> Character:
        """Convert CharacterStats to Character model"""
        return Character(
            name=self.name,
            level=self.level,
            hit_points=self.hit_points,
            max_hit_points=self.max_hit_points,
            armor_class=self.armor_class,
            strength=self.strength,
            dexterity=self.dexterity,
            constitution=self.constitution,
            intelligence=self.intelligence,
            wisdom=self.wisdom,
            charisma=self.charisma,
            race=self.race,
            character_class=self.character_class,
            background=self.background,
            alignment=self.alignment,
            skills=self.skills.copy(),
            equipment=self.equipment.copy(),
            experience_points=self.experience_points,
            proficiency_bonus=self.proficiency_bonus
        )

# Utility functions for working with models

def create_default_character() -> Character:
    """Create a default character for testing"""
    return Character(
        name="Test Hero",
        level=1,
        hit_points=10,
        max_hit_points=10,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )


def create_sample_npc(name: str, role: str) -> NPC:
    """Create a sample NPC for testing"""
    return NPC(
        name=name,
        role=role,
        relationship=TrustLevel.NEUTRAL,
        location="Starting Village"
    )


def create_sample_mission(name: str, description: str) -> Mission:
    """Create a sample mission for testing"""
    return Mission(
        name=name,
        description=description,
        status=MissionStatus.NOT_STARTED,
        objectives=["Investigate the issue", "Report back to quest giver"],
        priority="medium"
    )


# Export all models for easy importing
__all__ = [
    'TrustLevel', 'MissionStatus', 'LocationType',
    'DiceRoll', 'Character', 'CharacterStats', 'NPC', 'Location', 'Mission', 'Faction',
    'GameSession', 'CampaignState', 'CampaignFile',
    'create_default_character', 'create_sample_npc', 'create_sample_mission'
]