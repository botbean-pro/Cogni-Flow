# Create main.py - The main application entry point

main_py_content = '''#!/usr/bin/env python3
"""
Cogni-Flow Desktop Application
A digital learning companion that transforms study material into accessible formats.
Designed with special focus on dyslexia-friendly features.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import threading
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    print("CustomTkinter not available. Falling back to standard tkinter.")
    CTK_AVAILABLE = False

from config import AppConfig
from gui.main_window import MainWindow
from core.accessibility import AccessibilityManager
from utils.storage import StorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cogni_flow.log'),
        logging.StreamHandler()
    ]
)

class CogniFlowApp:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        self.storage = StorageManager()
        self.accessibility = AccessibilityManager()
        
        # Initialize the main window
        self.setup_gui()
        
    def setup_gui(self):
        """Initialize the graphical user interface."""
        try:
            if CTK_AVAILABLE:
                # Use CustomTkinter for modern appearance
                ctk.set_appearance_mode("light")  # Can be "dark" or "light"
                ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
                self.root = ctk.CTk()
            else:
                # Fall back to standard tkinter
                self.root = tk.Tk()
            
            # Configure main window
            self.root.title("Cogni-Flow - Digital Learning Companion")
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
            
            # Apply accessibility settings
            self.apply_accessibility_settings()
            
            # Initialize main window
            self.main_window = MainWindow(
                parent=self.root,
                app_config=self.config,
                accessibility_manager=self.accessibility,
                storage_manager=self.storage
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up GUI: {e}")
            messagebox.showerror("Error", f"Failed to initialize GUI: {e}")
            sys.exit(1)
    
    def apply_accessibility_settings(self):
        """Apply accessibility settings to the main window."""
        settings = self.storage.load_user_preferences()
        
        # Apply font settings
        if 'font_family' in settings:
            self.config.set_font_family(settings['font_family'])
        if 'font_size' in settings:
            self.config.set_font_size(settings['font_size'])
            
        # Apply theme settings
        if 'theme' in settings:
            self.config.set_theme(settings['theme'])
            
        # Apply other accessibility settings
        if 'high_contrast' in settings:
            self.config.set_high_contrast(settings['high_contrast'])
    
    def run(self):
        """Start the main application loop."""
        try:
            self.logger.info("Starting Cogni-Flow application...")
            
            # Set up cleanup on window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Start the main loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            self.cleanup()
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"Unexpected error occurred: {e}")
            self.cleanup()
    
    def on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit Cogni-Flow?"):
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources and save settings before closing."""
        try:
            # Save current user preferences
            self.storage.save_user_preferences({
                'font_family': self.config.font_family,
                'font_size': self.config.font_size,
                'theme': self.config.theme,
                'high_contrast': self.config.high_contrast
            })
            
            self.logger.info("Application closing...")
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            sys.exit(0)

def main():
    """Main entry point of the application."""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("Error: Python 3.8 or higher is required.")
            sys.exit(1)
        
        # Create and run the application
        app = CogniFlowApp()
        app.run()
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        print(f"Error: Failed to start Cogni-Flow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

# Save main.py
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(main_py_content)

print("✅ Created main.py")

# Create config.py - Configuration management
config_py_content = '''"""
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
'''

# Save config.py
with open('config.py', 'w', encoding='utf-8') as f:
    f.write(config_py_content)

print("✅ Created config.py")
print("\nMain application files created successfully!")
print("\nTo install dependencies, run:")
print("pip install -r requirements.txt")