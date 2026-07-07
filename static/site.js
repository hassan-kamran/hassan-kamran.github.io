/* engrhassankamran.com — progressive enhancement.
   Without this file the page is fully readable: hidden/dim states are
   scoped under `html.js` (and prefers-reduced-motion: no-preference). */
(() => {
  "use strict";

  const doc = document.documentElement;
  doc.classList.add("js");

  const motionOK = matchMedia("(prefers-reduced-motion: no-preference)").matches;
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => [...(c || document).querySelectorAll(s)];

  /* ---------- Reveal on scroll (staggered within each parent) ---------- */
  const reveals = $$(".reveal");
  if (motionOK && "IntersectionObserver" in window) {
    const perParent = new Map();
    for (const el of reveals) {
      const n = perParent.get(el.parentElement) || 0;
      perParent.set(el.parentElement, n + 1);
      el.style.setProperty("--d", Math.min(n, 5) * 70 + "ms");
    }
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      }
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("in"));
  }

  /* ---------- Stat counters ---------- */
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const countUp = (el) => {
    const target = parseInt(el.dataset.count, 10);
    const t0 = performance.now();
    const dur = 900;
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / dur);
      el.textContent = Math.round(easeOut(p) * target);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  const counters = $$("[data-count]");
  if (motionOK && counters.length && "IntersectionObserver" in window) {
    const cio = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          countUp(e.target);
          cio.unobserve(e.target);
        }
      }
    }, { threshold: 0.4 });
    counters.forEach((el) => cio.observe(el));
  }

  /* ---------- Kicker decode effect ---------- */
  const kicker = $(".kicker");
  if (kicker && motionOK) {
    const real = kicker.textContent;
    const glyphs = "01<>#/\\|+=*";
    const frames = Math.max(14, real.length);
    let frame = 0;
    kicker.setAttribute("aria-label", real);
    const iv = setInterval(() => {
      frame++;
      const solved = Math.floor((real.length * frame) / frames);
      kicker.textContent =
        real.slice(0, solved) +
        [...real.slice(solved)]
          .map((ch) => (ch === " " ? " " : glyphs[(Math.random() * glyphs.length) | 0]))
          .join("");
      if (frame >= frames) {
        kicker.textContent = real;
        kicker.removeAttribute("aria-label");
        clearInterval(iv);
      }
    }, 34);
  }

  /* ---------- Career path stepper ---------- */
  const nodes = $$(".path .node");
  nodes.forEach((node, i) => {
    if (motionOK) setTimeout(() => node.classList.add("on"), 600 + i * 170);
    else node.classList.add("on");
  });

  /* ---------- Scroll-driven: progress bar, spy, timeline, header, to-top ---------- */
  const bar = $(".progress span");
  const header = $(".site-header");
  const toTop = $(".to-top");
  const timeline = $(".timeline");
  const sections = $$("main section[id]");
  const navLinks = $$(".site-nav a").map((a) => [a.getAttribute("href").slice(1), a]);
  if (!motionOK && timeline) timeline.style.setProperty("--tl", "1");

  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      const y = scrollY;
      const max = doc.scrollHeight - innerHeight;
      if (bar) bar.style.transform = "scaleX(" + (max > 0 ? y / max : 0) + ")";
      if (header) header.classList.toggle("scrolled", y > 8);
      if (toTop) toTop.classList.toggle("show", y > 600);

      if (timeline && motionOK) {
        const r = timeline.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, (innerHeight * 0.8 - r.top) / r.height));
        timeline.style.setProperty("--tl", p.toFixed(3));
      }

      let current = null;
      for (const s of sections) {
        if (s.getBoundingClientRect().top <= innerHeight * 0.35) current = s.id;
      }
      for (const [id, a] of navLinks) {
        const active = id === current;
        a.classList.toggle("active", active);
        if (active) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      }
    });
  };
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll, { passive: true });
  onScroll();

  /* ---------- Hero dot-grid spotlight ---------- */
  const hero = $(".hero");
  if (hero && motionOK && matchMedia("(pointer: fine)").matches) {
    hero.addEventListener("pointermove", (e) => {
      const r = hero.getBoundingClientRect();
      hero.style.setProperty("--mx", e.clientX - r.left + "px");
      hero.style.setProperty("--my", e.clientY - r.top + "px");
      hero.classList.add("lit");
    });
    hero.addEventListener("pointerleave", () => hero.classList.remove("lit"));
  }

  /* ---------- Copy to clipboard ---------- */
  $$("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
      } catch {
        return; // clipboard unavailable — leave the button untouched
      }
      btn.classList.add("done");
      setTimeout(() => btn.classList.remove("done"), 1600);
    });
  });
})();
