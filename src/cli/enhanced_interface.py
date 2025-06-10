# src/cli/enhanced_interface.py - Character Creation Integration
"""
Enhanced CLI Interface with AI-Assisted Character Creation
Updates to integrate the character creation system
"""

# Add these imports to the top of your enhanced_interface.py file:
from ..game.character_creation import CharacterCreator, character_creation_menu, quick_character_creation

class EnhancedGameCLI:
    """Enhanced CLI with character creation capabilities"""
    
    # Add this method to your existing EnhancedGameCLI class:
    
    async def _main_menu(self):
        """Enhanced main menu with character creation option"""
        while self.running:
            print("\n" + "="*60)
            print("🎭 FEY BARGAIN GAME - MAIN MENU")
            print("="*60)
            
            # Show current session status
            current_session = self.session_manager.current_session
            if current_session:
                print(f"🎲 Active Session: {current_session.session_id}")
                print(f"   Character: {current_session.character.name} (Level {current_session.character.level})")
                print(f"   Duration: {self._format_duration(current_session)}")
            else:
                print("📝 No active session")
            
            print("\n📋 OPTIONS:")
            print("1. 🎲 Start New Session")
            print("2. 🎭 Create New Character")  # NEW OPTION
            print("3. 📂 Load Existing Session")
            print("4. 📊 List All Sessions")
            print("5. ⚙️  Campaign Management")
            print("6. 🔧 Settings & Info")
            print("7. 🚪 Exit")
            
            if current_session:
                print("8. ▶️  Continue Current Session")
            
            choice = input("\n👉 Enter choice: ").strip()
            
            try:
                if choice == "1":
                    await self._start_new_session()
                elif choice == "2":
                    await self._character_creation_menu()  # NEW METHOD
                elif choice == "3":
                    await self._load_session_menu()
                elif choice == "4":
                    self._list_sessions()
                elif choice == "5":
                    await self._campaign_management()
                elif choice == "6":
                    self._show_settings()
                elif choice == "7":
                    await self._exit_application()
                elif choice == "8" and current_session:
                    await self._game_loop()
                else:
                    max_choice = "8" if current_session else "7"
                    print(f"❌ Invalid choice. Please enter 1-{max_choice}.")
                    
            except KeyboardInterrupt:
                print("\n\n⏸️  Interrupted by user")
                if current_session:
                    await self._save_session()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                if self.settings.debug:
                    import traceback
                    traceback.print_exc()
    
    async def _character_creation_menu(self):
        """Character creation menu"""
        print("\n🎭 CHARACTER CREATION SYSTEM")
        print("=" * 50)
        print("Create your D&D character with AI assistance!")
        print()
        
        print("📋 CHARACTER CREATION OPTIONS:")
        print("1. 🤖 AI-Assisted Creation (Full Experience)")
        print("2. 🎲 Quick Random Character")
        print("3. 📄 View Sample Character")
        print("4. 📚 Character Creation Guide")
        print("0. 🔙 Back to Main Menu")
        
        choice = input("\n👉 Choose option (0-4): ").strip()
        
        try:
            if choice == "1":
                await self._full_character_creation()
            elif choice == "2":
                await self._quick_character_creation()
            elif choice == "3":
                self._show_sample_character()
            elif choice == "4":
                self._show_character_creation_guide()
            elif choice == "0":
                return
            else:
                print("❌ Invalid choice. Please enter 0-4.")
                
        except Exception as e:
            print(f"❌ Character creation error: {e}")
            if self.settings.debug:
                import traceback
                traceback.print_exc()
    
    async def _full_character_creation(self):
        """Full AI-assisted character creation"""
        print("\n🎭 STARTING AI-ASSISTED CHARACTER CREATION")
        print("=" * 60)
        print("🤖 I'll guide you through creating your D&D character step by step.")
        print("At each stage, I'll provide AI suggestions and feedback.")
        print("This will take about 10-15 minutes for the full experience.")
        print()
        
        proceed = input("Ready to begin? (y/n): ").strip().lower()
        if proceed not in ['y', 'yes']:
            print("🔙 Returning to character creation menu...")
            return
        
        try:
            # Create character using AI system
            creator = CharacterCreator()
            character = await creator.create_character()
            
            print("\n🎉 Character creation complete!")
            
            # Ask if they want to start a session immediately
            start_session = input("\n🎮 Start a game session with this character? (y/n): ").strip().lower()
            if start_session in ['y', 'yes']:
                # Override session manager to use new character
                await self._start_session_with_character(character)
            else:
                print("✅ Character saved! You can start a session anytime from the main menu.")
                
        except Exception as e:
            print(f"❌ Error during character creation: {e}")
            print("🔄 You can try again or contact support if the issue persists.")
    
    async def _quick_character_creation(self):
        """Quick random character generation"""
        print("\n🎲 QUICK CHARACTER GENERATION")
        print("-" * 40)
        print("This will create a random character for immediate play.")
        
        try:
            character = await quick_character_creation()
            
            print(f"\n✅ Created {character.name}!")
            self._display_quick_character_summary(character)
            
            # Ask if they want to start playing
            start_now = input("\n🎮 Start playing immediately? (y/n): ").strip().lower()
            if start_now in ['y', 'yes']:
                await self._start_session_with_character(character)
            else:
                print("✅ Character ready! Start a session from the main menu.")
                
        except Exception as e:
            print(f"❌ Error creating quick character: {e}")
    
    async def _start_session_with_character(self, character):
        """Start a new session with a specific character"""
        print(f"\n🎲 Starting session with {character.name}...")
        
        try:
            # Create a temporary character sheet file
            await self._save_temp_character_sheet(character)
            
            # Start session (it will load the character from file)
            session = await self.session_manager.start_new_session(character.name)
            print(f"✅ Session started with {character.name}!")
            
            # Ask if they want to play immediately
            play_now = input("▶️ Start playing now? (y/n): ").strip().lower()
            if play_now in ['y', 'yes']:
                await self._game_loop()
                
        except Exception as e:
            print(f"❌ Error starting session: {e}")
    
    def _display_quick_character_summary(self, character):
        """Display a quick summary of the generated character"""
        print(f"\n📋 CHARACTER SUMMARY:")
        print(f"   Name: {character.name}")
        print(f"   Level: {character.level}")
        print(f"   HP: {character.hit_points}")
        print(f"   Key Stats: STR {character.strength}, DEX {character.dexterity}, CON {character.constitution}")
    
    def _show_sample_character(self):
        """Show an example of a completed character"""
        print("\n📄 SAMPLE CHARACTER")
        print("=" * 40)
        
        sample_text = """
🎭 Lyra Moonwhisper the Half-Elf Ranger

📖 Background: Outlander
🧬 Subrace: None

📊 Ability Scores:
   Strength:     13 (+1)
   Dexterity:    16 (+3)  ⭐ Primary
   Constitution: 14 (+2)
   Intelligence: 12 (+1)
   Wisdom:       15 (+2)  ⭐ Primary
   Charisma:     10 (+0)

⚔️ Combat Stats:
   Hit Points: 12
   Armor Class: 13 (Leather armor + Dex)
   Proficiency Bonus: +2

🎭 Personality:
   Trait: "I have a knack for finding hidden paths and shortcuts"
   Ideal: "Nature must be protected from those who would exploit it"
   Bond: "My family was killed by raiders; I seek to prevent others' loss"
   Flaw: "I trust animals more than people"

📜 Backstory:
Born in a small forest settlement, Lyra learned to track and hunt from 
her elven grandmother. When raiders destroyed her village, she became 
a wandering protector of wilderness areas and remote communities.

🎒 Key Equipment:
- Longbow and arrows
- Leather armor  
- Survival gear
- Herbalism kit
"""
        print(sample_text)
        
        input("\nPress Enter to continue...")
    
    def _show_character_creation_guide(self):
        """Show character creation guide and tips"""
        print("\n📚 CHARACTER CREATION GUIDE")
        print("=" * 50)
        
        guide_text = """
🎯 CHARACTER CREATION PROCESS:

1. 🎭 CHARACTER CONCEPT
   - Start with a simple idea: "A wise wizard" or "A sneaky thief"
   - AI will suggest races, classes, and backgrounds that fit
   - Don't worry about optimization - focus on what sounds fun!

2. 🧬 RACE SELECTION  
   - Each race gives ability score bonuses and special traits
   - AI will recommend races that match your concept
   - ⭐ means the AI thinks it's a great fit for your idea

3. ⚔️ CLASS SELECTION
   - Your class determines your abilities and role
   - Fighter = combat, Wizard = magic, Rogue = stealth, etc.
   - AI shows synergy with your chosen race

4. 📚 BACKGROUND
   - Represents your character's life before adventuring
   - Gives skills, equipment, and story hooks
   - Soldier, Noble, Folk Hero, etc.

5. 🎲 ABILITY SCORES
   - Six stats that define your character's capabilities
   - Higher = better at that type of activity
   - Standard Array (recommended): balanced and fair
   - Rolling: random but potentially more powerful

6. 🎭 PERSONALITY
   - Trait: How you act day-to-day
   - Ideal: What drives you / your principles  
   - Bond: What you care about most
   - Flaw: Your weakness or vice

🎮 GAMEPLAY TIPS:

✅ DO:
- Choose what sounds interesting to you
- Trust the AI recommendations if you're new
- Focus on character personality over perfect stats
- Ask questions if you're unsure about anything

❌ DON'T:
- Worry about making the "perfect" character
- Stress about optimizing every choice
- Feel pressured to choose certain options

🤖 AI ASSISTANCE:
The AI will help by:
- Suggesting options that fit your concept
- Explaining why certain combinations work well  
- Providing personality ideas and backstory prompts
- Offering feedback on your choices

Remember: There are no wrong choices! D&D is about having fun
and telling a good story. The "best" character is the one you
enjoy playing.
"""
        
        print(guide_text)
        input("\nPress Enter to continue...")
    
    async def _save_temp_character_sheet(self, character):
        """Save character to campaign files temporarily"""
        from pathlib import Path
        
        campaign_dir = Path(self.settings.campaign_files_path)
        character_file = campaign_dir / "character-sheet.md"
        
        # Create basic character sheet content
        content = f"""# Character Sheet

## Basic Information
**Name:** {character.name}
**Level:** {character.level}

## Ability Scores
**Strength:** {character.strength}
**Dexterity:** {character.dexterity}
**Constitution:** {character.constitution}
**Intelligence:** {character.intelligence}
**Wisdom:** {character.wisdom}
**Charisma:** {character.charisma}

## Combat Stats
**Armor Class:** {character.armor_class}
**Hit Points:** {character.hit_points}/{character.max_hit_points}
**Speed:** 30 feet

## Equipment
- Basic adventuring gear
- Starting equipment

---
*Character created with character creation system*
"""
        
        character_file.write_text(content, encoding='utf-8')
        print(f"💾 Character sheet saved to campaign files")

    # Update the start new session method to include character creation option
    async def _start_new_session(self):
        """Enhanced start new session with character creation option"""
        print("\n🎲 STARTING NEW SESSION")
        print("-" * 30)
        
        # Check if character sheet exists
        campaign_dir = Path(self.settings.campaign_files_path)
        character_file = campaign_dir / "character-sheet.md"
        
        if not character_file.exists():
            print("📄 No character sheet found!")
            print("\nYou'll need a character to start a session.")
            print("1. 🎭 Create New Character")
            print("2. 📋 Use Sample Character") 
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nChoose option: ").strip()
            
            if choice == "1":
                await self._character_creation_menu()
                return
            elif choice == "2":
                await self._create_sample_character()
            elif choice == "0":
                return
            else:
                print("❌ Invalid choice")
                return
        
        # Ask for character name
        char_name = input("Character name (or press Enter for default): ").strip()
        if not char_name:
            char_name = None
        
        print("\n🔄 Initializing session...")
        try:
            session = await self.session_manager.start_new_session(char_name)
            print(f"\n✅ Session created: {session.session_id}")
            print(f"Character: {session.character.name}")
            
            # Ask if they want to start playing immediately
            start_now = input("\nStart playing now? (y/n): ").strip().lower()
            if start_now in ['y', 'yes']:
                await self._game_loop()
                
        except Exception as e:
            print(f"❌ Error starting session: {e}")
    
    async def _create_sample_character(self):
        """Create a sample character quickly"""
        from ..campaign.models import Character
        
        sample_character = Character(
            name="Sample Hero",
            level=1,
            hit_points=12,
            max_hit_points=12,
            armor_class=13,
            strength=14,
            dexterity=16,
            constitution=14,
            intelligence=12,
            wisdom=13,
            charisma=10
        )
        
        await self._save_temp_character_sheet(sample_character)
        print("✅ Sample character created!")


