/**
 * MEGA EFFECTS - Ultimate Interactions
 * Custom cursor, particle system, infinite marquee, and more
 */

(function() {
  'use strict';

  // ===========================================
  // CUSTOM CURSOR
  // ===========================================
  class CustomCursor {
    constructor() {
      if (window.innerWidth <= 1024) return;

      this.cursor = null;
      this.dot = null;
      this.mouseX = 0;
      this.mouseY = 0;
      this.cursorX = 0;
      this.cursorY = 0;
      this.dotX = 0;
      this.dotY = 0;
      this.init();
    }

    init() {
      // Create cursor elements
      this.cursor = document.createElement('div');
      this.cursor.className = 'custom-cursor';
      document.body.appendChild(this.cursor);

      this.dot = document.createElement('div');
      this.dot.className = 'cursor-dot';
      document.body.appendChild(this.dot);

      // Track mouse
      document.addEventListener('mousemove', (e) => {
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;
      });

      // Hover state for interactive elements
      const interactiveElements = document.querySelectorAll('a, button, [data-cursor-hover], input, textarea, .btn, .nav-link');
      interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => this.cursor.classList.add('cursor-hover'));
        el.addEventListener('mouseleave', () => this.cursor.classList.remove('cursor-hover'));
      });

      // Click state
      document.addEventListener('mousedown', () => this.cursor.classList.add('cursor-click'));
      document.addEventListener('mouseup', () => this.cursor.classList.remove('cursor-click'));

      // Hide default cursor
      document.body.style.cursor = 'none';
      document.querySelectorAll('a, button').forEach(el => el.style.cursor = 'none');

      this.animate();
    }

    animate() {
      // Smooth follow for outer cursor (faster)
      this.cursorX += (this.mouseX - this.cursorX) * 0.35;
      this.cursorY += (this.mouseY - this.cursorY) * 0.35;
      this.cursor.style.left = this.cursorX + 'px';
      this.cursor.style.top = this.cursorY + 'px';

      // Faster follow for dot (near instant)
      this.dotX += (this.mouseX - this.dotX) * 0.8;
      this.dotY += (this.mouseY - this.dotY) * 0.8;
      this.dot.style.left = this.dotX + 'px';
      this.dot.style.top = this.dotY + 'px';

      requestAnimationFrame(() => this.animate());
    }
  }

  // ===========================================
  // INTERACTIVE PARTICLE SYSTEM
  // ===========================================
  class ParticleSystem {
    constructor() {
      this.canvas = null;
      this.ctx = null;
      this.particles = [];
      this.mouseX = 0;
      this.mouseY = 0;
      this.particleCount = window.innerWidth > 768 ? 80 : 40;
      this.init();
    }

    init() {
      this.canvas = document.createElement('canvas');
      this.canvas.className = 'particle-canvas';
      document.body.prepend(this.canvas);
      this.ctx = this.canvas.getContext('2d');

      this.resize();
      window.addEventListener('resize', () => this.resize());

      document.addEventListener('mousemove', (e) => {
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;
      });

      // Create particles
      for (let i = 0; i < this.particleCount; i++) {
        this.particles.push(this.createParticle());
      }

      this.animate();
    }

    createParticle() {
      return {
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.2,
        hue: Math.random() * 60 + 250 // Purple to blue range
      };
    }

    resize() {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }

    animate() {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

      this.particles.forEach((particle, i) => {
        // Move particle
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Mouse interaction - particles move away from cursor
        const dx = this.mouseX - particle.x;
        const dy = this.mouseY - particle.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 150) {
          const force = (150 - dist) / 150;
          particle.vx -= (dx / dist) * force * 0.3;
          particle.vy -= (dy / dist) * force * 0.3;
        }

        // Damping
        particle.vx *= 0.99;
        particle.vy *= 0.99;

        // Bounce off edges
        if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;

        // Keep in bounds
        particle.x = Math.max(0, Math.min(this.canvas.width, particle.x));
        particle.y = Math.max(0, Math.min(this.canvas.height, particle.y));

        // Draw particle
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        this.ctx.fillStyle = `hsla(${particle.hue}, 70%, 60%, ${particle.opacity})`;
        this.ctx.fill();

        // Draw connections
        this.particles.slice(i + 1).forEach(other => {
          const dx2 = particle.x - other.x;
          const dy2 = particle.y - other.y;
          const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);

          if (dist2 < 120) {
            this.ctx.beginPath();
            this.ctx.moveTo(particle.x, particle.y);
            this.ctx.lineTo(other.x, other.y);
            this.ctx.strokeStyle = `hsla(270, 70%, 60%, ${0.15 * (1 - dist2 / 120)})`;
            this.ctx.stroke();
          }
        });
      });

      requestAnimationFrame(() => this.animate());
    }
  }

  // ===========================================
  // TYPEWRITER EFFECT V2 (with delete and loop)
  // ===========================================
  class TypewriterV2 {
    constructor(element) {
      this.element = element;
      this.texts = element.dataset.typewriter.split('|');
      this.currentIndex = 0;
      this.currentText = '';
      this.isDeleting = false;
      this.typeSpeed = 100;
      this.deleteSpeed = 50;
      this.pauseTime = 2000;
      this.init();
    }

    init() {
      // Add caret
      this.caret = document.createElement('span');
      this.caret.className = 'typewriter-caret';
      this.element.appendChild(this.caret);

      this.type();
    }

    type() {
      const fullText = this.texts[this.currentIndex];

      if (this.isDeleting) {
        this.currentText = fullText.substring(0, this.currentText.length - 1);
      } else {
        this.currentText = fullText.substring(0, this.currentText.length + 1);
      }

      // Update display
      this.element.textContent = this.currentText;
      this.element.appendChild(this.caret);

      let nextDelay = this.isDeleting ? this.deleteSpeed : this.typeSpeed;

      if (!this.isDeleting && this.currentText === fullText) {
        nextDelay = this.pauseTime;
        this.isDeleting = true;
      } else if (this.isDeleting && this.currentText === '') {
        this.isDeleting = false;
        this.currentIndex = (this.currentIndex + 1) % this.texts.length;
        nextDelay = 500;
      }

      setTimeout(() => this.type(), nextDelay);
    }
  }

  // ===========================================
  // WAVE TEXT EFFECT
  // ===========================================
  class WaveText {
    constructor(element) {
      this.element = element;
      this.init();
    }

    init() {
      const text = this.element.textContent;
      this.element.innerHTML = '';
      this.element.classList.add('wave-text');

      [...text].forEach((char, i) => {
        const span = document.createElement('span');
        span.textContent = char === ' ' ? '\u00A0' : char;
        span.style.setProperty('--char-index', i);
        this.element.appendChild(span);
      });
    }
  }

  // ===========================================
  // LIQUID BUTTON EFFECT
  // ===========================================
  class LiquidButton {
    constructor(element) {
      this.element = element;
      this.init();
    }

    init() {
      this.element.classList.add('btn-liquid');

      this.element.addEventListener('mousemove', (e) => {
        const rect = this.element.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        this.element.style.setProperty('--x', x + 'px');
        this.element.style.setProperty('--y', y + 'px');
      });
    }
  }

  // ===========================================
  // STAGGERED GRID REVEAL
  // ===========================================
  class StaggerGrid {
    constructor(element) {
      this.element = element;
      this.init();
    }

    init() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.element.classList.add('revealed');
            observer.unobserve(this.element);
          }
        });
      }, { threshold: 0.2 });

      observer.observe(this.element);
    }
  }

  // ===========================================
  // SMOOTH SCROLL ANCHORS
  // ===========================================
  class SmoothScrollAnchors {
    constructor() {
      this.init();
    }

    init() {
      document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
          const targetId = anchor.getAttribute('href');
          if (targetId === '#') return;

          const target = document.querySelector(targetId);
          if (target) {
            e.preventDefault();
            target.scrollIntoView({
              behavior: 'smooth',
              block: 'start'
            });
          }
        });
      });
    }
  }

  // ===========================================
  // TILT ON SCROLL (Cards tilt based on scroll)
  // ===========================================
  class ScrollTilt {
    constructor(element) {
      this.element = element;
      this.maxTilt = parseFloat(element.dataset.scrollTilt) || 5;
      this.init();
    }

    init() {
      window.addEventListener('scroll', () => this.onScroll(), { passive: true });
    }

    onScroll() {
      const rect = this.element.getBoundingClientRect();
      const centerY = window.innerHeight / 2;
      const elementCenter = rect.top + rect.height / 2;
      const distanceFromCenter = elementCenter - centerY;
      const normalizedDistance = distanceFromCenter / (window.innerHeight / 2);
      const tilt = normalizedDistance * this.maxTilt;

      if (rect.top < window.innerHeight && rect.bottom > 0) {
        this.element.style.transform = `perspective(1000px) rotateX(${tilt}deg)`;
      }
    }
  }

  // ===========================================
  // MAGNETIC DRAG
  // ===========================================
  class MagneticDrag {
    constructor(element) {
      this.element = element;
      this.strength = parseFloat(element.dataset.magneticDrag) || 0.5;
      this.init();
    }

    init() {
      this.element.addEventListener('mousemove', (e) => {
        const rect = this.element.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        this.element.style.transform = `translate(${x * this.strength}px, ${y * this.strength}px)`;
      });

      this.element.addEventListener('mouseleave', () => {
        this.element.style.transform = 'translate(0, 0)';
      });
    }
  }

  // ===========================================
  // PROGRESSIVE IMAGE LOADING
  // ===========================================
  class ProgressiveImage {
    constructor(element) {
      this.element = element;
      this.init();
    }

    init() {
      const img = this.element.querySelector('img');
      if (!img) return;

      // Add blur class
      img.style.filter = 'blur(10px)';
      img.style.transition = 'filter 0.5s ease';

      // When loaded, remove blur
      if (img.complete) {
        img.style.filter = 'none';
      } else {
        img.addEventListener('load', () => {
          img.style.filter = 'none';
        });
      }
    }
  }

  // ===========================================
  // COUNTER ANIMATION V2 (Spring physics)
  // ===========================================
  class SpringCounter {
    constructor(element) {
      this.element = element;
      this.target = parseFloat(element.dataset.target);
      this.current = 0;
      this.velocity = 0;
      this.stiffness = 0.1;
      this.damping = 0.8;
      this.prefix = element.dataset.prefix || '';
      this.suffix = element.dataset.suffix || '';
      this.init();
    }

    init() {
      const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          this.animate();
          observer.unobserve(this.element);
        }
      }, { threshold: 0.5 });

      observer.observe(this.element);
    }

    animate() {
      const force = (this.target - this.current) * this.stiffness;
      this.velocity += force;
      this.velocity *= this.damping;
      this.current += this.velocity;

      // Spring animation class
      if (Math.abs(this.velocity) > 0.5) {
        this.element.classList.add('counting');
      } else {
        this.element.classList.remove('counting');
      }

      this.element.textContent = this.prefix + Math.round(this.current) + this.suffix;

      if (Math.abs(this.target - this.current) > 0.1 || Math.abs(this.velocity) > 0.1) {
        requestAnimationFrame(() => this.animate());
      } else {
        this.element.textContent = this.prefix + this.target + this.suffix;
      }
    }
  }

  // ===========================================
  // TECH ARSENAL TOOLTIP (Always Horizontal)
  // ===========================================
  class TechArsenalTooltip {
    constructor() {
      this.tooltip = null;
      this.init();
    }

    init() {
      // Create tooltip element
      this.tooltip = document.createElement('div');
      this.tooltip.className = 'tech-tooltip';
      document.body.appendChild(this.tooltip);

      // Attach to all orbit-tech elements
      document.querySelectorAll('.orbit-tech').forEach(tech => {
        tech.addEventListener('mouseenter', (e) => this.show(e, tech));
        tech.addEventListener('mouseleave', () => this.hide());
        tech.addEventListener('mousemove', (e) => this.updatePosition(e));
      });
    }

    show(e, tech) {
      const name = tech.getAttribute('data-tech');
      if (!name) return;

      this.tooltip.textContent = name;
      this.tooltip.classList.add('visible');
      this.updatePosition(e);
    }

    hide() {
      this.tooltip.classList.remove('visible');
    }

    updatePosition(e) {
      // Position tooltip below cursor, always horizontal
      const x = e.clientX;
      const y = e.clientY + 25;

      // Ensure tooltip stays within viewport
      const tooltipRect = this.tooltip.getBoundingClientRect();
      const maxX = window.innerWidth - tooltipRect.width - 10;
      const adjustedX = Math.min(Math.max(10, x - tooltipRect.width / 2), maxX);

      this.tooltip.style.left = adjustedX + 'px';
      this.tooltip.style.top = y + 'px';
    }
  }

  // ===========================================
  // INITIALIZE ALL MEGA EFFECTS
  // ===========================================
  document.addEventListener('DOMContentLoaded', () => {
    // Custom cursor (desktop only)
    if (window.innerWidth > 1024) {
      new CustomCursor();
    }

    // Particle system (desktop only, and not on home hero to avoid conflict with blobs)
    if (window.innerWidth > 768) {
      new ParticleSystem();
    }

    // Smooth scroll
    new SmoothScrollAnchors();

    // Tech Arsenal tooltip (always horizontal)
    new TechArsenalTooltip();

    // Typewriter V2
    document.querySelectorAll('[data-typewriter]').forEach(el => {
      new TypewriterV2(el);
    });

    // Wave text
    document.querySelectorAll('[data-wave-text]').forEach(el => {
      new WaveText(el);
    });

    // Liquid buttons
    document.querySelectorAll('[data-liquid-btn]').forEach(el => {
      new LiquidButton(el);
    });

    // Stagger grids
    document.querySelectorAll('.stagger-grid').forEach(el => {
      new StaggerGrid(el);
    });

    // Scroll tilt
    document.querySelectorAll('[data-scroll-tilt]').forEach(el => {
      new ScrollTilt(el);
    });

    // Magnetic drag
    document.querySelectorAll('[data-magnetic-drag]').forEach(el => {
      new MagneticDrag(el);
    });

    // Progressive images
    document.querySelectorAll('[data-progressive-img]').forEach(el => {
      new ProgressiveImage(el);
    });

    // Spring counters
    document.querySelectorAll('[data-spring-counter]').forEach(el => {
      new SpringCounter(el);
    });

    // Glitch text - add data attribute
    document.querySelectorAll('[data-glitch]').forEach(el => {
      el.classList.add('glitch-text');
      el.dataset.text = el.textContent;
    });

    // Rainbow border on hover for featured items
    document.querySelectorAll('[data-rainbow-border]').forEach(el => {
      el.classList.add('rainbow-border-hover');
    });

    // Card stack effect
    document.querySelectorAll('[data-card-stack]').forEach(el => {
      el.classList.add('card-stack');
    });
  });

  // Expose classes
  window.MegaEffects = {
    CustomCursor,
    ParticleSystem,
    TypewriterV2,
    WaveText,
    LiquidButton,
    StaggerGrid,
    SpringCounter
  };
})();
