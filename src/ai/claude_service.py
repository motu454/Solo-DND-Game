"""
Claude AI Service - Handles all Claude API interactions
"""
import os
from typing import Dict, Any, List, Optional
import anthropic
from anthropic import APIError
from dotenv import load_dotenv

load_dotenv()


class ClaudeService:
    """Service for Claude AI interactions"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))

        print(f"🤖 Claude AI initialized with model: {self.model}")

    async def get_dm_response(self,
                              system_prompt: str,
                              context: Dict[str, Any],
                              player_input: str,
                              conversation_history: List[Dict[str, str]] = None) -> str:
        """Get DM response from Claude"""

        try:
            # Build the user message with context
            user_message = self._build_user_message(context, player_input)

            # Prepare messages for Claude
            messages = []

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            print(f"🎲 Sending request to Claude...")

            # Make API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )

            dm_response = response.content[0].text
            print(f"✅ Received response ({len(dm_response)} characters)")

            return dm_response

        except APIError as e:
            print(f"❌ Claude API Error: {e}")
            return "I'm having trouble connecting to my magical knowledge. Please try again."

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return "Something went wrong in the mystical realm. Please try again."

    def _build_user_message(self, context: Dict[str, Any], player_input: str) -> str:
        """Build formatted message for Claude"""

        message_parts = []

        # Current situation context
        if 'quick_reference' in context:
            qr = context['quick_reference']
            message_parts.append("## Current Situation")
            message_parts.append(f"Time: {qr.get('current_time', 'Unknown')}")
            message_parts.append(f"Location: {qr.get('current_location', 'Unknown')}")
            message_parts.append("")

        # Character status
        if 'character' in context:
            char = context['character']
            message_parts.append("## Character Status")
            message_parts.append(
                f"Level {char.level} | HP: {char.hit_points}/{char.max_hit_points} | AC: {char.armor_class}")
            message_parts.append("")

        # Active missions
        if 'missions' in context and context['missions']:
            message_parts.append("## Active Missions")
            for mission in context['missions'][:3]:  # Top 3 missions
                # Use 'name' instead of 'title' to match your Mission model
                mission_name = getattr(mission, 'name', getattr(mission, 'title', 'Unknown Mission'))
                mission_status = getattr(mission, 'status', 'Unknown')

                # Handle both string status and enum status
                if hasattr(mission_status, 'value'):
                    status_display = mission_status.value
                else:
                    status_display = str(mission_status)

                message_parts.append(f"- {mission_name} [{status_display}]")
            message_parts.append("")

        # Recent NPCs
        if 'recent_npcs' in context and context['recent_npcs']:
            message_parts.append("## Key NPCs")
            for npc in context['recent_npcs'][:5]:  # Top 5 NPCs
                stars = "⭐" * npc.trust_level
                message_parts.append(f"- {npc.name} {stars}: {npc.role}")
            message_parts.append("")

        # Player action
        message_parts.append("## Player Action")
        message_parts.append(player_input)

        return "\n".join(message_parts)


class SystemPromptBuilder:
    """Builds system prompts for different game scenarios"""

    @staticmethod
    def get_base_dm_prompt() -> str:
        """Get the base DM system prompt"""
        return """You are Claude, an expert Dungeon Master running "The Fey Bargain" D&D 5e campaign.

CRITICAL INSTRUCTIONS:
- NEVER control the player character's actions, thoughts, or decisions
- Describe the scene, NPC reactions, and consequences of player choices
- ALWAYS require skill checks for hidden information, NPC motivations, and supernatural detection
- Keep responses to 2-3 paragraphs maximum for social scenes
- Provide clear action options after your description

CAMPAIGN CONTEXT:
- Solo D&D campaign optimized for single player
- Motu of House Grant: Level 3 Tiefling Warlock with supernatural fey alliance
- Political intrigue in Western Trade Cities with intelligence network gameplay
- Environmental complexity compensates for solo play action economy

RESPONSE FORMAT:
1. Scene description (multi-sensory, concise)
2. NPC reactions (require skill checks for deeper insight)
3. Clear action options (combat, social, environmental, creative)

Use the provided context about current character status, missions, and NPCs to inform your response."""

    @staticmethod
    def get_combat_prompt() -> str:
        """Get combat-focused system prompt"""
        base = SystemPromptBuilder.get_base_dm_prompt()
        return base + """

COMBAT FOCUS:
- Emphasize environmental interactions over monster quantity
- Provide 2-3 tactical options each turn beyond basic attacks
- Target 15-25% of daily resources per Medium encounter
- Use dynamic environmental elements (destructible cover, moving platforms, etc.)"""

    @staticmethod
    def get_social_prompt() -> str:
        """Get social encounter system prompt"""
        base = SystemPromptBuilder.get_base_dm_prompt()
        return base + """

SOCIAL FOCUS:
- NPCs only know information they would realistically have access to
- Surface behavioral cues are automatic; deeper motivations require skill checks
- Scale information quality to roll success
- Provide multiple social approach options (intimidation, persuasion, deception, etc.)"""