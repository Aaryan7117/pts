/**
 * MediKiosk Web — Dynamic 9-Bar Audio Waveform Visualizer
 * Reacts to microphone input or generates organic speech frequency animations.
 */

export class AudioVisualizer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext('2d') : null;
    this.animId = null;
    this.analyser = null;
    this.dataArray = null;
    this.numBars = 9;
    this.isRecording = false;
  }

  attachStream(stream) {
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      const audioCtx = new AudioContextClass();
      const source = audioCtx.createMediaStreamSource(stream);
      this.analyser = audioCtx.createAnalyser();
      this.analyser.fftSize = 64;
      source.connect(this.analyser);
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    } catch (e) {
      console.warn('Could not attach microphone to WebAudio analyser:', e);
    }
  }

  start() {
    this.isRecording = true;
    this._render();
  }

  stop() {
    this.isRecording = false;
    if (this.animId) {
      cancelAnimationFrame(this.animId);
      this.animId = null;
    }
    this._clear();
  }

  _clear() {
    if (!this.ctx || !this.canvas) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  _render() {
    if (!this.isRecording || !this.ctx || !this.canvas) return;

    const width = this.canvas.width;
    const height = this.canvas.height;
    this.ctx.clearRect(0, 0, width, height);

    let frequencies = [];
    if (this.analyser && this.dataArray) {
      this.analyser.getByteFrequencyData(this.dataArray);
      // Sample 9 evenly distributed frequency bins
      const step = Math.floor(this.dataArray.length / this.numBars);
      for (let i = 0; i < this.numBars; i++) {
        frequencies.push(this.dataArray[i * step] / 255);
      }
    } else {
      // Organic speech simulation
      const time = Date.now() / 150;
      for (let i = 0; i < this.numBars; i++) {
        const val = 0.2 + 0.6 * (Math.sin(time + i * 0.7) * 0.5 + 0.5) * (Math.sin(time * 0.4 + i) * 0.5 + 0.5);
        frequencies.push(val);
      }
    }

    const barWidth = 6;
    const barGap = 8;
    const totalWidth = this.numBars * barWidth + (this.numBars - 1) * barGap;
    const startX = (width - totalWidth) / 2;

    frequencies.forEach((normHeight, i) => {
      const barHeight = Math.max(6, normHeight * (height - 8));
      const x = startX + i * (barWidth + barGap);
      const y = (height - barHeight) / 2;

      // Color gradient: Royal Blue to Sky Blue
      const grad = this.ctx.createLinearGradient(0, y, 0, y + barHeight);
      grad.addColorStop(0, '#5392F8');
      grad.addColorStop(1, '#1667D9');

      this.ctx.fillStyle = grad;
      this.ctx.beginPath();
      this.ctx.roundRect(x, y, barWidth, barHeight, 3);
      this.ctx.fill();
    });

    this.animId = requestAnimationFrame(() => this._render());
  }
}
