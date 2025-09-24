"""
Text processing and LLM integration for Cogni-Flow.
Handles content analysis, summarization, and intelligent processing.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

@dataclass 
class ProcessedContent:
    """Container for processed text content."""
    original_text: str
    title: str
    summary: str
    key_concepts: List[str]
    main_topics: List[str]
    complexity_level: str  # beginner, intermediate, advanced
    word_count: int
    reading_time: int  # estimated minutes

@dataclass
class SmartNotes:
    """Container for generated smart notes."""
    title: str
    sections: List[Dict[str, str]]  # [{"heading": "...", "content": "..."}]
    key_points: List[str]
    definitions: Dict[str, str]

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        pass

    @abstractmethod
    def extract_key_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        pass

    @abstractmethod
    def generate_smart_notes(self, text: str) -> SmartNotes:
        pass

    @abstractmethod
    def assess_complexity(self, text: str) -> str:
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider for text processing."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")

        self.client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
        self.model = model
        self.logger = logging.getLogger(__name__)

    def _make_api_call(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Make an API call to OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            return ""

    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a concise summary of the text."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that creates clear, concise summaries for students. Focus on the main ideas and key concepts."},
            {"role": "user", "content": f"Please create a {max_length}-word summary of this text that would be helpful for studying:

{text}"}
        ]
        return self._make_api_call(messages)

    def extract_key_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """Extract key concepts from the text."""
        messages = [
            {"role": "system", "content": "You are an educational assistant that identifies key concepts from academic text. Return only the concepts as a simple list."},
            {"role": "user", "content": f"Extract the top {max_concepts} key concepts from this text. Return them as a comma-separated list:

{text}"}
        ]

        response = self._make_api_call(messages)
        if response:
            # Parse the comma-separated list
            concepts = [concept.strip() for concept in response.split(',')]
            return concepts[:max_concepts]
        return []

    def generate_smart_notes(self, text: str) -> SmartNotes:
        """Generate structured smart notes from the text."""
        messages = [
            {"role": "system", "content": """You are an educational assistant that creates well-structured study notes. 
            Create notes with clear headings, bullet points, and key definitions. 
            Format your response as JSON with this structure:
            {
                "title": "Topic Title",
                "sections": [{"heading": "Section Name", "content": "Bullet points and content"}],
                "key_points": ["Point 1", "Point 2"],
                "definitions": {"Term": "Definition"}
            }"""},
            {"role": "user", "content": f"Create comprehensive study notes from this text:

{text}"}
        ]

        response = self._make_api_call(messages, max_tokens=1500)

        try:
            notes_data = json.loads(response)
            return SmartNotes(
                title=notes_data.get("title", "Study Notes"),
                sections=notes_data.get("sections", []),
                key_points=notes_data.get("key_points", []),
                definitions=notes_data.get("definitions", {})
            )
        except json.JSONDecodeError:
            # Fallback to basic parsing
            return SmartNotes(
                title="Study Notes",
                sections=[{"heading": "Content", "content": response}],
                key_points=[],
                definitions={}
            )

    def assess_complexity(self, text: str) -> str:
        """Assess the complexity level of the text."""
        messages = [
            {"role": "system", "content": "You are an educational assistant that assesses text complexity. Respond with only one word: beginner, intermediate, or advanced."},
            {"role": "user", "content": f"What is the complexity level of this text for students?

{text}"}
        ]

        response = self._make_api_call(messages, max_tokens=10)
        complexity = response.lower().strip()

        if complexity in ['beginner', 'intermediate', 'advanced']:
            return complexity
        return 'intermediate'  # Default fallback

class LocalProvider(LLMProvider):
    """Local transformer-based provider for text processing."""

    def __init__(self):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers package not available. Install with: pip install transformers torch")

        self.summarizer = None
        self.tokenizer = None
        self.logger = logging.getLogger(__name__)
        self._initialize_models()

    def _initialize_models(self):
        """Initialize local models."""
        try:
            # Use a smaller model that can run on most machines
            self.summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("Local models initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize local models: {e}")

    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate summary using local model."""
        if not self.summarizer:
            return "Local summarization model not available."

        try:
            # Truncate text if too long for the model
            max_input = 1024
            if len(text) > max_input:
                text = text[:max_input]

            result = self.summarizer(text, max_length=max_length, min_length=50, do_sample=False)
            return result[0]['summary_text']
        except Exception as e:
            self.logger.error(f"Local summarization failed: {e}")
            return "Error generating summary with local model."

    def extract_key_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """Extract key concepts using simple NLP techniques."""
        # This is a simplified implementation - could be enhanced with NER models
        import re
        from collections import Counter

        # Remove common words and extract important terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}

        # Extract words and phrases
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        word_freq = Counter([w for w in words if w not in stopwords])

        # Get most common terms
        key_concepts = [word.capitalize() for word, _ in word_freq.most_common(max_concepts)]
        return key_concepts

    def generate_smart_notes(self, text: str) -> SmartNotes:
        """Generate basic structured notes."""
        # Simple implementation - could be enhanced with better models
        summary = self.generate_summary(text)
        key_concepts = self.extract_key_concepts(text)

        return SmartNotes(
            title="Study Notes",
            sections=[
                {"heading": "Summary", "content": summary},
                {"heading": "Key Concepts", "content": "\n".join([f"• {concept}" for concept in key_concepts])}
            ],
            key_points=key_concepts[:5],
            definitions={}
        )

    def assess_complexity(self, text: str) -> str:
        """Assess complexity using simple metrics."""
        # Simple complexity assessment based on sentence length and vocabulary
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        vocabulary_ratio = unique_words / total_words if total_words > 0 else 0

        if avg_sentence_length > 25 or vocabulary_ratio > 0.7:
            return 'advanced'
        elif avg_sentence_length > 15 or vocabulary_ratio > 0.5:
            return 'intermediate'
        else:
            return 'beginner'

