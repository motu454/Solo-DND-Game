# src/game/character_creation.py
"""
AI-Assisted D&D Character Creation System
Interactive character building with Claude AI guidance and feedback
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from ..campaign.models import Character
from ..ai.claude_integration import ClaudeIntegration
from ..game.dice import DiceRoller
from ..config.settings import get_settings


class CreationMethod(Enum):
    """Methods for generating ability scores"""
    STANDARD_ARRAY = "standard_array"
    POINT_BUY = "point_buy"
    ROLL_4D6_DROP_LOWEST = "roll_4d6"
    ROLL_3D6_STRAIGHT = "roll_3d6"


@dataclass
class CharacterConcept:
    """Stores the character concept and AI-generated suggestions"""
    concept_description: str = ""
    suggested_races: List[str] = field(default_factory=list)
    suggested_classes: List[str] = field(default_factory=list)
    suggested_backgrounds: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    backstory_elements: List[str] = field(default_factory=list)


@dataclass
class CharacterBuild:
    """Stores the character build in progress"""
    name: str = ""
    race: str = ""
    subrace: str = ""
    character_class: str = ""
    subclass: str = ""
    background: str = ""

    # Ability scores
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Character details
    personality_trait: str = ""
    ideal: str = ""
    bond: str = ""
    flaw: str = ""
    backstory: str = ""

    # Starting equipment choices
    equipment_choices: Dict[str, str] = field(default_factory=dict)
    starting_spells: List[str] = field(default_factory=list)


class CharacterCreator:
    """
    AI-Assisted Character Creation System
    Like a D&D Beyond character builder but with AI guidance
    """

    def __init__(self):
        self.claude = ClaudeIntegration()
        self.dice = DiceRoller()
        self.settings = get_settings()

        # D&D 5e reference data
        self.races = {
            "Human": {"ability_bonus": {"str": 1, "dex": 1, "con": 1, "int": 1, "wis": 1, "cha": 1}},
            "Elf": {"ability_bonus": {"dex": 2}, "subraces": ["High Elf", "Wood Elf", "Drow"]},
            "Dwarf": {"ability_bonus": {"con": 2}, "subraces": ["Mountain Dwarf", "Hill Dwarf"]},
            "Halfling": {"ability_bonus": {"dex": 2}, "subraces": ["Lightfoot", "Stout"]},
            "Dragonborn": {"ability_bonus": {"str": 2, "cha": 1}},
            "Gnome": {"ability_bonus": {"int": 2}, "subraces": ["Forest Gnome", "Rock Gnome"]},
            "Half-Elf": {"ability_bonus": {"cha": 2, "choice": 2}},
            "Half-Orc": {"ability_bonus": {"str": 2, "con": 1}},
            "Tiefling": {"ability_bonus": {"int": 1, "cha": 2}}
        }

        self.classes = {
            "Fighter": {"hit_die": 10, "primary_ability": ["str", "dex"], "saves": ["str", "con"]},
            "Wizard": {"hit_die": 6, "primary_ability": ["int"], "saves": ["int", "wis"]},
            "Rogue": {"hit_die": 8, "primary_ability": ["dex"], "saves": ["dex", "int"]},
            "Cleric": {"hit_die": 8, "primary_ability": ["wis"], "saves": ["wis", "cha"]},
            "Ranger": {"hit_die": 10, "primary_ability": ["dex", "wis"], "saves": ["str", "dex"]},
            "Paladin": {"hit_die": 10, "primary_ability": ["str", "cha"], "saves": ["wis", "cha"]},
            "Barbarian": {"hit_die": 12, "primary_ability": ["str"], "saves": ["str", "con"]},
            "Bard": {"hit_die": 8, "primary_ability": ["cha"], "saves": ["dex", "cha"]},
            "Druid": {"hit_die": 8, "primary_ability": ["wis"], "saves": ["int", "wis"]},
            "Monk": {"hit_die": 8, "primary_ability": ["dex", "wis"], "saves": ["str", "dex"]},
            "Sorcerer": {"hit_die": 6, "primary_ability": ["cha"], "saves": ["con", "cha"]},
            "Warlock": {"hit_die": 8, "primary_ability": ["cha"], "saves": ["wis", "cha"]}
        }

        self.backgrounds = [
            "Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier",
            "Charlatan", "Entertainer", "Guild Artisan", "Hermit", "Outlander", "Sailor"
        ]

    async def create_character(self) -> Character:
        """
        Main character creation workflow
        Returns a fully built Character object
        """
        print("🎭 Welcome to AI-Assisted Character Creation!")
        print("=" * 50)
        print("I'll guide you through creating your D&D character step by step.")
        print("At each stage, I'll provide suggestions and feedback using AI.\n")

        build = CharacterBuild()

        # Step 1: Character Concept
        concept = await self._get_character_concept()

        # Step 2: Name
        build.name = await self._choose_name(concept)

        # Step 3: Race
        build.race, build.subrace = await self._choose_race(concept)

        # Step 4: Class
        build.character_class, build.subclass = await self._choose_class(concept, build.race)

        # Step 5: Background
        build.background = await self._choose_background(concept, build)

        # Step 6: Ability Scores
        await self._assign_ability_scores(build)

        # Step 7: Personality & Backstory
        await self._develop_personality(build, concept)

        # Step 8: Equipment
        await self._choose_equipment(build)

        # Step 9: Final Review
        character = await self._finalize_character(build)

        print("\n🎉 Character creation complete!")
        return character

    async def _get_character_concept(self) -> CharacterConcept:
        """Step 1: Get initial character concept with AI suggestions"""
        print("📝 STEP 1: CHARACTER CONCEPT")
        print("-" * 30)

        while True:
            concept_input = input(
                "Describe your character concept in a few sentences\n"
                "(e.g., 'A wise old wizard seeking forbidden knowledge' or 'A young noble who became a thief'):\n"
                "> "
            ).strip()

            if concept_input:
                break
            print("Please enter a character concept to continue.")

        print("\n🤖 Analyzing your concept with AI...")

        # Get AI suggestions based on concept
        concept = await self._analyze_concept_with_ai(concept_input)

        print(f"\n✨ AI Analysis of '{concept_input}':")
        print(f"🧬 Suggested Races: {', '.join(concept.suggested_races)}")
        print(f"⚔️ Suggested Classes: {', '.join(concept.suggested_classes)}")
        print(f"📚 Suggested Backgrounds: {', '.join(concept.suggested_backgrounds)}")

        if concept.personality_traits:
            print(f"🎭 Personality Ideas: {', '.join(concept.personality_traits[:2])}")

        return concept

    async def _choose_name(self, concept: CharacterConcept) -> str:
        """Step 2: Choose character name with AI suggestions"""
        print("\n📝 STEP 2: CHARACTER NAME")
        print("-" * 30)

        # Get AI name suggestions
        name_suggestions = await self._get_name_suggestions(concept)

        print("🤖 AI Name Suggestions:")
        for i, name in enumerate(name_suggestions, 1):
            print(f"{i}. {name}")

        while True:
            choice = input(
                f"\nChoose a suggested name (1-{len(name_suggestions)}) or enter your own:\n> "
            ).strip()

            if choice.isdigit() and 1 <= int(choice) <= len(name_suggestions):
                return name_suggestions[int(choice) - 1]
            elif choice:
                return choice

            print("Please enter a name or choose from the suggestions.")

    async def _choose_race(self, concept: CharacterConcept) -> Tuple[str, str]:
        """Step 3: Choose race and subrace with AI guidance"""
        print("\n📝 STEP 3: RACE SELECTION")
        print("-" * 30)

        # Show AI suggestions first
        if concept.suggested_races:
            print("🤖 AI Recommended Races (based on your concept):")
            for i, race in enumerate(concept.suggested_races, 1):
                bonus_info = self._get_race_bonus_description(race)
                print(f"{i}. {race} - {bonus_info}")

        print(f"\n📋 All Available Races:")
        race_list = list(self.races.keys())
        for i, race in enumerate(race_list, 1):
            bonus_info = self._get_race_bonus_description(race)
            recommended = "⭐ " if race in concept.suggested_races else ""
            print(f"{i:2d}. {recommended}{race} - {bonus_info}")

        # Get race choice
        while True:
            choice = input(f"\nChoose race (1-{len(race_list)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(race_list):
                chosen_race = race_list[int(choice) - 1]
                break
            print("Please enter a valid race number.")

        # Handle subraces
        subrace = ""
        if "subraces" in self.races[chosen_race]:
            subraces = self.races[chosen_race]["subraces"]
            print(f"\n🎯 {chosen_race} Subraces:")
            for i, sub in enumerate(subraces, 1):
                print(f"{i}. {sub}")

            while True:
                choice = input(f"Choose subrace (1-{len(subraces)}): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(subraces):
                    subrace = subraces[int(choice) - 1]
                    break
                print("Please enter a valid subrace number.")

        # Get AI feedback on choice
        feedback = await self._get_race_choice_feedback(chosen_race, subrace, concept)
        print(f"\n🤖 AI Feedback: {feedback}")

        return chosen_race, subrace

    async def _choose_class(self, concept: CharacterConcept, race: str) -> Tuple[str, str]:
        """Step 4: Choose class and subclass with AI guidance"""
        print("\n📝 STEP 4: CLASS SELECTION")
        print("-" * 30)

        # Show AI suggestions
        if concept.suggested_classes:
            print("🤖 AI Recommended Classes:")
            for i, cls in enumerate(concept.suggested_classes, 1):
                class_info = self._get_class_description(cls)
                print(f"{i}. {cls} - {class_info}")

        print(f"\n📋 All Available Classes:")
        class_list = list(self.classes.keys())
        for i, cls in enumerate(class_list, 1):
            class_info = self._get_class_description(cls)
            recommended = "⭐ " if cls in concept.suggested_classes else ""
            synergy = self._get_race_class_synergy(race, cls)
            print(f"{i:2d}. {recommended}{cls} - {class_info} {synergy}")

        # Get class choice
        while True:
            choice = input(f"\nChoose class (1-{len(class_list)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(class_list):
                chosen_class = class_list[int(choice) - 1]
                break
            print("Please enter a valid class number.")

        # For now, we'll leave subclass selection for later levels
        subclass = ""

        # Get AI feedback
        feedback = await self._get_class_choice_feedback(chosen_class, race, concept)
        print(f"\n🤖 AI Feedback: {feedback}")

        return chosen_class, subclass

    async def _choose_background(self, concept: CharacterConcept, build: CharacterBuild) -> str:
        """Step 5: Choose background with AI guidance"""
        print("\n📝 STEP 5: BACKGROUND SELECTION")
        print("-" * 30)

        # Show AI suggestions
        if concept.suggested_backgrounds:
            print("🤖 AI Recommended Backgrounds:")
            for i, bg in enumerate(concept.suggested_backgrounds, 1):
                print(f"{i}. {bg}")

        print(f"\n📋 All Available Backgrounds:")
        for i, bg in enumerate(self.backgrounds, 1):
            recommended = "⭐ " if bg in concept.suggested_backgrounds else ""
            print(f"{i:2d}. {recommended}{bg}")

        # Get background choice
        while True:
            choice = input(f"\nChoose background (1-{len(self.backgrounds)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(self.backgrounds):
                chosen_background = self.backgrounds[int(choice) - 1]
                break
            print("Please enter a valid background number.")

        # Get AI feedback
        feedback = await self._get_background_feedback(chosen_background, build, concept)
        print(f"\n🤖 AI Feedback: {feedback}")

        return chosen_background

    async def _assign_ability_scores(self, build: CharacterBuild):
        """Step 6: Assign ability scores with multiple methods"""
        print("\n📝 STEP 6: ABILITY SCORES")
        print("-" * 30)

        print("🎲 Choose your ability score generation method:")
        print("1. Standard Array (15, 14, 13, 12, 10, 8) - Balanced")
        print("2. Point Buy (27 points to spend) - Customizable")
        print("3. Roll 4d6, drop lowest - Random, potentially powerful")
        print("4. Roll 3d6 straight - Random, traditional")

        method_map = {
            1: CreationMethod.STANDARD_ARRAY,
            2: CreationMethod.POINT_BUY,
            3: CreationMethod.ROLL_4D6_DROP_LOWEST,
            4: CreationMethod.ROLL_3D6_STRAIGHT
        }

        while True:
            choice = input("Choose method (1-4): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= 4:
                method = method_map[int(choice)]
                break
            print("Please enter 1, 2, 3, or 4.")

        # Generate base scores
        if method == CreationMethod.STANDARD_ARRAY:
            scores = [15, 14, 13, 12, 10, 8]
        elif method == CreationMethod.POINT_BUY:
            scores = await self._point_buy_system()
        elif method == CreationMethod.ROLL_4D6_DROP_LOWEST:
            scores = self._roll_4d6_drop_lowest()
        else:  # ROLL_3D6_STRAIGHT
            scores = self._roll_3d6_straight()

        print(f"\n🎲 Your base ability scores: {scores}")

        # Get AI recommendations for assignment
        recommendations = await self._get_ability_score_recommendations(build, scores)
        print(f"\n🤖 AI Recommendations for {build.character_class}:")
        print(recommendations)

        # Assign scores to abilities
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        assignments = {}

        available_scores = scores.copy()

        for ability in abilities:
            print(f"\n📊 Assigning {ability}")
            print(f"Available scores: {available_scores}")

            while True:
                try:
                    choice = int(input(f"Assign which score to {ability}? "))
                    if choice in available_scores:
                        assignments[ability.lower()[:3]] = choice
                        available_scores.remove(choice)
                        break
                    else:
                        print("Score not available. Choose from available scores.")
                except ValueError:
                    print("Please enter a number.")

        # Apply racial bonuses
        racial_bonuses = self.races[build.race]["ability_bonus"]

        build.strength = assignments["str"] + racial_bonuses.get("str", 0)
        build.dexterity = assignments["dex"] + racial_bonuses.get("dex", 0)
        build.constitution = assignments["con"] + racial_bonuses.get("con", 0)
        build.intelligence = assignments["int"] + racial_bonuses.get("int", 0)
        build.wisdom = assignments["wis"] + racial_bonuses.get("wis", 0)
        build.charisma = assignments["cha"] + racial_bonuses.get("cha", 0)

        print(f"\n✅ Final Ability Scores (with racial bonuses):")
        print(f"   Strength: {build.strength}")
        print(f"   Dexterity: {build.dexterity}")
        print(f"   Constitution: {build.constitution}")
        print(f"   Intelligence: {build.intelligence}")
        print(f"   Wisdom: {build.wisdom}")
        print(f"   Charisma: {build.charisma}")

    async def _develop_personality(self, build: CharacterBuild, concept: CharacterConcept):
        """Step 7: Develop personality and backstory with AI"""
        print("\n📝 STEP 7: PERSONALITY & BACKSTORY")
        print("-" * 30)

        # Personality Trait
        trait_suggestions = await self._get_personality_suggestions(build, concept, "trait")
        print("🎭 Personality Trait Suggestions:")
        for i, trait in enumerate(trait_suggestions, 1):
            print(f"{i}. {trait}")

        build.personality_trait = await self._choose_or_create(
            "personality trait", trait_suggestions
        )

        # Ideal
        ideal_suggestions = await self._get_personality_suggestions(build, concept, "ideal")
        print("\n🌟 Ideal Suggestions:")
        for i, ideal in enumerate(ideal_suggestions, 1):
            print(f"{i}. {ideal}")

        build.ideal = await self._choose_or_create("ideal", ideal_suggestions)

        # Bond
        bond_suggestions = await self._get_personality_suggestions(build, concept, "bond")
        print("\n🔗 Bond Suggestions:")
        for i, bond in enumerate(bond_suggestions, 1):
            print(f"{i}. {bond}")

        build.bond = await self._choose_or_create("bond", bond_suggestions)

        # Flaw
        flaw_suggestions = await self._get_personality_suggestions(build, concept, "flaw")
        print("\n💔 Flaw Suggestions:")
        for i, flaw in enumerate(flaw_suggestions, 1):
            print(f"{i}. {flaw}")

        build.flaw = await self._choose_or_create("flaw", flaw_suggestions)

        # Backstory
        backstory_prompt = await self._generate_backstory_prompt(build, concept)
        print(f"\n📖 AI Backstory Prompt:")
        print(backstory_prompt)

        build.backstory = input(
            "\nWrite your character's backstory (or press Enter to use AI prompt as-is):\n> "
        ).strip() or backstory_prompt

    async def _choose_equipment(self, build: CharacterBuild):
        """Step 8: Choose starting equipment"""
        print("\n📝 STEP 8: STARTING EQUIPMENT")
        print("-" * 30)

        equipment_suggestions = await self._get_equipment_suggestions(build)
        print("🎒 Recommended Starting Equipment:")
        print(equipment_suggestions)

        custom_equipment = input(
            "\nAdd any custom equipment or press Enter to use recommendations:\n> "
        ).strip()

        if custom_equipment:
            build.equipment_choices["custom"] = custom_equipment

    async def _finalize_character(self, build: CharacterBuild) -> Character:
        """Step 9: Create final Character object"""
        print("\n📝 STEP 9: FINAL CHARACTER REVIEW")
        print("=" * 50)

        # Calculate derived stats
        con_modifier = (build.constitution - 10) // 2
        hit_points = self.classes[build.character_class]["hit_die"] + con_modifier

        # Create Character object
        character = Character(
            name=build.name,
            level=1,
            hit_points=hit_points,
            max_hit_points=hit_points,
            armor_class=10 + ((build.dexterity - 10) // 2),  # Base AC
            strength=build.strength,
            dexterity=build.dexterity,
            constitution=build.constitution,
            intelligence=build.intelligence,
            wisdom=build.wisdom,
            charisma=build.charisma
        )

        # Display final character
        await self._display_final_character(character, build)

        # Save character sheet
        await self._save_character_sheet(character, build)

        return character

    # Helper methods for AI integration

    async def _analyze_concept_with_ai(self, concept: str) -> CharacterConcept:
        """Use AI to analyze concept and suggest options"""
        prompt = f"""
