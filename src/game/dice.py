# src/game/dice.py
"""
D&D Dice Rolling System
Handles all dice mechanics for the game - like RNG for infrastructure testing but more fun!
"""

import random
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
from ..campaign.models import DiceRoll


class DiceRoller:
    """
    Professional-grade dice rolling system for D&D
    Your SRE background will appreciate the comprehensive error handling!
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialize dice roller with optional seed for testing"""
        if seed is not None:
            random.seed(seed)

    def roll_dice(self, dice_notation: str, advantage: bool = False, disadvantage: bool = False) -> DiceRoll:
        """
        Roll dice using standard D&D notation

        Examples:
        - "1d20" -> Roll one 20-sided die
        - "2d6+3" -> Roll two 6-sided dice, add 3
        - "1d8-1" -> Roll one 8-sided die, subtract 1
        - "3d4" -> Roll three 4-sided dice
        """
        count, dice_type, modifier = self._parse_dice_notation(dice_notation)

        # Create and calculate the roll
        roll = DiceRoll(
            dice_type=dice_type,
            count=count,
            modifier=modifier,
            advantage=advantage,
            disadvantage=disadvantage
        )

        return roll

    def roll_ability_scores(self) -> List[int]:
        """
        Roll ability scores using 4d6 drop lowest method
        Returns 6 ability scores
        """
        ability_scores = []

        for _ in range(6):
            # Roll 4d6, drop lowest
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort(reverse=True)
            score = sum(rolls[:3])  # Take highest 3
            ability_scores.append(score)

        return ability_scores

    def roll_hit_points(self, level: int, hit_die: int, constitution_modifier: int = 0) -> int:
        """
        Roll hit points for character level up
        First level gets max hit die + con modifier
        Subsequent levels roll hit die + con modifier
        """
        if level == 1:
            # First level gets maximum hit die
            return hit_die + constitution_modifier

        # Roll for the new level
        roll = random.randint(1, hit_die)
        return max(1, roll + constitution_modifier)  # Minimum 1 HP per level

    def roll_skill_check(self, difficulty_class: int, modifier: int = 0,
                         advantage: bool = False, disadvantage: bool = False) -> Tuple[bool, DiceRoll]:
        """
        Roll a skill check against a difficulty class
        Returns (success, roll_result)
        """
        roll = self.roll_dice("1d20", advantage=advantage, disadvantage=disadvantage)
        roll.modifier = modifier
        roll.total = sum(roll.individual_rolls) + modifier

        success = roll.total >= difficulty_class
        return success, roll

    def roll_saving_throw(self, save_type: str, base_modifier: int = 0, proficient: bool = False,
                          proficiency_bonus: int = 2, advantage: bool = False, disadvantage: bool = False) -> Tuple[
        bool, DiceRoll]:
        """
        Roll a saving throw
        save_type: str - "strength", "dexterity", etc.
        """
        modifier = base_modifier
        if proficient:
            modifier += proficiency_bonus

        roll = self.roll_dice("1d20", advantage=advantage, disadvantage=disadvantage)
        roll.modifier = modifier
        roll.total = sum(roll.individual_rolls) + modifier

        # Success depends on what we're saving against - return roll for GM to determine
        return True, roll  # Let the GM/AI determine success based on context

    def roll_attack(self, attack_bonus: int = 0, advantage: bool = False, disadvantage: bool = False) -> DiceRoll:
        """Roll an attack roll"""
        roll = self.roll_dice("1d20", advantage=advantage, disadvantage=disadvantage)
        roll.modifier = attack_bonus
        roll.total = sum(roll.individual_rolls) + attack_bonus
        return roll

    def roll_damage(self, damage_dice: str, bonus: int = 0) -> DiceRoll:
        """Roll damage dice"""
        roll = self.roll_dice(damage_dice)
        roll.modifier = bonus
        roll.total = sum(roll.individual_rolls) + bonus
        return roll

    def roll_initiative(self, dexterity_modifier: int = 0) -> DiceRoll:
        """Roll initiative"""
        roll = self.roll_dice("1d20")
        roll.modifier = dexterity_modifier
        roll.total = sum(roll.individual_rolls) + dexterity_modifier
        return roll

    def roll_percentile(self) -> int:
        """Roll percentile dice (1-100)"""
        return random.randint(1, 100)

    def roll_random_encounter(self, encounter_table: List[str]) -> str:
        """Roll on a random encounter table"""
        if not encounter_table:
            return "No encounters available"

        index = random.randint(0, len(encounter_table) - 1)
        return encounter_table[index]

    # Private helper methods

    def _parse_dice_notation(self, notation: str) -> Tuple[int, int, int]:
        """
        Parse dice notation like "2d6+3" into (count, dice_type, modifier)

        Supported formats:
        - "1d20" -> (1, 20, 0)
        - "2d6+3" -> (2, 6, 3)
        - "1d8-1" -> (1, 8, -1)
        - "d20" -> (1, 20, 0)
        - "3d4" -> (3, 4, 0)
        """
        # Clean up the notation
        notation = notation.strip().lower().replace(" ", "")

        # Pattern: optional count, 'd', dice type, optional modifier
        pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
        match = re.match(pattern, notation)

        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")

        # Extract parts
        count_str, dice_type_str, modifier_str = match.groups()

        # Parse count (default to 1 if not specified)
        count = int(count_str) if count_str else 1

        # Parse dice type
        dice_type = int(dice_type_str)

        # Parse modifier (default to 0 if not specified)
        modifier = int(modifier_str) if modifier_str else 0

        # Validate values
        if count <= 0:
            raise ValueError("Dice count must be positive")
        if dice_type <= 0:
            raise ValueError("Dice type must be positive")
        if count > 100:
            raise ValueError("Cannot roll more than 100 dice at once")
        if dice_type > 100:
            raise ValueError("Dice type cannot exceed 100 sides")

        return count, dice_type, modifier

    def get_advantage_description(self, advantage: bool, disadvantage: bool) -> str:
        """Get description of advantage/disadvantage state"""
        if advantage and disadvantage:
            return "Normal (advantage and disadvantage cancel out)"
        elif advantage:
            return "Advantage (roll twice, take higher)"
        elif disadvantage:
            return "Disadvantage (roll twice, take lower)"
        else:
            return "Normal roll"


