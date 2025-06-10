# src/campaign/models.py
"""
Enhanced Game Models with Session Support
Data structures for campaign management - think Terraform resource definitions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class TrustLevel(Enum):
    """NPC trust levels (like security group rules - from hostile to trusted)"""
    ENEMY = -5
    HOSTILE = -4
    UNFRIENDLY = -3
    NEUTRAL = -2
    CAUTIOUS = -1
    UNKNOWN = 0
    FRIENDLY = 1
    HELPFUL = 2
    ALLIED = 3
    TRUSTED = 4
    FAMILY = 5


class SessionState(Enum):
    """Session lifecycle states"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Character:
    """Player character data model"""
    name: str
    level: int = 1
    hit_points: int = 10
    max_hit_points: int = 10
    armor_class: int = 10
    
    # Core stats
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # Skills and abilities
    skills: Dict[str, int] = field(default_factory=dict)
    equipment: List[str] = field(default_factory=list)
    spells: List[str] = field(default_factory=list)
    
    # Character progression
    experience: int = 0
    proficiency_bonus: int = 2
    
    # Current state
    conditions: List[str] = field(default_factory=list)  # poisoned, exhausted, etc.
    temporary_hp: int = 0
    spell_slots: Dict[str, int] = field(default_factory=dict)
    
    def get_modifier(self, ability_score: int) -> int:
        """Calculate ability modifier from score"""
        return (ability_score - 10) // 2
    
    def get_skill_modifier(self, skill_name: str) -> int:
        """Get total modifier for a skill check"""
        base_modifier = self.skills.get(skill_name, 0)
        
        # Add ability modifier based on skill type
        skill_abilities = {
            'acrobatics': self.dexterity,
            'athletics': self.strength,
            'deception': self.charisma,
            'history': self.intelligence,
            'insight': self.wisdom,
            'intimidation': self.charisma,
            'investigation': self.intelligence,
            'perception': self.wisdom,
            'persuasion': self.charisma,
            'stealth': self.dexterity,
            # Add more as needed
        }
        
        ability_score = skill_abilities.get(skill_name.lower(), 10)
        ability_modifier = self.get_modifier(ability_score)
        
        return base_modifier + ability_modifier
    
    def take_damage(self, damage: int):
        """Apply damage to character"""
        if self.temporary_hp > 0:
            if damage <= self.temporary_hp:
                self.temporary_hp -= damage
                return
            else:
                damage -= self.temporary_hp
                self.temporary_hp = 0
        
        self.hit_points = max(0, self.hit_points - damage)
    
    def heal(self, healing: int):
        """Heal character damage"""
        self.hit_points = min(self.max_hit_points, self.hit_points + healing)
    
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.hit_points > 0
    
    def is_unconscious(self) -> bool:
        """Check if character is unconscious"""
        return self.hit_points <= 0

@dataclass
class CharacterStats:
    """Basic character statistics for file parsing"""
    level: int = 1
    hit_points: int = 10
    max_hit_points: int = 10
    armor_class: int = 10

@dataclass 
class NPC:
    """Non-player character model"""
    name: str
    role: str = ""
    location: str = ""
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    relationship: str = ""
    capabilities: str = ""
    current_status: str = ""
    background: str = ""
    
    # Relationship tracking
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    last_interaction: Optional[datetime] = None
    disposition_changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Game mechanics
    armor_class: int = 10
    hit_points: int = 10
    challenge_rating: float = 0.0
    
    def add_interaction(self, interaction_type: str, description: str, trust_change: int = 0):
        """Record an interaction with this NPC"""
        interaction = {
            'timestamp': datetime.now(),
            'type': interaction_type,
            'description': description,
            'trust_change': trust_change
        }
        
        self.interactions.append(interaction)
        self.last_interaction = datetime.now()
        
        # Apply trust level change
        if trust_change != 0:
            old_level = self.trust_level.value
            new_level = max(-5, min(5, old_level + trust_change))
            self.trust_level = TrustLevel(new_level)
            
            self.disposition_changes.append({
                'timestamp': datetime.now(),
                'old_level': old_level,
                'new_level': new_level,
                'reason': description
            })


@dataclass
class Location:
    """Location/area model"""
    name: str
    description: str = ""
    region: str = ""
    location_type: str = ""  # city, dungeon, wilderness, etc.
    
    # Connections
    connected_locations: List[str] = field(default_factory=list)
    travel_times: Dict[str, str] = field(default_factory=dict)
    
    # NPCs and features
    npcs_present: List[str] = field(default_factory=list)
    notable_features: List[str] = field(default_factory=list)
    available_services: List[str] = field(default_factory=list)
    
    # Environmental factors
    weather: str = ""
    danger_level: str = "safe"  # safe, caution, dangerous, deadly
    special_rules: List[str] = field(default_factory=list)
    
    # Visit tracking
    times_visited: int = 0
    last_visit: Optional[datetime] = None
    discoveries: List[Dict[str, Any]] = field(default_factory=list)
    
    def visit(self):
        """Record a visit to this location"""
        self.times_visited += 1
        self.last_visit = datetime.now()


