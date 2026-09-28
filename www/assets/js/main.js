/* Schneider & Musil – vanilla JS, no dependencies */
(function () {
  'use strict';

  var EN = document.documentElement.lang === 'en';
  /* Basis-URL der Assets aus dem eigenen Script-Pfad (funktioniert auch unter /en/) */
  var selfScript = document.querySelector('script[src*="main.js"]');
  var ASSETS = selfScript ? selfScript.src.replace(/js\/main\.js.*$/, '') : 'assets/';

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
        lot.src = ASSETS + 'js/lottie-light.min.js';
        lot.onload = function () {
          if (window.lottie && document.body.contains(anim)) {
            anim.innerHTML = '';
            window.lottie.loadAnimation({ container: anim, renderer: 'svg', loop: true, autoplay: true, path: ASSETS + 'img/preloader.json' });
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

  /* Mobile nav toggle (schwebender Menü-Button unten) */
  var toggle = document.querySelector('.nav-toggle');
  var setNav = function (open) {
    document.body.classList.toggle('nav-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    if (toggle) {
      toggle.setAttribute('aria-expanded', open);
    }
  };
  if (toggle) {
    toggle.addEventListener('click', function () {
      setNav(!document.body.classList.contains('nav-open'));
    });
    document.querySelectorAll('.nav-menu a').forEach(function (a) {
      a.addEventListener('click', function () { setNav(false); });
    });
    /* Tipp außerhalb des Menüs (abgedunkelter Hintergrund) schließt es */
    document.addEventListener('click', function (e) {
      if (document.body.classList.contains('nav-open') &&
          !e.target.closest('.nav-menu') && !e.target.closest('.fab-dock') && !e.target.closest('.site-header')) {
        setNav(false);
      }
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
      if (document.body.classList.contains('nav-open')) setNav(false);
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
      d.setAttribute('aria-label', (EN ? 'Show review ' : 'Bewertung ') + (idx + 1) + (EN ? '' : ' anzeigen'));
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

  /* Termin: zuerst Sprache wählen (Deutsch → Max oder Marco, Englisch → nur Marco) */
  var flow = document.querySelector('[data-termin-flow]');
  if (flow) {
    flow.classList.add('is-js');
    var langBtns = flow.querySelectorAll('[data-termin-lang]');
    var chooseLang = function (lang, scroll) {
      flow.setAttribute('data-choice', lang);
      langBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.terminLang === lang); });
      flow.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('revealed'); });
      var step2 = flow.querySelector('.termin-step2');
      if (scroll && step2) step2.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };
    langBtns.forEach(function (b) {
      b.addEventListener('click', function () { chooseLang(b.dataset.terminLang, true); });
    });
    /* Direktlink auf einen Makler (#max / #marco) überspringt die Auswahl */
    if (location.hash === '#max') chooseLang('de', false);
    else if (location.hash === '#marco') chooseLang(EN ? 'en' : 'de', false);
  }

  /* Google-Bewertung: Anzahl zählt hoch, wird fett, dann Konfetti */
  var rating = document.querySelector('[data-rating-celebrate]');
  if (rating && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var counters = rating.querySelectorAll('[data-count-to]');
    var fmt = function (el, v) {
      var dec = parseInt(el.dataset.decimals || '0', 10);
      var txt = v.toFixed(dec);
      el.textContent = EN ? txt : txt.replace('.', ',');
    };
    counters.forEach(function (el) { fmt(el, 0); });

    var confetti = function (origin) {
      var cv = document.createElement('canvas');
      cv.className = 'confetti-canvas';
      cv.setAttribute('aria-hidden', 'true');
      document.body.appendChild(cv);
      var dpr = window.devicePixelRatio || 1;
      cv.width = innerWidth * dpr; cv.height = innerHeight * dpr;
      var ctx = cv.getContext('2d');
      ctx.scale(dpr, dpr);
      var colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#245eed', '#FFD54F'];
      var parts = [];
      for (var k = 0; k < 140; k++) {
        var ang = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 0.9;
        var sp = 7 + Math.random() * 9;
        parts.push({
          x: origin.x, y: origin.y,
          vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp,
          w: 6 + Math.random() * 6, h: 8 + Math.random() * 8,
          r: Math.random() * Math.PI, vr: (Math.random() - 0.5) * 0.35,
          c: colors[k % colors.length], round: Math.random() < 0.3
        });
      }
      var start = performance.now();
      (function frame(now) {
        var t = now - start;
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        ctx.globalAlpha = t > 2200 ? Math.max(0, 1 - (t - 2200) / 800) : 1;
        parts.forEach(function (p) {
          p.vy += 0.28; p.vx *= 0.985; p.vy *= 0.985;
          p.x += p.vx; p.y += p.vy; p.r += p.vr;
          ctx.save();
          ctx.translate(p.x, p.y); ctx.rotate(p.r);
          ctx.fillStyle = p.c;
          if (p.round) { ctx.beginPath(); ctx.arc(0, 0, p.w / 2, 0, Math.PI * 2); ctx.fill(); }
          else ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.abs(Math.cos(p.r * 2)) + 2);
          ctx.restore();
        });
        if (t < 3000) requestAnimationFrame(frame); else cv.remove();
      })(start);
    };

    var run = function () {
      var dur = 1600, t0 = performance.now();
      (function tick(now) {
        var p = Math.min(1, (now - t0) / dur);
        var eased = 1 - Math.pow(1 - p, 3);
        counters.forEach(function (el) { fmt(el, parseFloat(el.dataset.countTo) * eased); });
        if (p < 1) { requestAnimationFrame(tick); return; }
        rating.classList.add('is-done');
        setTimeout(function () {
          var num = rating.querySelector('.rating-num') || rating;
          var r = num.getBoundingClientRect();
          confetti({ x: r.left + r.width / 2, y: r.top + r.height / 2 });
        }, 350);
      })(t0);
    };

    /* Start, sobald die Bewertung sichtbar ist und der Preloader weg ist */
    var started = false;
    var tryStart = function () {
      if (started) return;
      var pl = document.getElementById('preloader');
      if (pl && !pl.classList.contains('done')) { setTimeout(tryStart, 200); return; }
      started = true;
      setTimeout(run, pl ? 500 : 250);
    };
    if ('IntersectionObserver' in window) {
      var rio = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { rio.disconnect(); tryStart(); }
      }, { threshold: 0.6 });
      rio.observe(rating);
    } else { tryStart(); }
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