# Skill check difficulty classes (standard D&D 5e)
class DifficultyClass:
    """Standard D&D difficulty classes"""
    TRIVIAL = 5
    EASY = 10
    MEDIUM = 15
    HARD = 20
    VERY_HARD = 25
    NEARLY_IMPOSSIBLE = 30

    @classmethod
    def get_description(cls, dc: int) -> str:
        """Get description for a difficulty class"""
        if dc <= cls.TRIVIAL:
            return "Trivial"
        elif dc <= cls.EASY:
            return "Easy"
        elif dc <= cls.MEDIUM:
            return "Medium"
        elif dc <= cls.HARD:
            return "Hard"
        elif dc <= cls.VERY_HARD:
            return "Very Hard"
        else:
            return "Nearly Impossible"


# Common dice presets
class CommonRolls:
    """Common dice roll presets"""

    @staticmethod
    def perception_check(wisdom_modifier: int = 0, proficient: bool = False, proficiency_bonus: int = 2) -> str:
        """Generate perception check notation"""
        modifier = wisdom_modifier + (proficiency_bonus if proficient else 0)
        return f"1d20{'+' if modifier >= 0 else ''}{modifier}"

    @staticmethod
    def stealth_check(dexterity_modifier: int = 0, proficient: bool = False, proficiency_bonus: int = 2) -> str:
        """Generate stealth check notation"""
        modifier = dexterity_modifier + (proficiency_bonus if proficient else 0)
        return f"1d20{'+' if modifier >= 0 else ''}{modifier}"

    @staticmethod
    def persuasion_check(charisma_modifier: int = 0, proficient: bool = False, proficiency_bonus: int = 2) -> str:
        """Generate persuasion check notation"""
        modifier = charisma_modifier + (proficiency_bonus if proficient else 0)
        return f"1d20{'+' if modifier >= 0 else ''}{modifier}"

    @staticmethod
    def investigation_check(intelligence_modifier: int = 0, proficient: bool = False,
                            proficiency_bonus: int = 2) -> str:
        """Generate investigation check notation"""
        modifier = intelligence_modifier + (proficiency_bonus if proficient else 0)
        return f"1d20{'+' if modifier >= 0 else ''}{modifier}"


