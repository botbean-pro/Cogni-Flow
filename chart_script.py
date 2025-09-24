import plotly.graph_objects as go
import plotly.express as px
import json

# Parse the component data
data = {"components": [{"name": "main.py", "layer": "main", "description": "Application entry point and orchestration", "color": "#4A90E2"}, {"name": "Text Processor", "layer": "core", "description": "LLM integration for content analysis", "color": "#50C878"}, {"name": "Accessibility Manager", "layer": "core", "description": "Dyslexia-friendly features and TTS", "color": "#50C878"}, {"name": "Quiz Generator", "layer": "core", "description": "Automatic question creation", "color": "#50C878"}, {"name": "Mind Mapper", "layer": "core", "description": "Visual concept mapping", "color": "#50C878"}, {"name": "File Handlers", "layer": "utils", "description": "PDF/DOCX text extraction", "color": "#FFB347"}, {"name": "TTS Engine", "layer": "utils", "description": "Text-to-speech functionality", "color": "#FFB347"}, {"name": "Storage Manager", "layer": "utils", "description": "Data persistence and user preferences", "color": "#FFB347"}, {"name": "Main Window", "layer": "gui", "description": "Primary user interface", "color": "#DDA0DD"}, {"name": "Components", "layer": "gui", "description": "Reusable UI elements", "color": "#DDA0DD"}, {"name": "Themes", "layer": "gui", "description": "Visual styling and accessibility themes", "color": "#DDA0DD"}, {"name": "config.py", "layer": "config", "description": "Application configuration and settings", "color": "#F0E68C"}, {"name": "OpenAI API", "layer": "external", "description": "LLM processing service", "color": "#D3D3D3"}, {"name": "NetworkX", "layer": "external", "description": "Graph visualization library", "color": "#D3D3D3"}, {"name": "pyttsx3", "layer": "external", "description": "Cross-platform text-to-speech", "color": "#D3D3D3"}, {"name": "PyPDF2/pdfplumber", "layer": "external", "description": "PDF processing libraries", "color": "#D3D3D3"}, {"name": "CustomTkinter", "layer": "external", "description": "Modern GUI framework", "color": "#D3D3D3"}]}

components = data['components']

# Define layer positions
layer_positions = {
    'main': 5,
    'core': 4, 
    'utils': 3,
    'gui': 2,
    'config': 1,
    'external': 0
}

# Create coordinates for components
x_coords = []
y_coords = []
colors = []
names = []
descriptions = []
sizes = []

# Arrange components by layer
layer_counts = {}
for comp in components:
    layer = comp['layer']
    layer_counts[layer] = layer_counts.get(layer, 0) + 1

layer_indices = {layer: 0 for layer in layer_counts.keys()}

for comp in components:
    layer = comp['layer']
    y = layer_positions[layer]
    
    # Distribute components horizontally within each layer
    count = layer_counts[layer]
    index = layer_indices[layer]
    if count == 1:
        x = 0
    else:
        x = (index - (count - 1) / 2) * (8 / max(1, count - 1))
    
    x_coords.append(x)
    y_coords.append(y)
    colors.append(comp['color'])
    names.append(comp['name'])
    descriptions.append(comp['description'])
    sizes.append(60 if layer == 'main' else 45)
    
    layer_indices[layer] += 1

# Create the figure
fig = go.Figure()

# Add components as scatter points
fig.add_trace(go.Scatter(
    x=x_coords,
    y=y_coords,
    mode='markers+text',
    marker=dict(
        size=sizes,
        color=colors,
        line=dict(width=2, color='#333333')
    ),
    text=names,
    textposition='middle center',
    textfont=dict(size=10, color='white'),
    hovertemplate='<b>%{text}</b><br>%{customdata}<extra></extra>',
    customdata=descriptions,
    showlegend=False
))

# Add connection lines
connections = [
    # Main to core modules
    (0, 1), (0, 2), (0, 3), (0, 4),  # main to core modules
    (0, 8), (0, 11),  # main to GUI and config
    
    # Core to external/utils
    (1, 12), (1, 5),  # Text Processor to OpenAI and File Handlers
    (2, 6), (2, 14), (2, 5),  # Accessibility to TTS, pyttsx3, File Handlers
    (3, 7), (3, 5),  # Quiz Generator to Storage, File Handlers
    (4, 13),  # Mind Mapper to NetworkX
    
    # Utils to external
    (5, 15), (6, 14),  # File Handlers to PyPDF2, TTS to pyttsx3
    
    # GUI connections
    (8, 9), (8, 10), (8, 16),  # Main Window to Components, Themes, CustomTkinter
    (9, 16), (10, 16),  # Components and Themes to CustomTkinter
    
    # Config to Storage
    (11, 7)
]

for start_idx, end_idx in connections:
    fig.add_trace(go.Scatter(
        x=[x_coords[start_idx], x_coords[end_idx]],
        y=[y_coords[start_idx], y_coords[end_idx]],
        mode='lines',
        line=dict(width=1.5, color='#666666'),
        hoverinfo='skip',
        showlegend=False
    ))

# Add layer labels
layer_labels = {
    'main': 'Main Application',
    'core': 'Core Modules', 
    'utils': 'Utilities',
    'gui': 'GUI Layer',
    'config': 'Configuration',
    'external': 'External Dependencies'
}

for layer, y_pos in layer_positions.items():
    fig.add_annotation(
        x=-5,
        y=y_pos,
        text=f"<b>{layer_labels[layer]}</b>",
        showarrow=False,
        font=dict(size=12, color='#333333'),
        xanchor='right'
    )

# Update layout
fig.update_layout(
    title='Cogni-Flow System Architecture',
    xaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[-6, 6]
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[-0.5, 5.5]
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=600
)

# Save the chart
fig.write_image('cogni_flow_architecture.png')
fig.write_image('cogni_flow_architecture.svg', format='svg')

print("System architecture diagram saved successfully!")