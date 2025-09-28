document.addEventListener('DOMContentLoaded', () => {
  const listenButton = document.getElementById('listenButton');
  const clearButton = document.getElementById('clearButton');
  const questionsArea = document.getElementById('questionsArea');
  const answersArea = document.getElementById('answersArea');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const saveApiKeyButton = document.getElementById('saveApiKey');
  const deleteApiKeyButton = document.getElementById('deleteApiKey');
  const voiceStopButton = document.getElementById('voiceStopButton');
  const modal = document.getElementById('modal');
  const modalMessage = document.getElementById('modal-message');
  const closeModal = document.getElementById('modalClose');
  const ttsToggle = document.getElementById('ttsToggle');

  let ttsEnabled = true;  // TTS ON by default
  let currentUtterance = null;

  // Initialize listen button HTML
  listenButton.innerHTML = '<span class="btn-text">Start Listening</span><div class="spinner"></div>';

  // Modal close handlers
  closeModal.onclick = () => {
    modal.style.display = 'none';
  };
  window.onclick = (event) => {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  };

  const themeToggle = document.getElementById('themeToggle');
  themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    document.body.classList.toggle('light');
    themeToggle.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
  });
  

  // Voice stop button handler: stops the ongoing speech
  voiceStopButton.addEventListener('click', () => {
    if (currentUtterance || window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      currentUtterance = null;
      voiceStopButton.disabled = true;
      eel.audio_playback_ended();
    }
  });

  // Update UI on API key presence
  (async () => {
    const hasApiKey = await eel.has_api_key()();
    updateApiKeyUI(hasApiKey);
  })();

  // Toggle listening
  listenButton.addEventListener('click', async () => {
    const isListening = await eel.toggle_listening()();
    const btnText = listenButton.querySelector('.btn-text');
    if (isListening) {
      btnText.textContent = 'Stop Listening';
      listenButton.classList.add('loading');
    } else {
      btnText.textContent = 'Start Listening';
      listenButton.classList.remove('loading');
    }
  });

  // Clear textareas
  clearButton.addEventListener('click', () => {
    questionsArea.innerHTML = '<p style="color:#666; font-style:italic;">Your questions will appear here...</p>';
    answersArea.innerHTML = '<p style="color:#666; font-style:italic;">AI answers will appear here...</p>';
  });

  // Save API key
  saveApiKeyButton.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
      showModal('Please enter a valid API key.');
      return;
    }
    const result = await eel.save_api_key(apiKey)();
    if (result) {
      showModal('API key saved successfully!');
      apiKeyInput.value = '';
      updateApiKeyUI(true);
    } else {
      showModal('Failed to save API key. Please try again.');
    }
  });

  // Delete API key
  deleteApiKeyButton.addEventListener('click', async () => {
    const result = await eel.delete_api_key()();
    if (result) {
      showModal('API key removed successfully!');
      updateApiKeyUI(false);
    } else {
      showModal('Failed to delete API key. Please try again.');
    }
  });

  // Toggle Text-to-Speech
  ttsToggle.addEventListener('click', async () => {
    ttsEnabled = await eel.toggle_tts()();
    ttsToggle.classList.toggle('disabled', !ttsEnabled);
  });

  // Update UI for API key presence
  function updateApiKeyUI(hasApiKey) {
    apiKeyInput.style.display = hasApiKey ? 'none' : 'inline-block';
    saveApiKeyButton.style.display = hasApiKey ? 'none' : 'inline-block';
    deleteApiKeyButton.style.display = hasApiKey ? 'inline-block' : 'none';
    listenButton.disabled = !hasApiKey;
    voiceStopButton.disabled = true;
  }

  // Show modal message
  function showModal(message, logoSrc = null) {
    modalMessage.textContent = message;
    modal.style.display = 'block';
    modal.focus();
  }

  // Expose update_ui to backend (Eel)
  eel.expose(update_ui);
  function update_ui(question, answer) {
    if (question) {
      if (questionsArea.innerHTML.includes('Your questions will appear here')) {
        questionsArea.innerHTML = '';
      }
      const p = document.createElement('p');
      p.textContent = question;
      questionsArea.appendChild(p);
      questionsArea.scrollTop = questionsArea.scrollHeight;
    }
    if (answer) {
      if (answersArea.innerHTML.includes('AI answers will appear here')) {
        answersArea.innerHTML = '';
      }
      const container = document.createElement('div');
      container.className = 'answer-container';
      const p = document.createElement('p');
      let textToSpeak = null;
      try {
        const parsed = JSON.parse(answer);
        p.textContent = parsed.text;
        textToSpeak = parsed.text;
        if (parsed.audio) {
          const audio = new Audio(`data:audio/mp3;base64,${parsed.audio}`);
          audio.onplay = () => eel.audio_playback_started()();
          audio.onended = () => {
            eel.audio_playback_ended()();
            voiceStopButton.disabled = true;
          };
          const muteIcon = document.createElement('span');
          muteIcon.className = 'mute-icon';
          muteIcon.innerHTML = '🔊';
          muteIcon.title = 'Mute/Unmute';
          muteIcon.onclick = () => {
            audio.muted = !audio.muted;
            muteIcon.innerHTML = audio.muted ? '🔇' : '🔊';
          };
          container.appendChild(muteIcon);
          audio.play().catch(e => console.error('Error playing audio:', e));
        }
      } catch (e) {
        console.error('Error parsing answer:', e);
        p.textContent = answer;
        textToSpeak = answer;
      }
      container.appendChild(p);
      answersArea.appendChild(container);
      answersArea.scrollTop = answersArea.scrollHeight;
      if (ttsEnabled && window.speechSynthesis && textToSpeak) {
        speakText(textToSpeak);
      }
    }
  }

  // Speak text using Web Speech API
  function speakText(text) {
    if (currentUtterance) {
      window.speechSynthesis.cancel();
      currentUtterance = null;
      voiceStopButton.disabled = true;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.pitch = 1;
    utterance.rate = 1;
    utterance.onstart = () => {
      currentUtterance = utterance;
      voiceStopButton.disabled = false;
      eel.audio_playback_started();
    };
    utterance.onend = () => {
      currentUtterance = null;
      voiceStopButton.disabled = true;
      eel.audio_playback_ended();
    };
    window.speechSynthesis.speak(utterance);
  }
});