@dataclass
class Mission:
    """Quest/mission model"""
    title: str
    description: str
    mission_type: str = "main"  # main, side, personal, faction
    status: str = "active"  # active, completed, failed, abandoned
    
    # Mission details
    objectives: List[str] = field(default_factory=list)
    completed_objectives: List[str] = field(default_factory=list)
    rewards: List[str] = field(default_factory=list)
    
    # Tracking
    giver: str = ""
    location: str = ""
    deadline: Optional[datetime] = None
    priority: str = "normal"  # low, normal, high, urgent
    
    # Progress tracking
    progress_notes: List[Dict[str, Any]] = field(default_factory=list)
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    def add_progress(self, note: str, objective_completed: str = None):
        """Add progress note to mission"""
        progress = {
            'timestamp': datetime.now(),
            'note': note,
            'objective_completed': objective_completed
        }
        
        self.progress_notes.append(progress)
        
        if objective_completed and objective_completed not in self.completed_objectives:
            self.completed_objectives.append(objective_completed)
    
    def is_completed(self) -> bool:
        """Check if all objectives are completed"""
        return len(self.completed_objectives) >= len(self.objectives)
    
    def completion_percentage(self) -> float:
        """Get completion percentage"""
        if not self.objectives:
            return 0.0
        return len(self.completed_objectives) / len(self.objectives) * 100


@dataclass
class GameSession:
    """Complete game session state"""
    session_id: str
    character: Character
    current_scene: str = ""
    current_location: str = ""
    
    # Session metadata
    session_start: datetime = field(default_factory=datetime.now)
    session_end: Optional[datetime] = None
    state: SessionState = SessionState.ACTIVE
    
    # Game state
    active_npcs: List[str] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    context_summary: str = ""
    
    # Campaign data reference
    campaign_data: Dict[str, Any] = field(default_factory=dict)
    
    # Session statistics
    dice_rolls: List[Dict[str, Any]] = field(default_factory=list)
    scenes_played: int = 0
    experience_gained: int = 0
    
    def add_action(self, action: str, result: str = None):
        """Record a player action"""
        action_record = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'result': result,
            'scene_number': self.scenes_played
        }
        
        self.actions_taken.append(action_record)
    
    def add_dice_roll(self, dice_type: int, count: int, modifier: int, total: int, purpose: str = None):
        """Record a dice roll"""
        roll_record = {
            'timestamp': datetime.now().isoformat(),
            'dice_type': dice_type,
            'count': count,
            'modifier': modifier,
            'total': total,
            'purpose': purpose
        }
        
        self.dice_rolls.append(roll_record)
    
    def end_session(self):
        """Mark session as completed"""
        self.session_end = datetime.now()
        self.state = SessionState.COMPLETED
    
    def get_duration(self) -> float:
        """Get session duration in hours"""
        end_time = self.session_end or datetime.now()
        duration = end_time - self.session_start
        return duration.total_seconds() / 3600


@dataclass
class CampaignFile:
    """Represents a loaded campaign file"""
    filename: str
    content: str
    last_modified: datetime
    parsed_data: Optional[Any] = None
    file_type: str = "markdown"
    
    def get_size(self) -> int:
        """Get file content size"""
        return len(self.content)
    
    def get_word_count(self) -> int:
        """Get approximate word count"""
        return len(self.content.split())


@dataclass
class CampaignState:
    """Represents the overall state of a campaign"""
    campaign_name: str = ""
    current_session_id: Optional[str] = None
    total_sessions: int = 0
    campaign_start_date: Optional[datetime] = None
    last_played: Optional[datetime] = None

    # Campaign progress
    current_chapter: str = ""
    major_events: List[str] = field(default_factory=list)
    completed_missions: List[str] = field(default_factory=list)

    # World state
    current_location: str = ""
    active_npcs: List[str] = field(default_factory=list)
    faction_standings: Dict[str, int] = field(default_factory=dict)

    # Statistics
    total_playtime_hours: float = 0.0
    dice_rolls_made: int = 0
    scenes_played: int = 0

@dataclass
class DiceRoll:
    """Represents a dice roll result"""
    dice_type: int  # 4, 6, 8, 10, 12, 20, 100
    count: int
    modifier: int = 0
    advantage: bool = False
    disadvantage: bool = False
    
    # Results
    individual_rolls: List[int] = field(default_factory=list)
    total: int = 0
    is_critical: bool = False
    is_fumble: bool = False
    
    def __post_init__(self):
        """Calculate roll results"""
        import random
        
        if self.advantage or self.disadvantage:
            # Roll twice for advantage/disadvantage
            roll1 = [random.randint(1, self.dice_type) for _ in range(self.count)]
            roll2 = [random.randint(1, self.dice_type) for _ in range(self.count)]
            
            if self.advantage:
                self.individual_rolls = [max(r1, r2) for r1, r2 in zip(roll1, roll2)]
            else:
                self.individual_rolls = [min(r1, r2) for r1, r2 in zip(roll1, roll2)]
        else:
            self.individual_rolls = [random.randint(1, self.dice_type) for _ in range(self.count)]
        
        # Calculate total
        self.total = sum(self.individual_rolls) + self.modifier
        
        # Check for critical/fumble (only on d20)
        if self.dice_type == 20 and self.count == 1:
            natural_roll = self.individual_rolls[0]
            self.is_critical = natural_roll == 20
            self.is_fumble = natural_roll == 1
    
    def __str__(self) -> str:
        """String representation of the roll"""
        dice_notation = f"{self.count}d{self.dice_type}"
        if self.modifier > 0:
            dice_notation += f"+{self.modifier}"
        elif self.modifier < 0:
            dice_notation += f"{self.modifier}"
        
        result_parts = [f"Rolled {dice_notation}: {self.total}"]
        
        if len(self.individual_rolls) > 1:
            result_parts.append(f"({'+'.join(map(str, self.individual_rolls))})")
        
        if self.is_critical:
            result_parts.append("CRITICAL!")
        elif self.is_fumble:
            result_parts.append("FUMBLE!")
        
        if self.advantage:
            result_parts.append("(Advantage)")
        elif self.disadvantage:
            result_parts.append("(Disadvantage)")
        
        return " ".join(result_parts)