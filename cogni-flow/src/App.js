import React, { useEffect, useRef, useState } from "react";
import "./App.css";

// Firebase Configuration
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyDyy8AM0mc9oLi8ixywP4qo2dpJp2TYG6o",
  authDomain: "cogni-flow-d41db.firebaseapp.com",
  projectId: "cogni-flow-d41db",
  storageBucket: "cogni-flow-d41db.firebasestorage.app",
  messagingSenderId: "812584499671",
  appId: "1:812584499671:web:14516059d67a937ec47392",
  measurementId: "G-5W2RWBEHLE",
};

try {
  const app = initializeApp(firebaseConfig);
  getAnalytics(app);
} catch (e) {
  console.log("Firebase init error:", e);
}

// Gemini API configuration
const apiKey = "AIzaSyAaiJHfFeKRrF8Wy5rqUCwhN2l3-EEi-2Q";
const API_ENDPOINTS = [
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${apiKey}`,
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${apiKey}`,
];

export default function App() {
  const [activeTab, setActiveTab] = useState("input");
  const [theme, setTheme] = useState("scheme1");
  const [textInput, setTextInput] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [fileInput, setFileInput] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [genStatus, setGenStatus] = useState("");
  const [notesContent, setNotesContent] = useState("");
  const [mindmapContent, setMindmapContent] = useState("");
  const [quizContent, setQuizContent] = useState("");
  const [flashcardContent, setFlashcardContent] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    fontSize: 16,
    fontFamily: "Lexend, Arial, sans-serif",
    textAlign: "left",
    lineHeight: 1.5,
    letterSpacing: 0,
    bionic: false,
  });
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [speechSpeed, setSpeechSpeed] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);
  const speechSentencesRef = useRef([]);
  const currentUtteranceRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem("cogniSet");
    if (saved) setSettings(JSON.parse(saved));
  }, []);

  useEffect(() => {
    document.body.style.fontSize = `${settings.fontSize}px`;
    document.body.style.fontFamily = settings.fontFamily;
    document.body.style.lineHeight = settings.lineHeight;
    document.body.style.letterSpacing = `${settings.letterSpacing}px`;
    localStorage.setItem("cogniSet", JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  const showErrorDialog = (msg, err) => {
    console.error(msg, err || "");
    setErrorMessage(msg + (err?.message ? `: ${err.message}` : ""));
    setShowError(true);
  };

  const cleanHtmlResponse = (response) => {
    if (!response) {
      console.error("❌ Empty response received");
      return "";
    }
    
    console.log("🔧 Cleaning response, original length:", response.length);
    let cleaned = response.trim();
    
    // Remove markdown code fences
    cleaned = cleaned.replace(/^```html\s*/i, "");
    cleaned = cleaned.replace(/^```\s*/i, "");
    cleaned = cleaned.replace(/\s*```$/i, "");
    
    // Remove ONE set of quotes if wrapped
    if ((cleaned.startsWith('"') && cleaned.endsWith('"')) ||
        (cleaned.startsWith("'") && cleaned.endsWith("'"))) {
      cleaned = cleaned.slice(1, -1);
    }
    
    cleaned = cleaned.trim();
    
    // CRITICAL: Remove AI explanations that appear after the HTML
    // Find where actual HTML content ends (after closing </html>, </div>, or </body>)
    const htmlEndPatterns = [
      /<\/html>\s*/i,
      /<\/body>\s*/i,
      /<\/div>\s*$/i
    ];
    
    for (const pattern of htmlEndPatterns) {
      const match = cleaned.match(pattern);
      if (match) {
        const endIndex = match.index + match[0].length;
        // Check if there's significant text after the HTML
        const afterHtml = cleaned.substring(endIndex).trim();
        if (afterHtml.length > 50) {
          // Likely AI explanation - cut it off
          console.log("✂️ Removing AI explanation text after HTML");
          cleaned = cleaned.substring(0, endIndex);
          break;
        }
      }
    }
    
    cleaned = cleaned.trim();
    console.log("✨ Cleaned response length:", cleaned.length);
    console.log("📝 First 200 chars:", cleaned.substring(0, 200));
    
    // Validation
    if (cleaned.length < 20) {
      console.error("⚠️ Cleaned content too short! Returning original.");
      return response;
    }
    
    return cleaned;
  };

  const extractTextFromHtml = (htmlString) => {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlString;

    const unwantedTags = [
      "script", "style", "nav", "header", "footer", "aside", 
      "noscript", "iframe", "object", "embed"
    ];
    unwantedTags.forEach((tag) => {
      const elements = tempDiv.getElementsByTagName(tag);
      for (let i = elements.length - 1; i >= 0; i--) {
        elements[i].remove();
      }
    });

    let content = "";
    const mainSelectors = [
      "main", "article", "[role='main']", ".content",
      "#content", ".post", ".article", ".entry-content"
    ];

    for (const selector of mainSelectors) {
      const element = tempDiv.querySelector(selector);
      if (element && element.textContent.trim().length > content.length) {
        content = element.textContent.trim();
      }
    }

    if (!content || content.length < 100) {
      content = tempDiv.textContent || tempDiv.innerText || "";
    }

    return content.replace(/\s+/g, " ").trim();
  };

  const fetchUrlContent = async (url) => {
    try {
      const directResponse = await fetch(url, {
        mode: "cors",
        headers: {
          Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "User-Agent": "Mozilla/5.0 (compatible; Cogni-Flow/1.0)",
        },
      });
      if (directResponse.ok) {
        const textContent = await directResponse.text();
        const extractedContent = extractTextFromHtml(textContent);
        if (extractedContent && extractedContent.length > 100) return extractedContent;
      }
    } catch (error) {
      console.log("Direct fetch failed:", error);
    }
    
    const proxies = [
      "https://api.allorigins.win/get?url=", 
      "https://thingproxy.freeboard.io/fetch/"
    ];
    
    for (const proxy of proxies) {
      try {
        const proxyUrl = proxy.includes("allorigins") 
          ? proxy + encodeURIComponent(url) 
          : proxy + url;
        const response = await fetch(proxyUrl, {
          method: "GET",
          headers: {
            Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
          },
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        let responseData;
        if (proxy.includes("allorigins")) {
          const jsonResponse = await response.json();
          responseData = jsonResponse.contents;
        } else {
          responseData = await response.text();
        }
        
        if (responseData) {
          const extractedContent = extractTextFromHtml(responseData);
          if (extractedContent && extractedContent.length > 50) return extractedContent;
        }
      } catch (error) {
        console.log(`Proxy ${proxy} failed:`, error);
      }
    }
    throw new Error("Failed to fetch content from URL");
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileInput(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      setTextInput(content);
    };
    reader.onerror = () => {
      showErrorDialog("Failed to read file");
    };
    reader.readAsText(file);
  };

  const callGeminiAPI = async (endpoint, prompt) => {
    console.log("🔄 Calling Gemini API...");
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { 
          temperature: 0.25, 
          maxOutputTokens: 8192,
          topP: 0.95,
          topK: 40
        },
      }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ API Error:", response.status, errorText);
      throw new Error(`API failed: ${response.status}`);
    }
    
    const data = await response.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
    
    if (!text) {
      console.error("❌ No text in API response:", data);
      throw new Error("No content generated");
    }
    
    console.log("✅ API response received, length:", text.length);
    return text;
  };

  const handleGenerate = async () => {
    if (!textInput && !urlInput) {
      showErrorDialog("Please provide text, a file, or a URL");
      return;
    }
    
    setIsGenerating(true);
    setGenStatus("Processing input...");
    let sourceText = textInput;
    
    try {
      if (urlInput && !sourceText) {
        setGenStatus("Fetching content from URL...");
        try {
          sourceText = await fetchUrlContent(urlInput);
          if (!sourceText || sourceText.length < 100) {
            showErrorDialog("Could not extract enough content from URL. Try pasting text directly.");
            setIsGenerating(false);
            setGenStatus("");
            return;
          }
          setTextInput(sourceText);
        } catch (urlError) {
          showErrorDialog("Failed to fetch URL. Please paste the text directly instead.");
          setIsGenerating(false);
          setGenStatus("");
          return;
        }
      }
      
      if (!sourceText || sourceText.trim().length < 50) {
        showErrorDialog("Please provide more content (at least 50 characters)");
        setIsGenerating(false);
        setGenStatus("");
        return;
      }
      
      const truncatedText = sourceText.substring(0, 30000);
      console.log("📄 Processing text, length:", truncatedText.length);
      
      const prompts = {
        notes: `Create comprehensive study notes in HTML format. IMPORTANT: Return ONLY the HTML code, no explanations or markdown. Use proper HTML tags like <div>, <h2>, <h3>, <p>, <ul>, <li>, <strong>. Make it well-structured and easy to read. Add inline styles for colors if needed. Content:\n\n${truncatedText}`,
        
        mindmap: `Create an HTML mind map with nested <div> elements. IMPORTANT: Return ONLY the HTML code, no explanations. Use inline CSS for styling (colors, borders, padding, margins). Structure it as a visual hierarchy with a main topic and branches. Content:\n\n${truncatedText}`,
        
        quiz: `Generate 10 multiple-choice questions in HTML format. IMPORTANT: Return ONLY the HTML code, no explanations or instructions. Use <div> containers, proper structure, and include a way to check answers. Make questions clear and relevant. Content:\n\n${truncatedText}`,
        
        flashcard: `Create 10 flashcards in HTML format. IMPORTANT: Return ONLY the HTML code with no explanations, comments, or instructions after the HTML. Use <div> elements with classes 'flashcard', 'card-front', 'card-back'. Include inline CSS for styling. Make questions concise and answers clear. Content:\n\n${truncatedText}`
      };

      for (const [type, prompt] of Object.entries(prompts)) {
        setGenStatus(`Generating ${type}... (may take 10-30 seconds)`);
        let success = false;
        let lastError = null;
        
        for (let i = 0; i < API_ENDPOINTS.length; i++) {
          const endpoint = API_ENDPOINTS[i];
          try {
            console.log(`\n🔄 Trying endpoint ${i + 1}/${API_ENDPOINTS.length} for ${type}`);
            const response = await callGeminiAPI(endpoint, prompt);
            
            if (!response || response.length < 100) {
              console.warn(`⚠️ Response too short for ${type}:`, response?.length);
              continue;
            }
            
            const cleanedResponse = cleanHtmlResponse(response);
            
            console.log(`\n========================================`);
            console.log(`✅ GENERATED ${type.toUpperCase()}`);
            console.log(`   Cleaned Length: ${cleanedResponse.length}`);
            console.log(`   Preview: ${cleanedResponse.substring(0, 300)}...`);
            console.log(`========================================\n`);
            
            if (!cleanedResponse || cleanedResponse.length < 50) {
              console.error(`❌ Cleaned ${type} too short!`);
              throw new Error(`Generated ${type} is too short or empty`);
            }
            
            // Set content with explicit logging
            switch (type) {
              case "notes": 
                console.log("💾 Setting NOTES content...");
                setNotesContent(cleanedResponse);
                console.log("✅ Notes content SET successfully");
                break;
              case "mindmap": 
                console.log("💾 Setting MINDMAP content...");
                setMindmapContent(cleanedResponse);
                console.log("✅ Mindmap content SET successfully");
                break;
              case "quiz": 
                console.log("💾 Setting QUIZ content...");
                setQuizContent(cleanedResponse);
                console.log("✅ Quiz content SET successfully");
                break;
              case "flashcard": 
                console.log("💾 Setting FLASHCARD content...");
                setFlashcardContent(cleanedResponse);
                console.log("✅ Flashcard content SET successfully");
                break;
            }
            
            success = true;
            break;
          } catch (error) {
            console.error(`❌ Endpoint ${i + 1} failed for ${type}:`, error);
            lastError = error;
            if (i < API_ENDPOINTS.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 1000));
            }
          }
        }
        
        if (!success) {
          throw new Error(`Failed to generate ${type}. Error: ${lastError?.message || 'Unknown error'}`);
        }
        
        // Small delay between content types
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      console.log("🎉 ALL CONTENT GENERATED SUCCESSFULLY!");
      setGenStatus("✅ All materials generated successfully!");
      setActiveTab("notes");
      setTimeout(() => setGenStatus(""), 3000);
      
    } catch (error) {
      console.error("💥 Generation error:", error);
      showErrorDialog(`Failed to generate materials: ${error.message}. Please try with shorter text or check your API quota.`, error);
      setGenStatus("");
    } finally {
      setIsGenerating(false);
    }
  };

  const resetSpeechControls = () => {
    window.speechSynthesis.cancel();
    setIsPlaying(false);
    setIsPaused(false);
    setCurrentSentenceIndex(0);
    speechSentencesRef.current = [];
    currentUtteranceRef.current = null;
  };

  const extractTextFromContent = (htmlContent) => {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlContent;
    const text = tempDiv.textContent || tempDiv.innerText || "";
    return text.trim();
  };

  const splitIntoSentences = (text) => {
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
    return sentences.map((s) => s.trim()).filter((s) => s.length > 0);
  };

  const initializeSpeech = () => {
    if (!notesContent) {
      showErrorDialog("No notes to read. Please generate content first.");
      return false;
    }
    const textToSpeak = extractTextFromContent(notesContent);
    if (!textToSpeak) {
      showErrorDialog("No readable text found in notes.");
      return false;
    }
    const sentences = splitIntoSentences(textToSpeak);
    if (sentences.length === 0) {
      showErrorDialog("Could not parse text into sentences.");
      return false;
    }
    speechSentencesRef.current = sentences;
    return true;
  };

  const speakCurrentSentence = () => {
    const sentences = speechSentencesRef.current;
    const index = currentSentenceIndex;
    if (index >= sentences.length) {
      resetSpeechControls();
      return;
    }
    const utterance = new SpeechSynthesisUtterance(sentences[index]);
    utterance.rate = speechSpeed;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.onend = () => {
      setCurrentSentenceIndex((prevIndex) => {
        const newIndex = prevIndex + 1;
        if (newIndex < sentences.length) {
          setTimeout(speakCurrentSentence, 100);
        } else {
          resetSpeechControls();
        }
        return newIndex;
      });
    };
    utterance.onerror = (event) => {
      console.error("Speech error:", event);
      resetSpeechControls();
    };
    currentUtteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const handlePlay = () => {
    if (isPlaying && !isPaused) {
      resetSpeechControls();
      return;
    }
    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }
    if (!initializeSpeech()) return;
    setIsPlaying(true);
    speakCurrentSentence();
  };

  const handlePause = () => {
    if (window.speechSynthesis.speaking && !isPaused) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      setIsPlaying(false);
    }
  };

  const handleRewind = () => {
    if (isPlaying || isPaused) {
      window.speechSynthesis.cancel();
      setCurrentSentenceIndex((prevIndex) => Math.max(0, prevIndex - 2));
      setTimeout(speakCurrentSentence, 120);
    }
  };

  const handleSkip = () => {
    if (isPlaying || isPaused) {
      window.speechSynthesis.cancel();
      setCurrentSentenceIndex((prevIndex) => prevIndex + 1);
      setTimeout(speakCurrentSentence, 120);
    }
  };

  const onChangeSpeed = (value) => {
    const speedValue = parseFloat(value);
    setSpeechSpeed(speedValue);
    if (isPlaying) {
      window.speechSynthesis.cancel();
      setTimeout(speakCurrentSentence, 120);
    }
  };

  const handleTabChange = (tab) => {
    if (isGenerating) {
      alert("⏳ Please wait! Content is still generating. Don't switch tabs yet!");
      return;
    }
    window.speechSynthesis.cancel();
    resetSpeechControls();
    setActiveTab(tab);
  };

  return (
    <div className="App" data-theme={theme}>
      <div className="main-image-header">
        <img 
          src="/Main-Image.png" 
          alt="Cogni-Flow Main Visual" 
          className="main-header-image" 
        />
      </div>

      <header className="header">
        <div className="logo-space">
          <img 
            src="/Header-logo.png" 
            alt="Logo" 
            style={{ width: '64px', height: '64px' }} 
          />
        </div>
        <div className="right">
          <button onClick={() => setShowSettings(true)} title="Settings">⚙️</button>
          <button onClick={() => setTheme(theme === "scheme1" ? "scheme2" : "scheme1")} title="Switch Color Scheme">🎨</button>
        </div>
      </header>

      <main>
        <nav>
          <button className={activeTab === "input" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("input")}>📝 Input</button>
          <button className={activeTab === "notes" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("notes")}>📚 Smart Notes</button>
          <button className={activeTab === "mindmap" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("mindmap")}>🧠 Mind Map</button>
          <button className={activeTab === "quiz" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("quiz")}>❓ Quiz</button>
          <button className={activeTab === "flashcard" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("flashcard")}>🎴 Flashcards</button>
        </nav>

        {activeTab === "input" && (
          <section className="tab-panel active">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your text here and watch the magic happen! Upload a file or enter a link to get started..."
            />
            <input type="file" onChange={handleFileChange} accept=".txt,.md" />
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="Paste a public article link here"
            />
            <div className="center-btn">
              <button onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? "⏳ Generating..." : "🚀 Generate Learning Materials"}
              </button>
            </div>
            {genStatus && <div id="genStatus">{genStatus}</div>}
          </section>
        )}

        {activeTab === "notes" && (
          <section className="tab-panel active">
            {isGenerating ? (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <div className="loading-spinner"></div>
                <p style={{ marginTop: '24px', fontSize: '20px', fontWeight: 'bold' }}>
                  {genStatus || '⏳ Generating your notes...'}
                </p>
                <p style={{ fontSize: '16px', opacity: 0.8, marginTop: '12px' }}>
                  Please wait 30-90 seconds. Stay on this page!
                </p>
              </div>
            ) : notesContent ? (
              <>
                <div className="speech-controls">
                  <button onClick={handlePlay} className="speech-btn primary">
                    {isPlaying && !isPaused ? "⏹ Stop" : isPaused ? "▶️ Resume" : "🔊 Read Aloud"}
                  </button>
                  <button onClick={handlePause} disabled={!isPlaying || isPaused} className="speech-btn">⏸ Pause</button>
                  <button onClick={handleRewind} disabled={!isPlaying && !isPaused} className="speech-btn">⏪ Rewind</button>
                  <button onClick={handleSkip} disabled={!isPlaying && !isPaused} className="speech-btn">⏩ Skip</button>
                  <div className="speed-control">
                    <label htmlFor="speedSlider">Speed:</label>
                    <input
                      id="speedSlider"
                      type="range"
                      min="0.5"
                      max="2"
                      step="0.1"
                      value={speechSpeed}
                      onChange={(e) => onChangeSpeed(e.target.value)}
                    />
                    <span>{speechSpeed.toFixed(1)}x</span>
                  </div>
                </div>
                <div 
                  className="content-display"
                  style={{ 
                    textAlign: settings.textAlign,
                    padding: '20px',
                    minHeight: '300px',
                    color: '#000000'
                  }} 
                  dangerouslySetInnerHTML={{ __html: notesContent }} 
                />
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <p style={{ fontSize: '20px', opacity: 0.7 }}>
                  📝 No notes generated yet.<br/>
                  Go to the <strong>Input</strong> tab and click "Generate Learning Materials"!
                </p>
              </div>
            )}
          </section>
        )}

        {activeTab === "mindmap" && (
          <section className="tab-panel active">
            {isGenerating ? (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <div className="loading-spinner"></div>
                <p style={{ marginTop: '24px', fontSize: '20px', fontWeight: 'bold' }}>
                  {genStatus || '⏳ Generating your mind map...'}
                </p>
              </div>
            ) : mindmapContent ? (
              <div 
                className="content-display"
                style={{ padding: '20px', minHeight: '300px', color: '#000000' }}
                dangerouslySetInnerHTML={{ __html: mindmapContent }} 
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <p style={{ fontSize: '20px', opacity: 0.7 }}>
                  🧠 No mind map yet. Generate materials first!
                </p>
              </div>
            )}
          </section>
        )}

        {activeTab === "quiz" && (
          <section className="tab-panel active">
            {isGenerating ? (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <div className="loading-spinner"></div>
                <p style={{ marginTop: '24px', fontSize: '20px', fontWeight: 'bold' }}>
                  {genStatus || '⏳ Generating your quiz...'}
                </p>
              </div>
            ) : quizContent ? (
              <div 
                className="content-display"
                style={{ padding: '20px', minHeight: '300px', color: '#000000' }}
                dangerouslySetInnerHTML={{ __html: quizContent }} 
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <p style={{ fontSize: '20px', opacity: 0.7 }}>
                  ❓ No quiz yet. Generate materials first!
                </p>
              </div>
            )}
          </section>
        )}

        {activeTab === "flashcard" && (
          <section className="tab-panel active">
            {isGenerating ? (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <div className="loading-spinner"></div>
                <p style={{ marginTop: '24px', fontSize: '20px', fontWeight: 'bold' }}>
                  {genStatus || '⏳ Generating your flashcards...'}
                </p>
              </div>
            ) : flashcardContent ? (
              <div
                className="flashcard-host content-display"
                style={{ padding: '20px', minHeight: '300px' }}
                onClick={(e) => {
                  const card = e.target.closest(".flashcard");
                  if (card) card.classList.toggle("flipped");
                }}
                dangerouslySetInnerHTML={{ __html: flashcardContent }}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <p style={{ fontSize: '20px', opacity: 0.7 }}>
                  🎴 No flashcards yet. Generate materials first!
                </p>
              </div>
            )}
          </section>
        )}
      </main>

      {showSettings && (
        <div className="modal-bg" onClick={() => setShowSettings(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>⚙️ Settings</h2>
            <div className="form-row">
              <label>Font Size: {settings.fontSize}px</label>
              <input 
                type="range" 
                min="12" 
                max="24" 
                value={settings.fontSize} 
                onChange={(e) => setSettings({ ...settings, fontSize: parseInt(e.target.value) })} 
              />
            </div>
            <div className="form-row">
              <label>Font Family</label>
              <select 
                value={settings.fontFamily} 
                onChange={(e) => setSettings({ ...settings, fontFamily: e.target.value })}
              >
                <option>Lexend, Arial, sans-serif</option>
                <option>Inter, Arial, sans-serif</option>
                <option>OpenDyslexic, Arial, sans-serif</option>
              </select>
            </div>
            <div className="form-row">
              <label>Text Align</label>
              <select 
                value={settings.textAlign} 
                onChange={(e) => setSettings({ ...settings, textAlign: e.target.value })}
              >
                <option value="left">Left</option>
                <option value="justify">Justify</option>
                <option value="center">Center</option>
              </select>
            </div>
            <div className="form-row">
              <label>Line Height: {settings.lineHeight}</label>
              <input 
                type="range" 
                min="1.2" 
                max="2.5" 
                step="0.1" 
                value={settings.lineHeight} 
                onChange={(e) => setSettings({ ...settings, lineHeight: parseFloat(e.target.value) })} 
              />
            </div>
            <div className="form-row">
              <label>Letter Spacing: {settings.letterSpacing}px</label>
              <input 
                type="range" 
                min="0" 
                max="3" 
                step="0.1" 
                value={settings.letterSpacing} 
                onChange={(e) => setSettings({ ...settings, letterSpacing: parseFloat(e.target.value) })} 
              />
            </div>
            <div className="form-row">
              <label>
                <input 
                  type="checkbox" 
                  checked={settings.bionic} 
                  onChange={(e) => setSettings({ ...settings, bionic: e.target.checked})} 
                />
                Bionic Reading
              </label>
            </div>
            <div className="actions">
              <button onClick={() => setShowSettings(false)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {showError && (
        <div className="modal-bg" onClick={() => setShowError(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ color: "#ff000d" }}>❌ Error</h2>
            <p className="mb-4" style={{ color: '#000000' }}>{errorMessage}</p>
            <button onClick={() => setShowError(false)}>Got It!</button>
          </div>
        </div>
      )}
    </div>
  );
}