/**
 * Advanced Animations System
 * Scroll-triggered reveals, typing effects, counters, and more
 */

(function() {
  'use strict';

  // ===========================================
  // TYPING ANIMATION
  // ===========================================
  class TypeWriter {
    constructor(element, texts, options = {}) {
      this.element = element;
      this.texts = texts;
      this.textIndex = 0;
      this.charIndex = 0;
      this.isDeleting = false;
      this.options = {
        typeSpeed: options.typeSpeed || 80,
        deleteSpeed: options.deleteSpeed || 50,
        delayBetween: options.delayBetween || 2000,
        loop: options.loop !== false,
        cursor: options.cursor !== false
      };

      if (this.options.cursor) {
        this.element.classList.add('typing-cursor');
      }

      this.type();
    }

    type() {
      const currentText = this.texts[this.textIndex];

      if (this.isDeleting) {
        this.element.textContent = currentText.substring(0, this.charIndex - 1);
        this.charIndex--;
      } else {
        this.element.textContent = currentText.substring(0, this.charIndex + 1);
        this.charIndex++;
      }

      let timeout = this.isDeleting ? this.options.deleteSpeed : this.options.typeSpeed;

      if (!this.isDeleting && this.charIndex === currentText.length) {
        timeout = this.options.delayBetween;
        this.isDeleting = true;
      } else if (this.isDeleting && this.charIndex === 0) {
        this.isDeleting = false;
        this.textIndex = (this.textIndex + 1) % this.texts.length;
        timeout = 500;
      }

      setTimeout(() => this.type(), timeout);
    }
  }

  // ===========================================
  // COUNTER ANIMATION
  // ===========================================
  class CounterAnimation {
    constructor(element, options = {}) {
      this.element = element;
      this.target = parseInt(element.dataset.target || element.textContent, 10);
      this.duration = options.duration || 2000;
      this.suffix = element.dataset.suffix || '';
      this.prefix = element.dataset.prefix || '';
      this.hasAnimated = false;
    }

    animate() {
      if (this.hasAnimated) return;
      this.hasAnimated = true;

      const startTime = performance.now();
      const startValue = 0;

      const updateCounter = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / this.duration, 1);

        // Easing function (ease-out-expo)
        const easeOutExpo = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const current = Math.floor(startValue + (this.target - startValue) * easeOutExpo);

        this.element.textContent = this.prefix + current.toLocaleString() + this.suffix;

        if (progress < 1) {
          requestAnimationFrame(updateCounter);
        }
      };

      requestAnimationFrame(updateCounter);
    }
  }

  // ===========================================
  // SCROLL REVEAL ANIMATIONS
  // ===========================================
  class ScrollReveal {
    constructor() {
      this.elements = [];
      this.observer = null;
      this.init();
    }

    init() {
      // Create intersection observer
      this.observer = new IntersectionObserver(
        (entries) => this.handleIntersection(entries),
        {
          threshold: 0.1,
          rootMargin: '0px 0px -50px 0px'
        }
      );

      // Observe all elements with reveal classes
      document.querySelectorAll('[data-reveal]').forEach(el => {
        el.classList.add('reveal-hidden');
        this.observer.observe(el);
      });
    }

    handleIntersection(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const animation = el.dataset.reveal || 'fade-up';
          const delay = el.dataset.revealDelay || 0;

          setTimeout(() => {
            el.classList.remove('reveal-hidden');
            el.classList.add('reveal-visible', `reveal-${animation}`);
          }, parseInt(delay, 10));

          // Stop observing after animation
          this.observer.unobserve(el);
        }
      });
    }
  }

  // ===========================================
  // STAGGER ANIMATIONS
  // ===========================================
  class StaggerReveal {
    constructor() {
      this.observer = null;
      this.init();
    }

    init() {
      this.observer = new IntersectionObserver(
        (entries) => this.handleIntersection(entries),
        {
          threshold: 0.1,
          rootMargin: '0px 0px -30px 0px'
        }
      );

      document.querySelectorAll('[data-stagger]').forEach(container => {
        this.observer.observe(container);
      });
    }

    handleIntersection(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const container = entry.target;
          const children = container.querySelectorAll('[data-stagger-item]');
          const baseDelay = parseInt(container.dataset.staggerDelay || 100, 10);

          children.forEach((child, index) => {
            child.classList.add('stagger-hidden');
            setTimeout(() => {
              child.classList.remove('stagger-hidden');
              child.classList.add('stagger-visible');
            }, index * baseDelay);
          });

          this.observer.unobserve(container);
        }
      });
    }
  }

  // ===========================================
  // PARALLAX EFFECT
  // ===========================================
  class Parallax {
    constructor() {
      this.elements = document.querySelectorAll('[data-parallax]');
      if (this.elements.length > 0) {
        this.init();
      }
    }

    init() {
      // Use passive listener for better scroll performance
      window.addEventListener('scroll', () => this.update(), { passive: true });
      this.update();
    }

    update() {
      const scrollY = window.pageYOffset;

      this.elements.forEach(el => {
        const speed = parseFloat(el.dataset.parallax) || 0.5;
        const rect = el.getBoundingClientRect();
        const elementTop = rect.top + scrollY;
        const elementCenter = elementTop + rect.height / 2;
        const viewportCenter = scrollY + window.innerHeight / 2;
        const distance = viewportCenter - elementCenter;
        const translateY = distance * speed * 0.1;

        el.style.transform = `translateY(${translateY}px)`;
      });
    }
  }

  // ===========================================
  // SMOOTH SCROLL FOR ANCHORS
  // ===========================================
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;

        const target = document.querySelector(targetId);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  // ===========================================
  // COUNTER INITIALIZATION
  // ===========================================
  function initCounters() {
    const counterObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const counter = entry.target.counterInstance;
            if (counter) {
              counter.animate();
            }
            counterObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );

    document.querySelectorAll('[data-counter]').forEach(el => {
      el.counterInstance = new CounterAnimation(el);
      counterObserver.observe(el);
    });
  }

  // ===========================================
  // TYPING EFFECT INITIALIZATION
  // ===========================================
  function initTypingEffect() {
    document.querySelectorAll('[data-typing]').forEach(el => {
      const texts = el.dataset.typing.split('|');
      new TypeWriter(el, texts, {
        typeSpeed: parseInt(el.dataset.typeSpeed, 10) || 80,
        deleteSpeed: parseInt(el.dataset.deleteSpeed, 10) || 50,
        delayBetween: parseInt(el.dataset.delayBetween, 10) || 2000
      });
    });
  }

  // ===========================================
  // MAGNETIC BUTTON EFFECT
  // ===========================================
  function initMagneticButtons() {
    document.querySelectorAll('[data-magnetic]').forEach(button => {
      button.addEventListener('mousemove', (e) => {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        button.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
      });

      button.addEventListener('mouseleave', () => {
        button.style.transform = 'translate(0, 0)';
      });
    });
  }

  // ===========================================
  // TILT EFFECT FOR CARDS
  // ===========================================
  function initTiltEffect() {
    document.querySelectorAll('[data-tilt]').forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;

        const tiltX = (y - 0.5) * 10;
        const tiltY = (x - 0.5) * -10;

        card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
      });
    });
  }

  // ===========================================
  // INITIALIZE ALL ANIMATIONS
  // ===========================================
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize all animation systems
    new ScrollReveal();
    new StaggerReveal();
    new Parallax();

    initCounters();
    initTypingEffect();
    initSmoothScroll();
    initMagneticButtons();
    initTiltEffect();

    // Add loaded class for initial animations
    document.body.classList.add('page-loaded');
  });

  // Expose for external use
  window.Animations = {
    TypeWriter,
    CounterAnimation,
    ScrollReveal,
    StaggerReveal,
    Parallax
  };
})();
