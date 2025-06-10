# src/campaign/session_manager.py
"""
Enhanced Session Manager with Persistence
Think of this like Terraform state management - maintains game state across runs
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid
import asyncio
from dataclasses import asdict

from .file_manager import CampaignFileManager
from .models import GameSession, Character, SessionState
from ..ai.claude_integration import ClaudeIntegration
from ..game.dice import DiceRoller
from ..config.settings import Settings


class SessionManager:
    """
    Enhanced Session Manager with persistence capabilities
    Like Terraform workspace management but for D&D sessions
    """

    def __init__(self, campaign_dir: str = None):
        self.settings = Settings()
        self.file_manager = CampaignFileManager(campaign_dir)
        self.claude = ClaudeIntegration()
        self.dice = DiceRoller()
        self.current_session: Optional[GameSession] = None

        # Session persistence
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.auto_save_enabled = True
        self.last_auto_save = datetime.now()

        # Session cache for quick loading
        self._session_cache = {}

        print(f"📁 Session Manager initialized")
        print(f"   Sessions directory: {self.sessions_dir.absolute()}")
        print(f"   Campaign directory: {self.file_manager.campaign_dir}")

    async def start_new_session(self, character_name: str = None) -> GameSession:
        """
        Start new game session with full persistence
        Like 'terraform init' but for D&D
        """
        print("🎲 Starting new session...")

        # Load campaign files
        print("📚 Loading campaign files...")
        campaign_data = self.file_manager.load_campaign_files()

        if not campaign_data:
            raise ValueError("No campaign files found! Check your campaign_files directory.")

        # Create unique session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

        # Extract character from campaign files
        character = self._extract_character(campaign_data, character_name)

        # Create session object
        self.current_session = GameSession(
            session_id=session_id,
            character=character,
            current_scene="",
            session_start=datetime.now(),
            campaign_data=campaign_data
        )

        # Generate opening scene
        print("🎭 Generating opening scene...")
        opening_scene = await self._generate_opening_scene(campaign_data)
        self.current_session.current_scene = opening_scene

        # Auto-save the new session
        await self.save_session()

        # Create backup of campaign files
        backup_path = self._backup_campaign_files(session_id)
        print(f"💾 Campaign files backed up to: {backup_path}")

        print(f"✅ Session {session_id} started successfully!")
        return self.current_session

    async def load_session(self, session_id: str = None) -> GameSession:
        """
        Load existing session from disk
        Like 'terraform workspace select'
        """
        if session_id is None:
            # Load most recent session
            session_id = self._get_most_recent_session()

        if not session_id:
            raise ValueError("No sessions found to load")

        print(f"📂 Loading session: {session_id}")

        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")

        # Load session data
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)

        # Reconstruct session object
        self.current_session = self._deserialize_session(session_data)

        print(f"✅ Session loaded: {self.current_session.session_id}")
        print(f"   Character: {self.current_session.character.name}")
        print(f"   Session time: {self._format_session_duration()}")

        return self.current_session

    async def save_session(self, auto_save: bool = False) -> str:
        """
        Save current session to disk
        Like 'terraform state save'
        """
        if not self.current_session:
            raise ValueError("No active session to save")

        session_file = self.sessions_dir / f"{self.current_session.session_id}.json"

        # Prepare session data for serialization
        session_data = self._serialize_session(self.current_session)

        # Write to temp file first, then rename (atomic operation)
        temp_file = session_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        temp_file.rename(session_file)

        if not auto_save:
            print(f"💾 Session saved: {session_file}")

        self.last_auto_save = datetime.now()
        return str(session_file)

    async def process_player_action(self, action: str) -> str:
        """
        Process player action and update session state
        """
        if not self.current_session:
            raise ValueError("No active session")

        # Record the action
        self.current_session.actions_taken.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'scene_before': self.current_session.current_scene[:100] + "..."
        })

        # Process with Claude
        print("🤔 Processing action with AI...")
        response = await self._generate_scene_response(action)

        # Update current scene
        self.current_session.current_scene = response

        # Auto-save if enabled
        if self.auto_save_enabled:
            await self._check_auto_save()

        return response

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions"""
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                sessions.append({
                    'session_id': session_data['session_id'],
                    'character_name': session_data['character']['name'],
                    'start_time': session_data['session_start'],
                    'last_modified': datetime.fromtimestamp(session_file.stat().st_mtime),
                    'actions_count': len(session_data.get('actions_taken', [])),
                    'file_path': str(session_file)
                })
            except Exception as e:
                print(f"⚠️ Error reading session file {session_file}: {e}")
                continue

        # Sort by last modified (most recent first)
        sessions.sort(key=lambda x: x['last_modified'], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session file"""
        session_file = self.sessions_dir / f"{session_id}.json"

        if session_file.exists():
            session_file.unlink()
            print(f"🗑️ Session deleted: {session_id}")
            return True
        else:
            print(f"❌ Session not found: {session_id}")
            return False

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        if not self.current_session:
            return {"status": "No active session"}

        return {
            "session_id": self.current_session.session_id,
            "character_name": self.current_session.character.name,
            "character_level": self.current_session.character.level,
            "character_hp": f"{self.current_session.character.hit_points}/{self.current_session.character.max_hit_points}",
            "session_duration": self._format_session_duration(),
            "actions_taken": len(self.current_session.actions_taken),
            "current_location": self.current_session.current_location,
            "last_save": self.last_auto_save.strftime("%H:%M:%S")
        }

    # Private helper methods

    def _extract_character(self, campaign_data: Dict, character_name: str = None) -> Character:
        """Extract character information from campaign files"""
        # Look for character sheet
        char_data = campaign_data.get('character_sheet', {})

        if not char_data:
            print("⚠️ No character sheet found, creating default character")
            return Character(
                name=character_name or "Player Character",
                level=1,
                hit_points=10,
                max_hit_points=10
            )

        # Parse character sheet content
        content = char_data.get('content', '')

        # Extract basic info (this would be more sophisticated in real implementation)
        name = character_name or self._extract_field(content, r'Name:\s*([^\n]+)') or "Player Character"
        level = int(self._extract_field(content, r'Level:\s*(\d+)') or 1)
        hp_match = self._extract_field(content, r'HP:\s*(\d+)(?:/(\d+))?')

        if hp_match:
            current_hp = int(hp_match)
            max_hp = int(self._extract_field(content, r'HP:\s*\d+/(\d+)') or hp_match)
        else:
            current_hp = max_hp = 10

        return Character(
            name=name,
            level=level,
            hit_points=current_hp,
            max_hit_points=max_hp
        )

    def _extract_field(self, content: str, pattern: str) -> Optional[str]:
        """Extract field from markdown content using regex"""
        import re
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else None

    async def _generate_opening_scene(self, campaign_data: Dict) -> str:
        """Generate opening scene for new session"""
        context = self._build_session_context(campaign_data)

        try:
            scene = await self.claude.generate_scene(
                context=context,
                prompt="Generate an engaging opening scene for this D&D session."
            )
            return scene
        except Exception as e:
            print(f"⚠️ Error generating opening scene: {e}")
            return "You find yourself ready to begin a new adventure in the Feywild..."

    async def _generate_scene_response(self, action: str) -> str:
        """Generate AI response to player action"""
        context = self._build_current_context()

        try:
            response = await self.claude.generate_scene(
                context=context,
                prompt=f"Player action: {action}"
            )
            return response
        except Exception as e:
            print(f"⚠️ Error generating scene response: {e}")
            return f"As you attempt to {action.lower()}, something unexpected happens..."

    def _build_session_context(self, campaign_data: Dict) -> str:
        """Build context string for AI from campaign data"""
        context_parts = []

        # Add character info
        if self.current_session:
            char = self.current_session.character
            context_parts.append(f"Character: {char.name} (Level {char.level})")

        # Add key campaign information
        for file_key, file_data in campaign_data.items():
            if file_key in ['quick_reference', 'character_sheet', 'active_missions']:
                content = file_data.get('content', '')[:500]  # Limit content length
                context_parts.append(f"{file_key.replace('_', ' ').title()}:\n{content}")

        return "\n\n".join(context_parts)

    def _build_current_context(self) -> str:
        """Build context for current scene generation"""
        if not self.current_session:
            return ""

        context_parts = [
            f"Current Scene: {self.current_session.current_scene}",
            f"Character: {self.current_session.character.name}",
            f"Location: {self.current_session.current_location}"
        ]

        # Add recent actions
        recent_actions = self.current_session.actions_taken[-3:]  # Last 3 actions
        if recent_actions:
            context_parts.append("Recent Actions:")
            for action in recent_actions:
                context_parts.append(f"- {action['action']}")

        return "\n".join(context_parts)

    def _serialize_session(self, session: GameSession) -> Dict[str, Any]:
        """Convert session object to JSON-serializable dict"""
        return {
            'session_id': session.session_id,
            'character': asdict(session.character),
            'current_scene': session.current_scene,
            'current_location': session.current_location,
            'session_start': session.session_start.isoformat(),
            'actions_taken': session.actions_taken,
            'context_summary': session.context_summary,
            'saved_at': datetime.now().isoformat()
        }

    def _deserialize_session(self, session_data: Dict[str, Any]) -> GameSession:
        """Convert JSON dict back to session object"""
        character = Character(**session_data['character'])

        return GameSession(
            session_id=session_data['session_id'],
            character=character,
            current_scene=session_data.get('current_scene', ''),
            current_location=session_data.get('current_location', ''),
            session_start=datetime.fromisoformat(session_data['session_start']),
            actions_taken=session_data.get('actions_taken', []),
            context_summary=session_data.get('context_summary', '')
        )

    def _get_most_recent_session(self) -> Optional[str]:
        """Get the most recently modified session ID"""
        sessions = self.list_sessions()
        return sessions[0]['session_id'] if sessions else None

    def _format_session_duration(self) -> str:
        """Format session duration as human-readable string"""
        if not self.current_session:
            return "N/A"

        duration = datetime.now() - self.current_session.session_start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def _backup_campaign_files(self, session_id: str) -> Path:
        """Create backup of campaign files for this session"""
        backup_dir = self.sessions_dir / f"{session_id}_backup"
        backup_dir.mkdir(exist_ok=True)

        # Copy all campaign files
        for file_path in self.file_manager.campaign_dir.glob("*.md"):
            backup_file = backup_dir / file_path.name
            backup_file.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')

        return backup_dir

    async def _check_auto_save(self):
        """Check if auto-save is needed"""
        if not self.auto_save_enabled:
            return

        time_since_save = datetime.now() - self.last_auto_save
        if time_since_save > timedelta(minutes=5):  # Auto-save every 5 minutes
            await self.save_session(auto_save=True)
            print("💾 Auto-saved session")


# Additional models for enhanced session management

class SessionState:
    """Represents the complete state of a game session"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"