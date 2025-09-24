# Create a Mermaid flowchart for Cogni-Flow feature overview
diagram_code = """
flowchart TD
    %% Input Methods (Top)
    A[Text Input<br/>Direct text paste] --> E[LLM Analysis<br/>AI-powered content analysis]
    B[PDF Upload<br/>PDF document processing] --> E
    C[DOCX Upload<br/>Word document processing] --> E
    D[URL Input<br/>Web article extraction] --> E
    
    %% Processing Engine (Center)
    E --> F[Content Structuring<br/>Information organization]
    F --> G[Accessibility Enhancement<br/>Dyslexia-friendly formatting]
    
    %% Output Formats (Branches from center)
    G --> H[Smart Notes<br/>Structured study notes]
    G --> I[Interactive Mind Maps<br/>Visual concept mapping]
    G --> J[Generated Quizzes<br/>Custom practice questions]
    G --> K[Audio Output<br/>Text-to-speech playback]
    
    %% Accessibility Features (Side panel - integrated throughout)
    L[OpenDyslexic Font<br/>Dyslexia-friendly typography] -.-> G
    M[Bionic Reading<br/>Enhanced readability mode] -.-> G
    N[Text-to-Speech<br/>Audio content delivery] -.-> K
    O[High Contrast<br/>Visual accessibility themes] -.-> H
    O -.-> I
    P[Custom Spacing<br/>Adjustable text layout] -.-> H
    Q[Voice Control<br/>TTS speed and voice options] -.-> K
    
    %% User Preferences (Bottom)
    R[Font Settings<br/>Typography customization] --> S[User Preferences]
    T[Theme Selection<br/>Visual theme options] --> S
    U[TTS Configuration<br/>Audio settings] --> S
    V[Layout Options<br/>Interface customization] --> S
    
    %% Connect preferences to main flow
    S -.-> G
    
    %% Styling
    classDef inputStyle fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef processStyle fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef outputStyle fill:#DDA0DD,stroke:#333,stroke-width:2px,color:#000
    classDef accessStyle fill:#FFB347,stroke:#333,stroke-width:2px,color:#000
    classDef prefStyle fill:#F0E68C,stroke:#333,stroke-width:2px,color:#000
    
    class A,B,C,D inputStyle
    class E,F,G processStyle
    class H,I,J,K outputStyle
    class L,M,N,O,P,Q accessStyle
    class R,T,U,V,S prefStyle
"""

# Create the mermaid diagram and save as both PNG and SVG
create_mermaid_diagram(diagram_code, 'cogni_flow_diagram.png', 'cogni_flow_diagram.svg', width=1400, height=1000)