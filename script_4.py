# Create core/mind_mapper.py - Mind map generation

mind_mapper_content = '''"""
Mind map generation system for Cogni-Flow.
Creates visual mind maps from processed text content using NetworkX.
"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.patches as patches
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

@dataclass
class MindMapNode:
    """Container for a mind map node."""
    id: str
    label: str
    level: int  # Distance from center (0 = center, 1 = main branch, etc.)
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    color: str = "#4A90E2"
    size: int = 10
    position: Optional[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []

@dataclass 
class MindMapEdge:
    """Container for a mind map edge."""
    source_id: str
    target_id: str
    weight: float = 1.0
    color: str = "#666666"
    width: int = 2

@dataclass
class MindMap:
    """Container for a complete mind map."""
    title: str
    center_node: MindMapNode
    nodes: Dict[str, MindMapNode]
    edges: List[MindMapEdge]
    layout: str = "spring"  # spring, circular, hierarchical
    width: int = 1200
    height: int = 800

class TextAnalyzer:
    """Analyzes text to extract hierarchical concepts for mind mapping."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_main_topic(self, text: str, title: str = "") -> str:
        """Extract the main topic from text."""
        if title:
            return title
        
        # Try to find the main topic from the first sentence
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            first_sentence = sentences[0]
            # Look for patterns like "X is..." or "X are..." 
            match = re.search(r'^([^,]+)\\s+(?:is|are|involves|means)', first_sentence, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: use most frequent important words
        important_words = self._extract_important_words(text)
        if important_words:
            return important_words[0].title()
        
        return "Main Topic"
    
    def extract_key_concepts(self, text: str, max_concepts: int = 8) -> List[str]:
        """Extract key concepts that will become main branches."""
        concepts = []
        
        # Look for section headers (words followed by colons)
        headers = re.findall(r'^([A-Za-z][^:]{2,30}):', text, re.MULTILINE)
        concepts.extend([h.strip().title() for h in headers])
        
        # Look for enumerated items
        enum_items = re.findall(r'^\\d+\\.\\s*([A-Za-z][^.]{5,50})', text, re.MULTILINE)
        concepts.extend([item.strip().title() for item in enum_items])
        
        # Look for bullet points
        bullet_items = re.findall(r'^[•\\-\\*]\\s*([A-Za-z][^.]{5,50})', text, re.MULTILINE)
        concepts.extend([item.strip().title() for item in bullet_items])
        
        # Extract important noun phrases
        noun_phrases = self._extract_noun_phrases(text)
        concepts.extend(noun_phrases)
        
        # Remove duplicates and limit count
        unique_concepts = list(dict.fromkeys(concepts))  # Preserve order
        return unique_concepts[:max_concepts]
    
    def extract_subconcepts(self, text: str, main_concept: str, max_subconcepts: int = 5) -> List[str]:
        """Extract subconcepts related to a main concept."""
        subconcepts = []
        
        # Find sentences containing the main concept
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        related_sentences = [s for s in sentences if main_concept.lower() in s.lower()]
        
        if not related_sentences:
            # If no direct matches, use broader search
            concept_words = main_concept.lower().split()
            related_sentences = [s for s in sentences 
                               if any(word in s.lower() for word in concept_words)]
        
        # Extract important terms from related sentences
        for sentence in related_sentences[:3]:  # Limit to avoid too many
            terms = self._extract_important_words(sentence)
            subconcepts.extend(terms[:2])  # Top 2 terms per sentence
        
        # Remove the main concept itself and duplicates
        subconcepts = [sc for sc in subconcepts if sc.lower() != main_concept.lower()]
        unique_subconcepts = list(dict.fromkeys(subconcepts))
        
        return [sc.title() for sc in unique_subconcepts[:max_subconcepts]]
    
    def _extract_important_words(self, text: str) -> List[str]:
        """Extract important words from text using frequency and length."""
        # Common stop words to exclude
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 
            'must', 'can', 'this', 'that', 'these', 'those', 'there', 'where', 'when', 
            'which', 'who', 'why', 'how', 'what', 'it', 'its', 'they', 'them', 'their',
            'also', 'such', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'among', 'through', 'during', 'include', 'includes'
        }
        
        # Extract words (4+ characters, not stop words)
        words = re.findall(r'\\b[A-Za-z]{4,}\\b', text.lower())
        filtered_words = [w for w in words if w not in stop_words]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        # Return most frequent words
        return [word for word, _ in word_freq.most_common(10)]
    
    def _extract_noun_phrases(self, text: str) -> List[str]:
        """Extract noun phrases using simple patterns."""
        # Simple patterns for noun phrases
        patterns = [
            r'\\b([A-Z][a-z]+\\s+[A-Z][a-z]+)\\b',  # Proper noun pairs
            r'\\b(the\\s+[a-z]+\\s+[a-z]+)\\b',      # "the X Y" patterns
            r'\\b([a-z]+\\s+process)\\b',            # "X process" patterns
            r'\\b([a-z]+\\s+system)\\b',             # "X system" patterns
            r'\\b([a-z]+\\s+method)\\b',             # "X method" patterns
        ]
        
        noun_phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            noun_phrases.extend([m.title() for m in matches])
        
        return list(set(noun_phrases))  # Remove duplicates

class MindMapGenerator:
    """Generates mind maps from text content."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_analyzer = TextAnalyzer()
        
        # Color schemes for different node levels
        self.color_schemes = {
            'default': ['#4A90E2', '#50C878', '#FFB347', '#DDA0DD', '#F0E68C', '#98FB98', '#F5A9A9', '#87CEEB'],
            'blue': ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#EFF6FF'],
            'nature': ['#22543D', '#38A169', '#68D391', '#9AE6B4', '#C6F6D5', '#F0FFF4']
        }
    
    def generate_from_text(self, text: str, title: str = "", 
                          layout: str = "spring", color_scheme: str = "default") -> MindMap:
        """Generate a mind map from text content."""
        
        # Extract main topic
        main_topic = self.text_analyzer.extract_main_topic(text, title)
        
        # Create center node
        center_node = MindMapNode(
            id="center",
            label=main_topic,
            level=0,
            color=self.color_schemes[color_scheme][0],
            size=20
        )
        
        nodes = {"center": center_node}
        edges = []
        
        # Extract main concepts (level 1)
        main_concepts = self.text_analyzer.extract_key_concepts(text)
        
        for i, concept in enumerate(main_concepts):
            node_id = f"main_{i}"
            color_index = (i + 1) % len(self.color_schemes[color_scheme])
            
            main_node = MindMapNode(
                id=node_id,
                label=concept,
                level=1,
                parent_id="center",
                color=self.color_schemes[color_scheme][color_index],
                size=15
            )
            
            nodes[node_id] = main_node
            center_node.children_ids.append(node_id)
            
            # Create edge from center to main concept
            edges.append(MindMapEdge(
                source_id="center",
                target_id=node_id,
                color=main_node.color,
                width=3
            ))
            
            # Extract subconcepts (level 2)
            subconcepts = self.text_analyzer.extract_subconcepts(text, concept)
            
            for j, subconcept in enumerate(subconcepts):
                sub_node_id = f"sub_{i}_{j}"
                
                sub_node = MindMapNode(
                    id=sub_node_id,
                    label=subconcept,
                    level=2,
                    parent_id=node_id,
                    color=self._lighten_color(main_node.color),
                    size=10
                )
                
                nodes[sub_node_id] = sub_node
                main_node.children_ids.append(sub_node_id)
                
                # Create edge from main concept to subconcept
                edges.append(MindMapEdge(
                    source_id=node_id,
                    target_id=sub_node_id,
                    color=main_node.color,
                    width=2
                ))
        
        return MindMap(
            title=main_topic,
            center_node=center_node,
            nodes=nodes,
            edges=edges,
            layout=layout
        )
    
    def _lighten_color(self, hex_color: str, factor: float = 0.3) -> str:
        """Lighten a hex color by a factor."""
        # Simple color lightening - in real implementation use proper color library
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#E0E0E0"  # Default light gray

class MindMapRenderer:
    """Renders mind maps to various formats."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def render_to_matplotlib(self, mind_map: MindMap, save_path: Optional[str] = None) -> bool:
        """Render mind map using matplotlib."""
        if not NETWORKX_AVAILABLE:
            self.logger.error("NetworkX not available for mind map rendering")
            return False
        
        try:
            # Create NetworkX graph
            G = nx.Graph()
            
            # Add nodes
            for node_id, node in mind_map.nodes.items():
                G.add_node(node_id, 
                          label=node.label, 
                          color=node.color,
                          size=node.size * 50)  # Scale for matplotlib
            
            # Add edges
            for edge in mind_map.edges:
                G.add_edge(edge.source_id, edge.target_id, 
                          color=edge.color, width=edge.width)
            
            # Set up the plot
            plt.figure(figsize=(mind_map.width/100, mind_map.height/100))
            plt.clf()
            
            # Choose layout
            if mind_map.layout == "circular":
                pos = nx.circular_layout(G)
            elif mind_map.layout == "hierarchical":
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot') if hasattr(nx, 'nx_agraph') else nx.spring_layout(G)
            else:  # spring layout (default)
                pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Draw edges
            edge_colors = [G[u][v]['color'] for u, v in G.edges()]
            edge_widths = [G[u][v]['width'] for u, v in G.edges()]
            nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, alpha=0.7)
            
            # Draw nodes
            node_colors = [G.nodes[node]['color'] for node in G.nodes()]
            node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9)
            
            # Draw labels
            labels = {node_id: node.label for node_id, node in mind_map.nodes.items()}
            nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
            
            plt.title(mind_map.title, fontsize=16, fontweight='bold', pad=20)
            plt.axis('off')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
                self.logger.info(f"Mind map saved to {save_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rendering mind map: {e}")
            return False
    
    def render_to_html(self, mind_map: MindMap) -> str:
        """Render mind map as interactive HTML/SVG."""
        # Create a simple HTML representation
        html_template = """
        <div class="mind-map" style="width: {width}px; height: {height}px; position: relative; border: 1px solid #ddd; background: #f9f9f9;">
            <h3 style="text-align: center; margin: 10px;">{title}</h3>
            <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
                {content}
            </svg>
        </div>
        """
        
        svg_content = ""
        
        # Simple circular layout for HTML rendering
        import math
        center_x, center_y = mind_map.width // 2, mind_map.height // 2
        
        # Draw center node
        center_node = mind_map.center_node
        svg_content += f'''
        <circle cx="{center_x}" cy="{center_y}" r="40" fill="{center_node.color}" stroke="#333" stroke-width="2"/>
        <text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" fill="white" font-weight="bold">{center_node.label}</text>
        '''
        
        # Draw main branches in circle around center
        main_nodes = [node for node in mind_map.nodes.values() if node.level == 1]
        angle_step = 2 * math.pi / len(main_nodes) if main_nodes else 0
        
        for i, node in enumerate(main_nodes):
            angle = i * angle_step
            radius = 150
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Draw line from center to node
            svg_content += f'''
            <line x1="{center_x}" y1="{center_y}" x2="{x}" y2="{y}" stroke="{node.color}" stroke-width="3"/>
            '''
            
            # Draw node
            svg_content += f'''
            <circle cx="{x}" cy="{y}" r="25" fill="{node.color}" stroke="#333" stroke-width="1"/>
            <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" fill="white" font-size="12">{node.label[:10]}</text>
            '''
            
            # Draw subnodes
            subnodes = [n for n in mind_map.nodes.values() if n.parent_id == node.id]
            if subnodes:
                sub_angle_step = math.pi / 3 / len(subnodes) if len(subnodes) > 1 else 0
                for j, subnode in enumerate(subnodes):
                    sub_angle = angle + (j - len(subnodes)/2) * sub_angle_step
                    sub_radius = 80
                    sub_x = x + sub_radius * math.cos(sub_angle)
                    sub_y = y + sub_radius * math.sin(sub_angle)
                    
                    # Draw line from main node to subnode
                    svg_content += f'''
                    <line x1="{x}" y1="{y}" x2="{sub_x}" y2="{sub_y}" stroke="{subnode.color}" stroke-width="2"/>
                    '''
                    
                    # Draw subnode
                    svg_content += f'''
                    <circle cx="{sub_x}" cy="{sub_y}" r="15" fill="{subnode.color}" stroke="#333" stroke-width="1"/>
                    <text x="{sub_x}" y="{sub_y}" text-anchor="middle" dominant-baseline="middle" fill="white" font-size="10">{subnode.label[:8]}</text>
                    '''
        
        return html_template.format(
            width=mind_map.width,
            height=mind_map.height,
            title=mind_map.title,
            content=svg_content
        )
    
    def export_data(self, mind_map: MindMap) -> Dict[str, Any]:
        """Export mind map data as JSON-serializable dictionary."""
        return {
            'title': mind_map.title,
            'layout': mind_map.layout,
            'dimensions': {'width': mind_map.width, 'height': mind_map.height},
            'center_node': {
                'id': mind_map.center_node.id,
                'label': mind_map.center_node.label,
                'color': mind_map.center_node.color
            },
            'nodes': [
                {
                    'id': node.id,
                    'label': node.label,
                    'level': node.level,
                    'parent_id': node.parent_id,
                    'color': node.color,
                    'size': node.size
                }
                for node in mind_map.nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source_id,
                    'target': edge.target_id,
                    'color': edge.color,
                    'width': edge.width
                }
                for edge in mind_map.edges
            ]
        }

class MindMapManager:
    """Manager class for mind map operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.generator = MindMapGenerator()
        self.renderer = MindMapRenderer()
        self.mind_maps: Dict[str, MindMap] = {}
    
    def create_mind_map(self, text: str, title: str = "", 
                       layout: str = "spring", color_scheme: str = "default") -> str:
        """Create a new mind map and return its ID."""
        try:
            mind_map = self.generator.generate_from_text(text, title, layout, color_scheme)
            map_id = f"mindmap_{len(self.mind_maps) + 1}"
            self.mind_maps[map_id] = mind_map
            
            self.logger.info(f"Created mind map '{map_id}' with {len(mind_map.nodes)} nodes")
            return map_id
            
        except Exception as e:
            self.logger.error(f"Error creating mind map: {e}")
            raise
    
    def get_mind_map(self, map_id: str) -> Optional[MindMap]:
        """Get a mind map by ID."""
        return self.mind_maps.get(map_id)
    
    def render_mind_map(self, map_id: str, format: str = "html", save_path: Optional[str] = None) -> Any:
        """Render a mind map in the specified format."""
        mind_map = self.mind_maps.get(map_id)
        if not mind_map:
            raise ValueError(f"Mind map {map_id} not found")
        
        if format == "matplotlib":
            success = self.renderer.render_to_matplotlib(mind_map, save_path)
            return success
        elif format == "html":
            return self.renderer.render_to_html(mind_map)
        elif format == "data":
            return self.renderer.export_data(mind_map)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def list_mind_maps(self) -> List[Dict[str, Any]]:
        """List all available mind maps."""
        return [
            {
                'id': map_id,
                'title': mind_map.title,
                'node_count': len(mind_map.nodes),
                'layout': mind_map.layout
            }
            for map_id, mind_map in self.mind_maps.items()
        ]
    
    def delete_mind_map(self, map_id: str) -> bool:
        """Delete a mind map."""
        if map_id in self.mind_maps:
            del self.mind_maps[map_id]
            return True
        return False
    
    def is_available(self) -> bool:
        """Check if mind mapping functionality is available."""
        return NETWORKX_AVAILABLE
'''

