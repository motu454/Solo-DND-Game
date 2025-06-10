# src/config/settings.py
"""
Application Configuration Settings
Like Terraform variables but for your D&D game - centralized config management
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application configuration settings
    Uses environment variables with sensible defaults
    """

    # API Configuration
    anthropic_api_key: str = Field(
        default="",
        env="ANTHROPIC_API_KEY",
        description="Anthropic API key for Claude integration"
    )

    anthropic_model: str = Field(
        default="claude-3-haiku-20240307",
        env="ANTHROPIC_MODEL",
        description="Claude model to use for AI responses"
    )

    max_tokens: int = Field(
        default=2000,
        env="MAX_TOKENS",
        description="Maximum tokens for AI responses"
    )

    temperature: float = Field(
        default=0.7,
        env="TEMPERATURE",
        description="AI response temperature"
    )

    # Application Settings
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode for detailed logging"
    )

    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    # File Management
    campaign_files_path: str = Field(
        default="./campaign_files",
        env="CAMPAIGN_FILES_PATH",
        description="Path to directory containing campaign markdown files"
    )

    backup_enabled: bool = Field(
        default=True,
        env="BACKUP_ENABLED",
        description="Enable automatic backup of campaign files"
    )

    backup_retention_days: int = Field(
        default=30,
        env="BACKUP_RETENTION_DAYS",
        description="Number of days to retain backup files"
    )

    # AI Context Management
    max_context_size: int = Field(
        default=100000,
        env="MAX_CONTEXT_SIZE",
        description="Maximum context size for AI requests (in characters)"
    )

    context_window_size: int = Field(
        default=8000,
        env="CONTEXT_WINDOW_SIZE",
        description="Size of context window for AI conversations"
    )

    # Session Management
    auto_save_interval: int = Field(
        default=300,
        env="AUTO_SAVE_INTERVAL",
        description="Auto-save interval in seconds (default: 5 minutes)"
    )

    max_session_length: int = Field(
        default=14400,
        env="MAX_SESSION_LENGTH",
        description="Maximum session length in seconds (default: 4 hours)"
    )

    sessions_directory: str = Field(
        default="./sessions",
        env="SESSIONS_DIRECTORY",
        description="Directory to store session save files"
    )

    # Game Settings
    default_difficulty_class: int = Field(
        default=15,
        env="DEFAULT_DIFFICULTY_CLASS",
        description="Default difficulty class for skill checks"
    )

    enable_critical_successes: bool = Field(
        default=True,
        env="ENABLE_CRITICAL_SUCCESSES",
        description="Enable critical success/failure on skill checks"
    )

    dice_animation_enabled: bool = Field(
        default=True,
        env="DICE_ANIMATION_ENABLED",
        description="Enable dice rolling animations in GUI"
    )

    # Performance Settings
    file_cache_enabled: bool = Field(
        default=True,
        env="FILE_CACHE_ENABLED",
        description="Enable caching of campaign files"
    )

    ai_response_timeout: int = Field(
        default=30,
        env="AI_RESPONSE_TIMEOUT",
        description="Timeout for AI API requests in seconds"
    )

    max_retries: int = Field(
        default=3,
        env="MAX_RETRIES",
        description="Maximum number of retries for failed API requests"
    )

    # Development Settings
    mock_ai_responses: bool = Field(
        default=False,
        env="MOCK_AI_RESPONSES",
        description="Use mock AI responses for testing (development only)"
    )

    verbose_logging: bool = Field(
        default=False,
        env="VERBOSE_LOGGING",
        description="Enable verbose logging for debugging"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_settings()
        self._ensure_directories()

    def _validate_settings(self):
        """Validate configuration settings"""
        errors = []

        # Check required settings
        if not self.anthropic_api_key and not self.mock_ai_responses:
            errors.append("ANTHROPIC_API_KEY is required (or set MOCK_AI_RESPONSES=True for testing)")

        # Validate paths
        if not os.path.exists(self.campaign_files_path):
            errors.append(f"Campaign files directory does not exist: {self.campaign_files_path}")

        # Validate numeric ranges
        if self.auto_save_interval < 60:
            errors.append("Auto-save interval must be at least 60 seconds")

        if self.max_session_length < 3600:
            errors.append("Maximum session length must be at least 1 hour")

        if self.default_difficulty_class < 5 or self.default_difficulty_class > 30:
            errors.append("Default difficulty class must be between 5 and 30")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors))

    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.campaign_files_path,
            self.sessions_directory,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def get_campaign_files_path(self) -> Path:
        """Get campaign files path as Path object"""
        return Path(self.campaign_files_path)

    def get_sessions_path(self) -> Path:
        """Get sessions directory path as Path object"""
        return Path(self.sessions_directory)

    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return self.debug or self.mock_ai_responses or self.verbose_logging

    def get_ai_config(self) -> dict:
        """Get AI-specific configuration"""
        return {
            'api_key': self.anthropic_api_key,
            'model': self.anthropic_model,
            'max_context_size': self.max_context_size,
            'context_window_size': self.context_window_size,
            'timeout': self.ai_response_timeout,
            'max_retries': self.max_retries,
            'mock_responses': self.mock_ai_responses
        }

    def get_session_config(self) -> dict:
        """Get session management configuration"""
        return {
            'auto_save_interval': self.auto_save_interval,
            'max_session_length': self.max_session_length,
            'sessions_directory': self.sessions_directory,
            'backup_enabled': self.backup_enabled,
            'backup_retention_days': self.backup_retention_days
        }

    def get_game_config(self) -> dict:
        """Get game-specific configuration"""
        return {
            'default_difficulty_class': self.default_difficulty_class,
            'enable_critical_successes': self.enable_critical_successes,
            'dice_animation_enabled': self.dice_animation_enabled
        }

    def print_config_summary(self):
        """Print a summary of current configuration"""
        print("⚙️  Configuration Summary")
        print("=" * 40)
        print(f"🔧 Debug Mode: {self.debug}")
        print(f"🤖 AI Model: {self.anthropic_model}")
        print(f"📁 Campaign Path: {self.campaign_files_path}")
        print(f"💾 Sessions Path: {self.sessions_directory}")
        print(f"⏰ Auto-save: Every {self.auto_save_interval}s")
        print(f"🎯 Default DC: {self.default_difficulty_class}")
        print(f"🎲 Dice Animations: {'Enabled' if self.dice_animation_enabled else 'Disabled'}")
        print(f"🔄 File Cache: {'Enabled' if self.file_cache_enabled else 'Disabled'}")

        if self.is_development_mode():
            print(f"\n⚠️  Development Mode Active")
            if self.mock_ai_responses:
                print(f"   🤖 Using mock AI responses")
            if self.verbose_logging:
                print(f"   📝 Verbose logging enabled")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)"""
    global _settings
    load_dotenv(override=True)  # Reload .env file
    _settings = Settings()
    return _settings


# Configuration validation function
def validate_environment():
    """Validate the current environment configuration"""
    try:
        settings = get_settings()
        print("✅ Environment validation successful")
        return True
    except ValueError as e:
        print(f"❌ Environment validation failed:")
        print(str(e))
        return False
    except Exception as e:
        print(f"❌ Unexpected error during validation: {e}")
        return False


# Create sample .env file
def create_sample_env_file(filepath: str = ".env.example"):
    """Create a sample .env file with all available settings"""
    sample_content = """# Fey Bargain Game Configuration
