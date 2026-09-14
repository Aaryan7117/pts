/**
 * MediKiosk Web — Interactive AI Doctor Avatar
 * Renders a warm, reassuring clinical physician avatar for rural/elderly OPD patients.
 * Fully self-contained on Canvas/SVG with organic breathing and listening animations.
 */

export class DoctorAvatar {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.canvas = null;
    this.ctx = null;
    this.animId = null;
    this.isSpeaking = false;
    this.isListening = false;
    this.breathCycle = 0;
    this.blinkTimer = 0;
    this.isBlinking = false;
  }

  mount() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div style="display:flex; flex-direction:column; align-items:center; position:relative;">
        <canvas id="doctorAvatarCanvas" width="280" height="300" style="width:240px; height:260px; filter:drop-shadow(0 12px 24px rgba(16,35,62,0.12));"></canvas>
        <div id="avatarStatusPill" class="badge badge-teal" style="margin-top:-8px; z-index:2;">
          ● AI Clinical Attendant Ready
        </div>
      </div>
    `;

    this.canvas = document.getElementById('doctorAvatarCanvas');
    if (this.canvas) {
      this.ctx = this.canvas.getContext('2d');
      this._startLoop();
    }
  }

  setSpeaking(speaking) {
    this.isSpeaking = speaking;
    const pill = document.getElementById('avatarStatusPill');
    if (pill) {
      pill.className = speaking ? 'badge badge-blue' : 'badge badge-teal';
      pill.innerHTML = speaking ? '🔊 AI Attendant Speaking...' : '● AI Clinical Attendant Ready';
    }
  }

  setListening(listening) {
    this.isListening = listening;
    const pill = document.getElementById('avatarStatusPill');
    if (pill) {
      pill.className = listening ? 'badge badge-red' : 'badge badge-teal';
      pill.innerHTML = listening ? '🎙 Listening to Your Voice...' : '● AI Clinical Attendant Ready';
    }
  }

  _startLoop() {
    const render = () => {
      this._draw();
      this.animId = requestAnimationFrame(render);
    };
    this.animId = requestAnimationFrame(render);
  }

  _draw() {
    if (!this.ctx || !this.canvas) return;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.breathCycle += 0.04;
    const breathOffset = Math.sin(this.breathCycle) * 3;

    // Blinking logic
    this.blinkTimer += 1;
    if (this.blinkTimer > 180) {
      this.isBlinking = true;
      if (this.blinkTimer > 192) {
        this.isBlinking = false;
        this.blinkTimer = 0;
      }
    }

    const centerX = 140;
    const headY = 95 + breathOffset;

    // 1. Soft Circular Halo Glow
    const haloGrad = ctx.createRadialGradient(centerX, headY + 30, 40, centerX, headY + 30, 130);
    haloGrad.addColorStop(0, 'rgba(234, 243, 255, 0.9)');
    haloGrad.addColorStop(1, 'rgba(234, 243, 255, 0)');
    ctx.fillStyle = haloGrad;
    ctx.beginPath();
    ctx.arc(centerX, headY + 30, 130, 0, Math.PI * 2);
    ctx.fill();

    // 2. Doctor Shoulders & White Coat
    ctx.fillStyle = '#FFFFFF';
    ctx.strokeStyle = '#DCE5F0';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(centerX - 95, 290);
    ctx.bezierCurveTo(centerX - 80, 200 + breathOffset, centerX - 40, 180 + breathOffset, centerX, 185 + breathOffset);
    ctx.bezierCurveTo(centerX + 40, 180 + breathOffset, centerX + 80, 200 + breathOffset, centerX + 95, 290);
    ctx.fill();
    ctx.stroke();

    // 3. Inner Scrub Shirt (Clinical Teal #0B8F87)
    ctx.fillStyle = '#0B8F87';
    ctx.beginPath();
    ctx.moveTo(centerX - 32, 195 + breathOffset);
    ctx.lineTo(centerX + 32, 195 + breathOffset);
    ctx.lineTo(centerX, 250 + breathOffset);
    ctx.closePath();
    ctx.fill();

    // 4. Stethoscope
    ctx.strokeStyle = '#10233E';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(centerX, 205 + breathOffset, 42, 0.2 * Math.PI, 0.8 * Math.PI);
    ctx.stroke();

    // Stethoscope Bell
    ctx.fillStyle = '#CBD5E1';
    ctx.beginPath();
    ctx.arc(centerX, 252 + breathOffset, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // 5. Neck
    ctx.fillStyle = '#F8D7B8';
    ctx.fillRect(centerX - 16, headY + 45, 32, 35);

    // 6. Head
    ctx.fillStyle = '#F8D7B8';
    ctx.beginPath();
    ctx.ellipse(centerX, headY, 52, 60, 0, 0, Math.PI * 2);
    ctx.fill();

    // 7. Hair (Professional Styled Hair)
    ctx.fillStyle = '#1E293B';
    ctx.beginPath();
    ctx.arc(centerX, headY - 8, 55, Math.PI * 0.8, Math.PI * 2.2);
    ctx.fill();

    // 8. Eyes (with blinking)
    ctx.fillStyle = '#0F172A';
    if (this.isBlinking) {
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(centerX - 24, headY);
      ctx.lineTo(centerX - 10, headY);
      ctx.moveTo(centerX + 10, headY);
      ctx.lineTo(centerX + 24, headY);
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.arc(centerX - 17, headY, 5, 0, Math.PI * 2);
      ctx.arc(centerX + 17, headY, 5, 0, Math.PI * 2);
      ctx.fill();

      // Eye glimmer
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath();
      ctx.arc(centerX - 19, headY - 2, 2, 0, Math.PI * 2);
      ctx.arc(centerX + 15, headY - 2, 2, 0, Math.PI * 2);
      ctx.fill();
    }

    // 9. Welcoming Smile / Speaking Mouth
    ctx.strokeStyle = '#991B1B';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    if (this.isSpeaking) {
      const mouthOpen = 4 + Math.sin(this.breathCycle * 5) * 4;
      ctx.fillStyle = '#991B1B';
      ctx.ellipse(centerX, headY + 28, 9, mouthOpen, 0, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.arc(centerX, headY + 22, 12, 0.15 * Math.PI, 0.85 * Math.PI);
      ctx.stroke();
    }
  }

  destroy() {
    if (this.animId) {
      cancelAnimationFrame(this.animId);
      this.animId = null;
    }
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}
