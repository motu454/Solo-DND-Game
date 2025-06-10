# src/ai/claude_integration.py
import os
import asyncio
from typing import Dict, Any, List, Optional
from anthropic import Anthropic


class ClaudeAI:
    """Claude AI client for DM responses"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)

        # Load core DM instructions as system prompt
        self.system_prompt = self._load_dm_instructions()

    def _load_dm_instructions(self) -> str:
        """Load core DM instructions from your framework files"""
        base_instructions = """
        You are Claude, an expert D&D Dungeon Master running The Fey Bargain campaign.

        CORE PRINCIPLES:
        - ALWAYS reference current campaign files before responding
        - NEVER control character actions - describe results and options, not decisions  
        - ALWAYS provide multiple action options including environmental interactions
        - ALWAYS require skill checks for supernatural insight, NPC motivations, and hidden information

        RESPONSE STRUCTURE:
        1. Environmental Setup (multi-sensory, concise)
        2. NPC Reactions (behavioral cues requiring skill checks for deeper insight)
        3. Action Options (combat, social, environmental, creative) 
        4. Skill Check Opportunities (never reveal DCs)

        Use your skill-check-system.md for DC guidelines:
        - Trivial: 8 | Easy: 10 | Moderate: 13 | Hard: 16 | Very Hard: 19 | Nearly Impossible: 22+

        CHARACTER CONTEXT:
        - Motu of House Grant: Level 3 Tiefling Warlock
        - Current Status: Enhanced Summer Court alliance, regional political authority
        - Immediate Context: Preparations complete for tomorrow's Starfall Manor gathering
        - Stakes: Transformation from regional authority to supernatural-backed dominance

        Be engaging, follow established campaign tone, and maintain consistency with the 24-file system.
        Never break character or mention being an AI.
        """
        return base_instructions.strip()

    async def get_dm_response(self,
                              campaign_context: Dict[str, Any],
                              player_input: str,
                              scene_type: str = "general") -> str:
        """Get DM response from Claude"""

        try:
            # Build context message
            context_msg = self._build_context_message(campaign_context, scene_type)

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.7,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"{context_msg}\n\nPlayer Action: {player_input}"
                    }
                ]
            )

            return message.content[0].text

        except Exception as e:
            return f"🎲 DM Error: {str(e)}\nTry a different action or check your API key."

    def _build_context_message(self, campaign_context: Dict[str, Any], scene_type: str) -> str:
        """Build context message from campaign state"""

        character = campaign_context.get('character', {})
        immediate_context = campaign_context.get('immediate_context', '')
        key_npcs = campaign_context.get('key_npcs', [])
        current_location = campaign_context.get('current_location', 'Unknown')

        context_parts = [
            f"SCENE TYPE: {scene_type}",
            f"CURRENT LOCATION: {current_location}",
            f"IMMEDIATE CONTEXT: {immediate_context}",
            "",
            "CHARACTER STATUS:",
            f"- Level {character.get('level', 3)} Tiefling Warlock",
            f"- HP: {character.get('hit_points', 27)}/{character.get('max_hit_points', 27)}",
            f"- Wealth: {character.get('wealth', {}).get('gold', 448)}g available",
            f"- Location: {character.get('current_location', 'Personal chambers, Westmarch')}",
            "",
            "KEY ACTIVE NPCS:",
        ]

        # Add relevant NPCs for the scene
        for npc in key_npcs[:5]:  # Limit to most relevant
            trust_stars = "⭐" * max(0, npc.get('trust_level', 0))
            context_parts.append(
                f"- {npc.get('name', 'Unknown')} {trust_stars}: {npc.get('current_status', 'Unknown')}")

        return "\n".join(context_parts)


# src/ai/context_builder.py
from typing import Dict, Any, List
from ..campaign.models import CampaignState, NPC


class ContextBuilder:
    """Builds context for Claude based on current campaign state and scene type"""

    def __init__(self, campaign_state: CampaignState):
        self.campaign_state = campaign_state

    def build_context(self, scene_type: str = "general", relevant_npcs: List[str] = None) -> Dict[str, Any]:
        """Build context dictionary for Claude"""

        # Get relevant NPCs for this scene
        if relevant_npcs:
            key_npcs = [npc for npc in self.campaign_state.npcs if npc.name in relevant_npcs]
        else:
            # Default to highest trust level NPCs
            key_npcs = sorted(self.campaign_state.npcs, key=lambda x: x.relationship.value, reverse=True)[:5]

        context = {
            'scene_type': scene_type,
            'character': {
                'level': self.campaign_state.character.level,
                'hit_points': self.campaign_state.character.hit_points,
                'max_hit_points': self.campaign_state.character.max_hit_points,
                'wealth': self.campaign_state.character.wealth,
                'current_location': self.campaign_state.character.current_location,
                'active_effects': self.campaign_state.character.active_effects
            },
            'immediate_context': self.campaign_state.immediate_context,
            'next_major_event': self.campaign_state.next_major_event,
            'strategic_position': self.campaign_state.strategic_position,
            'current_location': self.campaign_state.character.current_location,
            'key_npcs': [
                {
                    'name': npc.name,
                    'role': npc.role,
                    'trust_level': npc.relationship.value,
                    'current_status': npc.current_status,
                    'capabilities': npc.capabilities[:3]  # Limit for context size
                }
                for npc in key_npcs
            ]
        }

        return context

    def build_combat_context(self, enemies: List[str] = None, environment: str = None) -> Dict[str, Any]:
        """Build specific context for combat scenarios"""
        base_context = self.build_context("combat")

        base_context.update({
            'combat_info': {
                'enemies': enemies or [],
                'environment': environment or "Unknown battlefield",
                'character_ac': self.campaign_state.character.armor_class,
                'character_speed': self.campaign_state.character.speed,
                'available_spells': self.campaign_state.character.spell_slots,
                'equipment': self.campaign_state.character.equipment[:5]  # Limit for context
            }
        })

        return base_context

    def build_social_context(self, npcs_present: List[str] = None, social_goal: str = None) -> Dict[str, Any]:
        """Build specific context for social encounters"""
        base_context = self.build_context("social", npcs_present)

        base_context.update({
            'social_info': {
                'goal': social_goal or "General interaction",
                'charisma_modifier': 9,  # Summer Court enhanced
                'social_skills': {
                    'Persuasion': 9,
                    'Deception': 9,
                    'Intimidation': 9,
                    'Performance': 9
                },
                'political_authority': "Emergency council powers, enhanced security contracts"
            }
        })

        return base_context