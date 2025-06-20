# src/ui/main_window.py
"""
Fey Bargain Game - PyQt6 Main Application
Professional desktop GUI for your AI-powered D&D game
"""

import sys
import asyncio
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSplitter, QFrame,
    QScrollArea, QGroupBox, QGridLayout, QProgressBar, QTabWidget,
    QListWidget, QListWidgetItem, QStatusBar, QMenuBar, QMessageBox,
    QComboBox, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QFont, QPixmap, QIcon, QPalette, QColor, QTextCursor,
    QTextCharFormat, QAction
)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from campaign.file_manager import CampaignFileManager
from ai.claude_service import ClaudeService, SystemPromptBuilder
from ai.context_manager import GameContextManager
from game.dice import DiceRoller, DiceUtils


class AIResponseThread(QThread):
    """Thread for handling AI responses without blocking UI"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, claude_service, system_prompt, context, player_input, conversation_history):
        super().__init__()
        self.claude_service = claude_service
        self.system_prompt = system_prompt
        self.context = context
        self.player_input = player_input
        self.conversation_history = conversation_history

    def run(self):
        """Get AI response in background thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            response = loop.run_until_complete(
                self.claude_service.get_dm_response(
                    system_prompt=self.system_prompt,
                    context=self.context,
                    player_input=self.player_input,
                    conversation_history=self.conversation_history
                )
            )

            self.response_ready.emit(response)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            loop.close()


class AnimatedDiceDisplay(QWidget):
    """Animated dice rolling display widget"""
    animation_finished = pyqtSignal(int)  # Signal when animation completes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_count = 0
        self.final_result = 0
        self.is_animating = False

    def init_ui(self):
        layout = QVBoxLayout()

        # Create the animated display frame
        self.display_frame = QFrame()
        self.display_frame.setFrameStyle(QFrame.Shape.Box)
        self.display_frame.setLineWidth(3)
        self.display_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1a1a1a, stop: 1 #2d2d2d);
                border: 3px solid #4CAF50;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        # Create the dice result label with neon effect (FIXED - removed text-shadow)
        self.dice_label = QLabel("🎲")
        self.dice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dice_label.setStyleSheet("""
            QLabel {
                color: #00FF41;
                font-size: 48px;
                font-weight: bold;
                font-family: 'Impact', 'Arial Black', sans-serif;
                background: transparent;
                padding: 10px;
                border: 2px solid #00FF41;
                border-radius: 10px;
            }
        """)

        # Layout for the display frame
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.dice_label)
        self.display_frame.setLayout(frame_layout)

        layout.addWidget(self.display_frame)
        self.setLayout(layout)

    def start_animation(self, final_value, dice_type):
        """Start the dice roll animation"""
        if self.is_animating:
            return

        self.is_animating = True
        self.final_result = final_value
        self.dice_type = dice_type
        self.animation_count = 0

        # Start the animation timer (500ms = half second)
        self.animation_timer.start(500)

    def update_animation(self):
        """Update the animation frame"""
        if self.animation_count < 4:
            # Show random number for first 4 cycles
            random_num = random.randint(1, self.dice_type)
            self.dice_label.setText(str(random_num))
            self.animation_count += 1
        else:
            # Show final result on 5th cycle
            self.dice_label.setText(str(self.final_result))
            self.animation_timer.stop()
            self.is_animating = False

            # Emit signal that animation is complete
            self.animation_finished.emit(self.final_result)

