/**
 * MediKiosk — Doctor Presentation Scene
 * Manages container layout, transitions, and framing for the Pixar clinical avatar.
 */
import * as THREE from 'three';

export class DoctorScene {
  constructor(container) {
    this.container = container;
    this.scene = new THREE.Scene();
    this.clock = new THREE.Clock();

    // DOM element representing the presentation stage
    this.renderer = {
      domElement: document.createElement('div'),
      dispose: () => {},
      setSize: () => {},
    };

    this.renderer.domElement.className = 'doctor-stage';
    this.renderer.domElement.style.cssText = `
      position: relative;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: visible;
    `;

    container.appendChild(this.renderer.domElement);
  }

  setHeroMode() {
    this.renderer.domElement.style.overflow = 'visible';
    window.dispatchEvent(new CustomEvent('doctor-mode-change', { detail: { isPip: false } }));
  }

  setPipMode() {
    this.renderer.domElement.style.overflow = 'hidden';
    window.dispatchEvent(new CustomEvent('doctor-mode-change', { detail: { isPip: true } }));
  }

  resize() {
    // Stage is automatically responsive via CSS flex
  }

  dispose() {
    if (this.renderer.domElement.parentElement) {
      this.renderer.domElement.parentElement.removeChild(this.renderer.domElement);
    }
  }
}
