// Cogni-Flow Application JavaScript

// Sample data from the requirements
const SAMPLE_DATA = {
  content: {
    title: "Photosynthesis in Plants",
    text: "Photosynthesis is the process by which plants convert light energy, usually from the sun, into chemical energy stored in glucose. This process occurs in the chloroplasts of plant cells and involves two main stages: the light reactions and the Calvin cycle. During the light reactions, chlorophyll absorbs light energy and converts it into ATP and NADPH. These energy carriers are then used in the Calvin cycle to convert carbon dioxide from the air into glucose. The overall equation for photosynthesis is: 6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂. This process is crucial for life on Earth as it produces oxygen and serves as the foundation of most food chains.",
    keyConcepts: ["Photosynthesis", "Chloroplasts", "Light reactions", "Calvin cycle", "ATP and NADPH", "Glucose production", "Oxygen release"]
  },
  mindMap: {
    center: "Photosynthesis",
    branches: [
      {
        topic: "Location",
        subtopics: ["Chloroplasts", "Plant cells", "Leaves"]
      },
      {
        topic: "Process",
        subtopics: ["Light reactions", "Calvin cycle", "Energy conversion"]
      },
      {
        topic: "Requirements",
        subtopics: ["Sunlight", "Carbon dioxide", "Water", "Chlorophyll"]
      },
      {
        topic: "Products",
        subtopics: ["Glucose", "Oxygen", "ATP", "NADPH"]
      }
    ]
  },
  quiz: [
    {
      type: "multiple_choice",
      question: "Where does photosynthesis primarily occur in plants?",
      options: ["Chloroplasts", "Mitochondria", "Nucleus", "Vacuole"],
      correct: 0,
      explanation: "Photosynthesis occurs in chloroplasts, which contain chlorophyll and are specialized for capturing light energy."
    },
    {
      type: "fill_blank",
      question: "The two main stages of photosynthesis are the light reactions and the _____ cycle.",
      answer: "Calvin",
      explanation: "The Calvin cycle is the second stage where CO₂ is converted to glucose using energy from the light reactions."
    },
    {
      type: "short_answer",
      question: "What is the overall chemical equation for photosynthesis?",
      answer: "6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂",
      explanation: "This equation shows how carbon dioxide and water are converted to glucose and oxygen using light energy."
    }
  ]
};

