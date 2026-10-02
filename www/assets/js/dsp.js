/* Amazon-DSP-Seite: Scroll-Motion (vanilla JS) */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) {
    /* SVG-Animationen (Transporter, Datenpunkte) anhalten */
    document.querySelectorAll('.dsp-page svg').forEach(function (s) { if (s.pauseAnimations) s.pauseAnimations(); });
    return;
  }
  document.documentElement.classList.add('js-motion');
  var els = document.querySelectorAll('.m-up');
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
  /* Kennzahl hochzählen (3.500) */
  var de = document.documentElement.lang !== 'en';
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var to = parseInt(el.dataset.count, 10);
    var fmt = function (v) { return Math.round(v).toLocaleString(de ? 'de-DE' : 'en-GB'); };
    el.textContent = fmt(0);
    var cio = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      cio.disconnect();
      var t0 = performance.now();
      (function tick(now) {
        var p = Math.min(1, (now - t0) / 1600);
        el.textContent = fmt(to * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(tick);
      })(t0);
    }, { threshold: 0.6 });
    cio.observe(el);
  });

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
