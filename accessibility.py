"""
Accessibility features manager for Cogni-Flow.
Handles dyslexia-friendly features, text-to-speech, and other accessibility tools.
"""

import logging
import re
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class ReadingMode(Enum):
    NORMAL = "normal"
    BIONIC = "bionic"
    HIGHLIGHTED = "highlighted"

@dataclass
class AccessibilitySettings:
    """Container for accessibility settings."""
    font_family: str = "Arial"
    font_size: int = 14
    line_height: float = 1.6
    letter_spacing: float = 0.5
    reading_mode: ReadingMode = ReadingMode.NORMAL
    high_contrast: bool = False
    tts_enabled: bool = True
    tts_speed: int = 150
    tts_voice_index: int = 0
    keyboard_navigation: bool = True
    focus_indicators: bool = True

class TextToSpeechEngine:
    """Text-to-Speech engine wrapper for accessibility."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.is_speaking = False
        self.is_paused = False
        self.current_text = ""
        self.voices = []

        if TTS_AVAILABLE:
            self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the TTS engine."""
        try:
            self.engine = pyttsx3.init()

            # Get available voices
            voices = self.engine.getProperty('voices')
            self.voices = []

            for i, voice in enumerate(voices):
                self.voices.append({
                    'id': voice.id,
                    'name': voice.name if hasattr(voice, 'name') else f"Voice {i}",
                    'language': getattr(voice, 'languages', ['en'])[0] if hasattr(voice, 'languages') else 'en'
                })

            # Set default properties
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)

            self.logger.info(f"TTS engine initialized with {len(self.voices)} voices")

        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        return self.voices

    def set_voice(self, voice_index: int):
        """Set the TTS voice."""
        if self.engine and 0 <= voice_index < len(self.voices):
            try:
                voice_id = self.voices[voice_index]['id']
                self.engine.setProperty('voice', voice_id)
            except Exception as e:
                self.logger.error(f"Failed to set voice: {e}")

    def set_speed(self, speed: int):
        """Set the TTS speaking speed."""
        if self.engine:
            try:
                # Clamp speed between 50 and 300
                speed = max(50, min(300, speed))
                self.engine.setProperty('rate', speed)
            except Exception as e:
                self.logger.error(f"Failed to set TTS speed: {e}")

    def speak(self, text: str, callback: Optional[Callable] = None):
        """Speak the given text."""
        if not self.engine or not text.strip():
            return

        try:
            self.current_text = text
            self.is_speaking = True
            self.is_paused = False

            if callback:
                self.engine.connect('finished-utterance', callback)

            self.engine.say(text)
            self.engine.runAndWait()

            self.is_speaking = False

        except Exception as e:
            self.logger.error(f"TTS speak failed: {e}")
            self.is_speaking = False

    def pause(self):
        """Pause TTS (if supported by the engine)."""
        # Note: pyttsx3 doesn't support pause/resume natively
        # This would need to be implemented with a more advanced TTS system
        self.is_paused = True
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

    def resume(self):
        """Resume TTS."""
        self.is_paused = False
        # Would need to continue from where it left off

    def stop(self):
        """Stop TTS."""
        self.is_speaking = False
        self.is_paused = False
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

    def is_available(self) -> bool:
        """Check if TTS is available."""
        return self.engine is not None

class TextFormatter:
    """Text formatting for accessibility features."""

    @staticmethod
    def apply_bionic_reading(text: str, intensity: float = 0.5) -> str:
        """Apply bionic reading formatting by bolding first letters."""
        if not text:
            return text

        def format_word(word):
            if len(word) <= 2:
                return f"<b>{word}</b>"

            # Calculate how many letters to bold based on word length and intensity
            bold_count = max(1, int(len(word) * intensity))
            bold_part = word[:bold_count]
            normal_part = word[bold_count:]

            return f"<b>{bold_part}</b>{normal_part}"

        # Split text into words and non-word characters
        words = re.findall(r'\b\w+\b|\W+', text)
        formatted_words = []

        for word in words:
            if re.match(r'\b\w+\b', word):  # It's a word
                formatted_words.append(format_word(word))
            else:  # It's whitespace or punctuation
                formatted_words.append(word)

        return ''.join(formatted_words)

    @staticmethod
    def apply_dyslexia_friendly_spacing(text: str, letter_spacing: float = 0.5, line_height: float = 1.6) -> str:
        """Apply dyslexia-friendly spacing to text."""
        # This would typically be handled by CSS in a GUI application
        # Here we return formatting hints
        return {
            'text': text,
            'letter_spacing': f"{letter_spacing}px",
            'line_height': str(line_height)
        }

    @staticmethod
    def highlight_text_segments(text: str, segments: List[str]) -> str:
        """Highlight specific text segments."""
        highlighted_text = text
        for segment in segments:
            highlighted_text = highlighted_text.replace(
                segment, 
                f"<mark>{segment}</mark>"
            )
        return highlighted_text