// Application state
let appState = {
  currentTheme: 'light',
  currentContent: null,
  currentQuiz: [],
  currentQuizIndex: 0,
  quizScore: 0,
  ttsActive: false,
  speechSynthesis: null,
  settings: {
    fontSize: 16,
    fontFamily: 'Arial, sans-serif',
    letterSpacing: 0,
    lineHeight: 1.5,
    bionicReading: false,
    readingSpeed: 1
  }
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

function initializeApp() {
  setupEventListeners();
  loadSettings();
  applySettings();
  switchTab('input');
}

function setupEventListeners() {
  // Settings panel
  const settingsToggle = document.getElementById('settingsToggle');
  const closeSettings = document.getElementById('closeSettings');
  const settingsPanel = document.getElementById('settingsPanel');
  
  if (settingsToggle) {
    settingsToggle.addEventListener('click', function(e) {
      e.preventDefault();
      settingsPanel.classList.toggle('active');
    });
  }
  
  if (closeSettings) {
    closeSettings.addEventListener('click', function(e) {
      e.preventDefault();
      settingsPanel.classList.remove('active');
    });
  }
  
  // Theme toggle
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  
  const themeButtons = document.querySelectorAll('.theme-btn');
  themeButtons.forEach(btn => {
    btn.addEventListener('click', (e) => setTheme(e.target.dataset.theme));
  });
  
  // Tab navigation
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tabId = e.target.id.replace('Tab', '');
      switchTab(tabId);
    });
  });
  
  // Input handling
  const selectFile = document.getElementById('selectFile');
  const fileInput = document.getElementById('fileInput');
  const fetchUrl = document.getElementById('fetchUrl');
  const processContent = document.getElementById('processContent');
  const loadSample = document.getElementById('loadSample');
  
  if (selectFile && fileInput) {
    selectFile.addEventListener('click', (e) => {
      e.preventDefault();
      fileInput.click();
    });
    fileInput.addEventListener('change', handleFileSelect);
  }
  
  if (fetchUrl) {
    fetchUrl.addEventListener('click', fetchUrlContent);
  }
  
  if (processContent) {
    processContent.addEventListener('click', processContentHandler);
  }
  
  if (loadSample) {
    loadSample.addEventListener('click', loadSampleContent);
  }
  
  // File upload area
  setupFileUpload();
  
  // Settings controls
  const fontFamily = document.getElementById('fontFamily');
  const fontSize = document.getElementById('fontSize');
  const letterSpacing = document.getElementById('letterSpacing');
  const lineHeight = document.getElementById('lineHeight');
  const bionicReading = document.getElementById('bionicReading');
  const readingSpeed = document.getElementById('readingSpeed');
  
  if (fontFamily) fontFamily.addEventListener('change', updateFontFamily);
  if (fontSize) fontSize.addEventListener('input', updateFontSize);
  if (letterSpacing) letterSpacing.addEventListener('input', updateLetterSpacing);
  if (lineHeight) lineHeight.addEventListener('input', updateLineHeight);
  if (bionicReading) bionicReading.addEventListener('change', toggleBionicReading);
  if (readingSpeed) readingSpeed.addEventListener('input', updateReadingSpeed);
  
  // Content controls
  const ttsNotesBtn = document.getElementById('ttsNotesBtn');
  const exportNotes = document.getElementById('exportNotes');
  const expandAllNodes = document.getElementById('expandAllNodes');
  const collapseAllNodes = document.getElementById('collapseAllNodes');
  
  if (ttsNotesBtn) ttsNotesBtn.addEventListener('click', startTTS);
  if (exportNotes) exportNotes.addEventListener('click', exportNotesHandler);
  if (expandAllNodes) expandAllNodes.addEventListener('click', expandAllNodesHandler);
  if (collapseAllNodes) collapseAllNodes.addEventListener('click', collapseAllNodesHandler);
  
  // TTS controls
  const ttsPlay = document.getElementById('ttsPlay');
  const ttsPause = document.getElementById('ttsPause');
  const ttsStop = document.getElementById('ttsStop');
  const ttsClose = document.getElementById('ttsClose');
  
  if (ttsPlay) ttsPlay.addEventListener('click', playTTS);
  if (ttsPause) ttsPause.addEventListener('click', pauseTTS);
  if (ttsStop) ttsStop.addEventListener('click', stopTTS);
  if (ttsClose) ttsClose.addEventListener('click', closeTTS);
}

// Settings functions
function loadSettings() {
  // In a real app, this would load from localStorage
  // For demo purposes, we'll use default settings
}

function saveSettings() {
  // In a real app, this would save to localStorage
}

function applySettings() {
  document.documentElement.style.setProperty('--dynamic-font-size', `${appState.settings.fontSize}px`);
  document.documentElement.style.setProperty('--dynamic-font-family', appState.settings.fontFamily);
  document.documentElement.style.setProperty('--dynamic-letter-spacing', `${appState.settings.letterSpacing}px`);
  document.documentElement.style.setProperty('--dynamic-line-height', appState.settings.lineHeight);
  
  // Update UI controls
  const fontSizeValue = document.getElementById('fontSizeValue');
  const letterSpacingValue = document.getElementById('letterSpacingValue');
  const lineHeightValue = document.getElementById('lineHeightValue');
  const readingSpeedValue = document.getElementById('readingSpeedValue');
  
  if (fontSizeValue) fontSizeValue.textContent = `${appState.settings.fontSize}px`;
  if (letterSpacingValue) letterSpacingValue.textContent = `${appState.settings.letterSpacing}px`;
  if (lineHeightValue) lineHeightValue.textContent = appState.settings.lineHeight;
  if (readingSpeedValue) readingSpeedValue.textContent = `${appState.settings.readingSpeed}x`;
  
  const fontSize = document.getElementById('fontSize');
  const fontFamily = document.getElementById('fontFamily');
  const letterSpacing = document.getElementById('letterSpacing');
  const lineHeight = document.getElementById('lineHeight');
  const bionicReading = document.getElementById('bionicReading');
  const readingSpeed = document.getElementById('readingSpeed');
  
  if (fontSize) fontSize.value = appState.settings.fontSize;
  if (fontFamily) fontFamily.value = appState.settings.fontFamily;
  if (letterSpacing) letterSpacing.value = appState.settings.letterSpacing;
  if (lineHeight) lineHeight.value = appState.settings.lineHeight;
  if (bionicReading) bionicReading.checked = appState.settings.bionicReading;
  if (readingSpeed) readingSpeed.value = appState.settings.readingSpeed;
  
  // Apply bionic reading
  if (appState.settings.bionicReading) {
    document.body.classList.add('bionic-reading');
  } else {
    document.body.classList.remove('bionic-reading');
  }
}

