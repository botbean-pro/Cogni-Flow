"""
Configuration management for Cogni-Flow application.
Handles application settings, themes, and user preferences.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    DYSLEXIA_FRIENDLY = "dyslexia_friendly"

class FontFamily(Enum):
    OPEN_DYSLEXIC = "OpenDyslexic"
    ARIAL = "Arial"
    HELVETICA = "Helvetica"
    VERDANA = "Verdana"
    LEXEND = "Lexend"

@dataclass
class ColorScheme:
    """Color scheme configuration for different themes."""
    background: str
    surface: str
    primary: str
    secondary: str
    text: str
    text_secondary: str
    accent: str
    error: str
    warning: str
    success: str

class AppConfig:
    """Central configuration management for the application."""

    def __init__(self):
        self.config_file = "cogni_flow_config.json"
        self.load_default_settings()
        self.load_user_config()

    def load_default_settings(self):
        """Load default application settings."""
        self.font_family = FontFamily.ARIAL.value
        self.font_size = 14
        self.line_height = 1.6
        self.letter_spacing = 0.5
        self.theme = Theme.LIGHT.value
        self.high_contrast = False
        self.bionic_reading = False
        self.tts_speed = 150
        self.tts_voice = "default"

        # Color schemes for different themes
        self.color_schemes = {
            Theme.LIGHT.value: ColorScheme(
                background="#FCFCF9",
                surface="#FFFFFCD", 
                primary="#208DD1",
                secondary="#2EA4B2",
                text="#1F3439",
                text_secondary="#626C71",
                accent="#29748C",
                error="#C0152F",
                warning="#A84B2F",
                success="#22C55E"
            ),
            Theme.DARK.value: ColorScheme(
                background="#1F2121",
                surface="#262828",
                primary="#32A0CB",
                secondary="#45B7C8",
                text="#F5F5F5",
                text_secondary="#A7A9A9",
                accent="#2D8CA8",
                error="#FF5459",
                warning="#E68161",
                success="#4ADE80"
            ),
            Theme.HIGH_CONTRAST.value: ColorScheme(
                background="#000000",
                surface="#111111",
                primary="#FFFFFF",
                secondary="#FFFF00",
                text="#FFFFFF",
                text_secondary="#CCCCCC",
                accent="#FFFF00",
                error="#FF0000",
                warning="#FFA500",
                success="#00FF00"
            ),
            Theme.DYSLEXIA_FRIENDLY.value: ColorScheme(
                background="#FDF6E3",  # Warm cream
                surface="#F7F3E9",
                primary="#0066CC",     # Blue (dyslexia-friendly)
                secondary="#6C7B7F",
                text="#2C2C54",        # Dark blue-gray
                text_secondary="#5E6B70",
                accent="#4A90E2",
                error="#CC3333",
                warning="#FF8C00",
                success="#228B22"
            )
        }

        # Accessibility features
        self.accessibility_features = {
            'screen_reader_support': True,
            'keyboard_navigation': True,
            'focus_indicators': True,
            'skip_links': True,
            'aria_labels': True
        }

        # LLM API settings
        self.llm_settings = {
            'provider': 'openai',  # or 'huggingface', 'local'
            'model': 'gpt-3.5-turbo',
            'max_tokens': 2000,
            'temperature': 0.7,
            'timeout': 30
        }

    def load_user_config(self):
        """Load user-specific configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)

                # Update settings with user preferences
                for key, value in user_config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

            except Exception as e:
                print(f"Warning: Could not load user config: {e}")

    def save_user_config(self):
        """Save current configuration to file."""
        try:
            config_data = {
                'font_family': self.font_family,
                'font_size': self.font_size,
                'line_height': self.line_height,
                'letter_spacing': self.letter_spacing,
                'theme': self.theme,
                'high_contrast': self.high_contrast,
                'bionic_reading': self.bionic_reading,
                'tts_speed': self.tts_speed,
                'tts_voice': self.tts_voice
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)

        except Exception as e:
            print(f"Error saving config: {e}")

    def get_current_color_scheme(self) -> ColorScheme:
        """Get the color scheme for the current theme."""
        return self.color_schemes.get(self.theme, self.color_schemes[Theme.LIGHT.value])

    def set_theme(self, theme: str):
        """Set the application theme."""
        if theme in [t.value for t in Theme]:
            self.theme = theme
            self.save_user_config()

    def set_font_family(self, font_family: str):
        """Set the font family."""
        self.font_family = font_family
        self.save_user_config()

    def set_font_size(self, font_size: int):
        """Set the font size."""
        if 10 <= font_size <= 32:  # Reasonable font size range
            self.font_size = font_size
            self.save_user_config()

    def set_high_contrast(self, enabled: bool):
        """Toggle high contrast mode."""
        self.high_contrast = enabled
        if enabled:
            self.theme = Theme.HIGH_CONTRAST.value
        self.save_user_config()

    def get_dyslexia_friendly_settings(self) -> Dict[str, Any]:
        """Get recommended settings for dyslexic users."""
        return {
            'font_family': FontFamily.OPEN_DYSLEXIC.value,
            'font_size': 16,
            'line_height': 2.0,
            'letter_spacing': 1.0,
            'theme': Theme.DYSLEXIA_FRIENDLY.value,
            'bionic_reading': True
        }

    def apply_dyslexia_friendly_settings(self):
        """Apply dyslexia-friendly settings."""
        settings = self.get_dyslexia_friendly_settings()
        for key, value in settings.items():
            setattr(self, key, value)
        self.save_user_config()

# Global config instance
app_config = AppConfig()