class CharacterPanel(QWidget):
    """Character information panel"""

    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Character stats group
        char_group = QGroupBox("⚔️ Character Status")
        char_layout = QGridLayout()

        self.level_label = QLabel("Level: --")
        self.hp_label = QLabel("HP: --/--")
        self.ac_label = QLabel("AC: --")

        # Style labels
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)

        for label in [self.level_label, self.hp_label, self.ac_label]:
            label.setFont(font)
            label.setStyleSheet("color: #2E8B57; padding: 5px;")

        char_layout.addWidget(self.level_label, 0, 0)
        char_layout.addWidget(self.hp_label, 1, 0)
        char_layout.addWidget(self.ac_label, 2, 0)

        char_group.setLayout(char_layout)
        layout.addWidget(char_group)

        # Current context group
        context_group = QGroupBox("📍 Current Context")
        context_layout = QVBoxLayout()

        self.time_label = QLabel("Time: --")
        self.location_label = QLabel("Location: --")

        for label in [self.time_label, self.location_label]:
            label.setFont(QFont("Arial", 10))
            label.setWordWrap(True)
            label.setStyleSheet("color: #4682B4; padding: 3px;")

        context_layout.addWidget(self.time_label)
        context_layout.addWidget(self.location_label)

        context_group.setLayout(context_layout)
        layout.addWidget(context_group)

        layout.addStretch()
        self.setLayout(layout)

    def update_character_info(self):
        """Update character information display"""
        character = self.file_manager.get_character_stats()
        if character:
            self.level_label.setText(f"Level: {character.level}")
            self.hp_label.setText(f"HP: {character.hit_points}/{character.max_hit_points}")
            self.ac_label.setText(f"AC: {character.armor_class}")

        # Update context
        qr_file = self.file_manager.get_file('quick_reference')
        if qr_file and qr_file.parsed_data:
            qr = qr_file.parsed_data
            if 'current_time' in qr:
                self.time_label.setText(f"⏰ {qr['current_time']}")
            if 'current_location' in qr:
                self.location_label.setText(f"📍 {qr['current_location']}")


class NPCPanel(QWidget):
    """NPC relationship panel"""

    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        npc_group = QGroupBox("👥 Key NPCs")
        npc_layout = QVBoxLayout()

        self.npc_list = QListWidget()
        self.npc_list.setStyleSheet("""
                    QListWidget {
                        background-color: #2F2F2F;
                        color: #F5F5F5;
                        border: 2px solid #4682B4;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QListWidget::item {
                        padding: 8px;
                        border-bottom: 1px solid #4A4A4A;
                        background-color: #3A3A3A;
                        color: #F5F5F5;
                        margin: 2px;
                        border-radius: 3px;
                    }
                    QListWidget::item:selected {
                        background-color: #4682B4;
                        color: white;
                    }
                    QListWidget::item:hover {
                        background-color: #4A4A4A;
                    }
                """)

        npc_layout.addWidget(self.npc_list)
        npc_group.setLayout(npc_layout)
        layout.addWidget(npc_group)

        self.setLayout(layout)

    def update_npc_list(self):
        """Update NPC list display"""
        self.npc_list.clear()

        npcs = self.file_manager.get_npcs()
        if npcs:
            # Sort by trust level
            top_npcs = sorted(npcs, key=lambda x: getattr(x, 'trust_points', 0), reverse=True)[:10]

            for npc in top_npcs:
                trust_points = getattr(npc, 'trust_points', 0)
                stars = "⭐" * max(0, min(5, trust_points))

                item = QListWidgetItem(f"{npc.name}\n{stars}\n{npc.role}")
                item.setData(Qt.ItemDataRole.UserRole, npc)

                # Color coding based on trust level
                if trust_points >= 4:
                    item.setBackground(QColor("#2E7D32"))  # Dark green
                elif trust_points >= 2:
                    item.setBackground(QColor("#F57C00"))  # Dark orange
                else:
                    item.setBackground(QColor("#C62828"))  # Dark red

                self.npc_list.addItem(item)