function updateFontFamily(e) {
  appState.settings.fontFamily = e.target.value;
  applySettings();
  saveSettings();
}

function updateFontSize(e) {
  appState.settings.fontSize = parseInt(e.target.value);
  applySettings();
  saveSettings();
}

function updateLetterSpacing(e) {
  appState.settings.letterSpacing = parseFloat(e.target.value);
  applySettings();
  saveSettings();
}

function updateLineHeight(e) {
  appState.settings.lineHeight = parseFloat(e.target.value);
  applySettings();
  saveSettings();
}

function toggleBionicReading(e) {
  appState.settings.bionicReading = e.target.checked;
  applySettings();
  saveSettings();
}

function updateReadingSpeed(e) {
  appState.settings.readingSpeed = parseFloat(e.target.value);
  applySettings();
  saveSettings();
}

// Theme functions
function toggleTheme() {
  const themes = ['light', 'dark', 'high-contrast', 'calm-blue'];
  const currentIndex = themes.indexOf(appState.currentTheme);
  const nextIndex = (currentIndex + 1) % themes.length;
  setTheme(themes[nextIndex]);
}

function setTheme(themeName) {
  appState.currentTheme = themeName;
  document.body.setAttribute('data-theme', themeName);
  
  // Update theme buttons
  const themeButtons = document.querySelectorAll('.theme-btn');
  themeButtons.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === themeName);
  });
  
  // Update theme toggle button text
  const themeEmojis = {
    light: '☀️',
    dark: '🌙',
    'high-contrast': '⚫',
    'calm-blue': '💙'
  };
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.innerHTML = `${themeEmojis[themeName]} Theme`;
  }
}

// Tab navigation
function switchTab(tabName) {
  // Update tab buttons
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.classList.toggle('active', btn.id === `${tabName}Tab`);
    btn.setAttribute('aria-selected', btn.id === `${tabName}Tab`);
  });
  
  // Update tab panels
  const tabPanels = document.querySelectorAll('.tab-panel');
  tabPanels.forEach(panel => {
    panel.classList.toggle('active', panel.id === `${tabName}Panel`);
  });
}

// File upload setup
function setupFileUpload() {
  const uploadArea = document.getElementById('fileUploadArea');
  if (!uploadArea) return;
  
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults);
  });
  
  ['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'));
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'));
  });
  
  uploadArea.addEventListener('drop', handleDrop);
}

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function handleDrop(e) {
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    processFile(files[0]);
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) {
    processFile(file);
  }
}

function processFile(file) {
  showLoading();
  
  // Simulate file processing
  setTimeout(() => {
    const reader = new FileReader();
    reader.onload = function(e) {
      const content = e.target.result;
      const textInput = document.getElementById('textInput');
      if (textInput) {
        textInput.value = content.substring(0, 1000); // Limit content for demo
      }
      hideLoading();
      showNotification('File processed successfully!', 'success');
    };
    
    reader.onerror = function() {
      hideLoading();
      showNotification('Error processing file', 'error');
    };
    
    reader.readAsText(file);
  }, 1500);
}