Analyze this D&D character concept and provide suggestions:

Character Concept: "{concept}"

Please suggest:
1. 3 appropriate races
2. 3 appropriate classes  
3. 3 appropriate backgrounds
4. 2 personality traits that fit
5. 2 backstory elements

Format as a structured response focusing on D&D 5e options.
"""

        try:
            response = await self.claude.generate_scene(context="", prompt=prompt)
            # Parse AI response into CharacterConcept
            # This would need more sophisticated parsing in a real implementation

            return CharacterConcept(
                concept_description=concept,
                suggested_races=["Human", "Half-Elf", "Variant Human"],  # Default fallback
                suggested_classes=["Fighter", "Rogue", "Ranger"],
                suggested_backgrounds=["Folk Hero", "Outlander", "Soldier"],
                personality_traits=["Determined", "Curious"],
                backstory_elements=["Lost family", "Seeking purpose"]
            )
        except Exception:
            # Fallback if AI unavailable
            return CharacterConcept(concept_description=concept)

    async def _get_name_suggestions(self, concept: CharacterConcept) -> List[str]:
        """Get AI-generated name suggestions"""
        # Implementation would call Claude AI for name suggestions
        return ["Aiden", "Lyra", "Theron", "Zara", "Marcus"]  # Fallback

    async def _get_race_choice_feedback(self, race: str, subrace: str, concept: CharacterConcept) -> str:
        """Get AI feedback on race choice"""
        return f"Excellent choice! {race} fits well with your concept and will provide good synergy."

    async def _get_class_choice_feedback(self, chosen_class: str, race: str, concept: CharacterConcept) -> str:
        """Get AI feedback on class choice"""
        return f"{chosen_class} pairs well with {race} and matches your character concept perfectly."

    async def _get_background_feedback(self, background: str, build: CharacterBuild, concept: CharacterConcept) -> str:
        """Get AI feedback on background choice"""
        return f"The {background} background provides excellent story hooks for your {build.race} {build.character_class}."

    async def _get_ability_score_recommendations(self, build: CharacterBuild, scores: List[int]) -> str:
        """Get AI recommendations for ability score assignment"""
        primary_abilities = self.classes[build.character_class]["primary_ability"]
        return f"For a {build.character_class}, prioritize: {', '.join(primary_abilities).upper()}. Put your highest scores there!"

    async def _get_personality_suggestions(self, build: CharacterBuild, concept: CharacterConcept, trait_type: str) -> \
    List[str]:
        """Get AI suggestions for personality elements"""
        # Would use AI to generate contextual suggestions
        return [f"Sample {trait_type} 1", f"Sample {trait_type} 2", f"Sample {trait_type} 3"]

    async def _generate_backstory_prompt(self, build: CharacterBuild, concept: CharacterConcept) -> str:
        """Generate AI backstory prompt"""
        return f"Born into the {build.background.lower()} life, {build.name} discovered their calling as a {build.character_class.lower()} when..."

    async def _get_equipment_suggestions(self, build: CharacterBuild) -> str:
        """Get AI equipment recommendations"""
        return f"Standard {build.character_class} equipment package with race-appropriate modifications."

    async def _choose_or_create(self, element_type: str, suggestions: List[str]) -> str:
        """Helper for choosing from suggestions or creating custom"""
        while True:
            choice = input(
                f"\nChoose {element_type} (1-{len(suggestions)}) or write your own:\n> "
            ).strip()

            if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                return suggestions[int(choice) - 1]
            elif choice:
                return choice

            print(f"Please choose a {element_type} or enter your own.")

    # Additional helper methods

    def _get_race_bonus_description(self, race: str) -> str:
        """Get description of racial ability bonuses"""
        bonuses = self.races[race]["ability_bonus"]
        bonus_strs = []
        for ability, bonus in bonuses.items():
            if ability != "choice":
                bonus_strs.append(f"+{bonus} {ability.upper()}")
        return ", ".join(bonus_strs) if bonus_strs else "Various bonuses"

    def _get_class_description(self, class_name: str) -> str:
        """Get brief class description"""
        descriptions = {
            "Fighter": "Combat specialist, versatile warrior",
            "Wizard": "Arcane spellcaster, scholarly magic user",
            "Rogue": "Stealthy skill expert, sneak attacker",
            "Cleric": "Divine spellcaster, healer and support",
            "Ranger": "Nature warrior, tracker and hunter",
            "Paladin": "Holy warrior, divine magic and combat",
            "Barbarian": "Primal warrior, rage and strength",
            "Bard": "Versatile performer, magic through music",
            "Druid": "Nature magic, wild shape abilities",
            "Monk": "Martial artist, ki-powered abilities",
            "Sorcerer": "Innate magic, powerful but limited",
            "Warlock": "Pact magic, otherworldly patron"
        }
        return descriptions.get(class_name, "Adventuring class")

    def _get_race_class_synergy(self, race: str, class_name: str) -> str:
        """Check for race/class synergy"""
        race_bonuses = self.races[race]["ability_bonus"]
        class_abilities = self.classes[class_name]["primary_ability"]

        synergy = any(ability[:3] in race_bonuses for ability in class_abilities)
        return "✨" if synergy else ""

    def _roll_4d6_drop_lowest(self) -> List[int]:
        """Roll 4d6, drop lowest for each ability score"""
        scores = []
        for _ in range(6):
            rolls = [self.dice.roll_dice("1d6").total for _ in range(4)]
            rolls.sort(reverse=True)
            scores.append(sum(rolls[:3]))
        return scores

    def _roll_3d6_straight(self) -> List[int]:
        """Roll 3d6 straight for each ability score"""
        return [self.dice.roll_dice("3d6").total for _ in range(6)]

    async def _point_buy_system(self) -> List[int]:
        """Implement point buy system (simplified)"""
        print("Point buy system - starting with all 8s, you have 27 points to spend.")
        print("Cost: 8→9(1pt), 9→10(1pt), 10→11(1pt), 11→12(1pt), 12→13(1pt),")
        print("      13→14(2pts), 14→15(2pts)")

        # Simplified - return standard array for now
        # Full implementation would allow interactive point spending
        return [15, 14, 13, 12, 10, 8]

    async def _display_final_character(self, character: Character, build: CharacterBuild):
        """Display the completed character for review"""
        print(f"\n🎭 {character.name} the {build.race} {build.character_class}")
        print("=" * 60)

        print(f"📖 Background: {build.background}")
        if build.subrace:
            print(f"🧬 Subrace: {build.subrace}")

        print(f"\n📊 Ability Scores:")
        print(f"   Strength:     {character.strength:2d} ({self._get_modifier_string(character.strength)})")
        print(f"   Dexterity:    {character.dexterity:2d} ({self._get_modifier_string(character.dexterity)})")
        print(f"   Constitution: {character.constitution:2d} ({self._get_modifier_string(character.constitution)})")
        print(f"   Intelligence: {character.intelligence:2d} ({self._get_modifier_string(character.intelligence)})")
        print(f"   Wisdom:       {character.wisdom:2d} ({self._get_modifier_string(character.wisdom)})")
        print(f"   Charisma:     {character.charisma:2d} ({self._get_modifier_string(character.charisma)})")

        print(f"\n⚔️ Combat Stats:")
        print(f"   Hit Points: {character.hit_points}")
        print(f"   Armor Class: {character.armor_class}")
        print(f"   Proficiency Bonus: +2")

        print(f"\n🎭 Personality:")
        print(f"   Trait: {build.personality_trait}")
        print(f"   Ideal: {build.ideal}")
        print(f"   Bond: {build.bond}")
        print(f"   Flaw: {build.flaw}")

        print(f"\n📜 Backstory:")
        print(f"   {build.backstory}")

        confirm = input("\n✅ Looks good? (y/n): ").strip().lower()
        return confirm in ['y', 'yes']

    async def _save_character_sheet(self, character: Character, build: CharacterBuild):
        """Save character sheet to campaign files"""
        from pathlib import Path

        campaign_dir = Path(self.settings.campaign_files_path)
        character_file = campaign_dir / "character-sheet.md"

        content = f"""# Character Sheet

