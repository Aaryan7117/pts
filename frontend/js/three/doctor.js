/**
 * MediKiosk — Living Pixar Doctor Avatar
 *
 * High-fidelity, studio-grade Pixar clinical doctor avatar built directly
 * from the master artwork reference (doctor2dpic.png).
 *
 * Features:
 * - 4 High-Resolution Poses:
 *     'point'  : Extends right index finger directly down at the central mic button
 *     'talk'   : Open smiling mouth, expressive clinical hand gestures
 *     'listen' : Attentive thoughtful posture, hand to chin, listening closely
 *     'idle'   : Warm, reassuring resting pose holding medical clipboard
 * - Gentle clinical breathing micro-animation (0.3Hz spring curve)
 * - Parallax depth reaction to touch and mouse movement
 * - Directional guiding pulse for illiterate patients toward the microphone
 * - Seamless Picture-in-Picture (PiP) support during intake
 */

export class DoctorCharacter {
  constructor() {
    this.currentState = 'point';
    this.container = null;
    this.domElement = null;
    this.innerElement = null;
    this.layers = {};
    this.guideEl = null;
    this.isPip = false;
    this.isLoaded = false;
    this.breathTime = 0;

    // Available poses matching high-res generated studio renders
    this.poseUrls = {
      point: '/doctor_pointing.jpg',
      talk: '/doctor_speaking.jpg',
      listen: '/doctor_listening.jpg',
      idle: '/doctor_idle.png',
    };

    this._buildDOM();

    window.addEventListener('doctor-mode-change', (e) => {
      this.setPipMode(e.detail.isPip);
    });
  }

  _buildDOM() {
    const root = document.createElement('div');
    root.className = 'pixar-doctor-avatar';
    root.style.cssText = `
      position: relative;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      user-select: none;
      pointer-events: none;
    `;

    // Inner container with breathing animation
    const inner = document.createElement('div');
    inner.className = 'pixar-doctor-inner';
    inner.style.cssText = `
      position: relative;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
    `;
    root.appendChild(inner);

    // Preload & build layers for all 4 poses
    for (const [key, url] of Object.entries(this.poseUrls)) {
      const img = document.createElement('img');
      img.src = url;
      img.alt = `Doctor ${key} pose`;
      img.className = `pixar-doctor-layer pixar-doctor-${key}`;
      img.style.cssText = `
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: contain;
        object-position: center bottom;
        opacity: ${key === 'point' ? '1' : '0'};
        transform: scale(${key === 'point' ? '1' : '0.98'});
        transition: opacity 0.35s ease, transform 0.35s cubic-bezier(0.25, 1, 0.5, 1);
        pointer-events: none;
      `;
      inner.appendChild(img);
      this.layers[key] = img;
    }

    // Directional pointing pulse guide (shows when pointing at mic)
    const guide = document.createElement('div');
    guide.className = 'pixar-doctor-mic-guide';
    guide.innerHTML = `
      <div class="guide-beacon">
        <span class="guide-pulse-ring"></span>
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <polyline points="19 12 12 19 5 12"></polyline>
        </svg>
      </div>
    `;
    guide.style.cssText = `
      position: absolute;
      bottom: -4px;
      left: 44.5%;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      opacity: 1;
      transition: opacity 0.3s ease;
      z-index: 10;
      color: var(--accent, #0891b2);
    `;
    inner.appendChild(guide);
    this.guideEl = guide;

    this.domElement = root;
    this.innerElement = inner;
    this.isLoaded = true;

    // Subtle 3D mouse parallax
    window.addEventListener('mousemove', (e) => this._onMouseMove(e));
  }

  _onMouseMove(e) {
    if (this.isPip || !this.innerElement) return;
    const cx = window.innerWidth / 2;
    const cy = window.innerHeight / 2;
    const dx = (e.clientX - cx) / cx;
    const dy = (e.clientY - cy) / cy;

    // Subtle perspective tilt (1.5 degrees max)
    const rotY = dx * 2.2;
    const rotX = -dy * 1.5;
    this.innerElement.style.transform = `perspective(800px) rotateY(${rotY}deg) rotateX(${rotX}deg)`;
  }

  setState(stateName) {
    // Map states
    let target = stateName;
    if (stateName === 'wave' || stateName === 'nod') {
      target = 'talk';
    } else if (!this.layers[target]) {
      target = 'idle';
    }

    this.currentState = target;

    // Crossfade layers
    for (const [key, el] of Object.entries(this.layers)) {
      if (key === target) {
        el.style.opacity = '1';
        el.style.transform = 'scale(1)';
      } else {
        el.style.opacity = '0';
        el.style.transform = 'scale(0.98)';
      }
    }

    // Toggle pointing guide (only on welcome screen when pointing)
    if (this.guideEl) {
      this.guideEl.style.opacity = (target === 'point' && !this.isPip) ? '1' : '0';
    }
  }

  setPipMode(isPip) {
    this.isPip = isPip;
    if (this.innerElement) {
      if (isPip) {
        // Zoom in slightly to focus on friendly face & stethoscope in PiP corner
        this.innerElement.style.transform = 'scale(1.35) translateY(-5%)';
        if (this.guideEl) this.guideEl.style.display = 'none';
      } else {
        this.innerElement.style.transform = 'scale(1) translateY(0)';
        if (this.guideEl) this.guideEl.style.display = 'flex';
      }
    }
  }

  mount(container) {
    if (!container) return;
    this.container = container;
    container.innerHTML = '';
    container.appendChild(this.domElement);
  }

  addToScene(scene) {
    const stage = document.querySelector('.doctor-stage');
    if (stage && !stage.contains(this.domElement)) {
      stage.appendChild(this.domElement);
    }
  }

  update(delta) {
    // Gentle natural breathing oscillation
    this.breathTime += delta || 0.016;
    if (!this.innerElement || this.isPip) return;

    const breatheY = Math.sin(this.breathTime * 2.2) * 2.5;
    const breatheScale = 1.0 + Math.sin(this.breathTime * 2.2) * 0.005;

    // Combine breathing with gentle float
    this.domElement.style.transform = `translateY(${breatheY}px) scale(${breatheScale})`;
  }
}
