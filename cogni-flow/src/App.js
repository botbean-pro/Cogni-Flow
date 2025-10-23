import React, { useEffect, useRef, useState } from "react";
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import "./App.css";

// Add Google Fonts link for Libre Franklin
if (!document.querySelector('link[href*="Libre+Franklin"]')) {
  const link = document.createElement('link');
  link.href = 'https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700&display=swap';
  link.rel = 'stylesheet';
  document.head.appendChild(link);
}

// Firebase Configuration - SECURITY NOTE: Move to environment variables
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyDyy8AM0mc9oLi8ixywP4qo2dpJp2TYG6o",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "cogni-flow-d41db.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "cogni-flow-d41db",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "cogni-flow-d41db.firebasestorage.app",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "812584499671",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:812584499671:web:14516059d67a937ec47392",
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID || "G-5W2RWBEHLE",
};

try {
  const app = initializeApp(firebaseConfig);
  getAnalytics(app);
} catch (e) {
  console.log("Firebase init error:", e);
}

// Gemini API configuration - SECURITY NOTE: Move to environment variable
const apiKey = process.env.REACT_APP_GEMINI_API_KEY || "AIzaSyAaiJHfFeKRrF8Wy5rqUCwhN2l3-EEi-2Q";
const API_ENDPOINTS = [
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-latest:generateContent?key=${apiKey}`,
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${apiKey}`,
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=${apiKey}`,
];

export default function App() {
  const [activeTab, setActiveTab] = useState("input");
  const [theme, setTheme] = useState("scheme1");
<<<<<<< HEAD
=======
  const [scrollProgress, setScrollProgress] = useState(0);
  const [animationComplete, setAnimationComplete] = useState(false);

  // Inputs
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
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
    fontFamily: "Libre Franklin, sans-serif",
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

<<<<<<< HEAD
=======
  // Home page scroll animation
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const progress = Math.min(scrollTop / (window.innerHeight * 0.8), 1);
      setScrollProgress(progress);
      const bg = document.querySelector(".front-bg");
      if (bg) bg.style.transform = `translateY(${scrollTop *0.4}px)`;
      if (progress > 0.8 && !animationComplete) setAnimationComplete(true);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [animationComplete]);

  // Load settings from localStorage
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
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

  // YOUR CLEAN HTML RESPONSE FUNCTION
  const cleanHtmlResponse = (response) => {
    if (!response) return "";
    let cleanedResponse = response;

<<<<<<< HEAD
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

    // Trim whitespace
    cleanedResponse = cleanedResponse.trim();

    // If still starts with backticks, remove first line
    if (cleanedResponse.indexOf("```") !== -1) {
      const lines = cleanedResponse.split("\n");
      lines.shift(); // Remove first line
      cleanedResponse = lines.join("\n");
    }

    return cleanedResponse;
  };