## Basic Information
**Name:** {character.name}
**Race:** {build.race}
{"**Subrace:** " + build.subrace if build.subrace else ""}
**Class:** {build.character_class}
{"**Subclass:** " + build.subclass if build.subclass else ""}
**Background:** {build.background}
**Level:** {character.level}

## Ability Scores
**Strength:** {character.strength} ({self._get_modifier_string(character.strength)})
**Dexterity:** {character.dexterity} ({self._get_modifier_string(character.dexterity)})
**Constitution:** {character.constitution} ({self._get_modifier_string(character.constitution)})
**Intelligence:** {character.intelligence} ({self._get_modifier_string(character.intelligence)})
**Wisdom:** {character.wisdom} ({self._get_modifier_string(character.wisdom)})
**Charisma:** {character.charisma} ({self._get_modifier_string(character.charisma)})

## Combat Stats
**Armor Class:** {character.armor_class}
**Hit Points:** {character.hit_points}/{character.max_hit_points}
**Speed:** 30 feet
**Proficiency Bonus:** +2

## Saving Throws
{self._get_saving_throw_profs(build.character_class)}

## Skills
{self._get_skill_profs(build.character_class, build.background)}

## Personality
**Personality Trait:** {build.personality_trait}
**Ideal:** {build.ideal}
**Bond:** {build.bond}
**Flaw:** {build.flaw}