function fetchUrlContent() {
  const urlInput = document.getElementById('urlInput');
  const url = urlInput ? urlInput.value.trim() : '';
  
  if (!url) {
    showNotification('Please enter a valid URL', 'error');
    return;
  }
  
  showLoading();
  
  // Simulate URL fetching
  setTimeout(() => {
    const textInput = document.getElementById('textInput');
    if (textInput) {
      textInput.value = SAMPLE_DATA.content.text;
    }
    hideLoading();
    showNotification('Content fetched successfully!', 'success');
  }, 2000);
}

function loadSampleContent() {
  const textInput = document.getElementById('textInput');
  if (textInput) {
    textInput.value = SAMPLE_DATA.content.text;
    showNotification('Sample content loaded!', 'success');
  }
}

// Content processing
function processContentHandler() {
  const textInput = document.getElementById('textInput');
  const text = textInput ? textInput.value.trim() : '';
  
  if (!text) {
    showNotification('Please provide some content to process', 'error');
    return;
  }
  
  showLoading();
  
  // Simulate processing
  setTimeout(() => {
    appState.currentContent = {
      text: text,
      title: 'Processed Content'
    };
    
    generateSmartNotes(text);
    generateMindMap();
    generateQuiz();
    
    hideLoading();
    showNotification('Content processed successfully!', 'success');
    switchTab('notes');
  }, 2500);
}

function generateSmartNotes(text) {
  // Generate structured notes from the content
  const notes = `
    <h2>${SAMPLE_DATA.content.title}</h2>
    
    <h3>📋 Key Concepts</h3>
    <ul>
      ${SAMPLE_DATA.content.keyConcepts.map(concept => 
        `<li><span class="key-concept">${concept}</span></li>`
      ).join('')}
    </ul>
    
    <h3>📝 Summary</h3>
    <p>${text.substring(0, 300)}...</p>
    
    <h3>🔍 Main Points</h3>
    <ul>
      <li>Photosynthesis converts light energy into chemical energy stored as glucose</li>
      <li>The process occurs in chloroplasts and involves two main stages</li>
      <li>Light reactions produce ATP and NADPH energy carriers</li>
      <li>The Calvin cycle uses these carriers to convert CO₂ into glucose</li>
      <li>This process is essential for life on Earth, producing oxygen and food</li>
    </ul>
    
    <h3>⚡ Chemical Equation</h3>
    <p><strong>6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂</strong></p>
  `;
  
  const notesContent = document.getElementById('notesContent');
  if (notesContent) {
    notesContent.innerHTML = notes;
    
    // Apply bionic reading if enabled
    if (appState.settings.bionicReading) {
      applyBionicReading(notesContent);
    }
  }
}

