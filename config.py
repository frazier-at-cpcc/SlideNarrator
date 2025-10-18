"""
Configuration settings for SlideNarrator
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for SlideNarrator."""

    # API Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    # Output Configuration
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")

    # Script Generation Settings
    DEFAULT_TONE = "professional"
    WORDS_PER_MINUTE = 150  # For duration estimation

    # Narration Length Settings
    MIN_NARRATION_SENTENCES = 2
    MAX_NARRATION_SENTENCES = 4
    TARGET_NARRATION_SECONDS = 30  # Target duration per slide

    # Polish Settings
    DEFAULT_FOCUS_AREAS = ["transitions", "consistency", "pacing", "engagement"]

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not cls.ANTHROPIC_API_KEY:
            return False
        return True

    @classmethod
    def get_api_key(cls) -> str:
        """
        Get the Anthropic API key.

        Returns:
            API key string

        Raises:
            ValueError: If API key is not configured
        """
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable or pass --api-key"
            )
        return cls.ANTHROPIC_API_KEY
