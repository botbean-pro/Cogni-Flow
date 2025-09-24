"""
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

        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())  # Words with 4+ letters
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