class AccessibilityManager:
    """Main accessibility manager coordinating all accessibility features."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = AccessibilitySettings()
        self.tts_engine = TextToSpeechEngine()
        self.text_formatter = TextFormatter()

        # Callbacks for UI updates
        self.ui_update_callbacks: List[Callable] = []

    def add_ui_update_callback(self, callback: Callable):
        """Add a callback for UI updates."""
        self.ui_update_callbacks.append(callback)

    def _notify_ui_update(self):
        """Notify UI of accessibility changes."""
        for callback in self.ui_update_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"UI update callback failed: {e}")

    def update_settings(self, **kwargs):
        """Update accessibility settings."""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
                self.logger.info(f"Updated accessibility setting: {key} = {value}")

        # Apply TTS settings
        if 'tts_speed' in kwargs:
            self.tts_engine.set_speed(kwargs['tts_speed'])
        if 'tts_voice_index' in kwargs:
            self.tts_engine.set_voice(kwargs['tts_voice_index'])

        self._notify_ui_update()

    def get_settings(self) -> AccessibilitySettings:
        """Get current accessibility settings."""
        return self.settings

    def apply_dyslexia_friendly_preset(self):
        """Apply dyslexia-friendly preset settings."""
        self.update_settings(
            font_family="OpenDyslexic",
            font_size=16,
            line_height=2.0,
            letter_spacing=1.0,
            reading_mode=ReadingMode.BIONIC,
            high_contrast=False,
            tts_enabled=True
        )

    def format_text_for_reading(self, text: str) -> str:
        """Format text based on current accessibility settings."""
        formatted_text = text

        if self.settings.reading_mode == ReadingMode.BIONIC:
            formatted_text = self.text_formatter.apply_bionic_reading(formatted_text)

        return formatted_text

    def speak_text(self, text: str, callback: Optional[Callable] = None):
        """Speak text if TTS is enabled."""
        if self.settings.tts_enabled and self.tts_engine.is_available():
            self.tts_engine.speak(text, callback)

    def pause_speech(self):
        """Pause text-to-speech."""
        self.tts_engine.pause()

    def resume_speech(self):
        """Resume text-to-speech."""
        self.tts_engine.resume()

    def stop_speech(self):
        """Stop text-to-speech."""
        self.tts_engine.stop()

    def is_tts_available(self) -> bool:
        """Check if text-to-speech is available."""
        return self.tts_engine.is_available()

    def get_font_recommendations(self) -> List[str]:
        """Get list of recommended fonts for accessibility."""
        return [
            "OpenDyslexic",
            "Arial",
            "Helvetica",
            "Verdana",
            "Calibri",
            "Tahoma",
            "Trebuchet MS"
        ]

    def get_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Get recommended color schemes for accessibility."""
        return {
            'light': {
                'background': '#FFFFF8',
                'text': '#1F2937',
                'accent': '#2563EB'
            },
            'dark': {
                'background': '#1F2937',
                'text': '#F9FAFB',
                'accent': '#60A5FA'
            },
            'high_contrast': {
                'background': '#000000',
                'text': '#FFFFFF',
                'accent': '#FFFF00'
            },
            'cream': {  # Dyslexia-friendly
                'background': '#FDF6E3',
                'text': '#2C3E50',
                'accent': '#3498DB'
            },
            'blue_light': {  # Reduces eye strain
                'background': '#F0F8FF',
                'text': '#191970',
                'accent': '#4169E1'
            }
        }

    def validate_contrast_ratio(self, bg_color: str, text_color: str) -> float:
        """Calculate color contrast ratio for accessibility."""
        # Simplified contrast ratio calculation
        # In a real implementation, you would convert hex to RGB and calculate luminance
        # This is a placeholder that returns a mock value
        return 4.5  # WCAG AA compliance threshold

    def export_settings(self) -> Dict[str, Any]:
        """Export current accessibility settings."""
        return {
            'font_family': self.settings.font_family,
            'font_size': self.settings.font_size,
            'line_height': self.settings.line_height,
            'letter_spacing': self.settings.letter_spacing,
            'reading_mode': self.settings.reading_mode.value,
            'high_contrast': self.settings.high_contrast,
            'tts_enabled': self.settings.tts_enabled,
            'tts_speed': self.settings.tts_speed,
            'tts_voice_index': self.settings.tts_voice_index
        }

    def import_settings(self, settings_dict: Dict[str, Any]):
        """Import accessibility settings."""
        for key, value in settings_dict.items():
            if key == 'reading_mode':
                try:
                    value = ReadingMode(value)
                except ValueError:
                    value = ReadingMode.NORMAL

            if hasattr(self.settings, key):
                setattr(self.settings, key, value)

        self._notify_ui_update()