# Save core/mind_mapper.py
with open('core/mind_mapper.py', 'w', encoding='utf-8') as f:
    f.write(mind_mapper_content)

print("✅ Created core/mind_mapper.py")

# Create utils/file_handlers.py - File processing utilities
file_handlers_content = '''"""
File handling utilities for Cogni-Flow.
Supports PDF, DOCX, and other document formats for text extraction.
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any, List, BinaryIO
from dataclasses import dataclass
from abc import ABC, abstractmethod

# PDF processing
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# DOCX processing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Web content extraction
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_EXTRACTION_AVAILABLE = True
except ImportError:
    WEB_EXTRACTION_AVAILABLE = False

@dataclass
class ExtractedContent:
    """Container for extracted content from files."""
    text: str
    title: str
    metadata: Dict[str, Any]
    page_count: int = 0
    word_count: int = 0
    file_type: str = "unknown"
    extraction_method: str = "unknown"

class FileExtractor(ABC):
    """Abstract base class for file extractors."""
    
    @abstractmethod
    def extract(self, file_path: str) -> ExtractedContent:
        pass
    
    @abstractmethod
    def is_supported(self, file_path: str) -> bool:
        pass

class PDFExtractor(FileExtractor):
    """PDF text extraction using multiple libraries."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_methods = []
        
        if PDFPLUMBER_AVAILABLE:
            self.available_methods.append("pdfplumber")
        if PYMUPDF_AVAILABLE:
            self.available_methods.append("pymupdf")
        if PYPDF2_AVAILABLE:
            self.available_methods.append("pypdf2")
    
    def extract(self, file_path: str) -> ExtractedContent:
        """Extract text from PDF using the best available method."""
        if not self.available_methods:
            raise RuntimeError("No PDF extraction libraries available")
        
        # Try methods in order of preference
        for method in self.available_methods:
            try:
                if method == "pdfplumber":
                    return self._extract_with_pdfplumber(file_path)
                elif method == "pymupdf":
                    return self._extract_with_pymupdf(file_path)
                elif method == "pypdf2":
                    return self._extract_with_pypdf2(file_path)
            except Exception as e:
                self.logger.warning(f"PDF extraction failed with {method}: {e}")
                continue
        
        raise RuntimeError("All PDF extraction methods failed")
    
    def _extract_with_pdfplumber(self, file_path: str) -> ExtractedContent:
        """Extract PDF text using pdfplumber."""
        with pdfplumber.open(file_path) as pdf:
            text_parts = []
            page_count = len(pdf.pages)
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            full_text = "\\n\\n".join(text_parts)
            
            # Extract metadata
            metadata = pdf.metadata or {}
            title = metadata.get('Title', os.path.basename(file_path))
            
            return ExtractedContent(
                text=full_text,
                title=title,
                metadata=dict(metadata),
                page_count=page_count,
                word_count=len(full_text.split()),
                file_type="pdf",
                extraction_method="pdfplumber"
            )
    
    def _extract_with_pymupdf(self, file_path: str) -> ExtractedContent:
        """Extract PDF text using PyMuPDF."""
        doc = fitz.open(file_path)
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)
        
        full_text = "\\n\\n".join(text_parts)
        
        # Extract metadata
        metadata = doc.metadata
        title = metadata.get('title', os.path.basename(file_path))
        
        doc.close()
        
        return ExtractedContent(
            text=full_text,
            title=title,
            metadata=metadata,
            page_count=len(doc),
            word_count=len(full_text.split()),
            file_type="pdf",
            extraction_method="pymupdf"
        )
    
    def _extract_with_pypdf2(self, file_path: str) -> ExtractedContent:
        """Extract PDF text using PyPDF2."""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_parts = []
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(page_text)
            
            full_text = "\\n\\n".join(text_parts)
            
            # Extract metadata
            metadata = pdf_reader.metadata or {}
            title = metadata.get('/Title', os.path.basename(file_path))
            
            return ExtractedContent(
                text=full_text,
                title=str(title) if title else os.path.basename(file_path),
                metadata={str(k): str(v) for k, v in metadata.items()},
                page_count=len(pdf_reader.pages),
                word_count=len(full_text.split()),
                file_type="pdf",
                extraction_method="pypdf2"
            )
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file is a supported PDF."""
        return file_path.lower().endswith('.pdf') and len(self.available_methods) > 0

class DOCXExtractor(FileExtractor):
    """DOCX text extraction."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract(self, file_path: str) -> ExtractedContent:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            raise RuntimeError("python-docx library not available")
        
        doc = Document(file_path)
        
        # Extract paragraphs
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        full_text = "\\n\\n".join(paragraphs)
        
        # Extract basic metadata
        metadata = {
            'author': doc.core_properties.author or 'Unknown',
            'title': doc.core_properties.title or os.path.basename(file_path),
            'subject': doc.core_properties.subject or '',
            'created': str(doc.core_properties.created) if doc.core_properties.created else '',
            'modified': str(doc.core_properties.modified) if doc.core_properties.modified else '',
        }
        
        return ExtractedContent(
            text=full_text,
            title=metadata['title'],
            metadata=metadata,
            page_count=1,  # DOCX doesn't have explicit pages in the same way
            word_count=len(full_text.split()),
            file_type="docx",
            extraction_method="python-docx"
        )
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file is a supported DOCX."""
        return file_path.lower().endswith('.docx') and DOCX_AVAILABLE

class TextExtractor(FileExtractor):
    """Plain text file extraction."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = ['.txt', '.md', '.rst', '.log']
    
    def extract(self, file_path: str) -> ExtractedContent:
        """Extract text from plain text file."""
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    text = file.read()
                
                # Extract title from first line or filename
                lines = text.split('\\n')
                first_line = lines[0].strip() if lines else ""
                
                # If first line looks like a title (short and no periods), use it
                title = first_line if len(first_line) < 100 and '.' not in first_line else os.path.basename(file_path)
                
                metadata = {
                    'encoding': encoding,
                    'file_size': os.path.getsize(file_path),
                    'line_count': len(lines)
                }
                
                return ExtractedContent(
                    text=text,
                    title=title,
                    metadata=metadata,
                    page_count=1,
                    word_count=len(text.split()),
                    file_type="text",
                    extraction_method="plain_text"
                )
                
            except UnicodeDecodeError:
                continue
        
        raise RuntimeError(f"Could not decode text file with any of the tried encodings: {encodings}")
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file is a supported text file."""
        return any(file_path.lower().endswith(ext) for ext in self.supported_extensions)

class WebExtractor:
    """Web content extraction from URLs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_from_url(self, url: str, timeout: int = 30) -> ExtractedContent:
        """Extract text content from a web URL."""
        if not WEB_EXTRACTION_AVAILABLE:
            raise RuntimeError("Web extraction libraries (requests, BeautifulSoup) not available")
        
        try:
            # Set up headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else url
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Extract text from main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
            
            if main_content:
                text = main_content.get_text(separator='\\n', strip=True)
            else:
                text = soup.get_text(separator='\\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\\n') if line.strip()]
            cleaned_text = '\\n'.join(lines)
            
            # Extract metadata
            metadata = {
                'url': url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content),
                'description': '',
            }
            
            # Try to get meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                metadata['description'] = desc_tag.get('content', '')
            
            return ExtractedContent(
                text=cleaned_text,
                title=title,
                metadata=metadata,
                page_count=1,
                word_count=len(cleaned_text.split()),
                file_type="web",
                extraction_method="web_scraping"
            )
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch URL {url}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to extract content from {url}: {e}")
    
    def is_available(self) -> bool:
        """Check if web extraction is available."""
        return WEB_EXTRACTION_AVAILABLE

class FileManager:
    """Main file manager that coordinates different extractors."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize extractors
        self.extractors = [
            PDFExtractor(),
            DOCXExtractor(),
            TextExtractor()
        ]
        
        self.web_extractor = WebExtractor()
    
    def extract_from_file(self, file_path: str) -> ExtractedContent:
        """Extract content from a file using the appropriate extractor."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Find suitable extractor
        for extractor in self.extractors:
            if extractor.is_supported(file_path):
                try:
                    return extractor.extract(file_path)
                except Exception as e:
                    self.logger.error(f"Extraction failed with {extractor.__class__.__name__}: {e}")
                    raise
        
        raise RuntimeError(f"No suitable extractor found for file: {file_path}")
    
    def extract_from_url(self, url: str) -> ExtractedContent:
        """Extract content from a web URL."""
        return self.web_extractor.extract_from_url(url)
    
    def extract_from_text(self, text: str, title: str = "Text Input") -> ExtractedContent:
        """Create ExtractedContent from plain text."""
        return ExtractedContent(
            text=text,
            title=title,
            metadata={'source': 'direct_input'},
            page_count=1,
            word_count=len(text.split()),
            file_type="text",
            extraction_method="direct_input"
        )
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        formats = []
        
        if any(isinstance(e, PDFExtractor) and e.available_methods for e in self.extractors):
            formats.append("PDF (.pdf)")
        
        if any(isinstance(e, DOCXExtractor) and DOCX_AVAILABLE for e in self.extractors):
            formats.append("Word Documents (.docx)")
        
        formats.append("Text Files (.txt, .md)")
        
        if self.web_extractor.is_available():
            formats.append("Web URLs (http/https)")
        
        return formats
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a file before extraction."""
        result = {
            'valid': False,
            'supported': False,
            'file_size': 0,
            'error': None
        }
        
        try:
            if not os.path.exists(file_path):
                result['error'] = "File does not exist"
                return result
            
            # Check file size (limit to 50MB for now)
            file_size = os.path.getsize(file_path)
            result['file_size'] = file_size
            
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                result['error'] = "File too large (>50MB)"
                return result
            
            if file_size == 0:
                result['error'] = "File is empty"
                return result
            
            # Check if supported
            for extractor in self.extractors:
                if extractor.is_supported(file_path):
                    result['supported'] = True
                    break
            
            if not result['supported']:
                result['error'] = "File format not supported"
                return result
            
            result['valid'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def create_temp_file(self, content: str, extension: str = ".txt") -> str:
        """Create a temporary file with content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False, encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up a temporary file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            self.logger.warning(f"Failed to clean up temp file {file_path}: {e}")
'''

# Save utils/file_handlers.py
with open('utils/file_handlers.py', 'w', encoding='utf-8') as f:
    f.write(file_handlers_content)

print("✅ Created utils/file_handlers.py")
print("\nCore functionality modules completed!")
print("\nTo test the application:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run the application: python main.py")
print("\n📝 Files created:")
print("- main.py (application entry point)")
print("- config.py (configuration management)")
print("- requirements.txt (dependencies)")
print("- core/text_processor.py (LLM integration)")
print("- core/accessibility.py (accessibility features)")
print("- core/quiz_generator.py (quiz creation)")
print("- core/mind_mapper.py (mind map generation)")
print("- utils/file_handlers.py (PDF/DOCX processing)")