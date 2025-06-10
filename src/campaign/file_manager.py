"""
Campaign File Manager - Loads and parses your existing campaign files
"""
import re
import markdown
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from .models import CampaignFile, NPC, Location, Mission, CharacterStats


class CampaignFileManager:
    """Manages loading and parsing of campaign markdown files"""

    def __init__(self, campaign_directory: str = "./campaign_files"):
        self.campaign_dir = Path(campaign_directory)
        self.files: Dict[str, CampaignFile] = {}

        # Map your actual filenames
        self.file_mapping = {
            'character_sheet': 'character_sheet.md',
            'active_missions': 'active_missions.md',
            'npc_directory': 'npc_directory.md',
            'location_directory': 'location_directory.md',
            'faction_tracker': 'faction_tracker.md',
            'campaign_timeline': 'campaign_timeline.md',
            'quick_reference': 'quick_reference.md',
            'session_log': 'session_log.md',
            'backstory_relationships': 'backstory_relationships.md',
            'character_progression': 'character_progression.md',
            'atmospheric_writing': 'atmospheric_writing.md',
            'companion_management': 'companion_management.md',
            'memory_management': 'memory_management.md',
            'skill_check_system': 'skill_check_system.md',
            'social_mechanics': 'social_mechanics.md',
            'world_progression': 'world_progression.md',
            'combat_templates': 'combat_templates.md',
            'core_dm_instructions': 'core_dm_instructions.md',
            'oracle_tables': 'oracle_tables.md',
            'house_rules': 'house_rules.md',
            'magic_item_catalog': 'magic_item_catalog.md',
            'name_generators': 'name_generators.md',
            'plot_hooks': 'plot_hooks.md',
            'world_secrets': 'world_secrets.md'
        }

    def load_all_files(self) -> Dict[str, CampaignFile]:
        """Load all campaign files"""
        print(f"📁 Loading campaign files from: {self.campaign_dir}")

        if not self.campaign_dir.exists():
            raise FileNotFoundError(f"Campaign directory not found: {self.campaign_dir}")

        loaded_count = 0
        for key, filename in self.file_mapping.items():
            file_path = self.campaign_dir / filename
            if file_path.exists():
                try:
                    self.files[key] = self._load_file(file_path)
                    loaded_count += 1
                    print(f"✅ Loaded: {filename}")
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
            else:
                print(f"⚠️  File not found: {filename}")

        print(f"📊 Loaded {loaded_count}/{len(self.file_mapping)} campaign files")
        return self.files

    def _load_file(self, file_path: Path) -> CampaignFile:
        """Load and parse a single markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Get file modification time
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

        # Create campaign file object
        campaign_file = CampaignFile(
            filename=file_path.name,
            content=content,
            last_modified=mod_time
        )

        # Parse specific file types
        if file_path.name == 'npc_directory.md':
            campaign_file.parsed_data = self._parse_npc_directory(content)
        elif file_path.name == 'character_sheet.md':
            campaign_file.parsed_data = self._parse_character_sheet(content)
        elif file_path.name == 'active_missions.md':
            campaign_file.parsed_data = self._parse_missions(content)
        elif file_path.name == 'quick_reference.md':
            campaign_file.parsed_data = self._parse_quick_reference(content)

        return campaign_file

    def _parse_npc_directory(self, content: str) -> List[NPC]:
        """Parse NPC directory to extract character data"""
        npcs = []

        # Look for NPC entries with star ratings
        # Pattern: ### **Name** ⭐⭐⭐⭐⭐ or ### **Name** ⭐⭐⭐⭐ [STATUS]
        npc_pattern = r'### \*\*(.*?)\*\* (⭐+)(?:\s*\[([^\]]+)\])?'

        matches = re.finditer(npc_pattern, content)

        for match in matches:
            name = match.group(1)
            stars = match.group(2)
            status_tag = match.group(3) if match.group(3) else ""

            # Count stars for trust level
            trust_level = len(stars)

            # Extract the section content for this NPC
            start_pos = match.end()
            # Find next NPC or section
            next_match = re.search(r'\n### ', content[start_pos:])
            if next_match:
                section_content = content[start_pos:start_pos + next_match.start()]
            else:
                section_content = content[start_pos:]

            # Parse role, relationship, etc. from the section
            role = self._extract_field(section_content, r'\*\*Role:\*\* (.+?)(?:\n|$)')
            relationship = self._extract_field(section_content, r'\*\*Relationship:\*\* (.+?)(?:\n|$)')
            capabilities = self._extract_field(section_content, r'\*\*Capabilities:\*\* (.+?)(?:\n|$)')
            current_status = self._extract_field(section_content, r'\*\*Current Status:\*\* (.+?)(?:\n|$)')

            npc = NPC(
                name=name,
                role=role or "",
                relationship=relationship or "",
                trust_level=trust_level,
                capabilities=[capabilities] if capabilities else [],
                current_status=current_status or "",
                notes=status_tag
            )
            npcs.append(npc)

        print(f"📝 Parsed {len(npcs)} NPCs from directory")
        return npcs

    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """Extract a field using regex pattern"""
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None

    def _parse_character_sheet(self, content: str) -> Optional[CharacterStats]:
        """Parse character sheet for basic stats"""
        # Extract key stats using regex
        level_match = re.search(r'Level (\d+)', content)
        hp_match = re.search(r'HP:\*\* (\d+)/(\d+)', content)
        ac_match = re.search(r'AC:\*\* (\d+)', content)

        if level_match:
            level = int(level_match.group(1))
            max_hp = int(hp_match.group(2)) if hp_match else 27
            current_hp = int(hp_match.group(1)) if hp_match else 27
            ac = int(ac_match.group(1)) if ac_match else 13

            return CharacterStats(
                level=level,
                hit_points=current_hp,
                max_hit_points=max_hp,
                armor_class=ac
            )
        return None

    def _parse_missions(self, content: str) -> List[Mission]:
        """Parse active missions"""
        missions = []

        # Look for mission headers
        mission_pattern = r'### \*\*(.*?)\*\* \[([^\]]+)\]'
        matches = re.finditer(mission_pattern, content)

        for match in matches:
            title = match.group(1)
            status = match.group(2)

            mission = Mission(
                title=title,
                status=status,
                priority=1 if "PRIORITY 1" in content[match.start():match.start() + 200] else 2
            )
            missions.append(mission)

        return missions

    def _parse_quick_reference(self, content: str) -> Dict[str, Any]:
        """Parse quick reference for immediate context"""
        quick_ref = {}

        # Extract character status
        level_match = re.search(r'Level (\d+)', content)
        if level_match:
            quick_ref['character_level'] = int(level_match.group(1))

        # Extract current context
        time_match = re.search(r'\*\*Time:\*\* (.+?)(?:\n|$)', content)
        if time_match:
            quick_ref['current_time'] = time_match.group(1)

        location_match = re.search(r'\*\*Location:\*\* (.+?)(?:\n|$)', content)
        if location_match:
            quick_ref['current_location'] = location_match.group(1)

        return quick_ref

    def get_file(self, file_key: str) -> Optional[CampaignFile]:
        """Get a specific campaign file"""
        return self.files.get(file_key)

    def get_npcs(self) -> List[NPC]:
        """Get parsed NPC list"""
        npc_file = self.get_file('npc_directory')
        if npc_file and npc_file.parsed_data:
            return npc_file.parsed_data
        return []

    def get_character_stats(self) -> Optional[CharacterStats]:
        """Get character statistics"""
        char_file = self.get_file('character_sheet')
        if char_file and char_file.parsed_data:
            return char_file.parsed_data
        return None

    def save_file(self, file_key: str, content: str):
        """Save updated content to a campaign file"""
        if file_key in self.file_mapping:
            filename = self.file_mapping[file_key]
            file_path = self.campaign_dir / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"💾 Saved: {filename}")
        else:
            print(f"❌ Unknown file key: {file_key}")