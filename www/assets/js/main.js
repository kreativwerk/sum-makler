/* Schneider & Musil – vanilla JS, no dependencies */
(function () {
  'use strict';

  /* Preloader (nur Startseite): blauer Punkt, dann ausblenden */
  var pre = document.getElementById('preloader');
  if (pre) {
    var hide = function () {
      pre.classList.add('done');
      setTimeout(function () { pre.remove(); }, 600);
    };
    if (sessionStorage.getItem('sumPreloaded')) {
      pre.remove();
    } else {
      sessionStorage.setItem('sumPreloaded', '1');
      var anim = document.getElementById('preloaderAnim');
      if (anim) {
        var lot = document.createElement('script');
        lot.src = 'assets/js/lottie-light.min.js';
        lot.onload = function () {
          if (window.lottie && document.body.contains(anim)) {
            anim.innerHTML = '';
            window.lottie.loadAnimation({ container: anim, renderer: 'svg', loop: true, autoplay: true, path: 'assets/img/preloader.json' });
          }
        };
        document.head.appendChild(lot);
      }
      window.addEventListener('load', function () { setTimeout(hide, 700); });
      setTimeout(hide, 2500); /* Fallback */
    }
  }

  /* Timeline: Fortschrittsbalken füllt sich beim Scrollen */
  var tl = document.querySelector('[data-timeline]');
  if (tl) {
    var bar = tl.querySelector('.timeline-progress');
    var onScroll = function () {
      var r = tl.getBoundingClientRect();
      var vh = window.innerHeight;
      var progress = (vh * 0.6 - r.top) / r.height;
      bar.style.height = Math.max(0, Math.min(1, progress)) * 100 + '%';
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* Sanfter Parallax-Effekt (App-Collage) */
  var pxEls = document.querySelectorAll('[data-parallax]');
  if (pxEls.length && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var pxTick = false;
    var pxUpdate = function () {
      pxTick = false;
      pxEls.forEach(function (el) {
        var f = parseFloat(el.dataset.parallax) || 0.05;
        var r = el.getBoundingClientRect();
        var offset = (r.top + r.height / 2 - window.innerHeight / 2) * f;
        el.style.translate = '0 ' + (-offset).toFixed(1) + 'px';
      });
    };
    window.addEventListener('scroll', function () {
      if (!pxTick) { pxTick = true; requestAnimationFrame(pxUpdate); }
    }, { passive: true });
    pxUpdate();
  }

  /* Mobile nav toggle */
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }

  /* Mega menu (Sparten) – click toggles, outside click closes */
  document.querySelectorAll('.mega').forEach(function (mega) {
    var btn = mega.querySelector('button');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = mega.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });
  });
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.mega.open').forEach(function (mega) {
      if (!mega.contains(e.target)) {
        mega.classList.remove('open');
        mega.querySelector('button').setAttribute('aria-expanded', 'false');
      }
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.mega.open').forEach(function (m) { m.classList.remove('open'); });
      if (header && header.classList.contains('nav-open')) {
        header.classList.remove('nav-open');
        document.body.style.overflow = '';
      }
    }
  });

  /* Testimonial slider */
  document.querySelectorAll('[data-slider]').forEach(function (slider) {
    var slides = slider.querySelectorAll('.slide');
    var dotsWrap = slider.querySelector('.slider-dots');
    var i = 0, timer;
    if (!slides.length) return;

    slides.forEach(function (_, idx) {
      var d = document.createElement('button');
      d.className = 'slider-dot' + (idx === 0 ? ' active' : '');
      d.setAttribute('aria-label', 'Bewertung ' + (idx + 1) + ' anzeigen');
      d.addEventListener('click', function () { go(idx); restart(); });
      dotsWrap.appendChild(d);
    });
    var dots = dotsWrap.children;

    function go(n, dir) {
      slides[i].classList.remove('active', 'from-left');
      dots[i].classList.remove('active');
      i = (n + slides.length) % slides.length;
      slides[i].classList.toggle('from-left', dir === 'left');
      slides[i].classList.add('active');
      dots[i].classList.add('active');
    }
    function restart() {
      clearInterval(timer);
      timer = setInterval(function () { go(i + 1); }, 5000);
    }
    slider.querySelectorAll('[data-prev]').forEach(function (b) {
      b.addEventListener('click', function () { go(i - 1, 'left'); restart(); });
    });
    slider.querySelectorAll('[data-next]').forEach(function (b) {
      b.addEventListener('click', function () { go(i + 1); restart(); });
    });
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) restart();
  });

  /* Scroll reveal */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal, .timeline-item, .feature-bar-inner').forEach(function (el) {
      io.observe(el);
    });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('revealed'); });
  }

  /* Blog filter */
  var filter = document.querySelector('.blog-filter');
  if (filter) {
    filter.addEventListener('click', function (e) {
      var btn = e.target.closest('button');
      if (!btn) return;
      filter.querySelectorAll('button').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var cat = btn.dataset.cat;
      document.querySelectorAll('.blog-grid .blog-card').forEach(function (card) {
        card.style.display = (cat === 'alle' || card.dataset.cat === cat) ? '' : 'none';
      });
    });
  }

  /* Lazy background videos: only load when near viewport */
  document.querySelectorAll('video[data-lazy]').forEach(function (video) {
    var load = function () {
      video.querySelectorAll('source[data-src]').forEach(function (s) {
        s.src = s.dataset.src;
      });
      video.load();
      video.play().catch(function () {});
    };
    if ('IntersectionObserver' in window) {
      var vio = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { load(); vio.disconnect(); }
        });
      }, { rootMargin: '200px' });
      vio.observe(video);
    } else { load(); }
  });
})();