## Backstory
{build.backstory}

## Equipment
{self._get_starting_equipment(build.character_class)}

## Features and Traits
{self._get_racial_traits(build.race)}
{self._get_class_features(build.character_class)}
{self._get_background_features(build.background)}

---
*Character created with AI-assisted character creation system*
"""

        character_file.write_text(content, encoding='utf-8')
        print(f"💾 Character sheet saved to: {character_file}")

    def _get_modifier_string(self, ability_score: int) -> str:
        """Get modifier string for ability score"""
        modifier = (ability_score - 10) // 2
        return f"+{modifier}" if modifier >= 0 else str(modifier)

    def _get_saving_throw_profs(self, class_name: str) -> str:
        """Get saving throw proficiencies for class"""
        saves = self.classes[class_name]["saves"]
        save_names = {"str": "Strength", "dex": "Dexterity", "con": "Constitution",
                      "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma"}
        prof_saves = [save_names[save] for save in saves]
        return "- " + "\n- ".join(prof_saves) + " (Proficient)"

    def _get_skill_profs(self, class_name: str, background: str) -> str:
        """Get skill proficiencies"""
        # Simplified - would be more complex in full implementation
        class_skills = {
            "Fighter": ["Acrobatics", "Athletics"],
            "Wizard": ["Arcana", "History"],
            "Rogue": ["Stealth", "Thieves' Tools"],
            "Cleric": ["Medicine", "Religion"]
        }

        background_skills = {
            "Soldier": ["Athletics", "Intimidation"],
            "Noble": ["History", "Persuasion"],
            "Folk Hero": ["Animal Handling", "Survival"]
        }

        skills = class_skills.get(class_name, ["Perception", "Insight"])
        skills.extend(background_skills.get(background, ["Investigation"]))

        return "- " + "\n- ".join(set(skills)) + " (Proficient)"

    def _get_starting_equipment(self, class_name: str) -> str:
        """Get starting equipment for class"""
        equipment = {
            "Fighter": "- Chain mail\n- Shield\n- Longsword\n- Light crossbow and 20 bolts\n- Explorer's pack",
            "Wizard": "- Quarterstaff\n- Dagger\n- Scholar's pack\n- Spellbook\n- Component pouch",
            "Rogue": "- Leather armor\n- Shortsword\n- Thieves' tools\n- Burglar's pack\n- Dagger (2)",
            "Cleric": "- Scale mail\n- Shield\n- Mace\n- Light crossbow and 20 bolts\n- Priest's pack"
        }
        return equipment.get(class_name, "- Basic adventuring gear")

    def _get_racial_traits(self, race: str) -> str:
        """Get racial traits and abilities"""
        traits = {
            "Human": "**Extra Skill:** Choose one additional skill proficiency\n**Extra Feat:** Choose one feat (if using variant human)",
            "Elf": "**Darkvision:** 60 feet\n**Keen Senses:** Proficiency with Perception\n**Fey Ancestry:** Advantage against charm, can't be magically put to sleep\n**Trance:** 4 hours of trance instead of 8 hours sleep",
            "Dwarf": "**Darkvision:** 60 feet\n**Dwarven Resilience:** Advantage against poison\n**Stonecunning:** Add proficiency bonus to History checks related to stonework",
            "Halfling": "**Lucky:** Reroll natural 1s on attack rolls, ability checks, and saving throws\n**Brave:** Advantage against being frightened\n**Halfling Nimbleness:** Move through space of larger creatures"
        }
        return traits.get(race, "**Racial Traits:** See Player's Handbook for details")

    def _get_class_features(self, class_name: str) -> str:
        """Get 1st level class features"""
        features = {
            "Fighter": "**Fighting Style:** Choose one fighting style\n**Second Wind:** Recover 1d10+1 hit points as bonus action",
            "Wizard": "**Spellcasting:** Cast wizard spells using Intelligence\n**Arcane Recovery:** Recover some spell slots on short rest",
            "Rogue": "**Expertise:** Double proficiency bonus on two skills\n**Sneak Attack:** 1d6 extra damage when you have advantage\n**Thieves' Cant:** Secret language of rogues",
            "Cleric": "**Spellcasting:** Cast cleric spells using Wisdom\n**Divine Domain:** Choose a divine domain\n**Domain Spells:** Always known domain spells"
        }
        return features.get(class_name, "**Class Features:** See Player's Handbook for details")

    def _get_background_features(self, background: str) -> str:
        """Get background features"""
        features = {
            "Soldier": "**Military Rank:** Recognized military authority\n**Equipment:** Insignia of rank, deck of cards",
            "Noble": "**Position of Privilege:** Welcome in high society\n**Equipment:** Signet ring, scroll of pedigree",
            "Folk Hero": "**Rustic Hospitality:** Common folk will help you\n**Equipment:** Smith's tools, set of artisan tools"
        }
        return features.get(background, "**Background Feature:** See Player's Handbook for details")


# Integration with session management
async def integrate_character_creation_with_session():
    """
    Example of how to integrate character creation with the session manager
    """
    from ..campaign.session_manager import SessionManager

    print("🎭 Starting new character creation...")

    # Create character
    creator = CharacterCreator()
    character = await creator.create_character()

    # Start session with new character
    session_manager = SessionManager()

    # Override the character extraction to use our new character
    session_manager._extract_character = lambda campaign_data, char_name=None: character

    # Start session
    session = await session_manager.start_new_session(character.name)

    print(f"🎮 Session started with {character.name}!")
    return session, character


# CLI integration function
async def character_creation_menu():
    """Menu option for character creation in the enhanced CLI"""
    print("\n🎭 CHARACTER CREATION")
    print("=" * 40)
    print("1. Create New Character (AI-Assisted)")
    print("2. Quick Character (Random Generation)")
    print("3. Import Character from File")
    print("0. Back to Main Menu")

    choice = input("\n👉 Choose option: ").strip()

    if choice == "1":
        creator = CharacterCreator()
        character = await creator.create_character()
        return character
    elif choice == "2":
        return await quick_character_creation()
    elif choice == "3":
        return await import_character_from_file()
    else:
        return None


async def quick_character_creation() -> Character:
    """Quick random character generation for testing"""
    import random

    races = ["Human", "Elf", "Dwarf", "Halfling"]
    classes = ["Fighter", "Wizard", "Rogue", "Cleric"]
    names = ["Aiden", "Luna", "Thorin", "Zara", "Marcus", "Elara"]

    # Random selections
    race = random.choice(races)
    char_class = random.choice(classes)
    name = random.choice(names)

    # Random ability scores (4d6 drop lowest)
    roller = DiceRoller()
    scores = []
    for _ in range(6):
        rolls = [roller.roll_dice("1d6").total for _ in range(4)]
        rolls.sort(reverse=True)
        scores.append(sum(rolls[:3]))

    print(f"🎲 Generated {name} the {race} {char_class}")

    character = Character(
        name=name,
        level=1,
        hit_points=10,  # Simplified
        max_hit_points=10,
        strength=scores[0],
        dexterity=scores[1],
        constitution=scores[2],
        intelligence=scores[3],
        wisdom=scores[4],
        charisma=scores[5]
    )

    return character


async def import_character_from_file() -> Optional[Character]:
    """Import character from existing character sheet file"""
    print("📁 Character import not yet implemented")
    return None