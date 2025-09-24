"""
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
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

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

class MindMapManager:
    """Manager class for mind map operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mind_maps: Dict[str, MindMap] = {}

    def create_mind_map(self, text: str, title: str = "") -> str:
        """Create a new mind map and return its ID."""
        try:
            # Simple mind map creation for demo
            map_id = f"mindmap_{len(self.mind_maps) + 1}"

            center_node = MindMapNode(
                id="center",
                label=title or "Main Topic",
                level=0,
                color="#4A90E2",
                size=20
            )

            nodes = {"center": center_node}
            edges = []

            # Create a basic mind map structure
            mind_map = MindMap(
                title=title or "Study Mind Map",
                center_node=center_node,
                nodes=nodes,
                edges=edges
            )

            self.mind_maps[map_id] = mind_map
            return map_id

        except Exception as e:
            self.logger.error(f"Error creating mind map: {e}")
            raise

    def get_mind_map(self, map_id: str) -> Optional[MindMap]:
        """Get a mind map by ID."""
        return self.mind_maps.get(map_id)

    def is_available(self) -> bool:
        """Check if mind mapping functionality is available."""
        return NETWORKX_AVAILABLE
