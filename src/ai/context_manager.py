"""
Context Manager - Builds game context for Claude
"""
from typing import Dict, Any, List, Optional
from src.campaign.file_manager import CampaignFileManager
from src.campaign.models import NPC, Mission


class GameContextManager:
    """Manages game context for AI interactions"""

    def __init__(self, file_manager: CampaignFileManager):
        self.file_manager = file_manager

    def build_context(self, scenario_type: str = "general") -> Dict[str, Any]:
        """Build context dictionary for Claude"""

        context = {
            'scenario_type': scenario_type,
            'character': self._get_character_context(),
            'quick_reference': self._get_quick_reference_context(),
            'missions': self._get_active_missions(),
            'recent_npcs': self._get_relevant_npcs()
        }

        # Add scenario-specific context
        if scenario_type == "combat":
            context.update(self._get_combat_context())
        elif scenario_type == "social":
            context.update(self._get_social_context())

        return context

    def _get_character_context(self) -> Optional[Any]:
        """Get current character stats"""
        return self.file_manager.get_character_stats()

    def _get_quick_reference_context(self) -> Dict[str, Any]:
        """Get quick reference data"""
        qr_file = self.file_manager.get_file('quick_reference')
        if qr_file and qr_file.parsed_data:
            return qr_file.parsed_data
        return {}

    def _get_active_missions(self) -> List[Mission]:
        """Get current active missions"""
        mission_file = self.file_manager.get_file('active_missions')
        if mission_file and mission_file.parsed_data:
            return mission_file.parsed_data
        return []

    def _get_relevant_npcs(self, limit: int = 10) -> List[NPC]:
        """Get most relevant NPCs (highest trust levels)"""
        npcs = self.file_manager.get_npcs()
        # Sort by trust level, highest first
        sorted_npcs = sorted(npcs, key=lambda x: x.trust_level or 0, reverse=True)
        return sorted_npcs[:limit]

    def _get_combat_context(self) -> Dict[str, Any]:
        """Additional context for combat scenarios"""
        return {
            'combat_focus': True,
            'environmental_emphasis': True
        }

    def _get_social_context(self) -> Dict[str, Any]:
        """Additional context for social scenarios"""
        return {
            'social_focus': True,
            'npc_knowledge_limits': True
        }