function generateMindMap() {
  const mindMapHTML = `
    <div class="mindmap">
      <div class="mindmap-center" tabindex="0" role="button">${SAMPLE_DATA.mindMap.center}</div>
      <div class="mindmap-branches">
        ${SAMPLE_DATA.mindMap.branches.map(branch => `
          <div class="mindmap-branch">
            <div class="branch-header" tabindex="0" role="button" onclick="toggleBranch(this)">
              <span class="branch-title">${branch.topic}</span>
              <span class="branch-toggle">▼</span>
            </div>
            <div class="branch-content">
              ${branch.subtopics.map(subtopic => `
                <div class="subtopic">${subtopic}</div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  
  const mindmapContainer = document.getElementById('mindmapContainer');
  if (mindmapContainer) {
    mindmapContainer.innerHTML = mindMapHTML;
  }
}

function generateQuiz() {
  appState.currentQuiz = [...SAMPLE_DATA.quiz];
  appState.currentQuizIndex = 0;
  appState.quizScore = 0;
  
  updateQuizStats();
  displayCurrentQuestion();
}

function displayCurrentQuestion() {
  const quiz = appState.currentQuiz;
  const current = quiz[appState.currentQuizIndex];
  
  if (!current) {
    displayQuizResults();
    return;
  }
  
  let questionHTML = `
    <div class="quiz-question">
      <div class="question-content">
        <div class="question-type">${formatQuestionType(current.type)}</div>
        <div class="question-text">${current.question}</div>
      </div>
  `;
  
  if (current.type === 'multiple_choice') {
    questionHTML += `
      <div class="quiz-options">
        ${current.options.map((option, index) => `
          <div class="quiz-option" tabindex="0" role="button" onclick="selectOption(${index})" data-index="${index}">
            <span>${String.fromCharCode(65 + index)}.</span>
            <span>${option}</span>
          </div>
        `).join('')}
      </div>
    `;
  } else if (current.type === 'fill_blank') {
    questionHTML += `
      <div class="quiz-input-container">
        <input type="text" class="quiz-input" id="fillBlankAnswer" placeholder="Type your answer here...">
      </div>
    `;
  } else if (current.type === 'short_answer') {
    questionHTML += `
      <div class="quiz-input-container">
        <textarea class="quiz-input" id="shortAnswer" rows="3" placeholder="Type your answer here..."></textarea>
      </div>
    `;
  }
  
  questionHTML += `
    </div>
    <div class="quiz-navigation">
      <button class="btn btn--outline" onclick="previousQuestion()" ${appState.currentQuizIndex === 0 ? 'disabled' : ''}>
        ⬅️ Previous
      </button>
      <button class="btn btn--primary" onclick="submitAnswer()">
        Submit Answer
      </button>
      <button class="btn btn--outline" onclick="nextQuestion()">
        Next ➡️
      </button>
    </div>
  `;
  
  const quizContainer = document.getElementById('quizContainer');
  if (quizContainer) {
    quizContainer.innerHTML = questionHTML;
  }
}

function formatQuestionType(type) {
  const types = {
    'multiple_choice': '📝 Multiple Choice',
    'fill_blank': '✏️ Fill in the Blank',
    'short_answer': '💬 Short Answer'
  };
  return types[type] || type;
}

function selectOption(index) {
  const options = document.querySelectorAll('.quiz-option');
  options.forEach(option => option.classList.remove('selected'));
  options[index].classList.add('selected');
}

function submitAnswer() {
  const current = appState.currentQuiz[appState.currentQuizIndex];
  let userAnswer = null;
  let isCorrect = false;
  
  if (current.type === 'multiple_choice') {
    const selected = document.querySelector('.quiz-option.selected');
    if (!selected) {
      showNotification('Please select an answer', 'warning');
      return;
    }
    userAnswer = parseInt(selected.dataset.index);
    isCorrect = userAnswer === current.correct;
    
    // Show correct/incorrect styling
    const options = document.querySelectorAll('.quiz-option');
    options.forEach((option, index) => {
      if (index === current.correct) {
        option.classList.add('correct');
      } else if (index === userAnswer && !isCorrect) {
        option.classList.add('incorrect');
      }
    });
    
  } else if (current.type === 'fill_blank') {
    const input = document.getElementById('fillBlankAnswer');
    userAnswer = input ? input.value.trim() : '';
    isCorrect = userAnswer.toLowerCase() === current.answer.toLowerCase();
    
  } else if (current.type === 'short_answer') {
    const input = document.getElementById('shortAnswer');
    userAnswer = input ? input.value.trim() : '';
    isCorrect = userAnswer.toLowerCase().includes(current.answer.toLowerCase());
  }
  
  if (isCorrect) {
    appState.quizScore++;
  }
  
  // Show explanation
  const explanation = `
    <div class="quiz-answer">
      <strong>${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</strong>
      <div class="quiz-explanation">${current.explanation}</div>
      ${current.type !== 'multiple_choice' ? `<p><strong>Expected answer:</strong> ${current.answer}</p>` : ''}
    </div>
  `;
  
  const questionDiv = document.querySelector('.quiz-question');
  if (questionDiv) {
    questionDiv.insertAdjacentHTML('afterend', explanation);
  }
  
  updateQuizStats();
  
  // Disable submit button
  const submitBtn = document.querySelector('.quiz-navigation .btn--primary');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = isCorrect ? '✅ Correct!' : '❌ Incorrect';
  }
}

function nextQuestion() {
  if (appState.currentQuizIndex < appState.currentQuiz.length - 1) {
    appState.currentQuizIndex++;
    displayCurrentQuestion();
    updateQuizStats();
  }
}

function previousQuestion() {
  if (appState.currentQuizIndex > 0) {
    appState.currentQuizIndex--;
    displayCurrentQuestion();
    updateQuizStats();
  }
}

function updateQuizStats() {
  const currentQ = document.getElementById('currentQ');
  const totalQ = document.getElementById('totalQ');
  const score = document.getElementById('score');
  const maxScore = document.getElementById('maxScore');
  
  if (currentQ) currentQ.textContent = appState.currentQuizIndex + 1;
  if (totalQ) totalQ.textContent = appState.currentQuiz.length;
  if (score) score.textContent = appState.quizScore;
  if (maxScore) maxScore.textContent = appState.currentQuiz.length;
}

function displayQuizResults() {
  const percentage = Math.round((appState.quizScore / appState.currentQuiz.length) * 100);
  const resultsHTML = `
    <div class="quiz-results">
      <div class="results-header">
        <h2>🎉 Quiz Complete!</h2>
      </div>
      <div class="results-stats">
        <div class="stat">
          <div class="stat-value">${appState.quizScore}/${appState.currentQuiz.length}</div>
          <div class="stat-label">Correct Answers</div>
        </div>
        <div class="stat">
          <div class="stat-value">${percentage}%</div>
          <div class="stat-label">Score</div>
        </div>
      </div>
      <div class="results-message">
        ${percentage >= 80 ? '🌟 Excellent work!' : percentage >= 60 ? '👍 Good job!' : '📚 Keep studying!'}
      </div>
      <button class="btn btn--primary" onclick="restartQuiz()">🔄 Restart Quiz</button>
    </div>
  `;
  
  const quizContainer = document.getElementById('quizContainer');
  if (quizContainer) {
    quizContainer.innerHTML = resultsHTML;
  }
}

function restartQuiz() {
  appState.currentQuizIndex = 0;
  appState.quizScore = 0;
  displayCurrentQuestion();
  updateQuizStats();
}

// Mind map functions
function toggleBranch(element) {
  const branch = element.parentElement;
  const content = branch.querySelector('.branch-content');
  const toggle = element.querySelector('.branch-toggle');
  
  content.classList.toggle('expanded');
  toggle.classList.toggle('expanded');
}

function expandAllNodesHandler() {
  const branches = document.querySelectorAll('.branch-content');
  const toggles = document.querySelectorAll('.branch-toggle');
  
  branches.forEach(branch => branch.classList.add('expanded'));
  toggles.forEach(toggle => toggle.classList.add('expanded'));
}

function collapseAllNodesHandler() {
  const branches = document.querySelectorAll('.branch-content');
  const toggles = document.querySelectorAll('.branch-toggle');
  
  branches.forEach(branch => branch.classList.remove('expanded'));
  toggles.forEach(toggle => toggle.classList.remove('expanded'));
}

// Text-to-Speech functions
function startTTS() {
  if ('speechSynthesis' in window) {
    const notesContent = document.getElementById('notesContent');
    const content = notesContent ? notesContent.textContent || 'No content to read' : 'No content to read';
    
    appState.speechSynthesis = new SpeechSynthesisUtterance(content);
    appState.speechSynthesis.rate = appState.settings.readingSpeed;
    appState.speechSynthesis.onend = () => {
      stopTTS();
    };
    
    speechSynthesis.speak(appState.speechSynthesis);
    appState.ttsActive = true;
    
    const ttsControls = document.getElementById('ttsControls');
    if (ttsControls) {
      ttsControls.classList.remove('hidden');
    }
    
    // Simulate text highlighting
    simulateTextHighlighting();
  } else {
    showNotification('Text-to-speech not supported in this browser', 'error');
  }
}

function playTTS() {
  if (appState.ttsActive && speechSynthesis.paused) {
    speechSynthesis.resume();
  }
}

function pauseTTS() {
  if (appState.ttsActive) {
    speechSynthesis.pause();
  }
}

function stopTTS() {
  if (appState.ttsActive) {
    speechSynthesis.cancel();
    appState.ttsActive = false;
    const ttsControls = document.getElementById('ttsControls');
    if (ttsControls) {
      ttsControls.classList.add('hidden');
    }
    
    // Remove highlighting
    const highlighted = document.querySelectorAll('.tts-highlight');
    highlighted.forEach(el => {
      el.classList.remove('tts-highlight');
    });
  }
}

function closeTTS() {
  stopTTS();
}

function simulateTextHighlighting() {
  const notesContent = document.getElementById('notesContent');
  if (!notesContent) return;
  
  const paragraphs = notesContent.querySelectorAll('p, li');
  let currentIndex = 0;
  
  const highlightInterval = setInterval(() => {
    // Remove previous highlight
    const highlighted = document.querySelectorAll('.tts-highlight');
    highlighted.forEach(el => el.classList.remove('tts-highlight'));
    
    // Add highlight to current paragraph
    if (currentIndex < paragraphs.length && appState.ttsActive) {
      paragraphs[currentIndex].classList.add('tts-highlight');
      currentIndex++;
    } else {
      clearInterval(highlightInterval);
    }
  }, 2000);
}

// Export functions
function exportNotesHandler() {
  const notesContent = document.getElementById('notesContent');
  const content = notesContent ? notesContent.innerHTML : '<p>No content to export</p>';
  const blob = new Blob([content], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cogni-flow-notes.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  showNotification('Notes exported successfully!', 'success');
}

// Utility functions
function showLoading() {
  const loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
    loadingOverlay.classList.remove('hidden');
  }
}

function hideLoading() {
  const loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
    loadingOverlay.classList.add('hidden');
  }
}

function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification--${type}`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background: var(--color-surface);
    border: 2px solid var(--color-primary);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    z-index: 1500;
    max-width: 300px;
    animation: slideIn 0.3s ease-out;
  `;
  
  const typeEmojis = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };
  
  notification.innerHTML = `${typeEmojis[type]} ${message}`;
  document.body.appendChild(notification);
  
  // Add slide in animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.animation = 'slideIn 0.3s ease-out reverse';
    setTimeout(() => {
      if (notification.parentNode) {
        document.body.removeChild(notification);
      }
      if (style.parentNode) {
        document.head.removeChild(style);
      }
    }, 300);
  }, 3000);
}

// Bionic reading
function applyBionicReading(element) {
  const textNodes = getTextNodes(element);
  
  textNodes.forEach(node => {
    const words = node.textContent.split(' ');
    const bionicWords = words.map(word => {
      if (word.length > 2) {
        const boldLength = Math.ceil(word.length / 2);
        const boldPart = word.substring(0, boldLength);
        const regularPart = word.substring(boldLength);
        return `<span class="bionic-word">${boldPart}</span>${regularPart}`;
      }
      return word;
    });
    
    const span = document.createElement('span');
    span.innerHTML = bionicWords.join(' ');
    node.parentNode.replaceChild(span, node);
  });
}

function getTextNodes(element) {
  const textNodes = [];
  const walker = document.createTreeWalker(
    element,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );
  
  let node;
  while (node = walker.nextNode()) {
    if (node.textContent.trim().length > 0) {
      textNodes.push(node);
    }
  }
  
  return textNodes;
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
  // Escape key closes settings panel
  if (e.key === 'Escape') {
    const settingsPanel = document.getElementById('settingsPanel');
    if (settingsPanel && settingsPanel.classList.contains('active')) {
      settingsPanel.classList.remove('active');
    }
    if (appState.ttsActive) {
      stopTTS();
    }
  }
  
  // Tab navigation with arrow keys
  if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
    const activeTab = document.querySelector('.tab-btn.active');
    const tabs = Array.from(document.querySelectorAll('.tab-btn'));
    const currentIndex = tabs.indexOf(activeTab);
    
    if (e.key === 'ArrowLeft' && currentIndex > 0) {
      const tabId = tabs[currentIndex - 1].id.replace('Tab', '');
      switchTab(tabId);
    } else if (e.key === 'ArrowRight' && currentIndex < tabs.length - 1) {
      const tabId = tabs[currentIndex + 1].id.replace('Tab', '');
      switchTab(tabId);
    }
  }
});

// Global functions for HTML onclick handlers
window.toggleBranch = toggleBranch;
window.selectOption = selectOption;
window.submitAnswer = submitAnswer;
window.nextQuestion = nextQuestion;
window.previousQuestion = previousQuestion;
window.restartQuiz = restartQuiz;