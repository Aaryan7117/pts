/**
 * MediKiosk Web — Browser Text-to-Speech (TTS) Reader
 * Provides auditory explain-back across Hindi, Tamil, Telugu, Marathi, and English.
 */

class TTSReader {
  constructor() {
    this.synth = window.speechSynthesis || null;
    this.voices = [];
    if (this.synth) {
      this.synth.onvoiceschanged = () => {
        this.voices = this.synth.getVoices();
      };
      this.voices = this.synth.getVoices();
    }
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
    this.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const targetLocale = this._mapLocale(lang);
    utterance.lang = targetLocale;
    utterance.rate = 0.95; // Slightly slower for elderly comprehension

    // Pick best matching voice if available
    const matchedVoice = this.voices.find(v => v.lang === targetLocale || v.lang.startsWith(targetLocale.slice(0, 2)));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    this.synth.speak(utterance);
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
    }
  }
}

export const tts = new TTSReader();
