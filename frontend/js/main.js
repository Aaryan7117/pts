/**
 * MediKiosk Web — Main Application Bootstrap
 */

import { Router } from './router.js';
import { store } from './store.js';

document.addEventListener('DOMContentLoaded', () => {
  const appContainer = document.getElementById('app');
  if (!appContainer) {
    console.error('#app element not found');
    return;
  }

  // Initialize Router
  const router = new Router(appContainer);
  router.start();

  // Toast container manager
  store.subscribe(state => {
    const toastBox = document.getElementById('toastContainer');
    if (toastBox) {
      toastBox.innerHTML = state.ui.toasts.map(t => `
        <div class="toast">
          <span>${t.type === 'error' ? '❌' : (t.type === 'success' ? '✓' : 'ℹ')}</span>
          <span>${t.message}</span>
        </div>
      `).join('');
    }
  });

  console.log('MediKiosk AI Web Application initialized. RetinopathyScan Light Medical Standard.');
});
