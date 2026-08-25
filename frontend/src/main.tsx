import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { registerSW } from 'virtual:pwa-register';

console.log('main.tsx loaded');

// Register service worker
registerSW({ immediate: true });

const root = document.getElementById('root');
console.log('Root element:', root);

if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
  console.log('App rendered to root');
} else {
  console.error('Root element not found!');
}
