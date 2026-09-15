/**
 * MediKiosk Web — Photorealistic 2D Frame-by-Frame Doctor Avatar
 *
 * Implements smooth 25 FPS clinical physician animation driven by high-fidelity
 * 6-second video sequences (150 idle frames and 150 speaking frames).
 * Synchronized with browser TTS and audio playback lifecycle.
 */

import { tts } from '../audio/tts-reader.js';

const AVATAR_I18N = {
  ready: {
    en: '● AI Clinical Attendant Ready',
    hi: '● एआई चिकित्सक तैयार',
    ta: '● AI மருத்துவர் தயார்',
    te: '● AI వైద్య సహాయకుడు సిద్ధం',
    mr: '● AI वैद्यकीय सहाय्यक सज्ज'
  },
  listening: {
    en: '🎙 Listening to Your Voice...',
    hi: '🎙 आपकी आवाज़ सुन रहे हैं...',
    ta: '🎙 உங்கள் குரலைக் கேட்கிறது...',
    te: '🎙 మీ వాయిస్ వింటున్నారు...',
    mr: '🎙 तुमचा आवाज ऐकत आहे...'
  },
  speaking: {
    en: '🔊 AI Attendant Speaking...',
    hi: '🔊 डॉक्टर बोल रहे हैं...',
    ta: '🔊 மருத்துவர் பேசுகிறார்...',
    te: '🔊 డాక్టర్ మాట్లాడుతున్నారు...',
    mr: '🔊 डॉक्टर बोलत आहेत...'
  },
  pointing: {
    en: '👉 Tap Microphone on Right',
    hi: '👉 दाईं ओर माइक दबाएं',
    ta: '👉 வலதுபுறம் மைக்-ஐ அழுத்தவும்',
    te: '👉 కుడివైపు మైక్ నొక్కండి',
    mr: '👉 उजवीकडील माइक दाबा'
  },
  loading: {
    en: 'Loading AI Physician...',
    hi: 'एआई चिकित्सक लोड हो रहा है...',
    ta: 'AI மருத்துவர் ஏற்றப்படுகிறார்...',
    te: 'AI వైద్యుడు లోడ్ అవుతున్నాడు...',
    mr: 'AI वैद्यकीय सहाय्यक लोड होत आहे...'
  }
};

export class DoctorAvatar {
  /**
   * @param {string|HTMLElement} container - Container ID or HTMLElement
   * @param {Object} options - Configuration options
   */
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.getElementById(container) : container;
    this.options = Object.assign({
      fps: 25, // 150 frames / 6.0 seconds = 25 FPS
      totalFrames: 150,
      idlePath: '/avatar/idle',
      speakingPath: '/avatar/speaking',
      pointingPath: '/avatar/pointing',
      autoSyncAudio: true,
      language: options.language || 'hi',
    }, options);

    this.state = 'idle'; // 'idle' | 'pointing' | 'speaking'
    this.canvas = null;
    this.ctx = null;
    this.animId = null;

    // Frame storage
    this.idleFrames = new Array(this.options.totalFrames);
    this.speakingFrames = new Array(this.options.totalFrames);
    this.pointingFrames = new Array(this.options.totalFrames);
    this.idleLoadedCount = 0;
    this.speakingLoadedCount = 0;
    this.pointingLoadedCount = 0;
    this.pointingCompleteCallback = null;
    this.isPreloaded = false;

    // Playback state
    this.currentFrameIdx = 0;
    this.lastFrameTime = 0;
    this.frameDuration = 1000 / this.options.fps; // 40.0 ms

