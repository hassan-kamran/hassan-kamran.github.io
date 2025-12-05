/**
 * ULTRA EFFECTS - Next Level Interactions
 * Cursor spotlight, text scramble, magnetic buttons, and more
 */

(function() {
  'use strict';

  // ===========================================
  // CURSOR SPOTLIGHT EFFECT
  // ===========================================
  class CursorSpotlight {
    constructor() {
      this.spotlight = null;
      this.mouseX = 0;
      this.mouseY = 0;
      this.currentX = 0;
      this.currentY = 0;
      this.init();
    }

    init() {
      // Create spotlight element
      this.spotlight = document.createElement('div');
      this.spotlight.className = 'cursor-spotlight';
      document.body.appendChild(this.spotlight);

      // Track mouse
      document.addEventListener('mousemove', (e) => {
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;
      });

      // Smooth animation loop
      this.animate();
    }

    animate() {
      // Smooth lerp
      this.currentX += (this.mouseX - this.currentX) * 0.1;
      this.currentY += (this.mouseY - this.currentY) * 0.1;

      this.spotlight.style.left = this.currentX + 'px';
      this.spotlight.style.top = this.currentY + 'px';

      requestAnimationFrame(() => this.animate());
    }
  }

  // ===========================================
  // TEXT SCRAMBLE EFFECT
  // ===========================================
  class TextScramble {
    constructor(el) {
      this.el = el;
      this.chars = '!<>-_\\/[]{}—=+*^?#________';
      this.update = this.update.bind(this);
    }

    setText(newText) {
      const oldText = this.el.innerText;
      const length = Math.max(oldText.length, newText.length);
      const promise = new Promise((resolve) => this.resolve = resolve);
      this.queue = [];

      for (let i = 0; i < length; i++) {
        const from = oldText[i] || '';
        const to = newText[i] || '';
        const start = Math.floor(Math.random() * 40);
        const end = start + Math.floor(Math.random() * 40);
        this.queue.push({ from, to, start, end });
      }

      cancelAnimationFrame(this.frameRequest);
      this.frame = 0;
      this.update();
      return promise;
    }

    update() {
      let output = '';
      let complete = 0;

      for (let i = 0, n = this.queue.length; i < n; i++) {
        let { from, to, start, end, char } = this.queue[i];

        if (this.frame >= end) {
          complete++;
          output += to;
        } else if (this.frame >= start) {
          if (!char || Math.random() < 0.28) {
            char = this.randomChar();
            this.queue[i].char = char;
          }
          output += `<span class="scramble-char">${char}</span>`;
        } else {
          output += from;
        }
      }

      this.el.innerHTML = output;

      if (complete === this.queue.length) {
        this.resolve();
      } else {
        this.frameRequest = requestAnimationFrame(this.update);
        this.frame++;
      }
    }

    randomChar() {
      return this.chars[Math.floor(Math.random() * this.chars.length)];
    }
  }

  // ===========================================
  // MAGNETIC BUTTON EFFECT (Enhanced)
  // ===========================================
  class MagneticElement {
    constructor(el) {
      this.el = el;
      this.boundingRect = null;
      this.magnetStrength = parseFloat(el.dataset.magnetStrength) || 0.3;
      this.init();
    }

    init() {
      this.el.addEventListener('mouseenter', () => this.onEnter());
      this.el.addEventListener('mousemove', (e) => this.onMove(e));
      this.el.addEventListener('mouseleave', () => this.onLeave());
    }

    onEnter() {
      this.boundingRect = this.el.getBoundingClientRect();
    }

    onMove(e) {
      if (!this.boundingRect) return;

      const x = e.clientX - this.boundingRect.left - this.boundingRect.width / 2;
      const y = e.clientY - this.boundingRect.top - this.boundingRect.height / 2;

      this.el.style.transform = `translate(${x * this.magnetStrength}px, ${y * this.magnetStrength}px)`;
    }

    onLeave() {
      this.el.style.transform = 'translate(0, 0)';
      this.boundingRect = null;
    }
  }

  // ===========================================
  // CARD SPOTLIGHT EFFECT
  // ===========================================
  class CardSpotlight {
    constructor(el) {
      this.el = el;
      this.spotlight = null;
      this.init();
    }

    init() {
      // Create spotlight overlay
      this.spotlight = document.createElement('div');
      this.spotlight.className = 'card-spotlight-overlay';
      this.el.style.position = 'relative';
      this.el.style.overflow = 'hidden';
      this.el.appendChild(this.spotlight);

      this.el.addEventListener('mousemove', (e) => this.onMove(e));
      this.el.addEventListener('mouseleave', () => this.onLeave());
    }

    onMove(e) {
      const rect = this.el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      this.spotlight.style.opacity = '1';
      this.spotlight.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(168, 85, 247, 0.15) 0%, transparent 50%)`;
    }

    onLeave() {
      this.spotlight.style.opacity = '0';
    }
  }

  // ===========================================
  // SCROLL PROGRESS INDICATOR
  // ===========================================
  class ScrollProgress {
    constructor() {
      this.progressBar = null;
      this.init();
    }

    init() {
      this.progressBar = document.createElement('div');
      this.progressBar.className = 'scroll-progress-bar';
      document.body.appendChild(this.progressBar);

      window.addEventListener('scroll', () => this.update(), { passive: true });
      this.update();
    }

    update() {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (scrollTop / docHeight) * 100;

      this.progressBar.style.width = progress + '%';
    }
  }

  // ===========================================
  // STAGGERED TEXT REVEAL
  // ===========================================
  class SplitTextReveal {
    constructor(el) {
      this.el = el;
      this.init();
    }

    init() {
      const text = this.el.textContent;
      const words = text.split(' ');

      this.el.innerHTML = words.map((word, i) =>
        `<span class="word-reveal" style="--word-index: ${i}">${word}</span>`
      ).join(' ');

      // Trigger animation when in view
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.el.classList.add('text-revealed');
            observer.unobserve(this.el);
          }
        });
      }, { threshold: 0.5 });

      observer.observe(this.el);
    }
  }

  // ===========================================
  // FLOATING CTA BUTTON
  // ===========================================
  class FloatingCTA {
    constructor() {
      this.button = null;
      this.isVisible = false;
      this.init();
    }

    init() {
      this.button = document.createElement('a');
      this.button.href = 'https://wa.me/923039441945';
      this.button.target = '_blank';
      this.button.rel = 'noopener noreferrer';
      this.button.className = 'floating-cta';
      this.button.innerHTML = `
        <span class="floating-cta-text">Let's Talk</span>
        <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
      `;
      document.body.appendChild(this.button);

      window.addEventListener('scroll', () => this.checkVisibility(), { passive: true });
    }

    checkVisibility() {
      const scrollY = window.scrollY;
      const shouldShow = scrollY > 500;

      if (shouldShow && !this.isVisible) {
        this.button.classList.add('visible');
        this.isVisible = true;
      } else if (!shouldShow && this.isVisible) {
        this.button.classList.remove('visible');
        this.isVisible = false;
      }
    }
  }

  // ===========================================
  // PARALLAX TILT (Enhanced 3D)
  // ===========================================
  class ParallaxTilt {
    constructor(el) {
      this.el = el;
      this.maxTilt = parseFloat(el.dataset.maxTilt) || 10;
      this.perspective = parseFloat(el.dataset.perspective) || 1000;
      this.scale = parseFloat(el.dataset.scale) || 1.05;
      this.init();
    }

    init() {
      this.el.style.transformStyle = 'preserve-3d';
      this.el.style.transition = 'transform 0.15s ease-out';

      this.el.addEventListener('mouseenter', () => this.onEnter());
      this.el.addEventListener('mousemove', (e) => this.onMove(e));
      this.el.addEventListener('mouseleave', () => this.onLeave());
    }

    onEnter() {
      this.el.style.transition = 'transform 0.15s ease-out';
    }

    onMove(e) {
      const rect = this.el.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;

      const tiltX = (this.maxTilt / 2 - x * this.maxTilt).toFixed(2);
      const tiltY = (y * this.maxTilt - this.maxTilt / 2).toFixed(2);

      this.el.style.transform = `
        perspective(${this.perspective}px)
        rotateX(${tiltY}deg)
        rotateY(${tiltX}deg)
        scale3d(${this.scale}, ${this.scale}, ${this.scale})
      `;
    }

    onLeave() {
      this.el.style.transform = `
        perspective(${this.perspective}px)
        rotateX(0deg)
        rotateY(0deg)
        scale3d(1, 1, 1)
      `;
    }
  }

  // ===========================================
  // BLOB MORPH BACKGROUND
  // ===========================================
  class BlobMorph {
    constructor(container) {
      this.container = container;
      this.blobs = [];
      this.init();
    }

    init() {
      const blobContainer = document.createElement('div');
      blobContainer.className = 'blob-container';

      for (let i = 0; i < 3; i++) {
        const blob = document.createElement('div');
        blob.className = `blob blob-${i + 1}`;
        blobContainer.appendChild(blob);
        this.blobs.push(blob);
      }

      this.container.prepend(blobContainer);
    }
  }

  // ===========================================
  // RIPPLE EFFECT ON CLICK
  // ===========================================
  function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();

    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.className = 'ripple-effect';

    button.appendChild(ripple);

    ripple.addEventListener('animationend', () => ripple.remove());
  }

  // ===========================================
  // INITIALIZE ALL EFFECTS
  // ===========================================
  document.addEventListener('DOMContentLoaded', () => {
    // Cursor spotlight (only on desktop)
    if (window.innerWidth > 1024) {
      new CursorSpotlight();
    }

    // Scroll progress
    new ScrollProgress();

    // Floating CTA
    new FloatingCTA();

    // Text scramble on hero
    const scrambleEl = document.querySelector('[data-scramble]');
    if (scrambleEl) {
      const fx = new TextScramble(scrambleEl);
      const phrases = scrambleEl.dataset.scramble.split('|');
      let counter = 0;

      const next = () => {
        fx.setText(phrases[counter]).then(() => {
          setTimeout(next, 3000);
        });
        counter = (counter + 1) % phrases.length;
      };

      next();
    }

    // Magnetic elements
    document.querySelectorAll('[data-magnetic]').forEach(el => {
      new MagneticElement(el);
    });

    // Card spotlight effect
    document.querySelectorAll('[data-spotlight]').forEach(el => {
      new CardSpotlight(el);
    });

    // Enhanced 3D tilt
    document.querySelectorAll('[data-parallax-tilt]').forEach(el => {
      new ParallaxTilt(el);
    });

    // Split text reveal
    document.querySelectorAll('[data-split-reveal]').forEach(el => {
      new SplitTextReveal(el);
    });

    // Blob morph backgrounds
    document.querySelectorAll('[data-blob-bg]').forEach(el => {
      new BlobMorph(el);
    });

    // Ripple effect on buttons
    document.querySelectorAll('.btn-primary, .btn-ripple').forEach(button => {
      button.style.position = 'relative';
      button.style.overflow = 'hidden';
      button.addEventListener('click', createRipple);
    });

    // Smooth reveal for sections
    const revealSections = document.querySelectorAll('section');
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('section-visible');
        }
      });
    }, { threshold: 0.1 });

    revealSections.forEach(section => sectionObserver.observe(section));
  });

  // Expose classes for external use
  window.UltraEffects = {
    TextScramble,
    MagneticElement,
    CardSpotlight,
    ParallaxTilt,
    BlobMorph
  };
})();
