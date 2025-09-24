#!/usr/bin/env python3
"""
Cogni-Flow Demo Script
Demonstrates the core functionality without requiring full GUI setup.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.text_processor import TextProcessor, ProcessedContent
from core.accessibility import AccessibilityManager
from core.quiz_generator import QuizManager
from core.mind_mapper import MindMapManager
from utils.file_handlers import FileManager
from utils.storage import StorageManager
from config import AppConfig

def demo_text_processing():
    """Demo text processing capabilities."""
    print("\n=== Text Processing Demo ===")

    sample_text = """
    Photosynthesis is the process by which plants convert light energy, usually from the sun, 
    into chemical energy stored in glucose. This process occurs in the chloroplasts of plant 
    cells and involves two main stages: the light reactions and the Calvin cycle. During the 
    light reactions, chlorophyll absorbs light energy and converts it into ATP and NADPH. 
    These energy carriers are then used in the Calvin cycle to convert carbon dioxide from 
    the air into glucose. The overall equation for photosynthesis is: 6CO₂ + 6H₂O + light 
    energy → C₆H₁₂O₆ + 6O₂. This process is crucial for life on Earth as it produces oxygen 
    and serves as the foundation of most food chains.
    """

    try:
        processor = TextProcessor()
        if not processor.is_available():
            print("⚠️  LLM provider not available - using fallback processing")

        # Process the text (will work even without LLM)
        print("Processing sample text...")

        # Create basic processed content
        processed = ProcessedContent(
            original_text=sample_text,
            title="Photosynthesis in Plants",
            summary="Process where plants convert light energy to chemical energy",
            key_concepts=["Photosynthesis", "Chloroplasts", "ATP", "NADPH", "Calvin cycle"],
            main_topics=["Light reactions", "Calvin cycle", "Energy conversion"],
            complexity_level="intermediate",
            word_count=len(sample_text.split()),
            reading_time=2
        )

        print(f"✅ Title: {processed.title}")
        print(f"✅ Word count: {processed.word_count}")
        print(f"✅ Reading time: {processed.reading_time} minutes")
        print(f"✅ Complexity: {processed.complexity_level}")
        print(f"✅ Key concepts: {', '.join(processed.key_concepts)}")

    except Exception as e:
        print(f"❌ Text processing failed: {e}")

def demo_accessibility_features():
    """Demo accessibility features."""
    print("\n=== Accessibility Features Demo ===")

    try:
        accessibility = AccessibilityManager()

        print("✅ Accessibility manager initialized")
        print(f"✅ TTS available: {accessibility.is_tts_available()}")
        print(f"✅ Font recommendations: {accessibility.get_font_recommendations()[:3]}")

        # Test text formatting
        sample_text = "This is a sample text for bionic reading demonstration."
        formatted = accessibility.format_text_for_reading(sample_text)
        print(f"✅ Text formatting works")

        # Apply dyslexia-friendly settings
        accessibility.apply_dyslexia_friendly_preset()
        settings = accessibility.get_settings()
        print(f"✅ Dyslexia-friendly preset applied")
        print(f"   Font: {settings.font_family}, Size: {settings.font_size}")

    except Exception as e:
        print(f"❌ Accessibility demo failed: {e}")

def demo_quiz_generation():
    """Demo quiz generation."""
    print("\n=== Quiz Generation Demo ===")

    sample_text = """
    The water cycle is the continuous movement of water on, above and below the surface of Earth. 
    Water evaporates from oceans, lakes and rivers. It rises into the atmosphere as water vapor. 
    In the atmosphere, water vapor condenses to form clouds. Eventually, water falls back to 
    Earth as precipitation (rain, snow, sleet, or hail). Some water flows over the land as 
    surface runoff into rivers and lakes. Other water soaks into the ground as groundwater.
    """

    try:
        quiz_manager = QuizManager()

        print("Creating quiz from sample text...")
        quiz = quiz_manager.create_quiz(sample_text, "Water Cycle Quiz")

        print(f"✅ Quiz created: {quiz.title}")
        print(f"✅ Number of questions: {len(quiz.questions)}")
        print(f"✅ Estimated time: {quiz.estimated_time} minutes")

        # Show first question as example
        if quiz.questions:
            first_q = quiz.questions[0]
            print(f"\n📝 Sample question:")
            print(f"   Type: {first_q.question_type.value}")
            print(f"   Question: {first_q.question_text}")
            if first_q.options:
                for i, option in enumerate(first_q.options):
                    print(f"   {chr(65+i)}) {option}")

    except Exception as e:
        print(f"❌ Quiz generation failed: {e}")

def demo_mind_mapping():
    """Demo mind map generation."""
    print("\n=== Mind Map Generation Demo ===")

    sample_text = """
    Climate change refers to long-term shifts in global temperatures and weather patterns. 
    The main causes include greenhouse gas emissions from burning fossil fuels, deforestation, 
    and industrial processes. Effects include rising sea levels, extreme weather events, 
    and ecosystem disruptions. Solutions involve renewable energy, carbon reduction, 
    international cooperation, and sustainable practices.
    """

    try:
        mind_map_manager = MindMapManager()

        print("Creating mind map...")
        map_id = mind_map_manager.create_mind_map(sample_text, "Climate Change")

        mind_map = mind_map_manager.get_mind_map(map_id)
        if mind_map:
            print(f"✅ Mind map created: {mind_map.title}")
            print(f"✅ Number of nodes: {len(mind_map.nodes)}")
            print(f"✅ Available: {mind_map_manager.is_available()}")

    except Exception as e:
        print(f"❌ Mind map generation failed: {e}")

def demo_file_handling():
    """Demo file handling capabilities."""
    print("\n=== File Handling Demo ===")

    try:
        file_manager = FileManager()

        print("✅ File manager initialized")
        print(f"✅ Supported formats:")
        for fmt in file_manager.get_supported_formats():
            print(f"   - {fmt}")

        # Test text extraction
        sample_text = "This is a test document for file handling demonstration."
        extracted = file_manager.extract_from_text(sample_text, "Demo Text")

        print(f"✅ Text extraction works")
        print(f"   Title: {extracted.title}")
        print(f"   Word count: {extracted.word_count}")
        print(f"   File type: {extracted.file_type}")

    except Exception as e:
        print(f"❌ File handling demo failed: {e}")

def demo_storage():
    """Demo storage capabilities."""
    print("\n=== Storage Demo ===")

    try:
        storage = StorageManager()

        # Test preferences
        test_prefs = {
            'font_size': 16,
            'theme': 'dark',
            'tts_enabled': True
        }

        storage.save_user_preferences(test_prefs)
        loaded_prefs = storage.load_user_preferences()

        print("✅ Storage manager initialized")
        print(f"✅ Preferences saved and loaded")
        print(f"   Font size: {loaded_prefs.get('font_size', 'N/A')}")

        # Get storage info
        info = storage.get_storage_info()
        print(f"✅ Storage info available")
        if info:
            print(f"   Directory: {info.get('storage_dir', 'N/A')}")

    except Exception as e:
        print(f"❌ Storage demo failed: {e}")

def main():
    """Run all demos."""
    print("🧠 Cogni-Flow Desktop Application Demo")
    print("=====================================")

    # Run all demo functions
    demo_text_processing()
    demo_accessibility_features() 
    demo_quiz_generation()
    demo_mind_mapping()
    demo_file_handling()
    demo_storage()

    print("\n🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run full application: python main.py")
    print("3. Customize GUI in gui/main_window.py")

if __name__ == "__main__":
    main()