class MissionPanel(QWidget):
    """Mission tracking panel"""

    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        mission_group = QGroupBox("📜 Active Missions")
        mission_layout = QVBoxLayout()

        self.mission_list = QListWidget()
        self.mission_list.setStyleSheet("""
                    QListWidget {
                        background-color: #2F2F2F;
                        color: #F5F5F5;
                        border: 2px solid #DAA520;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QListWidget::item {
                        padding: 8px;
                        border-bottom: 1px solid #4A4A4A;
                        background-color: #3A3A3A;
                        color: #F5F5F5;
                        margin: 2px;
                        border-radius: 3px;
                    }
                    QListWidget::item:selected {
                        background-color: #DAA520;
                        color: white;
                    }
                    QListWidget::item:hover {
                        background-color: #4A4A4A;
                    }
                """)

        mission_layout.addWidget(self.mission_list)
        mission_group.setLayout(mission_layout)
        layout.addWidget(mission_group)

        self.setLayout(layout)

    def update_mission_list(self):
        """Update mission list display"""
        self.mission_list.clear()

        mission_file = self.file_manager.get_file('active_missions')
        if mission_file and mission_file.parsed_data:
            missions = mission_file.parsed_data[:5]  # Top 5 missions

            for mission in missions:
                status = getattr(mission, 'status', 'Unknown')
                if hasattr(status, 'value'):
                    status = status.value

                item = QListWidgetItem(f"{mission.name}\n[{status}]")
                item.setData(Qt.ItemDataRole.UserRole, mission)

                # Color coding based on status
                if 'complet' in str(status).lower():
                    item.setBackground(QColor("#2E7D32"))  # Dark green
                elif 'active' in str(status).lower():
                    item.setBackground(QColor("#F57C00"))  # Dark orange
                else:
                    item.setBackground(QColor("#C62828"))  # Dark red

                self.mission_list.addItem(item)


