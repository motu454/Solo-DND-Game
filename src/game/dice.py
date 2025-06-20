# src/game/dice.py
"""
D&D Dice Rolling System
Handles all dice mechanics for the game - like RNG for infrastructure testing but more fun!
"""

import random
import re
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

# Fix the relative import issue by using absolute import or local import
try:
    from campaign.models import DiceRoll
except ImportError:
    # Fallback: define DiceRoll locally if import fails
    @dataclass
    class DiceRoll:
        dice_type: int
        num_dice: int
        modifier: int
        total: int
        rolls: List[int]
        advantage: bool = False
        disadvantage: bool = False


@dataclass
class DiceResult:
    """Result of a dice roll"""
    total: int
    rolls: List[int]
    dice_type: int
    num_dice: int
    modifier: int = 0
    advantage: bool = False
    disadvantage: bool = False
    critical: bool = False

    def __str__(self) -> str:
        """String representation of dice result"""
        roll_str = " + ".join(map(str, self.rolls))
        if self.modifier != 0:
            mod_str = f" + {self.modifier}" if self.modifier > 0 else f" - {abs(self.modifier)}"
            return f"[{roll_str}]{mod_str} = {self.total}"
        return f"[{roll_str}] = {self.total}"


class DiceRoller:
    """
    Professional-grade dice rolling system for D&D
    Your SRE background will appreciate the comprehensive error handling!
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialize dice roller with optional seed for testing"""
        if seed is not None:
            random.seed(seed)
        self.roll_history: List[DiceResult] = []

    def roll(self, dice_type: int, count: int = 1, modifier: int = 0,
             advantage: bool = False, disadvantage: bool = False) -> DiceResult:
        """
        Roll dice with D&D 5e mechanics

        Args:
            dice_type: Type of die (4, 6, 8, 10, 12, 20, 100)
            count: Number of dice to roll
            modifier: Modifier to add to total
            advantage: Roll twice, take higher (only works with single d20)
            disadvantage: Roll twice, take lower (only works with single d20)

        Returns:
            DiceResult with all roll information
        """
        if dice_type not in [4, 6, 8, 10, 12, 20, 100]:
            raise ValueError(f"Invalid dice type: d{dice_type}")

        if count <= 0:
            raise ValueError("Number of dice must be positive")

        # Handle advantage/disadvantage (only for single d20)
        if (advantage or disadvantage) and (dice_type != 20 or count != 1):
            raise ValueError("Advantage/disadvantage only works with single d20 rolls")

        rolls = []

        if advantage or disadvantage:
            # Roll twice for advantage/disadvantage
            roll1 = random.randint(1, dice_type)
            roll2 = random.randint(1, dice_type)

            if advantage:
                chosen_roll = max(roll1, roll2)
                rolls = [roll1, roll2]  # Keep both for display
            else:  # disadvantage
                chosen_roll = min(roll1, roll2)
                rolls = [roll1, roll2]  # Keep both for display

            # For calculation, use only the chosen roll
            final_rolls = [chosen_roll]
        else:
            # Normal rolling
            for _ in range(count):
                roll = random.randint(1, dice_type)
                rolls.append(roll)
            final_rolls = rolls

        total = sum(final_rolls) + modifier

        # Check for critical hit/miss (natural 20/1 on d20)
        critical = False
        if dice_type == 20 and count == 1:
            natural_roll = final_rolls[0] if not (advantage or disadvantage) else max(rolls) if advantage else min(
                rolls)
            critical = natural_roll == 20 or natural_roll == 1

        result = DiceResult(
            total=total,
            rolls=rolls,
            dice_type=dice_type,
            num_dice=count,
            modifier=modifier,
            advantage=advantage,
            disadvantage=disadvantage,
            critical=critical
        )

        self.roll_history.append(result)
        return result

    def skill_check(self, modifier: int, difficulty_class: int = 15,
                    advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Make a D&D skill check

        Args:
            modifier: Character's skill modifier
            difficulty_class: Target DC
            advantage: Roll with advantage
            disadvantage: Roll with disadvantage

        Returns:
            Dict with check results
        """
        result = self.roll(20, 1, modifier, advantage, disadvantage)
        success = result.total >= difficulty_class

        return {
            'result': result.total,
            'success': success,
            'dc': difficulty_class,
            'roll_info': result,
            'critical': result.critical
        }

    def parse_dice_notation(self, notation: str) -> DiceResult:
        """
        Parse standard dice notation (e.g., "2d6+3", "1d20 adv")

        Args:
            notation: Dice notation string

        Returns:
            DiceResult from parsed and rolled dice
        """
        notation = notation.lower().strip()

        # Check for advantage/disadvantage
        advantage = 'adv' in notation or 'advantage' in notation
        disadvantage = 'dis' in notation or 'disadvantage' in notation

        # Remove advantage/disadvantage keywords
        notation = re.sub(r'\b(adv|advantage|dis|disadvantage)\b', '', notation).strip()

        # Parse dice notation: XdY+Z or XdY-Z
        pattern = r'(\d*)d(\d+)([+-]\d+)?'
        match = re.match(pattern, notation)

        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")

        count_str, dice_type_str, modifier_str = match.groups()

        count = int(count_str) if count_str else 1
        dice_type = int(dice_type_str)
        modifier = int(modifier_str) if modifier_str else 0

        return self.roll(dice_type, count, modifier, advantage, disadvantage)


class DiceUtils:
    """Utility functions for dice operations"""

    @staticmethod
    def format_roll_result(result: DiceResult) -> str:
        """Format dice result for display"""
        if result.advantage:
            return f"🎲 {result.dice_type}: [{', '.join(map(str, result.rolls))}] (advantage) → {result.total}"
        elif result.disadvantage:
            return f"🎲 {result.dice_type}: [{', '.join(map(str, result.rolls))}] (disadvantage) → {result.total}"
        else:
            roll_display = ', '.join(map(str, result.rolls))
            if result.modifier != 0:
                mod_str = f"+{result.modifier}" if result.modifier > 0 else str(result.modifier)
                return f"🎲 {result.num_dice}d{result.dice_type}{mod_str}: [{roll_display}] → {result.total}"
            else:
                return f"🎲 {result.num_dice}d{result.dice_type}: [{roll_display}] → {result.total}"

    @staticmethod
    def get_dice_emoji(dice_type: int) -> str:
        """Get emoji for dice type"""
        emoji_map = {
            4: "🔸",
            6: "⚅",
            8: "🔶",
            10: "🔹",
            12: "🔷",
            20: "🎲",
            100: "💯"
        }
        return emoji_map.get(dice_type, "🎲")

    @staticmethod
    def calculate_average_damage(dice_notation: str) -> float:
        """Calculate average damage for dice notation"""
        # This is a simplified calculation
        # You could extend this for more complex damage calculations
        pattern = r'(\d*)d(\d+)([+-]\d+)?'
        match = re.match(pattern, dice_notation.lower())

        if not match:
            raise ValueError(f"Invalid dice notation: {dice_notation}")

        count_str, dice_type_str, modifier_str = match.groups()

        count = int(count_str) if count_str else 1
        dice_type = int(dice_type_str)
        modifier = int(modifier_str) if modifier_str else 0

        average_per_die = (dice_type + 1) / 2
        return (count * average_per_die) + modifier


# Example usage for testing
if __name__ == "__main__":
    roller = DiceRoller()

    # Test basic rolling
    result = roller.roll(20, 1, 5)
    print(f"Basic roll: {DiceUtils.format_roll_result(result)}")

    # Test advantage
    result = roller.roll(20, 1, 3, advantage=True)
    print(f"Advantage roll: {DiceUtils.format_roll_result(result)}")

    # Test skill check
    check = roller.skill_check(modifier=7, difficulty_class=15)
    print(f"Skill check: {check['result']} vs DC {check['dc']} - {'SUCCESS' if check['success'] else 'FAILURE'}")

    # Test dice notation parsing
    result = roller.parse_dice_notation("2d6+3")
    print(f"Parsed notation: {DiceUtils.format_roll_result(result)}")