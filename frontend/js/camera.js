/**
 * MediKiosk — Camera Utilities
 * getUserMedia for prescription photo capture.
 */

export class CameraCapture {
  constructor(videoElement) {
    this.video = videoElement;
    this.stream = null;
    if (this.video) {
      this.video.muted = true;
      this.video.playsInline = true;
      this.video.setAttribute('playsinline', '');
      this.video.setAttribute('muted', '');
    }
  }

  async start() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } }
      });
      this.video.srcObject = this.stream;
      await this.video.play().catch(e => console.warn('Camera play notice:', e));
      return true;
    } catch (err) {
      console.warn('Environment camera failed, falling back to user camera:', err);
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: true
        });
        this.video.srcObject = this.stream;
        await this.video.play().catch(e => console.warn('Camera play notice:', e));
        return true;
      } catch (err2) {
        console.error('All camera access failed:', err2);
        throw err2;
      }
    }
  }

  /** Capture a still frame as a JPEG Blob */
  capture() {
    return new Promise((resolve, reject) => {
      if (!this.video || !this.video.videoWidth) {
        reject(new Error('Camera stream is not ready or has zero dimensions.'));
        return;
      }
      const canvas = document.createElement('canvas');
      canvas.width = this.video.videoWidth;
      canvas.height = this.video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(this.video, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) resolve(blob);
        else reject(new Error('Failed to create image blob'));
      }, 'image/jpeg', 0.92);
    });
  }

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(t => t.stop());
      this.stream = null;
    }
    if (this.video) {
      this.video.srcObject = null;
    }
  }
}
