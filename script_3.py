# Create core/accessibility.py - Accessibility features manager

accessibility_content = '''"""
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
        words = re.findall(r'\\b\\w+\\b|\\W+', text)
        formatted_words = []
        
        for word in words:
            if re.match(r'\\b\\w+\\b', word):  # It's a word
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
'''

# Save core/accessibility.py
with open('core/accessibility.py', 'w', encoding='utf-8') as f:
    f.write(accessibility_content)

print("✅ Created core/accessibility.py")

# Create core/quiz_generator.py - Quiz generation logic
quiz_generator_content = '''"""
Quiz generation system for Cogni-Flow.
Creates various types of quizzes from processed text content.
"""

import re
import json
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

class QuizType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    MATCHING = "matching"

@dataclass
class QuizQuestion:
    """Container for a single quiz question."""
    question_id: str
    question_type: QuizType
    question_text: str
    correct_answer: Any
    options: Optional[List[str]] = None  # For multiple choice
    explanation: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard
    keywords: Optional[List[str]] = None
    source_text: Optional[str] = None

@dataclass
class Quiz:
    """Container for a complete quiz."""
    title: str
    description: str
    questions: List[QuizQuestion]
    total_score: int
    estimated_time: int  # minutes
    difficulty_level: str
    tags: List[str] = None

@dataclass
class QuizResult:
    """Container for quiz results."""
    quiz_id: str
    user_answers: Dict[str, Any]
    correct_answers: Dict[str, Any]
    score: int
    total_questions: int
    time_taken: int  # seconds
    feedback: Dict[str, str]

class QuizGenerator(ABC):
    """Abstract base class for quiz generators."""
    
    @abstractmethod
    def generate_multiple_choice(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        pass
    
    @abstractmethod
    def generate_fill_in_blank(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        pass
    
    @abstractmethod
    def generate_true_false(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        pass

class LLMQuizGenerator(QuizGenerator):
    """LLM-based quiz generator using text processing capabilities."""
    
    def __init__(self, text_processor=None):
        self.logger = logging.getLogger(__name__)
        self.text_processor = text_processor
    
    def _make_llm_request(self, prompt: str, max_tokens: int = 500) -> str:
        """Make a request to the LLM for quiz generation."""
        if not self.text_processor or not self.text_processor.provider:
            return ""
        
        # This would use the text processor's LLM provider
        # For now, return a mock response
        return "Mock LLM response for quiz generation"
    
    def generate_multiple_choice(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        """Generate multiple choice questions from text."""
        prompt = f"""
        Based on the following text, create {num_questions} multiple choice questions.
        Each question should have 4 options with only one correct answer.
        Format as JSON with this structure:
        {{
            "questions": [
                {{
                    "question": "Question text?",
                    "options": ["A", "B", "C", "D"],
                    "correct": 0,
                    "explanation": "Why this is correct"
                }}
            ]
        }}
        
        Text: {text}
        """
        
        # Mock implementation - in real version, this would use LLM
        questions = []
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            if len(sentence.split()) < 5:
                continue
                
            # Extract key term for the question
            words = sentence.split()
            key_word = max(words, key=len) if words else "concept"
            
            question = QuizQuestion(
                question_id=f"mc_{i+1}",
                question_type=QuizType.MULTIPLE_CHOICE,
                question_text=f"What is the main concept discussed in: '{sentence[:50]}...'?",
                correct_answer=0,
                options=[
                    key_word.capitalize(),
                    f"Alternative {key_word}",
                    f"Related {key_word}",
                    f"Similar {key_word}"
                ],
                explanation=f"The correct answer is {key_word} based on the context provided.",
                difficulty="medium",
                source_text=sentence
            )
            questions.append(question)
        
        return questions
    
    def generate_fill_in_blank(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        """Generate fill-in-the-blank questions from text."""
        questions = []
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            words = sentence.split()
            
            if len(words) < 5:
                continue
            
            # Find important words (longer than 4 characters, not common words)
            important_words = [w for w in words if len(w) > 4 and w.lower() not in 
                              {'this', 'that', 'these', 'those', 'there', 'where', 'when', 'which'}]
            
            if not important_words:
                continue
            
            # Select a word to blank out
            blank_word = random.choice(important_words)
            question_text = sentence.replace(blank_word, "______")
            
            question = QuizQuestion(
                question_id=f"fib_{i+1}",
                question_type=QuizType.FILL_IN_BLANK,
                question_text=question_text,
                correct_answer=blank_word.lower(),
                explanation=f"The missing word is '{blank_word}' based on the context.",
                difficulty="medium",
                source_text=sentence
            )
            questions.append(question)
        
        return questions
    
    def generate_true_false(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        """Generate true/false questions from text."""
        questions = []
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            if len(sentence.split()) < 5:
                continue
            
            # Create true statement from original text
            true_question = QuizQuestion(
                question_id=f"tf_{i+1}_true",
                question_type=QuizType.TRUE_FALSE,
                question_text=sentence,
                correct_answer=True,
                options=["True", "False"],
                explanation="This statement is directly supported by the text.",
                difficulty="easy",
                source_text=sentence
            )
            
            # Create false statement by modifying the original
            modified_sentence = self._create_false_statement(sentence)
            false_question = QuizQuestion(
                question_id=f"tf_{i+1}_false",
                question_type=QuizType.TRUE_FALSE,
                question_text=modified_sentence,
                correct_answer=False,
                options=["True", "False"],
                explanation="This statement contradicts information in the text.",
                difficulty="easy",
                source_text=sentence
            )
            
            # Randomly choose between true and false question
            questions.append(random.choice([true_question, false_question]))
        
        return questions[:num_questions]
    
    def _create_false_statement(self, sentence: str) -> str:
        """Create a false statement by modifying the original sentence."""
        # Simple approach: negate the statement or change key terms
        if " is " in sentence:
            return sentence.replace(" is ", " is not ")
        elif " are " in sentence:
            return sentence.replace(" are ", " are not ")
        elif " can " in sentence:
            return sentence.replace(" can ", " cannot ")
        else:
            # Add "not" after the first verb
            words = sentence.split()
            for i, word in enumerate(words):
                if word.lower() in ['contains', 'includes', 'shows', 'demonstrates', 'involves']:
                    words.insert(i+1, 'not')
                    return ' '.join(words)
            return f"It is false that {sentence.lower()}"

class SimpleQuizGenerator(QuizGenerator):
    """Simple rule-based quiz generator for when LLM is not available."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_multiple_choice(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        """Generate simple multiple choice questions."""
        questions = []
        
        # Extract key terms from text
        key_terms = self._extract_key_terms(text)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for i, term in enumerate(key_terms[:num_questions]):
            # Find sentence containing this term
            context_sentence = next((s for s in sentences if term.lower() in s.lower()), sentences[0] if sentences else "")
            
            question = QuizQuestion(
                question_id=f"mc_simple_{i+1}",
                question_type=QuizType.MULTIPLE_CHOICE,
                question_text=f"According to the text, which term is most relevant to '{context_sentence[:30]}...'?",
                correct_answer=0,
                options=[
                    term,
                    f"General {term}",
                    f"Basic {term}",
                    f"Common {term}"
                ],
                explanation=f"The term '{term}' appears in the context and is most relevant.",
                difficulty="medium"
            )
            questions.append(question)
        
        return questions
    
    def generate_fill_in_blank(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        """Generate simple fill-in-the-blank questions."""
        questions = []
        key_terms = self._extract_key_terms(text)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for i, term in enumerate(key_terms[:num_questions]):
            # Find sentence with this term
            for sentence in sentences:
                if term.lower() in sentence.lower():
                    question_text = sentence.replace(term, "______")
                    
                    question = QuizQuestion(
                        question_id=f"fib_simple_{i+1}",
                        question_type=QuizType.FILL_IN_BLANK,
                        question_text=question_text,
                        correct_answer=term.lower(),
                        explanation=f"The missing term is '{term}'.",
                        difficulty="medium"
                    )
                    questions.append(question)
                    break
        
        return questions
    
    def generate_true_false(self, text: str, num_questions: int = 5) -> List[QuizQuestion]:
        """Generate simple true/false questions."""
        questions = []
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for i, sentence in enumerate(sentences[:num_questions]):
            if len(sentence.split()) < 5:
                continue
            
            question = QuizQuestion(
                question_id=f"tf_simple_{i+1}",
                question_type=QuizType.TRUE_FALSE,
                question_text=sentence,
                correct_answer=True,
                options=["True", "False"],
                explanation="This statement is directly from the source text.",
                difficulty="easy"
            )
            questions.append(question)
        
        return questions
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text using simple methods."""
        from collections import Counter
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        words = re.findall(r'\\b[A-Za-z]{4,}\\b', text.lower())  # Words with 4+ letters
        word_freq = Counter([w for w in words if w not in stop_words])
        
        # Return most common terms
        return [word.capitalize() for word, _ in word_freq.most_common(10)]

class QuizManager:
    """Manager class for handling quiz generation and evaluation."""
    
    def __init__(self, text_processor=None):
        self.logger = logging.getLogger(__name__)
        
        # Try to use LLM-based generator, fallback to simple
        if text_processor:
            self.generator = LLMQuizGenerator(text_processor)
        else:
            self.generator = SimpleQuizGenerator()
        
        self.quizzes: Dict[str, Quiz] = {}
    
    def create_quiz(self, text: str, title: str = "Study Quiz", 
                   question_types: List[QuizType] = None, 
                   questions_per_type: int = 3) -> Quiz:
        """Create a comprehensive quiz from text."""
        
        if question_types is None:
            question_types = [QuizType.MULTIPLE_CHOICE, QuizType.FILL_IN_BLANK, QuizType.TRUE_FALSE]
        
        all_questions = []
        
        for q_type in question_types:
            try:
                if q_type == QuizType.MULTIPLE_CHOICE:
                    questions = self.generator.generate_multiple_choice(text, questions_per_type)
                elif q_type == QuizType.FILL_IN_BLANK:
                    questions = self.generator.generate_fill_in_blank(text, questions_per_type)
                elif q_type == QuizType.TRUE_FALSE:
                    questions = self.generator.generate_true_false(text, questions_per_type)
                else:
                    continue
                
                all_questions.extend(questions)
                
            except Exception as e:
                self.logger.error(f"Error generating {q_type.value} questions: {e}")
        
        # Create quiz
        quiz = Quiz(
            title=title,
            description=f"Quiz generated from study material with {len(all_questions)} questions",
            questions=all_questions,
            total_score=len(all_questions),
            estimated_time=max(5, len(all_questions) * 2),  # 2 minutes per question
            difficulty_level="mixed",
            tags=["auto-generated", "study"]
        )
        
        # Store quiz
        quiz_id = f"quiz_{len(self.quizzes) + 1}"
        self.quizzes[quiz_id] = quiz
        
        return quiz
    
    def evaluate_quiz(self, quiz: Quiz, user_answers: Dict[str, Any]) -> QuizResult:
        """Evaluate quiz answers and provide results."""
        correct_answers = {}
        feedback = {}
        score = 0
        
        for question in quiz.questions:
            qid = question.question_id
            user_answer = user_answers.get(qid)
            correct_answer = question.correct_answer
            
            correct_answers[qid] = correct_answer
            
            # Evaluate answer
            is_correct = False
            
            if question.question_type == QuizType.MULTIPLE_CHOICE:
                is_correct = user_answer == correct_answer
            elif question.question_type == QuizType.TRUE_FALSE:
                is_correct = user_answer == correct_answer
            elif question.question_type == QuizType.FILL_IN_BLANK:
                if user_answer and isinstance(correct_answer, str):
                    is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
            
            if is_correct:
                score += 1
                feedback[qid] = "Correct! " + (question.explanation or "")
            else:
                feedback[qid] = f"Incorrect. The correct answer is: {correct_answer}. " + (question.explanation or "")
        
        return QuizResult(
            quiz_id=quiz.title,
            user_answers=user_answers,
            correct_answers=correct_answers,
            score=score,
            total_questions=len(quiz.questions),
            time_taken=0,  # Would be calculated by the UI
            feedback=feedback
        )
    
    def get_quiz_statistics(self, quiz: Quiz) -> Dict[str, Any]:
        """Get statistics about a quiz."""
        type_counts = {}
        for question in quiz.questions:
            q_type = question.question_type.value
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        return {
            'total_questions': len(quiz.questions),
            'question_types': type_counts,
            'estimated_time': quiz.estimated_time,
            'difficulty': quiz.difficulty_level
        }
'''

# Save core/quiz_generator.py
with open('core/quiz_generator.py', 'w', encoding='utf-8') as f:
    f.write(quiz_generator_content)

print("✅ Created core/quiz_generator.py")
print("\nCore modules created successfully!")
print("\nNext: Create GUI components and utility modules...")