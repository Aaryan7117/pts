/**
 * MediKiosk Web — Browser Text-to-Speech (TTS) Reader
 * Provides auditory explain-back across Hindi, Tamil, Telugu, Marathi, and English.
 */

class TTSReader {
  constructor() {
    this.synth = window.speechSynthesis || null;
    this.voices = [];
    this.currentUtterance = null;
    this._speaking = false;
    this._listeners = { start: [], end: [] };

    if (this.synth) {
      this.synth.onvoiceschanged = () => {
        this.voices = this.synth.getVoices();
      };
      this.voices = this.synth.getVoices();
    }
  }

  get isSpeaking() {
    return this._speaking;
  }

  on(event, callback) {
    if (this._listeners[event]) {
      this._listeners[event].push(callback);
    }
  }

  off(event, callback) {
    if (this._listeners[event]) {
      this._listeners[event] = this._listeners[event].filter(cb => cb !== callback);
    }
  }

  _emit(event, data) {
    if (this._listeners[event]) {
      this._listeners[event].forEach(cb => {
        try { cb(data); } catch (err) { console.error('TTS listener error:', err); }
      });
    }
    window.dispatchEvent(new CustomEvent(`medikiosk-tts-${event}`, { detail: data }));
  }

  // Language mapping to standard BCP-47 locale tags
  _mapLocale(langCode) {
    switch (langCode) {
      case 'hi': return 'hi-IN';
      case 'ta': return 'ta-IN';
      case 'te': return 'te-IN';
      case 'mr': return 'mr-IN';
      case 'en': return 'en-IN';
      default:   return 'hi-IN';
    }
  }

  speak(text, lang = 'hi') {
    if (!this.synth || !text) return;

    // Cancel any active utterance
    this.stop();

    const utterance = new SpeechSynthesisUtterance(text);
    const targetLocale = this._mapLocale(lang);
    utterance.lang = targetLocale;
    utterance.rate = 0.95; // Slightly slower for elderly comprehension

    // Pick best matching voice if available
    const matchedVoice = this.voices.find(v => v.lang === targetLocale || v.lang.startsWith(targetLocale.slice(0, 2)));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.onstart = () => {
      this._speaking = true;
      this._emit('start', { text, lang });
    };

    utterance.onend = () => {
      this._speaking = false;
      this.currentUtterance = null;
      this._emit('end', { text, lang });
    };

    utterance.onerror = (e) => {
      this._speaking = false;
      this.currentUtterance = null;
      this._emit('end', { text, lang, error: e });
    };

    utterance.onpause = () => {
      this._speaking = false;
      this._emit('end', { text, lang });
    };

    utterance.onresume = () => {
      this._speaking = true;
      this._emit('start', { text, lang });
    };

    // Store reference on instance to prevent aggressive garbage collection by browser
    this.currentUtterance = utterance;
    this.synth.speak(utterance);
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
    }
    if (this._speaking) {
      this._speaking = false;
      this.currentUtterance = null;
      this._emit('end', { stopped: true });
    }
  }
}

export const tts = new TTSReader();