=======
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

  // Trim whitespace
  cleanedResponse = cleanedResponse.trim();

  // If still starts with backticks, remove first line
  if (cleanedResponse.indexOf("```") !== -1) {
    const lines = cleanedResponse.split("\n");
    lines.shift(); // Remove first line
    cleanedResponse = lines.join("\n");
  }

  return cleanedResponse;
};


  // Extract text from HTML
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
  const extractTextFromHtml = (htmlString) => {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlString;

    const unwantedTags = [
      "script",
      "style",
      "nav",
      "header",
      "footer",
      "aside",
      "noscript",
      "iframe",
      "object",
      "embed"
    ];
    unwantedTags.forEach((tag) => {
      const elements = tempDiv.getElementsByTagName(tag);
      for (let i = elements.length - 1; i >= 0; i--) {
        elements[i].remove();
      }
    });

    let content = "";
    const mainSelectors = [
      "main",
      "article",
      "[role='main']",
      ".content",
      "#content",
      ".post",
      ".article",
      ".entry-content"
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
    throw new Error("Failed to fetch content from URL");
  };

<<<<<<< HEAD
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
=======
  // YOUR GENERATE CONTENT FROM GEMINI FUNCTION
  const generateContentFromGemini = async (prompt) => {
  const payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: { temperature: 0.7, topK: 40, topP: 0.95, maxOutputTokens: 8192 },
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
  };

  const callGeminiAPI = async (endpoint, prompt) => {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.25, maxOutputTokens: 8192 },
      }),
    });
    if (!response.ok) throw new Error(`API failed: ${response.status}`);
    const data = await response.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || "";
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
<<<<<<< HEAD
      if (urlInput && !sourceText) {
        setGenStatus("Fetching content from URL...");
        sourceText = await fetchUrlContent(urlInput);
        if (!sourceText) {
          showErrorDialog("Could not extract content from the URL");
          return;
        }
        setTextInput(sourceText);
=======
      const response = await fetch(API_ENDPOINTS[i], {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const jsonResponse = await response.json();

      if (!response.ok) {
        if (i < API_ENDPOINTS.length - 1) continue;
        throw new Error(jsonResponse.error?.message || "Unknown API error");
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
      }
      if (!sourceText) {
        showErrorDialog("No valid content to process");
        return;
      }
      const truncatedText = sourceText.substring(0, 30000);
      const prompts = {
        notes: `Convert this content into comprehensive, well-structured study notes in HTML format. Use semantic HTML5 elements, headings (h2, h3, h4), lists (ul/ol), and paragraphs. Include <strong> for emphasis, <mark> for highlights, and <blockquote> for important concepts. Make it educational and easy to scan: ${truncatedText}`,
        mindmap: `Create an interactive, colorful mind map HTML visualization of this content. Use nested divs with CSS for styling. Center the main topic, branch out key concepts, and include sub-branches for details. Use colors, borders, and padding to create visual hierarchy: ${truncatedText}`,
        quiz: `Generate an interactive quiz in HTML format with 10 multiple-choice questions based on this content. Include radio buttons, a submit button, and JavaScript for scoring. Show correct answers on submission with explanations: ${truncatedText}`,
        flashcard: `Create interactive flashcards in HTML format. Generate 10 cards with question on front and answer on back. Use CSS transforms for flip animation. Include navigation buttons and card counter: ${truncatedText}`
      };

<<<<<<< HEAD
      for (const [type, prompt] of Object.entries(prompts)) {
        setGenStatus(`Generating ${type}...`);
        let success = false;
        for (const endpoint of API_ENDPOINTS) {
          try {
            const response = await callGeminiAPI(endpoint, prompt);
            const cleanedResponse = cleanHtmlResponse(response);
            switch (type) {
              case "notes": setNotesContent(cleanedResponse); break;
              case "mindmap": setMindmapContent(cleanedResponse); break;
              case "quiz": setQuizContent(cleanedResponse); break;
              case "flashcard": setFlashcardContent(cleanedResponse); break;
            }
            success = true;
            break;
          } catch (error) {
            console.log(`Endpoint failed: ${endpoint}`, error);
          }
        }
        if (!success) throw new Error(`Failed to generate ${type} with all endpoints`);
      }
      setGenStatus("All materials generated successfully!");
      setActiveTab("notes");
      setTimeout(() => setGenStatus(""), 3000);
=======
      // ✅ Proper optional chaining
      const generatedText =
        jsonResponse?.candidates?.[0]?.content?.parts?.[0]?.text;

      if (generatedText) return cleanHtmlResponse(generatedText);

      if (i < API_ENDPOINTS.length - 1) continue;
      throw new Error("Invalid API response.");
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
    } catch (error) {
      showErrorDialog("Failed to generate materials", error);
    } finally {
      setIsGenerating(false);
    }
<<<<<<< HEAD
=======
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
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
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

<<<<<<< HEAD
  const splitIntoSentences = (text) => {
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
    return sentences.map((s) => s.trim()).filter((s) => s.length > 0);
  };

=======
  // YOUR GENERATE FLASHCARDS FUNCTION
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

Content: ${inputText}`;
  
  const htmlContent = await generateContentFromGemini(prompt);
  setFlashcardContent(htmlContent);
};

// ✅ Event handlers
const handleFileChange = (e) => {
  const file = e.target.files?.[0] || null;
  setFileInput(file);
};

const handleGenerate = async () => {
  setIsGenerating(true);
  setGenStatus("Preparing your content...");
  let processedText = textInput.trim();

  try {
    if (!processedText && urlInput && !fileInput) {
      setGenStatus("Fetching content from URL...");
      processedText = await fetchUrlContent(urlInput);
      setGenStatus("URL content loaded!");
    }

    if (!processedText && fileInput) {
      setGenStatus("Reading file...");
      processedText = await fileInput.text();
    }

    if (!processedText) {
      throw new Error("Please provide text, a URL, or a file.");
    }

    setGenStatus("Creating Smart Notes...");
    await generateSmartNotes(processedText);
    await new Promise((resolve) => setTimeout(resolve, 400));

    setGenStatus("Building Mind Map...");
    await generateMindMap(processedText);
    await new Promise((resolve) => setTimeout(resolve, 400));

    setGenStatus("Crafting Quiz...");
    await generateQuiz(processedText);
    await new Promise((resolve) => setTimeout(resolve, 400));

    setGenStatus("Designing Flashcards...");
    await generateFlashcards(processedText);

    setGenStatus("✅ All materials generated! Check the tabs above.");
    setActiveTab("notes");
  } catch (error) {
    showErrorDialog("Generation failed", error);
    setGenStatus("Error occurred.");
  } finally {
    setIsGenerating(false);
  }
};


  // Speech synthesis functions
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
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
<<<<<<< HEAD
=======
    
    const selectedVoices = pickVoice();
    if (selectedVoices && selectedVoices.length > 0)
      utterance.voice = selectedVoices;

    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
    };
    
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
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
    window.speechSynthesis.cancel();
    resetSpeechControls();
    setActiveTab(tab);
  };

  return (
<<<<<<< HEAD
    <div className="App" data-theme={theme}>
      {/* Main Image Header - Replaces the logos */}
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
            style={{
              width: '64px', 
              height: '64px',
            }} 
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
              <input type="range" min="12" max="24" value={settings.fontSize} onChange={(e) => setSettings({ ...settings, fontSize: parseInt(e.target.value) })} />
            </div>
            <div className="form-row">
              <label>Font Family</label>
              <select value={settings.fontFamily} onChange={(e) => setSettings({ ...settings, fontFamily: e.target.value })}>
                <option>Libre Franklin, sans-serif</option>
                <option>Inter, Arial, sans-serif</option>
                <option>OpenDyslexic, Arial, sans-serif</option>
              </select>
            </div>
            <div className="form-row">
              <label>Text Align</label>
              <select value={settings.textAlign} onChange={(e) => setSettings({ ...settings, textAlign: e.target.value })}>
                <option value="left">Left</option>
                <option value="justify">Justify</option>
                <option value="center">Center</option>
              </select>
            </div>
            <div className="form-row">
              <label>Line Height</label>
              <input type="range" min="1.2" max="2.5" step="0.1" value={settings.lineHeight} onChange={(e) => setSettings({ ...settings, lineHeight: parseFloat(e.target.value) })} />
            </div>
            <div className="form-row">
              <label>Letter Spacing</label>
              <input type="range" min="0" max="3" step="0.1" value={settings.letterSpacing} onChange={(e) => setSettings({ ...settings, letterSpacing: parseFloat(e.target.value) })} />
            </div>
            <div className="form-row">
              <label>
                <input type="checkbox" checked={settings.bionic} onChange={(e) => setSettings({ ...settings, bionic: e.target.checked})} />
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
            <h2 style={{ color: "var(--color-red-500)" }}>Error</h2>
            <p className="mb-4">{errorMessage}</p>
            <button onClick={() => setShowError(false)}>Got It!</button>
          </div>
        </div>
      )}
    </div>
  );
}
=======
    <div className="home-page">
      <section className="front-section">
  <div className="front-bg"></div>

  <img
    src="/Cogni-Flow-1.png"
    alt="Cogni-Flow Logo 1"
    className="logo-animated logo-top"
    style={{
      transform: `translate(-50%, ${-scrollProgress * 180}px)`,
      opacity: Math.max(0, 1 - scrollProgress * 1.5),
    }}
  />

  <img
    src="/Cogni-Flow-2.png"
    alt="Cogni-Flow Logo 2"
    className="logo-animated logo-bottom-left"
    style={{
      transform: `translate(${-scrollProgress * 120}px, ${scrollProgress * 120}px)`,
      opacity: Math.max(0, 1 - scrollProgress * 1.5),
    }}
  />

  <img
    src="/Cogni-Flow-3.png"
    alt="Cogni-Flow Logo 3"
    className="logo-animated logo-bottom-right"
    style={{
      transform: `translate(${scrollProgress * 120}px, ${scrollProgress * 120}px)`,
      opacity: Math.max(0, 1 - scrollProgress * 1.5),
    }}
  />

  <img
    src="/Cogni-Flow-4.png"
    alt="Cogni-Flow Logo 4"
    className={`logo-animated logo-center ${animationComplete ? 'to-header' : ''}`}
    style={
      animationComplete || scrollProgress > 0.8
        ? {
            position: 'fixed',
            top: '20px',
            left: '40px',
            transform: 'scale(0.60)',
            zIndex: 10000,
          }
        : {
            transform: `translate(-50%, -50%) scale(${1 - scrollProgress * 0.36})`,
            opacity: Math.max(0, 1 - scrollProgress * 0.8),
          }   
          }
          />
          </section>

      {/* Main App Content - APPEARS ON SCROLL */}
      <div className="main-app-content" style={{ 
        marginTop: '100vh',
        background: 'white',
        borderRadius: '40px 40px 0 0',
        paddingTop: '60px',
        boxShadow: '0 -20px 50px rgba(0,0,0,0.1)',
        position: 'relative',
        zIndex: 1000,
        minHeight: '100vh'
      }}>
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
                <h2 style={{ color: "var(--color-red-500)" }}>Error</h2>
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
>>>>>>> cbc13805d99cad7bf8a6aa44a04fadae040f765c