# Add these command handlers to your existing enhanced CLI:

# Update your existing commands dictionary to include character creation:
def __init__(self):
    # ... existing initialization ...
    
    self.commands.update({
        'create': self._handle_character_creation,
        'newchar': self._handle_character_creation,
        'quickchar': self._handle_quick_character,
    })

async def _handle_character_creation(self, full_command: str) -> None:
    """Handle character creation command during gameplay"""
    print("\n🎭 Character creation during an active session isn't supported.")
    print("Please finish your current session and create a character from the main menu.")

async def _handle_quick_character(self, full_command: str) -> None:
    """Handle quick character creation command"""
    print("\n🎲 Quick character creation during gameplay isn't supported.")
    print("Please use the main menu for character creation.")


# Example integration with your existing game commands:
async def _show_help(self, full_command: str) -> None:
    """Enhanced help with character creation info"""
    print("\n📋 AVAILABLE COMMANDS:")
    print("-" * 30)
    print("🎮 GAME COMMANDS:")
    print("  help, h          - Show this help")
    print("  character, char  - Show character sheet")
    print("  roll, r [dice]   - Roll dice (e.g., 'roll 1d20+5', 'r 2d6')")
    print("  save             - Save current session")
    print("  info             - Show session information")
    print("  status           - Show current status")
    print("  quit, exit       - Return to main menu")
    print("\n🎭 CHARACTER COMMANDS:")
    print("  create, newchar  - Info about character creation")
    print("  quickchar        - Info about quick character generation")
    print("\n💬 GAME ACTIONS:")
    print("  Just type what you want to do!")
    print("  Examples: 'examine the door', 'talk to the guard', 'cast fireball'")
    print("\n🎲 DICE EXAMPLES:")
    print("  roll 1d20        - Standard d20 roll")
    print("  roll 1d20+5      - d20 with +5 modifier")
    print("  roll 2d6         - Two six-sided dice")
    print("  roll 1d20 adv    - Roll with advantage")
    print("  roll 1d20 dis    - Roll with disadvantage")
    print("\n💡 TIP: Return to main menu to create new characters or manage sessions!")


# Example of how to modify your session manager to work with created characters
class EnhancedSessionManager:
    """Extended session manager with character creation support"""
    
    def __init__(self):
        # ... existing initialization ...
        self.created_characters = {}  # Store created characters
    
    async def start_new_session_with_character(self, character, character_name: str = None) -> GameSession:
        """Start new session with a pre-created character"""
        print("🎲 Starting new session with created character...")
        
        # Load campaign files
        print("📚 Loading campaign files...")
        campaign_data = self.file_manager.load_campaign_files()
        
        if not campaign_data:
            raise ValueError("No campaign files found! Check your campaign_files directory.")
        
        # Create unique session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Use the provided character instead of extracting from files
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