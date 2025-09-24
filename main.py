#!/usr/bin/env python3
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
