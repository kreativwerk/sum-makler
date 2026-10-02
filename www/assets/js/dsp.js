/* Amazon-DSP-Seite: Scroll-Motion (vanilla JS) */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) {
    /* SVG-Animationen (Transporter, Datenpunkte) anhalten */
    document.querySelectorAll('.dsp-page svg').forEach(function (s) { if (s.pauseAnimations) s.pauseAnimations(); });
    document.querySelectorAll('.q-chart').forEach(function (c) { c.classList.add('is-in'); });
    return;
  }
  document.documentElement.classList.add('js-motion');
  var els = document.querySelectorAll('.m-in, .m-up, .m-left, .m-right, .m-scale, .q-chart');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('is-in'); });
  }
  /* Scroll-Fortschritt (--p) für Parallax-Elemente */
  var prog = document.querySelectorAll('[data-progress]');
  var ticking = false;
  var update = function () {
    ticking = false;
    prog.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height)));
      el.style.setProperty('--p', p.toFixed(3));
    });
  };
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  update();
})();
