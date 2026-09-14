/**
 * MediKiosk — Audio Utilities
 * MediaRecorder, waveform visualization, base64 audio playback.
 */

/** Play base64-encoded audio (WAV/OGG/MP3) */
export function playAudioBase64(base64, format = 'wav') {
  return new Promise((resolve, reject) => {
    if (!base64) { resolve(); return; }
    const audio = new Audio(`data:audio/${format};base64,${base64}`);

    const notifyStart = () => {
      window.dispatchEvent(new CustomEvent('medikiosk-speech-start'));
    };

    const notifyEnd = () => {
      window.dispatchEvent(new CustomEvent('medikiosk-speech-end'));
    };

    audio.addEventListener('play', notifyStart);
    audio.addEventListener('playing', notifyStart);
    audio.addEventListener('pause', notifyEnd);
    audio.addEventListener('ended', () => {
      notifyEnd();
      resolve();
    });
    audio.addEventListener('error', (err) => {
      notifyEnd();
      reject(err);
    });

    audio.play().catch((err) => {
      notifyEnd();
      reject(err);
    });
  });
}

/** Play a short "ding" notification sound (synthesized) */
export function playDing() {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.frequency.setValueAtTime(880, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.1);
  gain.gain.setValueAtTime(0.3, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
  osc.start(ctx.currentTime);
  osc.stop(ctx.currentTime + 0.4);
  setTimeout(() => ctx.close(), 500);
}

/**
 * Audio Recorder — wraps MediaRecorder for mic capture.
 * Returns a Blob when stopped.
 */
export class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.chunks = [];
    this.stream = null;
    this.analyser = null;
    this.audioCtx = null;
    this.vadInterval = null;
    this.hasSpoken = false;
    this.silenceStartTime = null;
    this.onSpeechEnd = null;
  }

  async start() {
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = this.audioCtx.createMediaStreamSource(this.stream);
    this.analyser = this.audioCtx.createAnalyser();
    this.analyser.fftSize = 256;
    source.connect(this.analyser);

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm';

    this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });
    this.chunks = [];
    this.hasSpoken = false;
    this.silenceStartTime = null;

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data);
    };

    this.mediaRecorder.start(100); // collect every 100ms

    // Start VAD auto-silence monitor
    this._startVAD();
  }

  _startVAD() {
    if (this.vadInterval) clearInterval(this.vadInterval);
    const data = new Uint8Array(this.analyser.frequencyBinCount);

    this.vadInterval = setInterval(() => {
      if (!this.analyser || !this.mediaRecorder || this.mediaRecorder.state !== 'recording') return;

      this.analyser.getByteFrequencyData(data);
      let sum = 0;
      for (let i = 0; i < data.length; i++) sum += data[i];
      const avg = sum / data.length;

      // Threshold: speech detected
      if (avg > 16) {
        this.hasSpoken = true;
        this.silenceStartTime = null;
      } else if (this.hasSpoken) {
        // Patient was speaking and is now silent
        if (!this.silenceStartTime) {
          this.silenceStartTime = performance.now();
        } else if (performance.now() - this.silenceStartTime > 1400) {
          // 1.4 seconds of continuous silence after speaking → auto stop!
          clearInterval(this.vadInterval);
          this.vadInterval = null;
          if (this.onSpeechEnd) {
            this.onSpeechEnd();
          }
        }
      }
    }, 100);
  }

  stop() {
    if (this.vadInterval) {
      clearInterval(this.vadInterval);
      this.vadInterval = null;
    }
    return new Promise((resolve) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        resolve(null);
        return;
      }
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: this.mediaRecorder.mimeType });
        this.cleanup();
        resolve(blob);
      };
      this.mediaRecorder.stop();
    });
  }

  cleanup() {
    if (this.vadInterval) {
      clearInterval(this.vadInterval);
      this.vadInterval = null;
    }
    if (this.stream) {
      this.stream.getTracks().forEach(t => t.stop());
      this.stream = null;
    }
    if (this.audioCtx && this.audioCtx.state !== 'closed') {
      this.audioCtx.close();
    }
    this.analyser = null;
  }

  /** Get frequency data for waveform visualization */
  getFrequencyData() {
    if (!this.analyser) return new Uint8Array(0);
    const data = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(data);
    return data;
  }
}

/**
 * Waveform Visualizer — draws frequency bars on a canvas.
 */
export class WaveformVisualizer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.animationId = null;
    this.recorder = null;
  }

  start(recorder) {
    this.recorder = recorder;
    this.resize();
    this.draw();
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    this.clear();
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  clear() {
    const w = this.canvas.width / window.devicePixelRatio;
    const h = this.canvas.height / window.devicePixelRatio;
    this.ctx.clearRect(0, 0, w, h);
  }

  draw() {
    const w = this.canvas.width / window.devicePixelRatio;
    const h = this.canvas.height / window.devicePixelRatio;
    this.ctx.clearRect(0, 0, w, h);

    if (!this.recorder) return;
    const data = this.recorder.getFrequencyData();

    const barCount = Math.min(data.length, 64);
    const barWidth = w / barCount - 2;
    const accent = getComputedStyle(document.documentElement)
      .getPropertyValue('--accent').trim() || '#0891b2';

    for (let i = 0; i < barCount; i++) {
      const val = data[i] / 255;
      const barHeight = Math.max(2, val * h * 0.9);
      const x = i * (barWidth + 2);
      const y = (h - barHeight) / 2;

      this.ctx.fillStyle = accent;
      this.ctx.globalAlpha = 0.3 + val * 0.7;
      this.ctx.beginPath();
      this.ctx.roundRect(x, y, barWidth, barHeight, 2);
      this.ctx.fill();
    }

    this.ctx.globalAlpha = 1;
    this.animationId = requestAnimationFrame(() => this.draw());
  }
}
