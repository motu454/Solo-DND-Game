"""
Enhanced Game Interface with Claude Integration
"""
from typing import List, Dict
from ui import CampaignFileManager
from ui import ClaudeService, SystemPromptBuilder
from ui import GameContextManager


class GameInterface:
    """Main game interface with Claude AI integration"""

    def __init__(self):
        print("🎲 Initializing The Fey Bargain Game...")

        # Initialize services
        self.file_manager = CampaignFileManager("./campaign_files")
        self.claude_service = ClaudeService()
        self.context_manager = GameContextManager(self.file_manager)
        self.conversation_history: List[Dict[str, str]] = []

        print("🎭 Services initialized successfully!")

    async def start_session(self):
        """Start a new game session"""
        print("\n" + "=" * 60)
        print("🌟 Welcome to The Fey Bargain! 🌟")
        print("A Solo D&D Campaign with Claude as your DM")
        print("=" * 60)

        # Load campaign files
        print("\n📁 Loading campaign files...")
        try:
            files = self.file_manager.load_all_files()
            print(f"✅ Loaded {len(files)} campaign files")
        except Exception as e:
            print(f"❌ Error loading campaign files: {e}")
            return

        # Show current status
        await self._show_status()

        # Start game loop
        print("\n🎮 Game session started!")
        print("💡 Commands: 'help', 'status', 'quit', or describe your action")
        print("-" * 50)

        while True:
            try:
                user_input = input("\n🔮 What do you do? > ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for playing The Fey Bargain!")
                    break
                elif user_input.lower() in ['help', 'h']:
                    self._show_help()
                elif user_input.lower() in ['status', 'stat', 's']:
                    await self._show_status()
                else:
                    await self._process_action(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Session ended. Farewell, adventurer!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def _process_action(self, player_input: str):
        """Process player action and get DM response"""
        print(f"\n🎯 Processing: {player_input}")

        # Determine scenario type from input
        scenario_type = self._determine_scenario_type(player_input)

        # Build context
        context = self.context_manager.build_context(scenario_type)

        # Get appropriate system prompt
        if scenario_type == "combat":
            system_prompt = SystemPromptBuilder.get_combat_prompt()
        elif scenario_type == "social":
            system_prompt = SystemPromptBuilder.get_social_prompt()
        else:
            system_prompt = SystemPromptBuilder.get_base_dm_prompt()

        # Get Claude's response
        dm_response = await self.claude_service.get_dm_response(
            system_prompt=system_prompt,
            context=context,
            player_input=player_input,
            conversation_history=self.conversation_history[-6:]  # Last 3 exchanges
        )

        # Display response
        print("\n" + "🎭 DM".center(50, "="))
        print(dm_response)
        print("=" * 50)

        # Update conversation history
        self.conversation_history.extend([
            {"role": "user", "content": player_input},
            {"role": "assistant", "content": dm_response}
        ])

        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def _determine_scenario_type(self, player_input: str) -> str:
        """Determine the type of scenario from player input"""
        input_lower = player_input.lower()

        # Combat keywords
        if any(word in input_lower for word in ['attack', 'fight', 'cast', 'spell', 'weapon', 'combat']):
            return "combat"

        # Social keywords
        if any(word in input_lower for word in
               ['talk', 'speak', 'negotiate', 'persuade', 'intimidate', 'conversation']):
            return "social"

        return "general"

    async def _show_status(self):
        """Show current character and campaign status"""
        print("\n📊 CURRENT STATUS")
        print("-" * 30)

        # Character stats
        character = self.file_manager.get_character_stats()
        if character:
            print(f"⚔️  Character: Level {character.level}")
            print(f"❤️  HP: {character.hit_points}/{character.max_hit_points}")
            print(f"🛡️  AC: {character.armor_class}")

        # Quick reference
        qr_file = self.file_manager.get_file('quick_reference')
        if qr_file and qr_file.parsed_data:
            qr = qr_file.parsed_data
            if 'current_time' in qr:
                print(f"⏰ Time: {qr['current_time']}")
            if 'current_location' in qr:
                print(f"📍 Location: {qr['current_location']}")

        # Top NPCs - Fixed the trust_level issue!
        npcs = self.file_manager.get_npcs()
        if npcs:
            print(f"\n👥 Key NPCs:")
            # Use trust_points instead of trust_level
            top_npcs = sorted(npcs, key=lambda x: getattr(x, 'trust_points', 0), reverse=True)[:5]
            for npc in top_npcs:
                # Use trust_points to display stars
                trust_points = getattr(npc, 'trust_points', 0)
                stars = "⭐" * max(0, min(5, trust_points))  # Limit to 5 stars max
                print(f"   {npc.name} {stars}")

        print("-" * 30)

    def _show_help(self):
        """Show help information"""
        print("\n📜 THE FEY BARGAIN - HELP")
        print("=" * 40)
        print("🎯 COMMANDS:")
        print("  help, h       - Show this help")
        print("  status, s     - Show character status")
        print("  quit, q       - End session")
        print("")
        print("🎲 GAMEPLAY:")
        print("  • Describe what your character does")
        print("  • Be specific about actions and intentions")
        print("  • The DM will ask for skill checks when needed")
        print("")
        print("💡 EXAMPLES:")
        print("  'I examine the door for traps'")
        print("  'I approach the guard and try to persuade them'")
        print("  'I cast Eldritch Blast at the goblin'")
        print("  'I search for information about the merchant'")
        print("=" * 40)