# Copy this to .env and customize your settings

# API Configuration (REQUIRED)
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Application Settings
DEBUG=False
LOG_LEVEL=INFO

# File Management
CAMPAIGN_FILES_PATH=./campaign_files
BACKUP_ENABLED=True
BACKUP_RETENTION_DAYS=30

# AI Configuration
MAX_CONTEXT_SIZE=100000
CONTEXT_WINDOW_SIZE=8000

# Session Management
AUTO_SAVE_INTERVAL=300
MAX_SESSION_LENGTH=14400
SESSIONS_DIRECTORY=./sessions

# Game Settings
DEFAULT_DIFFICULTY_CLASS=15
ENABLE_CRITICAL_SUCCESSES=True
DICE_ANIMATION_ENABLED=True

# Performance Settings
FILE_CACHE_ENABLED=True
AI_RESPONSE_TIMEOUT=30
MAX_RETRIES=3

# Development Settings (for testing)
MOCK_AI_RESPONSES=False
VERBOSE_LOGGING=False
"""

    with open(filepath, 'w') as f:
        f.write(sample_content)

    print(f"📝 Sample configuration created: {filepath}")
    print("Copy this to .env and customize your settings!")


if __name__ == "__main__":
    # When run directly, validate environment and show config
    if validate_environment():
        settings = get_settings()
        settings.print_config_summary()
    else:
        print("\n💡 Creating sample configuration file...")
        create_sample_env_file()