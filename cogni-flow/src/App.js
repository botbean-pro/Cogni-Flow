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
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=${apiKey}`,
];

export default function App() {
  // UI state
  const [activeTab, setActiveTab] = useState("input");
  const [theme, setTheme] = useState("scheme1");

  // NEW: Home page state
  const [showHomePage, setShowHomePage] = useState(true);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [animationComplete, setAnimationComplete] = useState(false);

  // Inputs
  const [textInput, setTextInput] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [fileInput, setFileInput] = useState(null);

  // Generation
  const [isGenerating, setIsGenerating] = useState(false);
  const [genStatus, setGenStatus] = useState("");

  // Outputs
  const [notesContent, setNotesContent] = useState("");
  const [mindmapContent, setMindmapContent] = useState("");
  const [quizContent, setQuizContent] = useState("");
  const [flashcardContent, setFlashcardContent] = useState("");

  // Settings modal
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    fontSize: 16,
    fontFamily: "Lexend, Arial, sans-serif",
    textAlign: "left",
    lineHeight: 1.5,
    letterSpacing: 0,
    bionic: false,
  });

  // Error modal
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Speech state/refs
  const [speechSpeed, setSpeechSpeed] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);
  const speechSentencesRef = useRef([]);
  const currentUtteranceRef = useRef(null);

  // NEW: Home page scroll animation
  useEffect(() => {
    if (!showHomePage) return;
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = Math.min(scrollTop / (documentHeight * 0.65), 1);
      setScrollProgress(progress);
      if (progress > 0.80 && !animationComplete) setAnimationComplete(true);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [showHomePage, animationComplete]);

  // Load settings from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("cogniSet");
    if (saved) setSettings(JSON.parse(saved));
  }, []);

  // Apply settings
  useEffect(() => {
    document.body.style.fontSize = `${settings.fontSize}px`;
    document.body.style.fontFamily = settings.fontFamily;
    document.body.style.lineHeight = settings.lineHeight;
    document.body.style.letterSpacing = `${settings.letterSpacing}px`;
    localStorage.setItem("cogniSet", JSON.stringify(settings));
  }, [settings]);

  // Theme application
  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  // Helper functions
  const showErrorDialog = (msg, err) => {
    console.error(msg, err || "");
    setErrorMessage(msg + (err?.message ? `: ${err.message}` : ""));
    setShowError(true);
  };

  const cleanHtmlResponse = (response) => {
  if (!response) return "";
  let cleanedResponse = response;


  // Remove HTML code block markers
  cleanedResponse = cleanedResponse.replace(/```html/g, "");
  cleanedResponse = cleanedResponse.replace(/```/g, "");


  // Remove quotes at start and end
  while (
    cleanedResponse.startsWith('"') ||
    cleanedResponse.startsWith("'") ||
    cleanedResponse.startsWith("`")
  ) {
    cleanedResponse = cleanedResponse.substring(1);
  }
  while (
    cleanedResponse.endsWith('"') ||
    cleanedResponse.endsWith("'") ||
    cleanedResponse.endsWith("`")
  ) {
    cleanedResponse = cleanedResponse.substring(0, cleanedResponse.length - 1);
  }

  // Extract text from HTML
  const extractTextFromHtml = (htmlString) => {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlString;

    const unwantedTags = ["script", "style", "nav", "header", "footer", "aside", "noscript", "iframe", "object", "embed"];
    unwantedTags.forEach((tag) => {
      const elements = tempDiv.getElementsByTagName(tag);
      for (let i = elements.length - 1; i >= 0; i--) {
        elements[i].remove();
      }
    });

    let content = "";
    const mainSelectors = ["main", "article", "[role='main']", ".content", "#content", ".post", ".article", ".entry-content"];
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

  // Fetch URL content with CORS proxy fallbacks
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

    const proxies = ["https://api.allorigins.win/get?url=", "https://thingproxy.freeboard.io/fetch/"];
    for (const proxy of proxies) {
      try {
        const proxyUrl = proxy.includes("allorigins") ? proxy + encodeURIComponent(url) : proxy + url;
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
    throw new Error("Unable to fetch URL content due to CORS. Please copy-paste the article text into the textarea.");
  };

  // Generate content using Gemini API
  const generateContentFromGemini = async (prompt) => {
  const payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.7,
      topK: 40,
      topP: 0.95,
      maxOutputTokens: 8192,
    },
  };

  for (let i = 0; i < API_ENDPOINTS.length; i++) {
    try {
      const response = await fetch(API_ENDPOINTS[i], {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const jsonResponse = await response.json();

      if (!response.ok) {
        if (i < API_ENDPOINTS.length - 1) continue;
        throw new Error(jsonResponse.error?.message || "Unknown API error");
      }

      // ✅ Fix: Properly navigate the response structure
      const generatedText =
        jsonResponse?.candidates?.[0]?.content?.parts?.[0]?.text;

      if (generatedText) return cleanHtmlResponse(generatedText);

      if (i < API_ENDPOINTS.length - 1) continue;
      throw new Error("Invalid API response.");
    } catch (error) {
      if (i === API_ENDPOINTS.length - 1) throw error;
    }
  }

  return "";
};


  // Content generators
  const generateSmartNotes = async (inputText) => {
    const prompt = `Create study notes from this content. Return ONLY clean HTML without markdown blocks, backticks, emojis, or code fences:
${inputText}

Structure:
<h2>Title</h2>
<h3>Section Heading</h3>
<ul><li>Key point</li></ul>
<strong>Important terms</strong>
No emojis or special characters.
Return clean HTML only.`;
    const htmlContent = await generateContentFromGemini(prompt);
    setNotesContent(htmlContent);
  };

  const generateMindMap = async (inputText) => {
    const prompt = `Create a mind map from this content. Return ONLY clean HTML, no markdown fences, no emojis. Short sub-points (<= 8 words).
Use exact structure:
<h2>MAIN TOPIC</h2>
<ul>
  <li>BRANCH 1 - Short Title
    <ul>
      <li>Short sub-point 1</li>
      <li>Short sub-point 2</li>
      <li>Short sub-point 3</li>
    </ul>
  </li>
</ul>

Content: ${inputText}`;
    const htmlContent = await generateContentFromGemini(prompt);
    setMindmapContent(htmlContent);
  };

  const generateQuiz = async (inputText) => {
    const prompt = `Create a quiz from this content. Return ONLY clean HTML, no markdown fences, no emojis.
Structure:
<h2>Quiz Time!</h2>
<div class="q">Question text</div>
<ul>
  <li>A) Option A</li>
  <li>B) Option B</li>
  <li>C) Option C</li>
  <li>D) Option D</li>
</ul>
<div class="answer" style="display:none">Correct: A) Option A</div>

Content: ${inputText}`;
    const htmlContent = await generateContentFromGemini(prompt);
    setQuizContent(htmlContent);
  };

  const generateFlashcards = async (inputText) => {
  const prompt = `Create 8 flashcards from this content. Return ONLY clean HTML, no markdown fences, no emojis.
Use this exact structure per card:
<div class="flashcard">
  <div class="card-inner">
    <div class="card-face card-front"><p>QUESTION</p></div>
    <div class="card-face card-back"><p>ANSWER</p></div>
  </div>
</div>
Wrap all cards inside:
<div class="flashcard-deck"> ...cards... </div>

Content:
${inputText}`;

  try {
    const htmlContent = await generateContentFromGemini(prompt);
    if (!htmlContent || !htmlContent.includes("flashcard-deck")) {
      throw new Error("Invalid flashcard HTML returned.");
    }
    setFlashcardContent(htmlContent);
  } catch (error) {
    showErrorDialog("Failed to generate flashcards", error);
  }
};


  // Speech synthesis functions
  const initializeSpeech = () => {
    const tempElement = document.createElement("div");
    tempElement.innerHTML = notesContent || "";
    const textContent = tempElement.textContent || tempElement.innerText || "";
    const cleanedText = textContent.replace(/\s+/g, " ").trim();
    
    if (!cleanedText) {
      showErrorDialog("No content to read. Generate some notes first!");
      return false;
    }
    
    speechSentencesRef.current = cleanedText.split(/[.!?]+/).map((sentence) => sentence.trim()).filter(Boolean);
    setCurrentSentenceIndex(0);
    return true;
  };

  const pickVoice = () => {
    const voices = window.speechSynthesis.getVoices();
    const preferredVoices = voices.filter(
      (voice) =>
        voice.lang?.startsWith("en") &&
        (voice.name.includes("Natural") ||
          voice.name.includes("Premium") ||
          voice.name.includes("Enhanced") ||
          voice.name.includes("Google") ||
          voice.name.includes("Microsoft"))
    );
    if (preferredVoices.length) return preferredVoices;
    
    const englishVoices = voices.filter((voice) => voice.lang?.startsWith("en"));
    return englishVoices || null;
  };

  const speakCurrentSentence = () => {
    const sentenceIndex = currentSentenceIndex;
    const sentences = speechSentencesRef.current;
    
    if (!sentences || sentenceIndex >= sentences.length) {
      resetSpeechControls();
      return;
    }
    
    const sentence = sentences[sentenceIndex];
    if (!sentence) {
      setCurrentSentenceIndex((prevIndex) => prevIndex + 1);
      setTimeout(speakCurrentSentence, 50);
      return;
    }
    
    const utterance = new SpeechSynthesisUtterance(sentence);
    utterance.rate = speechSpeed;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    const selectedVoice = pickVoice();
    if (selectedVoice) utterance.voice = selectedVoice;

    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
    };
    
    utterance.onend = () => {
      setCurrentSentenceIndex((prevIndex) => prevIndex + 1);
      const nextIndex = sentenceIndex + 1;
      if (nextIndex < sentences.length && !isPaused) {
        setTimeout(speakCurrentSentence, 150);
      } else {
        resetSpeechControls();
      }
    };
    
    utterance.onerror = () => resetSpeechControls();

    currentUtteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const resetSpeechControls = () => {
    setIsPlaying(false);
    setIsPaused(false);
    currentUtteranceRef.current = null;
  };

  // Speech control handlers
  const handlePlay = () => {
    if (isPlaying && !isPaused) {
      window.speechSynthesis.cancel();
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
    window.speechSynthesis.cancel();
    resetSpeechControls();
    setActiveTab(tab);
  };

  if (showHomePage) {
    return (
      <div className="home-page">
        {/* White background fill */}
        <div className="white-bg-fill"></div>
        
        <img 
          src="/Cogni-Flow-1.png" 
          alt="Cogni-Flow Logo 1"
          className="logo-animated logo-top"
          style={{
            transform: `translate(-50%, ${-scrollProgress * 180}px)`,
            opacity: 1 - scrollProgress * 1.12
          }}
        />
        <img 
          src="/Cogni-Flow-2.png" 
          alt="Cogni-Flow Logo 2"
          className="logo-animated logo-bottom-left"
          style={{
            transform: `translate(${-scrollProgress * 120}px, ${scrollProgress * 120}px)`,
            opacity: 1 - scrollProgress * 1.2
          }}
        />
        <img 
          src="/Cogni-Flow-3.png" 
          alt="Cogni-Flow Logo 3"
          className="logo-animated logo-bottom-right"
          style={{
            transform: `translate(${scrollProgress * 120}px, ${scrollProgress * 120}px)`,
            opacity: 1 - scrollProgress * 1.2
          }}
        />
        <img 
          src="/Cogni-Flow-4.png" 
          alt="Cogni-Flow Logo 4"
          className={`logo-animated logo-center ${animationComplete ? 'to-header' : ''}`}
          style={animationComplete ? {
            position: 'fixed',
            top: '20px',
            left: '40px',
            transform: 'scale(0.60)',
            zIndex: 10000
          } : {
            transform: `translate(-50%, -50%) scale(${1 - scrollProgress * 0.36})`,
            opacity: 1 - scrollProgress * 0.19
          }}
        />

        <div className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">Welcome to Cogni-Flow</h1>
            <p className="hero-subtitle">Where every learner finds their flow</p>
            {animationComplete && (
              <button 
                className="enter-app-btn"
                onClick={() => setShowHomePage(false)}
              >
                Enter App
              </button>
            )}
          </div>
        </div>

        {/* Main App Content - Scrollable below hero */}
        <div className="main-app-content" style={{ 
          position: 'relative',
          background: 'black',
          minHeight: '100vh',
          zIndex: 1000,
          marginTop: '100vh'
        }}>
          <div className="App" data-theme={theme} style={{ 
            background: 'black',
            color: 'white',
            minHeight: '100vh'
          }}>
            <header className="header" style={{ background: 'black', color: 'white' }}>
              <div className="logo-section">
                <div className="logo">
                  <img src="/Cogni-Flow-4.png" alt="Cogni-Flow Logo" />
                </div>
                <div className="title-area">
                  <h1 style={{ color: 'white' }}>Cogni-Flow</h1>
                  <p className="subtitle" style={{ color: 'white' }}>Your Digital Learning Companion</p>
                </div>
              </div>
              <div className="right">
                <button onClick={() => setShowSettings(true)} title="Settings">⚙️</button>
                <button onClick={() => setTheme(theme === "scheme1" ? "scheme2" : "scheme1")} title="Switch Color Scheme">🎨</button>
              </div>
            </header>

            <main>
              <nav>
                <button className={activeTab === "input" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("input")}>Input</button>
                <button className={activeTab === "notes" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("notes")}>Smart Notes</button>
                <button className={activeTab === "mindmap" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("mindmap")}>Mind Map</button>
                <button className={activeTab === "quiz" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("quiz")}>Quiz</button>
                <button className={activeTab === "flashcard" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("flashcard")}>Flashcards</button>
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
                      {isGenerating ? "Generating..." : "Generate Learning Materials"}
                    </button>
                  </div>
                  <div id="genStatus">{genStatus}</div>
                </section>
              )}

              {activeTab === "notes" && (
                <section className="tab-panel">
                  <div className="speech-controls">
                    <button onClick={handlePlay} className="speech-btn primary">
                      {isPlaying && !isPaused ? "Stop" : isPaused ? "Resume" : "Read Aloud"}
                    </button>
                    <button onClick={handlePause} disabled={!isPlaying || isPaused} className="speech-btn">Pause</button>
                    <button onClick={handleRewind} disabled={!isPlaying && !isPaused} className="speech-btn">Rewind</button>
                    <button onClick={handleSkip} disabled={!isPlaying && !isPaused} className="speech-btn">Skip</button>
                    <label htmlFor="speedSlider" className="ml-2">Speed</label>
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
                  <div style={{ textAlign: settings.textAlign }} dangerouslySetInnerHTML={{ __html: notesContent }} />
                </section>
              )}

              {activeTab === "mindmap" && (
                <section className="tab-panel">
                  <div dangerouslySetInnerHTML={{ __html: mindmapContent }} />
                </section>
              )}

              {activeTab === "quiz" && (
                <section className="tab-panel">
                  <div dangerouslySetInnerHTML={{ __html: quizContent }} />
                </section>
              )}

              {activeTab === "flashcard" && (
                <section className="tab-panel">
                  <div
                    className="flashcard-host"
                    onClick={(e) => {
                      const card = e.target.closest(".flashcard");
                      if (card) card.classList.toggle("flipped");
                    }}
                    dangerouslySetInnerHTML={{ __html: flashcardContent }}
                  />
                </section>
              )}
            </main>

            {showSettings && (
              <div className="modal-bg" onClick={() => setShowSettings(false)}>
                <div className="modal" onClick={(e) => e.stopPropagation()}>
                  <h2>Settings</h2>
                  <div className="form-row">
                    <label>Font Size</label>
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
                    <label>Line Height</label>
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
                    <label>Letter Spacing</label>
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
                        onChange={(e) => setSettings({ ...settings, bionic: e.target.checked })}
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
                  <h2 style={{ color: "var(--accent4)" }}>Error</h2>
                  <p className="mb-4">{errorMessage}</p>
                  <button onClick={() => setShowError(false)}>Got It!</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Original App Content (when Enter App is clicked)
  return (
    <div className="App" data-theme={theme}>
      <header className="header">
        <div className="logo-section">
          <div className="logo">
            <img src="/Cogni-Flow-4.png" alt="Cogni-Flow Logo" />
          </div>
          <div className="title-area">
            <h1>Cogni-Flow</h1>
            <p className="subtitle">Your Digital Learning Companion</p>
          </div>
        </div>
        <div className="right">
          <button onClick={() => setShowSettings(true)} title="Settings">⚙️</button>
          <button onClick={() => setTheme(theme === "scheme1" ? "scheme2" : "scheme1")} title="Switch Color Scheme">🎨</button>
        </div>
      </header>

      <main>
        <nav>
          <button className={activeTab === "input" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("input")}>Input</button>
          <button className={activeTab === "notes" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("notes")}>Smart Notes</button>
          <button className={activeTab === "mindmap" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("mindmap")}>Mind Map</button>
          <button className={activeTab === "quiz" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("quiz")}>Quiz</button>
          <button className={activeTab === "flashcard" ? "tab-btn active" : "tab-btn"} onClick={() => handleTabChange("flashcard")}>Flashcards</button>
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
                {isGenerating ? "Generating..." : "Generate Learning Materials"}
              </button>
            </div>
            <div id="genStatus">{genStatus}</div>
          </section>
        )}

        {activeTab === "notes" && (
          <section className="tab-panel">
            <div className="speech-controls">
              <button onClick={handlePlay} className="speech-btn primary">
                {isPlaying && !isPaused ? "Stop" : isPaused ? "Resume" : "Read Aloud"}
              </button>
              <button onClick={handlePause} disabled={!isPlaying || isPaused} className="speech-btn">Pause</button>
              <button onClick={handleRewind} disabled={!isPlaying && !isPaused} className="speech-btn">Rewind</button>
              <button onClick={handleSkip} disabled={!isPlaying && !isPaused} className="speech-btn">Skip</button>
              <label htmlFor="speedSlider" className="ml-2">Speed</label>
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
            <div style={{ textAlign: settings.textAlign }} dangerouslySetInnerHTML={{ __html: notesContent }} />
          </section>
        )}

        {activeTab === "mindmap" && (
          <section className="tab-panel">
            <div dangerouslySetInnerHTML={{ __html: mindmapContent }} />
          </section>
        )}

        {activeTab === "quiz" && (
          <section className="tab-panel">
            <div dangerouslySetInnerHTML={{ __html: quizContent }} />
          </section>
        )}

        {activeTab === "flashcard" && (
          <section className="tab-panel">
            <div
              className="flashcard-host"
              onClick={(e) => {
                const card = e.target.closest(".flashcard");
                if (card) card.classList.toggle("flipped");
              }}
              dangerouslySetInnerHTML={{ __html: flashcardContent }}
            />
          </section>
        )}
      </main>

      {showSettings && (
        <div className="modal-bg" onClick={() => setShowSettings(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Settings</h2>
            <div className="form-row">
              <label>Font Size</label>
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
              <label>Line Height</label>
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
              <label>Letter Spacing</label>
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
                  onChange={(e) => setSettings({ ...settings, bionic: e.target.checked })}
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
            <h2 style={{ color: "var(--accent4)" }}>Error</h2>
            <p className="mb-4">{errorMessage}</p>
            <button onClick={() => setShowError(false)}>Got It!</button>
          </div>
        </div>
      )}
    </div>
  );
}
}