class TextProcessor:
    """Main text processing coordinator."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.logger = logging.getLogger(__name__)

        # Initialize provider
        if provider:
            self.provider = provider
        else:
            # Try to initialize OpenAI first, fallback to local
            try:
                self.provider = OpenAIProvider()
                self.logger.info("Using OpenAI provider")
            except Exception as e:
                self.logger.warning(f"OpenAI provider failed: {e}")
                try:
                    self.provider = LocalProvider()
                    self.logger.info("Using local provider")
                except Exception as e:
                    self.logger.error(f"All providers failed: {e}")
                    self.provider = None

    def process_content(self, text: str, title: str = "") -> ProcessedContent:
        """Process text content and extract structured information."""
        if not self.provider:
            raise RuntimeError("No LLM provider available")

        # Basic text analysis
        word_count = len(text.split())
        reading_time = max(1, word_count // 200)  # Assume 200 words per minute

        # Extract title if not provided
        if not title:
            title = self._extract_title(text)

        # Generate processed content
        summary = self.provider.generate_summary(text)
        key_concepts = self.provider.extract_key_concepts(text)
        complexity = self.provider.assess_complexity(text)

        # Extract main topics (simplified implementation)
        main_topics = key_concepts[:5]  # Use top 5 key concepts as main topics

        return ProcessedContent(
            original_text=text,
            title=title,
            summary=summary,
            key_concepts=key_concepts,
            main_topics=main_topics,
            complexity_level=complexity,
            word_count=word_count,
            reading_time=reading_time
        )

    def generate_smart_notes(self, text: str) -> SmartNotes:
        """Generate smart notes from text."""
        if not self.provider:
            raise RuntimeError("No LLM provider available")

        return self.provider.generate_smart_notes(text)

    def _extract_title(self, text: str) -> str:
        """Extract a title from the beginning of the text."""
        # Look for the first sentence or line that could be a title
        lines = text.split('\n')
        first_line = lines[0].strip() if lines else ""

        # If first line is short and doesn't end with period, likely a title
        if first_line and len(first_line) < 100 and not first_line.endswith('.'):
            return first_line

        # Otherwise, take first few words
        words = text.split()[:8]
        return ' '.join(words) + "..." if len(words) == 8 else ' '.join(words)

    def is_available(self) -> bool:
        """Check if text processor is available."""
        return self.provider is not None