# Dice rolling utilities
class DiceUtils:
    """Utility functions for dice operations"""

    @staticmethod
    def calculate_average(dice_notation: str) -> float:
        """Calculate average roll for dice notation"""
        roller = DiceRoller()
        count, dice_type, modifier = roller._parse_dice_notation(dice_notation)

        # Average of a die is (max + min) / 2 = (dice_type + 1) / 2
        average_per_die = (dice_type + 1) / 2
        total_average = (count * average_per_die) + modifier

        return total_average

    @staticmethod
    def calculate_range(dice_notation: str) -> Tuple[int, int]:
        """Calculate minimum and maximum possible rolls"""
        roller = DiceRoller()
        count, dice_type, modifier = roller._parse_dice_notation(dice_notation)

        minimum = count + modifier  # All 1s
        maximum = (count * dice_type) + modifier  # All max

        return minimum, maximum

    @staticmethod
    def format_roll_result(roll: DiceRoll, include_breakdown: bool = True) -> str:
        """Format a dice roll result for display"""
        result_parts = []

        # Basic result
        dice_notation = f"{roll.count}d{roll.dice_type}"
        if roll.modifier > 0:
            dice_notation += f"+{roll.modifier}"
        elif roll.modifier < 0:
            dice_notation += f"{roll.modifier}"

        result_parts.append(f"🎲 {dice_notation}: **{roll.total}**")

        # Breakdown
        if include_breakdown and len(roll.individual_rolls) > 1:
            rolls_str = ", ".join(map(str, roll.individual_rolls))
            result_parts.append(f"   Rolls: [{rolls_str}]")

        # Special results
        if roll.is_critical:
            result_parts.append("   🌟 **CRITICAL SUCCESS!**")
        elif roll.is_fumble:
            result_parts.append("   💥 **CRITICAL FAILURE!**")

        # Advantage/Disadvantage
        if roll.advantage:
            result_parts.append("   ⬆️ (Advantage)")
        elif roll.disadvantage:
            result_parts.append("   ⬇️ (Disadvantage)")

        return "\n".join(result_parts)


# Testing and validation functions
def test_dice_roller():
    """Test the dice roller functionality"""
    roller = DiceRoller(seed=42)  # Fixed seed for reproducible tests

    print("🧪 Testing Dice Roller")
    print("=" * 30)

    # Test basic rolls
    test_cases = [
        "1d20",
        "2d6+3",
        "1d8-1",
        "3d4",
        "d6",  # Should default to 1d6
    ]

    for notation in test_cases:
        try:
            result = roller.roll_dice(notation)
            print(f"✅ {notation}: {result}")
        except Exception as e:
            print(f"❌ {notation}: {e}")

    # Test advantage/disadvantage
    print(f"\n🎯 Advantage/Disadvantage Tests:")
    adv_roll = roller.roll_dice("1d20", advantage=True)
    print(f"Advantage: {adv_roll}")

    dis_roll = roller.roll_dice("1d20", disadvantage=True)
    print(f"Disadvantage: {dis_roll}")

    # Test skill checks
    print(f"\n🎪 Skill Check Tests:")
    success, roll = roller.roll_skill_check(difficulty_class=15, modifier=5)
    print(f"DC 15 check with +5: {roll} ({'Success' if success else 'Failure'})")

    # Test utility functions
    print(f"\n📊 Utility Tests:")
    avg = DiceUtils.calculate_average("2d6+3")
    min_val, max_val = DiceUtils.calculate_range("2d6+3")
    print(f"2d6+3 - Average: {avg}, Range: {min_val}-{max_val}")


if __name__ == "__main__":
    test_dice_roller()