    // Event handlers bound to this
    this._onTtsStart = this._onTtsStart.bind(this);
    this._onTtsEnd = this._onTtsEnd.bind(this);
    this._onSpeechStart = this._onSpeechStart.bind(this);
    this._onSpeechEnd = this._onSpeechEnd.bind(this);
    this._onMediaPlay = this._onMediaPlay.bind(this);
    this._onMediaPause = this._onMediaPause.bind(this);
    this._onMediaEnded = this._onMediaEnded.bind(this);
  }

  /**
   * Mount the avatar into the container element and start the animation loop.
   */
  mount() {
    if (!this.container) {
      console.warn('DoctorAvatar: target container not found');
      return;
    }

    this.container.innerHTML = `
      <div class="doctor-avatar-wrapper" style="display:flex; flex-direction:column; align-items:center; position:relative; width:100%; max-width:440px; margin:0 auto;">
        <div class="doctor-avatar-frame" style="position:relative; width:100%; aspect-ratio:16/9; border-radius:18px; overflow:hidden; box-shadow:0 16px 36px rgba(16,35,62,0.14), 0 0 0 1px rgba(2,132,199,0.15); background:#0f172a;">
          <canvas id="doctorAvatarCanvas" width="960" height="540" style="width:100%; height:100%; display:block; object-fit:contain;"></canvas>
          <div id="avatarLoadingOverlay" style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; background:#0f172a; transition:opacity 0.3s ease; pointer-events:none;">
            <div style="color:var(--brand-primary, #0284c7); font-size:13px; font-weight:600; display:flex; align-items:center; gap:8px;">
              <span class="pulse-dot" style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#0284c7;"></span>
              ${this._getAvatarText('loading')}
            </div>
          </div>
        </div>
        <div id="avatarStatusPill" class="badge badge-teal" style="margin-top:12px; z-index:2; font-weight:600; font-size:13px; padding:6px 16px; box-shadow:0 2px 8px rgba(0,0,0,0.06); transition:all 0.2s ease;">
          ${this._getAvatarText('ready')}
        </div>
      </div>
    `;

    this.canvas = this.container.querySelector('#doctorAvatarCanvas');
    if (this.canvas) {
      this.ctx = this.canvas.getContext('2d', { alpha: false });
    }

    // Preload frames and begin rendering
    this._preloadFrames();
    this._attachAudioListeners();
    this._startLoop();
  }

  _getAvatarText(key) {
    const lang = this.options.language || 'hi';
    return AVATAR_I18N[key]?.[lang] || AVATAR_I18N[key]?.en || '';
  }

  setLanguage(lang) {
    this.options.language = lang;
    this._updateStatusPill();
  }

  /**
   * Set explicit avatar state ('idle', 'pointing', or 'speaking')
   * @param {'idle'|'pointing'|'speaking'} nextState
   * @param {Function} [callback] - Optional completion callback for non-looping states (e.g. pointing)
   */
  setState(nextState, callback) {
    if (nextState !== 'idle' && nextState !== 'speaking' && nextState !== 'pointing') return;
    if (this.state === nextState && nextState !== 'pointing') return;

    this.state = nextState;

    // Reset frame index on speaking or pointing start for natural onset
    if (nextState === 'speaking' || nextState === 'pointing') {
      this.currentFrameIdx = 0;
    }

    if (nextState === 'pointing') {
      this.pointingCompleteCallback = callback || null;
    } else {
      this.pointingCompleteCallback = null;
    }

    this._updateStatusPill();
  }

  /**
   * Play the pointing onboarding animation once, then transition back to idle.
   * @param {Function} [onComplete] - Callback executed when pointing finishes
   */
  playPointingOnce(onComplete) {
    this.currentFrameIdx = 0;
    this.pointingCompleteCallback = onComplete || null;
    this.state = 'pointing';
    this._updateStatusPill();
  }

  /**
   * Compatibility method
   * @param {boolean} speaking
   */
  setSpeaking(speaking) {
    this.setState(speaking ? 'speaking' : 'idle');
  }

  /**
   * Compatibility method
   * @param {boolean} listening
   */
  setListening(listening) {
    // Listening is idle state (attentive listening posture, seated calmly)
    this.state = 'idle';
    this.pointingCompleteCallback = null;
    if (listening) {
      const pill = this.container ? this.container.querySelector('#avatarStatusPill') : null;
      if (pill) {
        pill.className = 'badge badge-red';
        pill.innerHTML = this._getAvatarText('listening');
      }
    } else {
      this._updateStatusPill();
    }
  }

  _updateStatusPill() {
    const pill = this.container ? this.container.querySelector('#avatarStatusPill') : null;
    if (!pill) return;

    if (this.state === 'speaking') {
      pill.className = 'badge badge-blue';
      pill.innerHTML = this._getAvatarText('speaking');
    } else if (this.state === 'pointing') {
      pill.className = 'badge badge-amber';
      pill.innerHTML = this._getAvatarText('pointing');
    } else {
      pill.className = 'badge badge-teal';
      pill.innerHTML = this._getAvatarText('ready');
    }
  }

  _attachAudioListeners() {
    if (!this.options.autoSyncAudio) return;

    // Global custom events from TTSReader & Audio utility
    window.addEventListener('medikiosk-tts-start', this._onTtsStart);
    window.addEventListener('medikiosk-tts-end', this._onTtsEnd);
    window.addEventListener('medikiosk-speech-start', this._onSpeechStart);
    window.addEventListener('medikiosk-speech-end', this._onSpeechEnd);

    // Capture standard audio element events from any Audio/HTMLMediaElement in the DOM
    window.addEventListener('play', this._onMediaPlay, true);
    window.addEventListener('playing', this._onMediaPlay, true);
    window.addEventListener('pause', this._onMediaPause, true);
    window.addEventListener('ended', this._onMediaEnded, true);
    window.addEventListener('error', this._onMediaEnded, true);

    // Also check if TTS is currently active
    if (tts && tts.isSpeaking) {
      this.setState('speaking');
    }
  }

  _detachAudioListeners() {
    window.removeEventListener('medikiosk-tts-start', this._onTtsStart);
    window.removeEventListener('medikiosk-tts-end', this._onTtsEnd);
    window.removeEventListener('medikiosk-speech-start', this._onSpeechStart);
    window.removeEventListener('medikiosk-speech-end', this._onSpeechEnd);

    window.removeEventListener('play', this._onMediaPlay, true);
    window.removeEventListener('playing', this._onMediaPlay, true);
    window.removeEventListener('pause', this._onMediaPause, true);
    window.removeEventListener('ended', this._onMediaEnded, true);
    window.removeEventListener('error', this._onMediaEnded, true);
  }

  _onMediaPlay(e) {
    if (e.target && (e.target instanceof HTMLMediaElement || e.target.tagName === 'AUDIO')) {
      this.setState('speaking');
    }
  }

  _onMediaPause(e) {
    if (e.target && (e.target instanceof HTMLMediaElement || e.target.tagName === 'AUDIO')) {
      if (tts && tts.isSpeaking) return;
      this.setState('idle');
    }
  }

  _onMediaEnded(e) {
    if (e.target && (e.target instanceof HTMLMediaElement || e.target.tagName === 'AUDIO')) {
      if (tts && tts.isSpeaking) return;
      this.setState('idle');
    }
  }

  _onTtsStart() {
    this.setState('speaking');
  }

  _onTtsEnd() {
    this.setState('idle');
  }

  _onSpeechStart() {
    this.setState('speaking');
  }

  _onSpeechEnd() {
    this.setState('idle');
  }

  /**
   * Intelligent asynchronous preloader:
   * First loads initial idle frame to display immediately, then idle sequence, then speaking sequence.
   */
  _preloadFrames() {
    const total = this.options.totalFrames;
    const pad = (num) => String(num).padStart(3, '0');

    const loadImage = (basePath, index, onLoaded) => {
      const p = pad(index + 1);
      const img = new Image();
      let hasTriedJpg = false;
      img.onload = () => {
        if (onLoaded) onLoaded(img);
      };
      img.onerror = () => {
        if (!hasTriedJpg) {
          hasTriedJpg = true;
          img.src = `${basePath}/ezgif-frame-${p}.jpg`;
        }
      };
      // Primary format: webp, fallback to ezgif-frame jpg
      img.src = `${basePath}/frame-${p}.webp`;
      return img;
    };

    // 1. Load first idle frame with high priority for instant first paint
    const firstIdle = loadImage(this.options.idlePath, 0, (img) => {
      this.idleFrames[0] = img;
      this.idleLoadedCount++;
      this._drawFrame(img);
      const overlay = this.container ? this.container.querySelector('#avatarLoadingOverlay') : null;
      if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300);
      }
    });
    this.idleFrames[0] = firstIdle;

    // 2. Load the remaining idle frames
    for (let i = 1; i < total; i++) {
      this.idleFrames[i] = loadImage(this.options.idlePath, i, () => {
        this.idleLoadedCount++;
      });
    }

    // 3. Load pointing frames concurrently
    for (let i = 0; i < total; i++) {
      this.pointingFrames[i] = loadImage(this.options.pointingPath, i, () => {
        this.pointingLoadedCount++;
      });
    }

    // 4. Load speaking frames concurrently
    for (let i = 0; i < total; i++) {
      this.speakingFrames[i] = loadImage(this.options.speakingPath, i, () => {
        this.speakingLoadedCount++;
      });
    }
  }

  _startLoop() {
    this.lastFrameTime = performance.now();

    const loop = (timestamp) => {
      this.animId = requestAnimationFrame(loop);

      const elapsed = timestamp - this.lastFrameTime;
      if (elapsed >= this.frameDuration) {
        const framesToAdvance = Math.floor(elapsed / this.frameDuration);
        this.lastFrameTime = timestamp - (elapsed % this.frameDuration);

        // Advance frames based on actual elapsed time (drop frames smoothly if CPU is slow)
        const total = this.options.totalFrames;

        if (this.state === 'pointing') {
          const nextIdx = this.currentFrameIdx + framesToAdvance;
          if (nextIdx >= total) {
            // Pointing animation complete! Transition back to IDLE
            this.state = 'idle';
            this.currentFrameIdx = 0;
            this._updateStatusPill();
            const cb = this.pointingCompleteCallback;
            this.pointingCompleteCallback = null;
            if (typeof cb === 'function') {
              try {
                cb();
              } catch (err) {
                console.error('Pointing callback error:', err);
              }
            }
          } else {
            this.currentFrameIdx = nextIdx;
          }
        } else {
          // IDLE and SPEAKING loop seamlessly
          this.currentFrameIdx = (this.currentFrameIdx + framesToAdvance) % total;
        }

        this._render();
      }
    };

    this.animId = requestAnimationFrame(loop);
  }

  _render() {
    if (!this.ctx || !this.canvas) return;

    let activeFrames;
    if (this.state === 'speaking') {
      activeFrames = this.speakingFrames;
    } else if (this.state === 'pointing') {
      activeFrames = this.pointingFrames;
    } else {
      activeFrames = this.idleFrames;
    }

    const fallbackFrames = this.idleFrames;
    const total = this.options.totalFrames;

    // Get current frame or fallback to first frame if still loading
    const currentImg = activeFrames[this.currentFrameIdx] || fallbackFrames[0];
    if (!currentImg || !currentImg.complete) return;

    // Seamless loop smoothing:
    // When reaching the last 2 frames (148, 149), perform a gentle 2-frame crossfade
    // into frame 0 to eliminate any visible jump between repetitions (for looping states).
    const isLoopBoundary = this.currentFrameIdx >= total - 2 && this.state !== 'pointing';
    const targetFirstImg = activeFrames[0] || fallbackFrames[0];

    if (isLoopBoundary && targetFirstImg && targetFirstImg.complete) {
      const crossfadeAlpha = (this.currentFrameIdx - (total - 3)) / 3; // 0.33, 0.66
      this.ctx.drawImage(currentImg, 0, 0, this.canvas.width, this.canvas.height);
      this.ctx.save();
      this.ctx.globalAlpha = crossfadeAlpha;
      this.ctx.drawImage(targetFirstImg, 0, 0, this.canvas.width, this.canvas.height);
      this.ctx.restore();
    } else {
      this.ctx.drawImage(currentImg, 0, 0, this.canvas.width, this.canvas.height);
    }
  }

  _drawFrame(img) {
    if (!this.ctx || !this.canvas || !img || !img.complete) return;
    this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
  }

  /**
   * Stop animations, detach audio events, and clean up container.
   */
  destroy() {
    if (this.animId) {
      cancelAnimationFrame(this.animId);
      this.animId = null;
    }

    this._detachAudioListeners();

    if (this.canvas) {
      this.canvas.width = 1;
      this.canvas.height = 1;
      this.canvas = null;
      this.ctx = null;
    }

    if (this.container) {
      this.container.innerHTML = '';
    }

    // Clear frame references to assist garbage collection
    this.idleFrames.length = 0;
    this.speakingFrames.length = 0;
    this.pointingFrames.length = 0;
  }
}