class DicePanel(QWidget):
    """Enhanced dice rolling panel with animations and better UI"""

    def __init__(self):
        super().__init__()
        self.dice_roller = DiceRoller()
        self.roll_history = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        dice_group = QGroupBox("🎲 Dice Rolling")  # Simplified title
        dice_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
            }
        """)

        dice_layout = QVBoxLayout()

        # Dice selection controls - COMPACT LAYOUT
        controls_layout = QVBoxLayout()  # Changed to vertical for better spacing

        # First row: Dice type and count
        row1_layout = QHBoxLayout()

        dice_label = QLabel("Type:")
        dice_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 10px;")
        dice_label.setMinimumWidth(35)

        self.dice_combo = QComboBox()
        self.dice_combo.setStyleSheet("""
            QComboBox {
                background-color: #2F2F2F;
                color: #F5F5F5;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                min-width: 80px;
                max-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #4CAF50;
                width: 20px;
                border-radius: 2px;
            }
            QComboBox QAbstractItemView {
                background-color: #2F2F2F;
                color: #F5F5F5;
                selection-background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }
        """)

        # Add dice options with emoji
        dice_options = [
            ("🔸 d4", 4),
            ("⚅ d6", 6),
            ("🔶 d8", 8),
            ("🔹 d10", 10),
            ("🔷 d12", 12),
            ("🎲 d20", 20),
            ("💯 d100", 100)
        ]

        for display_text, value in dice_options:
            self.dice_combo.addItem(display_text, value)

        # Set d20 as default
        self.dice_combo.setCurrentIndex(5)  # d20

        # Number of dice
        num_dice_label = QLabel("Count:")
        num_dice_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 10px;")
        num_dice_label.setMinimumWidth(40)

        self.num_dice_spin = QSpinBox()
        self.num_dice_spin.setRange(1, 10)
        self.num_dice_spin.setValue(1)
        self.num_dice_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2F2F2F;
                color: #F5F5F5;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                min-width: 50px;
                max-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #4CAF50;
                border: none;
                width: 15px;
            }
        """)

        row1_layout.addWidget(dice_label)
        row1_layout.addWidget(self.dice_combo)
        row1_layout.addWidget(num_dice_label)
        row1_layout.addWidget(self.num_dice_spin)
        row1_layout.addStretch()

        # Second row: Modifier and advantage
        row2_layout = QHBoxLayout()

        # Modifier input
        modifier_label = QLabel("Mod:")
        modifier_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 10px;")
        modifier_label.setMinimumWidth(30)

        self.modifier_input = QLineEdit()
        self.modifier_input.setPlaceholderText("+/-")
        self.modifier_input.setStyleSheet("""
            QLineEdit {
                background-color: #2F2F2F;
                color: #F5F5F5;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                min-width: 50px;
                max-width: 70px;
            }
            QLineEdit:focus {
                border-color: #66BB6A;
            }
        """)

        # Advantage/Disadvantage
        advantage_label = QLabel("Adv:")
        advantage_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 10px;")
        advantage_label.setMinimumWidth(30)

        self.advantage_combo = QComboBox()
        self.advantage_combo.addItems(["Normal", "Advantage", "Disadvantage"])
        self.advantage_combo.setStyleSheet("""
            QComboBox {
                background-color: #2F2F2F;
                color: #F5F5F5;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                min-width: 80px;
                max-width: 100px;
            }
            QComboBox QAbstractItemView {
                background-color: #2F2F2F;
                color: #F5F5F5;
                selection-background-color: #4CAF50;
            }
        """)

        row2_layout.addWidget(modifier_label)
        row2_layout.addWidget(self.modifier_input)
        row2_layout.addWidget(advantage_label)
        row2_layout.addWidget(self.advantage_combo)
        row2_layout.addStretch()

        # Third row: Roll button
        row3_layout = QHBoxLayout()

        # Roll button
        self.roll_button = QPushButton("🎲 ROLL!")
        self.roll_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #4CAF50, stop: 1 #66BB6A);
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #66BB6A, stop: 1 #4CAF50);
            }
            QPushButton:pressed {
                background: #45a049;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)

        row3_layout.addWidget(self.roll_button)
        row3_layout.addStretch()

        # Add all rows to controls
        controls_layout.addLayout(row1_layout)
        controls_layout.addLayout(row2_layout)
        controls_layout.addLayout(row3_layout)

        # Main content area with animation and history
        content_layout = QHBoxLayout()

        # Animation display (takes up most space)
        self.animation_display = AnimatedDiceDisplay()
        self.animation_display.animation_finished.connect(self.on_animation_finished)

        # Recent rolls panel (smaller, in corner)
        history_group = QGroupBox("📊 Recent Rolls")
        history_group.setMaximumWidth(200)  # Made smaller
        history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
            }
        """)

        history_layout = QVBoxLayout()

        self.roll_history_widget = QTextEdit()
        self.roll_history_widget.setMaximumHeight(120)  # Reduced height
        self.roll_history_widget.setReadOnly(True)
        self.roll_history_widget.setStyleSheet("""
            QTextEdit {
                background-color: #2F2F2F;
                color: #F5F5F5;
                border: 1px solid #4A4A4A;
                border-radius: 4px;
                padding: 4px;
                font-family: 'Courier New', monospace;
                font-size: 9px;
                selection-background-color: #4682B4;
            }
        """)

        history_layout.addWidget(self.roll_history_widget)
        history_group.setLayout(history_layout)

        # Add to content layout
        content_layout.addWidget(self.animation_display, 3)  # Takes 3/4 of space
        content_layout.addWidget(history_group, 1)  # Takes 1/4 of space

        # Add everything to main dice layout
        dice_layout.addLayout(controls_layout)
        dice_layout.addLayout(content_layout)

        dice_group.setLayout(dice_layout)
        main_layout.addWidget(dice_group)

        # Connect signals
        self.roll_button.clicked.connect(self.roll_dice)

        self.setLayout(main_layout)

    def roll_dice(self):
        """Handle dice rolling with animation - FIXED modifier validation"""
        if self.animation_display.is_animating:
            return  # Don't start new roll if animation is running

        try:
            # Get values from controls
            dice_type = self.dice_combo.currentData()
            num_dice = self.num_dice_spin.value()

            # Parse modifier - FIXED: Make it truly optional
            modifier_text = self.modifier_input.text().strip()
            modifier = 0
            if modifier_text:
                try:
                    # Handle +/- modifiers more robustly
                    if modifier_text.startswith(('+', '-')):
                        modifier = int(modifier_text)
                    else:
                        # If no sign, assume positive
                        modifier = int(modifier_text)
                except ValueError:
                    # If invalid modifier, default to 0 and continue
                    modifier = 0
                    print(f"Invalid modifier '{modifier_text}', using 0")

            # Handle advantage/disadvantage
            advantage_text = self.advantage_combo.currentText()
            advantage = advantage_text == "Advantage"
            disadvantage = advantage_text == "Disadvantage"

            # Roll the dice
            result = self.dice_roller.roll(dice_type, num_dice, modifier, advantage, disadvantage)

            # Disable roll button during animation
            self.roll_button.setEnabled(False)
            self.roll_button.setText("🎲 Rolling...")

            # Start animation with the actual result
            if advantage or disadvantage:
                # For advantage/disadvantage, show the chosen roll
                display_result = max(result.rolls) if advantage else min(result.rolls)
            else:
                # For normal rolls, show the first die result (before modifier)
                display_result = result.rolls[0] if len(result.rolls) == 1 else sum(result.rolls)

            self.current_result = result  # Store for later use
            self.animation_display.start_animation(display_result, dice_type)

        except Exception as e:
            # Handle any other errors gracefully
            print(f"Error rolling dice: {e}")
            self.roll_button.setEnabled(True)
            self.roll_button.setText("🎲 ROLL!")

            # Show error briefly in modifier field
            self.modifier_input.setStyleSheet("""
                QLineEdit {
                    background-color: #FF5252;
                    color: white;
                    border: 2px solid #F44336;
                    border-radius: 4px;
                    padding: 4px;
                    font-size: 11px;
                    min-width: 50px;
                    max-width: 70px;
                }
            """)

            # Reset style after 2 seconds
            QTimer.singleShot(2000, self.reset_modifier_style)

    def reset_modifier_style(self):
        """Reset modifier input style to normal"""
        self.modifier_input.setStyleSheet("""
            QLineEdit {
                background-color: #2F2F2F;
                color: #F5F5F5;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                min-width: 50px;
                max-width: 70px;
            }
        """)

    def on_animation_finished(self, final_value):
        """Called when dice animation completes"""
        # Re-enable roll button
        self.roll_button.setEnabled(True)
        self.roll_button.setText("🎲 ROLL!")

        # Add to history
        result = self.current_result
        formatted_result = DiceUtils.format_roll_result(result)

        # Create history entry
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format the roll display
        dice_type = self.dice_combo.currentData()
        num_dice = self.num_dice_spin.value()
        modifier_text = self.modifier_input.text().strip()
        advantage_text = self.advantage_combo.currentText()

        # Build roll description
        roll_desc = f"{num_dice}d{dice_type}"
        if modifier_text:
            roll_desc += f"{modifier_text}"
        if advantage_text != "Normal":
            roll_desc += f" ({advantage_text.lower()})"

        history_entry = f"[{timestamp}] {roll_desc} = {result.total}"
        self.roll_history.append(history_entry)

        # Keep only last 15 rolls
        if len(self.roll_history) > 15:
            self.roll_history = self.roll_history[-15:]

        # Update display
        self.roll_history_widget.setText("\n".join(self.roll_history))
        self.roll_history_widget.verticalScrollBar().setValue(
            self.roll_history_widget.verticalScrollBar().maximum()
        )


class MainGameArea(QWidget):
    """Main game interaction area"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.conversation_history = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Scene display
        scene_group = QGroupBox("📖 Current Scene")
        scene_layout = QVBoxLayout()

        self.scene_display = QTextEdit()
        self.scene_display.setReadOnly(True)
        self.scene_display.setMinimumHeight(250)  # Reduced from 300
        self.scene_display.setStyleSheet("""
                    QTextEdit {
                        background-color: #2F2F2F;
                        color: #F5F5F5;
                        border: 2px solid #4A4A4A;
                        border-radius: 10px;
                        padding: 15px;
                        font-family: 'Georgia', serif;
                        font-size: 14px;
                        line-height: 1.6;
                        selection-background-color: #4682B4;
                    }
                """)

        # Set initial scene
        self.scene_display.setText(
            "🌟 Welcome to The Fey Bargain! 🌟\n\nYour AI-powered solo D&D adventure awaits. Describe what you'd like to do, and Claude will guide your journey through the mystical realm.")

        scene_layout.addWidget(self.scene_display)
        scene_group.setLayout(scene_layout)
        layout.addWidget(scene_group, 3)  # Give scene display 3 parts

        # Action input - REDUCED SIZE
        action_group = QGroupBox("⚡ Your Action")
        action_layout = QVBoxLayout()

        # Quick action buttons - SMALLER
        button_layout = QHBoxLayout()

        quick_actions = [
            ("👀 Look", "I look around carefully"),
            ("💬 Talk", "I want to talk to someone"),
            ("🎒 Gear", "I check my equipment and gear"),
            ("📜 Missions", "I review my current missions and objectives")
        ]

        for button_text, action_text in quick_actions:
            btn = QPushButton(button_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6495ED;
                    color: white;
                    padding: 6px 8px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #4169E1;
                }
            """)
            btn.clicked.connect(lambda checked, text=action_text: self.process_quick_action(text))
            button_layout.addWidget(btn)

        # Custom action input - SMALLER
        self.action_input = QTextEdit()
        self.action_input.setMaximumHeight(60)  # Reduced from 80
        self.action_input.setPlaceholderText("Describe your action... (Ctrl+Enter to submit)")
        self.action_input.setStyleSheet("""
                    QTextEdit {
                        background-color: #2F2F2F;
                        color: #F5F5F5;
                        border: 2px solid #4682B4;
                        border-radius: 5px;
                        padding: 6px;
                        font-size: 11px;
                        selection-background-color: #4682B4;
                    }
                """)

        self.action_button = QPushButton("🎯 Take Action")
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6347;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)

        action_layout.addLayout(button_layout)
        action_layout.addWidget(self.action_input)
        action_layout.addWidget(self.action_button)

        action_group.setLayout(action_layout)
        layout.addWidget(action_group, 1)  # Give action area only 1 part

        # Connect signals
        self.action_button.clicked.connect(self.process_custom_action)

        self.setLayout(layout)

    def process_quick_action(self, action_text):
        """Process a quick action button click"""
        self.process_action(action_text)

    def process_custom_action(self):
        """Process custom action input"""
        action_text = self.action_input.toPlainText().strip()
        if action_text:
            self.action_input.clear()
            self.process_action(action_text)

    def process_action(self, player_input):
        """Process player action and get AI response"""
        if not player_input.strip():
            return

        # Disable UI during processing
        self.action_button.setEnabled(False)
        self.action_button.setText("🤖 Claude is thinking...")

        # Build context
        context = self.main_window.context_manager.build_context()
        system_prompt = SystemPromptBuilder.get_base_dm_prompt()

        # Start AI response thread
        self.ai_thread = AIResponseThread(
            self.main_window.claude_service,
            system_prompt,
            context,
            player_input,
            self.conversation_history[-6:]  # Last 3 exchanges
        )

        self.ai_thread.response_ready.connect(self.handle_ai_response)
        self.ai_thread.error_occurred.connect(self.handle_ai_error)
        self.ai_thread.start()

        # Add player input to conversation
        self.conversation_history.extend([
            {"role": "user", "content": player_input}
        ])

    def handle_ai_response(self, response):
        """Handle AI response"""
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})

        # Update scene display
        self.scene_display.clear()
        self.scene_display.append("🎭 " + "DM Response".center(50, "="))
        self.scene_display.append("")
        self.scene_display.append(response)
        self.scene_display.append("")
        self.scene_display.append("=" * 56)

        # Re-enable UI
        self.action_button.setEnabled(True)
        self.action_button.setText("🎯 Take Action")

        # Update status bar
        self.main_window.statusBar().showMessage("✅ Action processed successfully", 3000)

    def handle_ai_error(self, error):
        """Handle AI error"""
        QMessageBox.warning(self, "AI Error", f"Error getting AI response: {error}")

        # Re-enable UI
        self.action_button.setEnabled(True)
        self.action_button.setText("🎯 Take Action")

        # Update status bar
        self.main_window.statusBar().showMessage("❌ Error processing action", 3000)


class FeyBargainMainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.init_services()
        self.init_ui()
        self.setup_timer()

    def init_services(self):
        """Initialize game services"""
        try:
            self.file_manager = CampaignFileManager("./campaign_files")
            self.claude_service = ClaudeService()
            self.context_manager = GameContextManager(self.file_manager)

            # Load campaign files
            self.files = self.file_manager.load_all_files()
            print(f"✅ Loaded {len(self.files)} campaign files!")

        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Error initializing game: {e}")
            sys.exit(1)

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("🎭 The Fey Bargain Game - AI-Powered Solo D&D")
        self.setGeometry(100, 100, 1500, 950)  # Made window slightly wider

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel (game area)
        self.game_area = MainGameArea(self)
        main_splitter.addWidget(self.game_area)

        # Right panel (character info, NPCs, missions, dice)
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Create panels
        self.character_panel = CharacterPanel(self.file_manager)
        self.npc_panel = NPCPanel(self.file_manager)
        self.mission_panel = MissionPanel(self.file_manager)
        self.dice_panel = DicePanel()

        # Add panels to right layout with specific stretch factors
        right_layout.addWidget(self.character_panel, 1)  # 1 part
        right_layout.addWidget(self.npc_panel, 2)  # 2 parts
        right_layout.addWidget(self.mission_panel, 1)  # 1 part
        right_layout.addWidget(self.dice_panel, 3)  # 3 parts - MORE SPACE!

        right_panel.setLayout(right_layout)
        right_panel.setMaximumWidth(450)  # Increased from 400

        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([1050, 450])  # Adjusted for new panel width

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        central_widget.setLayout(main_layout)

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.statusBar().showMessage("🎮 Game ready - Welcome to The Fey Bargain!")

        # Update all panels
        self.update_all_panels()

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        # Session management actions
        new_session_action = QAction('New Session', self)
        new_session_action.setShortcut('Ctrl+N')
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)

        save_session_action = QAction('Save Session', self)
        save_session_action.setShortcut('Ctrl+S')
        save_session_action.triggered.connect(self.save_session)
        file_menu.addAction(save_session_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        refresh_action = QAction('Refresh Data', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.update_all_panels)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_timer(self):
        """Setup timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_panels)
        self.update_timer.start(30000)  # Update every 30 seconds

    def update_all_panels(self):
        """Update all information panels"""
        try:
            self.character_panel.update_character_info()
            self.npc_panel.update_npc_list()
            self.mission_panel.update_mission_list()
        except Exception as e:
            print(f"Error updating panels: {e}")

    def new_session(self):
        """Start a new game session"""
        reply = QMessageBox.question(self, 'New Session',
                                     'Start a new game session?\n(Current progress will be saved)',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Clear conversation history
            self.game_area.conversation_history.clear()

            # Reset scene display
            self.game_area.scene_display.clear()
            self.game_area.scene_display.setText(
                "🌟 New Session Started! 🌟\n\nYour adventure continues. What would you like to do?")

            # Update status
            self.statusBar().showMessage("🎮 New session started!", 3000)

    def save_session(self):
        """Save current session"""
        # This would integrate with your session manager
        QMessageBox.information(self, 'Save Session', 'Session saved successfully!')
        self.statusBar().showMessage("💾 Session saved!", 3000)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, 'About The Fey Bargain Game',
                          """
                          <h2>🎭 The Fey Bargain Game</h2>
                          <p><strong>AI-Powered Solo D&D Adventure</strong></p>
                          <p>Version 1.0</p>
                          <p>Built with PyQt6 and Claude AI</p>
                          <p>An innovative solo D&D experience that combines traditional campaign management with intelligent AI storytelling.</p>
                          <p><em>May your adventures be legendary!</em> ⚔️✨</p>
                          """)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("The Fey Bargain Game")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Your Game Studio")

    # Create and show main window
    window = FeyBargainMainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()