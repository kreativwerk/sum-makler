# -*- coding: utf-8 -*-
"""Static site generator for sum-makler.de rebuild.

Reads _cms/sparten.csv and _cms/blogs.csv, writes the finished site to www/.
Run:  python3 build.py
"""
import csv
import html
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "www")
BASE = "https://www.sum-makler.de"
TODAY = date.today().isoformat()

e = html.escape

# ---------------------------------------------------------------- CMS data
def read_csv(name):
    with open(os.path.join(ROOT, "_cms", name), encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh) if r.get("Draft") != "true" and r.get("Archived") != "true"]

sparten = read_csv("sparten.csv")
blogs = read_csv("blogs.csv")

CATS = [  # (csv value, display, anchor id, icon)
    ("Sach und Kfz", "Sach & KFZ", "kfz", "icon-sach-kfz.svg"),
    ("Wohnung & Haus", "Wohnung & Haus", "haus", "icon-haus.svg"),
    ("Pflege & Krankheit", "Pflege & Krankheit", "pflege", "icon-pflege.svg"),
    ("Rente & Vorsorge", "Rente & Vorsorge", "rente", "icon-rente.svg"),
]
by_cat = {c[0]: sorted([s for s in sparten if s["Kategorie"] == c[0]], key=lambda r: r["Name"]) for c in CATS}

# ---------------------------------------------------------------- fragments
def mega_menu():
    cols = []
    for csvcat, disp, anchor, icon in CATS:
        links = "".join(
            f'<a href="/sparten/{s["Slug"]}/">{e(s["Name"])}</a>' for s in by_cat[csvcat]
        )
        cols.append(
            f'<div class="mega-col"><div class="mega-col-head">'
            f'<img src="/assets/img/{icon}" alt="" width="34" height="34" loading="lazy">{e(disp)}</div>{links}</div>'
        )
    return "".join(cols)

CARET = ('<svg width="16" height="16" viewBox="0 0 20 20" fill="none" aria-hidden="true">'
         '<path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="1.67" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')

def header(active=""):
    def cur(k):
        return ' aria-current="page"' if k == active else ""
    return f"""<a class="skip-link" href="#main">Zum Inhalt springen</a>
<header class="site-header">
  <nav class="nav" aria-label="Hauptnavigation">
    <a href="/" class="nav-logo" aria-label="Schneider &amp; Musil – Startseite">
      <img src="/assets/img/logo-text.svg" alt="Schneider &amp; Musil Versicherungsmakler" width="180" height="40">
    </a>
    <div class="nav-socials">
      <a href="https://www.instagram.com/summakler/" rel="noopener" aria-label="Instagram"><img src="/assets/img/icon-instagram.svg" alt="" width="24" height="24" loading="lazy"></a>
      <a href="https://www.facebook.com/schneidermusilmakler/" rel="noopener" aria-label="Facebook"><img src="/assets/img/icon-facebook.svg" alt="" width="24" height="24" loading="lazy"></a>
      <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" aria-label="WhatsApp"><img src="/assets/img/icon-wa-round.svg" alt="" width="24" height="24" loading="lazy"></a>
    </div>
    <button class="nav-toggle" aria-expanded="false" aria-label="Menü öffnen"><span></span></button>
    <div class="nav-menu">
      <a href="/" class="nav-link"{cur('start')}>Start</a>
      <a href="/blog/" class="nav-link"{cur('blog')}>Blog</a>
      <a href="/#service" class="nav-link">Service</a>
      <div class="mega">
        <button aria-expanded="false" aria-haspopup="true">Sparten {CARET}</button>
        <div class="mega-panel">{mega_menu()}</div>
      </div>
      <div class="nav-cta">
        <a href="https://login.simplr.de/#/login" class="nav-portal" rel="noopener">Kundenportal</a>
        <a href="/termin/" class="nav-book">Termin buchen</a>
      </div>
      <div class="nav-social">
        <a href="https://www.instagram.com/summakler/" rel="noopener" aria-label="Instagram"><img src="/assets/img/icon-instagram.svg" alt="" width="28" height="28" loading="lazy"></a>
        <a href="https://www.facebook.com/schneidermusilmakler/" rel="noopener" aria-label="Facebook"><img src="/assets/img/icon-facebook.svg" alt="" width="28" height="28" loading="lazy"></a>
        <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" aria-label="WhatsApp"><img src="/assets/img/icon-wa-round.svg" alt="" width="28" height="28" loading="lazy"></a>
      </div>
    </div>
  </nav>
</header>"""

FOOTER = f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="/assets/img/logo-full.svg" alt="Schneider &amp; Musil Logo" width="200" height="44" loading="lazy">
        <div class="footer-contact">
          <span><strong>Schneider &amp; Musil Versicherungsmakler GbR</strong></span>
          <span>Blütenstr. 41, 90765 Fürth</span>
          <a href="tel:+4991137758430">Tel.: +49 (911) 37758430</a>
          <span>Fax: +49 (911) 37758432</span>
          <a href="mailto:info@sum-makler.de">info@sum-makler.de</a>
        </div>
        <div class="footer-social">
          <a href="https://www.instagram.com/summakler/" rel="noopener" aria-label="Instagram"><img src="/assets/img/icon-instagram.svg" alt="" width="26" height="26" loading="lazy"></a>
          <a href="https://www.facebook.com/schneidermusilmakler/" rel="noopener" aria-label="Facebook"><img src="/assets/img/icon-facebook.svg" alt="" width="26" height="26" loading="lazy"></a>
          <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" aria-label="WhatsApp"><img src="/assets/img/icon-wa-round.svg" alt="" width="26" height="26" loading="lazy"></a>
        </div>
      </div>
      <nav class="footer-links" aria-label="Footer Navigation">
        <h3>Navigation</h3>
        <a href="/">Start</a>
        <a href="/blog/">Blog</a>
        <a href="/#service">Service</a>
        <a href="/#app">Unsere App</a>
        <a href="/termin/">Termin buchen</a>
      </nav>
      <nav class="footer-links" aria-label="Sparten">
        <h3><a href="/sparten/">Sparten</a></h3>
        <a href="/sparten/#kfz">Sach &amp; KFZ</a>
        <a href="/sparten/#haus">Wohnung &amp; Haus</a>
        <a href="/sparten/#pflege">Pflege &amp; Krankheit</a>
        <a href="/sparten/#rente">Rente &amp; Vorsorge</a>
      </nav>
    </div>
    <div class="footer-bottom">
      <span>© {date.today().year} www.sum-makler.de</span>
      <div class="footer-legal">
        <a href="/impressum/">Impressum</a>
        <a href="/datenschutzerklarung/">Datenschutzerklärung</a>
      </div>
    </div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>"""

ORG_LD = """{
  "@context": "https://schema.org",
  "@type": "InsuranceAgency",
  "@id": "https://www.sum-makler.de/#organization",
  "name": "Schneider & Musil Versicherungsmakler GbR",
  "url": "https://www.sum-makler.de/",
  "logo": "https://www.sum-makler.de/assets/img/logo-full.svg",
  "image": "https://www.sum-makler.de/assets/img/og-home.jpg",
  "description": "Unabhängige Versicherungsmakler aus der Metropolregion Nürnberg – persönliche und kostenfreie Beratung, 100% unabhängig, vollständig digital.",
  "telephone": "+49 911 37758430",
  "email": "info@sum-makler.de",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Blütenstr. 41",
    "postalCode": "90765",
    "addressLocality": "Fürth",
    "addressRegion": "Bayern",
    "addressCountry": "DE"
  },
  "areaServed": "Metropolregion Nürnberg",
  "founder": [
    {"@type": "Person", "name": "Maximilian Schneider", "jobTitle": "Versicherungsfachmann (IHK)"},
    {"@type": "Person", "name": "Marco Musil", "jobTitle": "Diplom Betriebswirt (FH)"}
  ],
  "sameAs": [
    "https://www.instagram.com/summakler/",
    "https://www.facebook.com/schneidermusilmakler/"
  ]
}"""

def page(*, path, title, desc, body, active="", og_image="/assets/img/og-home.jpg",
         extra_ld=None, og_type="website", noindex=False):
    """Write a full HTML page. path is relative to www/, e.g. 'termin/index.html'."""
    canonical = BASE + "/" + os.path.dirname(path).replace(os.sep, "/")
    canonical = canonical.rstrip("/") + "/" if os.path.dirname(path) else BASE + "/"
    if path == "404.html":
        canonical = BASE + "/404.html"
    lds = [ORG_LD] + (extra_ld or [])
    ld_tags = "".join(f'<script type="application/ld+json">{ld}</script>' for ld in lds)
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    doc = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">{robots}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Schneider &amp; Musil Versicherungsmakler">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}{og_image}">
<link rel="icon" href="/assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/webclip.png">
<link rel="preload" href="/assets/fonts/montserrat-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
{ld_tags}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{FOOTER}
</body>
</html>"""
    # Interne Links relativ machen, damit die Seite aus jedem (Unter-)Verzeichnis läuft
    depth = path.count("/")
    prefix = "../" * depth if depth else "./"
    doc = re.sub(r'\b(href|src|data-src|poster)="/(?!/)', lambda m: f'{m.group(1)}="{prefix}', doc)
    doc = doc.replace('srcset="/', f'srcset="{prefix}').replace(', /assets/', f', {prefix}assets/')
    dst = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dst) or OUT, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return canonical

def kontakt_section(topic=None):
    sub = f"Wir finden die passende {e(topic)} für Dich – kostenfrei, unabhängig und unverbindlich." if topic \
        else "Wir beraten Dich kostenfrei, unabhängig und unverbindlich."
    return f"""<section class="section" aria-label="Kontakt">
  <div class="container">
    <div class="kontakt-banner">
      <div class="kontakt-banner-left">
        <img src="/assets/img/logo-full.svg" alt="Schneider &amp; Musil Versicherungsmakler" width="240" height="117" loading="lazy">
        <p>Schneider &amp; Musil Versicherungsmakler GbR<br>Blütenstr. 41, 90765 Fürth</p>
      </div>
      <div class="kontakt-banner-right">
        <h2>Wir freuen uns auf Deine Nachricht.</h2>
        <p>{sub}</p>
        <div class="kontakt-tiles">
          <a href="/termin/" class="kontakt-tile">
            <img src="/assets/img/arrow.svg" alt="" width="20" height="20" loading="lazy">
            <strong>Termin buchen</strong><span>online &amp; kostenfrei</span>
          </a>
          <a href="tel:+4991137758430" class="kontakt-tile">
            <img src="/assets/img/icon-tel.svg" alt="" width="20" height="20" loading="lazy">
            <strong>Anrufen</strong><span>+49 (911) 37758430</span>
          </a>
          <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" class="kontakt-tile">
            <img src="/assets/img/icon-whatsapp.svg" alt="" width="20" height="20" loading="lazy">
            <strong>WhatsApp</strong><span>direkt schreiben</span>
          </a>
          <a href="mailto:info@sum-makler.de?subject=Unverbindliche%20Anfrage" class="kontakt-tile">
            <img src="/assets/img/icon-mail.svg" alt="" width="20" height="20" loading="lazy">
            <strong>E-Mail</strong><span>info@sum-makler.de</span>
          </a>
        </div>
        <div class="cta-checks kontakt-checks"><span>✔ kostenfrei</span><span>✔ unverbindlich</span><span>✔ unkompliziert</span></div>
      </div>
    </div>
  </div>
</section>"""

ARROW_BTN = '<span class="btn-icon"><img src="/assets/img/arrow.svg" alt="" width="16" height="16"></span>'
PHONE_BTN = '<span class="btn-icon"><img src="/assets/img/icon-phone-call.svg" alt="" width="16" height="16"></span>'

def cta_buttons():
    return f"""<div class="cta-row">
  <a href="/termin/" class="btn">{ARROW_BTN}Termin buchen</a>
  <a href="tel:+4991137758430" class="btn btn--ghost">{PHONE_BTN}Jetzt anrufen</a>
</div>"""

CHECK_SVG = ('<svg class="check-circle" viewBox="0 0 40 40" aria-hidden="true">'
             '<circle class="halo" cx="20" cy="20" r="20"/>'
             '<circle class="ring" cx="20" cy="20" r="12.5"/>'
             '<path class="tick" d="M14 20.5l4.5 4.5 9.5-10.5"/></svg>')

TESTIMONIALS = [
    ("Super Beratung mit flexibler Kommunikation. Seit mehreren Jahren Kunde – kann mir sicher sein, immer das beste Angebot zu bekommen – Vertrauenspartner!", "Hannahnas13", "avatar-hannah-160.webp"),
    ("Hier wird Vertrauen, eine ausgezeichnete Kompetenz und individueller Service für den Klienten ganz großgeschrieben! 5 Sterne reichen nicht!", "Christian M.", "avatar-christian-160.webp"),
    ("Kann mich nur sehr positiv äußern! Beide Herren haben mir bislang in allen Situationen schnell und unkompliziert geholfen. Hab mich nie gefühlt, als ob mir jemand etwas aufschwatzen wollen würde.", "Sylwia Paweska", "avatar-sylvia-160.webp"),
    ("Bin wirklich super zufrieden! Alle unglaublich freundlich! Telefonisch jederzeit erreichbar. Fühle mich gut beraten und aufgehoben. Sehr zu empfehlen.", "Lea K.", "avatar-lea-160.webp"),
    ("Absolut zu empfehlen, immer freundlich und hilfsbereit, auch wenn es mal schnell gehen muss. Moderne und unkomplizierte Prozesse in der Betreuung, verständliche Erklärungen für alle Fragen.", "Dominik Altmann", "avatar-dominik-160.webp"),
    ("Der KFZ-Schaden wurde umgehend und zu meiner vollen Zufriedenheit abgewickelt. Toll, in einer solchen Situation hier die Unterstützung zu bekommen, die man sich wünscht!", "Marcus Mailwald", "avatar-marcus-160.webp"),
]

def slider_html():
    slides = ""
    for i, (text, name, img) in enumerate(TESTIMONIALS):
        slides += f"""<article class="slide{' active' if i == 0 else ''}">
  <div class="slide-head">
    <img class="g-logo" src="/assets/img/google-g.svg" alt="Google" width="20" height="20" loading="lazy">
    <img class="stars" src="/assets/img/sterne-5.svg" alt="5 von 5 Sternen" width="110" height="18" loading="lazy">
    <span class="slide-verified">von Google verifiziert</span>
  </div>
  <p class="slide-text">{e(text)}</p>
  <div class="slide-person">
    <img src="/assets/img/{img}" alt="" width="38" height="38" loading="lazy">
    <span>{e(name)}</span>
  </div>
</article>"""
    chev_l = '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4l-8 8 8 8"/></svg>'
    chev_r = '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 4l8 8-8 8"/></svg>'
    return f"""<div class="slider" data-slider aria-label="Google Bewertungen">
  <button class="slider-arrow slider-arrow--prev" data-prev aria-label="Vorherige Bewertung">{chev_l}</button>
  <div class="slide-track">{slides}</div>
  <button class="slider-arrow slider-arrow--next" data-next aria-label="Nächste Bewertung">{chev_r}</button>
  <div class="slider-dots"></div>
</div>"""

# ================================================================ INDEX
faq_ld_home = """{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "Was kostet die Beratung bei Schneider & Musil?",
     "acceptedAnswer": {"@type": "Answer", "text": "Unsere Beratung ist zu 100% kostenlos und unverbindlich. Ausgehend von Deiner aktuellen Situation und Deinen individuellen Bedürfnissen stellen wir Dir passende Möglichkeiten vor."}},
    {"@type": "Question", "name": "Was ist der Unterschied zwischen Versicherungsmakler und Versicherungsvertreter?",
     "acceptedAnswer": {"@type": "Answer", "text": "Ein Versicherungsmakler (§ 93 HGB) handelt unabhängig im Auftrag des Kunden und kann Produkte aller Versicherer frei wählen. Ein Versicherungsvertreter (§ 84 HGB) handelt im Auftrag eines Versicherers und ist an dessen Weisungen und Produkte gebunden."}},
    {"@type": "Question", "name": "Wie läuft das erste Beratungsgespräch ab?",
     "acceptedAnswer": {"@type": "Answer", "text": "1. Vorstellung: Wir erklären, wer wir sind und wie wir arbeiten. 2. Analyse: Wir verschaffen uns einen gemeinsamen Überblick über Deine Wünsche und Ziele. 3. Besprechung der Möglichkeiten: Wir stellen Empfehlungen und Angebote vor. 4. Wir geben Sicherheit: Wir übernehmen die zukünftige Betreuung bis zur kompletten Schadenabwicklung."}}
  ]
}"""

def build_index():
    latest = blogs[:3]
    blog_cards = ""
    for b in latest:
        blog_cards += f"""<a href="/sum-blog/{b['Slug']}/" class="blog-card reveal">
  <span class="blog-tag">{e(b['Kategorie'])}</span>
  <h3>{e(b['Name'])}</h3>
  <p>{e(b['Headline'])}</p>
  <span class="blog-more">Mehr erfahren <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5"/></svg></span>
</a>"""

    timeline_steps = [
        ("1. Vorstellung", "service-1.svg", "Wir stellen uns vor und erklären Dir genau, wer wir sind und wie wir arbeiten. Wir erklären Dir den Unterschied zwischen einem Versicherungsvertreter und einem Versicherungsmakler, aber auch den Unterschied zu anderen Maklerkollegen und was uns ausmacht."),
        ("2. Analyse", "service-2.svg", "Wir verschaffen uns einen gemeinsamen Überblick, sprechen über Deine individuellen Wünsche und Ziele, aber auch darüber, was Dir besonders wichtig ist."),
        ("3. Besprechung der Möglichkeiten", "service-3.svg", "Wir besprechen unsere erarbeitete Analyse. Wir stellen Dir unsere Empfehlungen und Angebote vor, geben Dir Tipps für Deine optimale und sinnvolle Absicherung."),
        ("4. Wir geben Sicherheit", "service-4.svg", "Ab jetzt heißt es für Dich zurücklehnen. Um alles Weitere kümmern wir uns – von der zukünftigen Betreuung bis hin zur kompletten Schadenabwicklung."),
    ]
    timeline_html = "".join(f"""<div class="timeline-item">
  <div class="timeline-step">{e(step)}</div>
  <div class="timeline-dot" aria-hidden="true"></div>
  <div class="timeline-body">
    <img src="/assets/img/{icon}" alt="" width="115" height="115" loading="lazy">
    <p>{e(text)}</p>
  </div>
</div>""" for step, icon, text in timeline_steps)
    timeline_html = f"""<div class="timeline" data-timeline>
  <div class="timeline-line" aria-hidden="true"><div class="timeline-progress"></div></div>
  {timeline_html}
  <div class="timeline-fade-top" aria-hidden="true"></div>
  <div class="timeline-fade-bottom" aria-hidden="true"></div>
</div>"""

    makler_points = ["Handelt für den Mandanten", "Ist im Auftrag des Kunden tätig", "Ungebunden / Unabhängig",
                     "Versicherer hat kein Weisungsrecht", "Freie Produktwahl"]
    vertreter_points = ["Handelt für den Versicherer", "Im Auftrag des Versicherers tätig", "Gebunden / Abhängig",
                        "Weisung des Versicherers", "Produktauswahl des Versicherers"]
    mk = "".join(f'<div class="vs-point"><img src="/assets/img/check-blau.svg" alt="Vorteil:" width="22" height="22" loading="lazy">{e(p)}</div>' for p in makler_points)
    vt = "".join(f'<div class="vs-point"><img src="/assets/img/x-circle.svg" alt="Nachteil:" width="22" height="22" loading="lazy">{e(p)}</div>' for p in vertreter_points)

    vorteile = [
        ("Kostenfrei & unverbindlich", "Unsere Beratung ist zu 100% kostenlos und unverbindlich. Ausgehend von Deiner aktuellen Situation und Deinen individuellen Bedürfnissen stellen wir Dir passende Möglichkeiten vor.", ["Persönlich beraten", "Vollkommen kostenfrei"]),
        ("Unabhängige Experten", "Egal ob es um die private Krankenversicherung oder z. B. Beamte geht. Wir sind zu 100% unabhängig und empfehlen Dir nur Versicherer, von welchen wir selbst überzeugt sind.", ["Spezialisierte Makler", "Zu 100% unabhängig"]),
        ("Direkter Ansprechpartner", "Bei uns gibt es keine Hotline und keine wechselnden Gesprächspartner – unser Team steht Dir für alle Anliegen und Fragen jederzeit zur Verfügung.", ["Keine nervige Hotline", "Einfach und bequem"]),
        ("Ortsunabhängige Beratung", "Egal wo Du Dich gerade befindest und welche Absicherung Du Dir wünschst – wir helfen Dir, Dich richtig abzusichern. Egal ob persönlich, online oder telefonisch.", ["Vollständig digital", "Zeitersparnis"]),
    ]
    vorteile_html = ""
    for i, (t, txt, points) in enumerate(vorteile):
        pts = "".join(f'<div class="vorteil-point"><img src="/assets/img/check-ring.svg" alt="" width="24" height="24" loading="lazy">{e(p)}</div>' for p in points)
        vorteile_html += f'<div class="vorteil-card" style="--i:{i}"><h3>{e(t)}</h3><p>{e(txt)}</p><div class="vorteil-points">{pts}</div></div>'

    body = f"""
<div class="preloader" id="preloader" aria-hidden="true"><div class="preloader-anim" id="preloaderAnim"><div class="preloader-dot"></div></div></div>
<section class="hero" id="start">
  <div class="container hero-grid">
    <div>
      <p class="hero-label">Persönlich versichert</p>
      <h1>Wir sind Deine <strong>unabhängigen</strong> Versicherungsmakler aus der Metropolregion Nürnberg</h1>
      <p class="hero-sub">Buche jetzt einen Termin für eine <strong>persönliche &amp; kostenfreie</strong> Beratung!</p>
      {cta_buttons()}
      <div class="rating">
        <strong>5,0</strong>
        <img class="stars" src="/assets/img/sterne-5.svg" alt="5 von 5 Sternen bei Google" width="110" height="20">
        <span class="rating-count">185 Google Rezensionen</span>
        <img class="badge" src="/assets/img/google-badge-160.webp" srcset="/assets/img/google-badge-160.webp 1x, /assets/img/google-badge-320.webp 2x" alt="Google" width="66" height="44" loading="lazy">
      </div>
    </div>
    <div class="hero-visual">
      <div class="photo-wrap">
        <img class="pattern" src="/assets/img/grosse-auswahl.svg" alt="" aria-hidden="true">
        <img class="hero-photo" src="/assets/img/hero-team-800.webp"
             srcset="/assets/img/hero-team-480.webp 480w, /assets/img/hero-team-800.webp 800w, /assets/img/hero-team-1035.webp 1035w"
             sizes="(min-width: 992px) 45vw, 90vw" width="723" height="669" fetchpriority="high"
             alt="Marco Musil und Maximilian Schneider – unabhängige Versicherungsmakler aus der Metropolregion Nürnberg">
        {slider_html()}
      </div>
    </div>
  </div>
</section>

<section class="feature-bar" aria-label="Unsere Versprechen">
  <div class="container feature-bar-inner">
    <div class="feature-item">{CHECK_SVG}<span>100% unabhängig</span></div>
    <div class="feature-item">{CHECK_SVG}<span>Vollkommen kostenfrei</span></div>
    <div class="feature-item">{CHECK_SVG}<span>Vollständig digital</span></div>
  </div>
</section>

<section class="video-section">
  <video data-lazy autoplay muted loop playsinline preload="none" poster="/assets/video/hero-desktop-poster.jpg" aria-hidden="true" tabindex="-1">
    <source data-src="/assets/video/hero-desktop.webm" type="video/webm">
    <source data-src="/assets/video/hero-desktop.mp4" type="video/mp4">
  </video>
  <div class="container video-content">
    <div class="video-text">
      <h2>Wir versichern Dich.<br><strong>persönlich &amp; digital</strong></h2>
      <p>Buche jetzt einen Termin für eine<br><strong>persönliche &amp; kostenfreie</strong> Beratung!</p>
      <div class="cta-row">
        <a href="/termin/" class="btn">{ARROW_BTN}Termin buchen</a>
        <a href="#app" class="btn btn--ghost">{ARROW_BTN}Unsere App</a>
      </div>
    </div>
  </div>
</section>

<section class="timeline-section" id="service">
  <div class="container">
    <div class="timeline-head reveal">
      <p class="eyebrow"><strong>Unser Beratungsservice</strong></p>
      <h2>Das erwartet Dich in unserem ersten kostenlosen und unverbindlichen Beratungsgespräch</h2>
    </div>
  </div>
  {timeline_html}
  <div class="timeline-cta reveal">
    <div class="container">
      <h2>Wir freuen uns auf Deine Anfrage.</h2>
      <p>Ganz bequem per Telefon, E-Mail, WhatsApp oder Social Media</p>
      <a href="/termin/" class="btn btn--solid">Jetzt Termin vereinbaren&nbsp;<img src="/assets/img/pfeil-weiss.svg" alt="" width="26" height="26"></a>
      <div class="cta-checks"><span>✔ kostenfrei</span> <span>✔ unverbindlich</span> <span>✔ unkompliziert</span></div>
    </div>
  </div>
</section>

<section class="app-section section" id="app">
  <div class="app-collage" aria-hidden="true">
    <img src="/assets/img/fuerth-02-800.webp" alt="" loading="lazy" data-parallax="0.06">
    <img src="/assets/img/fuerth-04-800.webp" alt="" loading="lazy" data-parallax="-0.05">
    <img src="/assets/img/fuerth-01-800.webp" alt="" loading="lazy" data-parallax="0.05">
    <img src="/assets/img/fuerth-03-800.webp" alt="" loading="lazy" data-parallax="-0.06">
  </div>
  <div class="container">
    <div class="app-head reveal">
      <h2>Verwaltungschaos?</h2>
      <p>… wir <strong>digitalisieren</strong> Deinen Versicherungsordner!</p>
    </div>
    <div class="app-grid">
      <div class="app-phone reveal">
        <img src="/assets/img/app-05-400.webp" srcset="/assets/img/app-05-400.webp 400w, /assets/img/app-05-800.webp 800w" sizes="250px" width="250" height="507" loading="lazy" alt="Versicherungsapp von Schneider und Musil – Übersicht Deiner Verträge">
        <div class="app-feature">
          <h3><img src="/assets/img/check-blau.svg" alt="" width="26" height="26" loading="lazy">Überall dabei.</h3>
          <p>Nie mehr einen Versicherungsschein suchen, wenn man diesen braucht. Mit unserer App hast Du alle Deine wichtigen Daten immer griffbereit.</p>
        </div>
      </div>
      <div class="app-phone reveal reveal-d1">
        <img src="/assets/img/app-06-400.webp" srcset="/assets/img/app-06-400.webp 400w, /assets/img/app-06-800.webp 800w" sizes="250px" width="250" height="507" loading="lazy" alt="Versicherungsapp von Schneider und Musil – Police-Vorschau">
        <div class="app-feature">
          <h3><img src="/assets/img/check-blau.svg" alt="" width="26" height="26" loading="lazy">Dein Schutz.</h3>
          <p>Der Schutz Deiner Daten ist uns besonders wichtig! Deshalb werden Deine Daten ausschließlich verschlüsselt übertragen.</p>
        </div>
      </div>
      <div class="app-phone reveal reveal-d2">
        <img src="/assets/img/app-07-400.webp" srcset="/assets/img/app-07-400.webp 400w, /assets/img/app-07-800.webp 800w" sizes="250px" width="250" height="507" loading="lazy" alt="Versicherungsapp von Schneider und Musil – direkter Kontakt">
        <div class="app-feature">
          <h3><img src="/assets/img/check-blau.svg" alt="" width="26" height="26" loading="lazy">Persönlich.</h3>
          <p>Wir stehen Dir mit Rat und Tat auch vor Ort und nicht nur per Telefon, E-Mail oder SMS zur Seite. Online muss nicht anonym sein.</p>
        </div>
      </div>
    </div>
    <div class="app-cta reveal">
      <h2>Du möchtest Deinen Versicherungsordner auch digitalisieren?</h2>
      <p>Du kannst uns per Telefon, E-Mail, WhatsApp oder Social Media erreichen.</p>
      <div class="cta-row" style="justify-content:center">
        <a href="/termin/" class="btn">{ARROW_BTN}Termin buchen</a>
        <a href="tel:+4991137758430" class="btn btn--ghost">{PHONE_BTN}Jetzt anrufen</a>
      </div>
    </div>
  </div>
</section>

<section class="section team-section" id="team">
  <div class="container team-vorteile">
    <div class="team-col">
      <h2 class="split-head">Unser Team</h2>
      <div class="team-member reveal">
        <img src="/assets/img/team-max-400.webp" width="128" height="128" loading="lazy" alt="Maximilian Schneider, Versicherungsfachmann (IHK)">
        <div><h3>Maximilian Schneider</h3><p>Versicherungsfachmann (IHK)</p></div>
      </div>
      <div class="team-member reveal reveal-d1">
        <img src="/assets/img/team-marco-400.webp" width="128" height="128" loading="lazy" alt="Marco Musil, Diplom Betriebswirt (FH)">
        <div><h3>Marco Musil</h3><p>Diplom Betriebswirt (FH)</p></div>
      </div>
      <div class="team-member reveal reveal-d2">
        <img src="/assets/img/team-justin-400.webp" width="128" height="128" loading="lazy" alt="Justin Duensing, Office Manager">
        <div><h3>Justin Duensing</h3><p>Office Manager</p></div>
      </div>
    </div>
    <div class="vorteile-col">
      <h2 class="split-head">Deine Vorteile</h2>
      <div class="vorteile-grid">
        {vorteile_html}
        <div class="vorteil-card kontakt-card" style="--i:4">
          <h3>Termin vereinbaren</h3>
          <p>Wie Du uns erreichen kannst:</p>
          <div class="kontakt-links">
            <a href="tel:+4991137758430"><img src="/assets/img/icon-tel.svg" alt="" width="24" height="24" loading="lazy">Telefon</a>
            <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener"><img src="/assets/img/icon-whatsapp.svg" alt="" width="24" height="24" loading="lazy">WhatsApp</a>
            <a href="mailto:info@sum-makler.de?subject=Unverbindliche%20Anfrage"><img src="/assets/img/icon-mail.svg" alt="" width="24" height="24" loading="lazy">E-Mail</a>
          </div>
          <a href="/termin/" class="btn">{ARROW_BTN}Termin buchen</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="vs-section section">
  <div class="container">
    <div class="vs-head reveal">
      <h2>Verwechslungsgefahr…</h2>
      <p>Wichtige Unterscheidung zwischen „<strong>Versicherungsmakler</strong>“ und „<strong>Versicherungsvertreter</strong>“:<br><strong>Wir klären Euch auf:</strong></p>
    </div>
    <div class="vs-grid">
      <div class="vs-badge" aria-hidden="true">vs</div>
      <div class="vs-card makler reveal">
        <h3>Makler</h3>
        <details class="vs-law">
          <summary>Rechtsposition: <strong>§ 93 (1) Satz 1 HGB</strong><img src="/assets/img/caret-down.svg" alt="" width="16" height="16" loading="lazy"></summary>
          <div class="vs-law-body">(1) Wer gewerbsmäßig für andere Personen, ohne von ihnen auf Grund eines Vertragsverhältnisses ständig damit betraut zu sein, die Vermittlung von Verträgen über Anschaffung oder Veräußerung von Waren oder Wertpapieren, über Versicherungen, Güterbeförderungen, Schiffsmiete oder sonstige Gegenstände des Handelsverkehrs übernimmt, hat die Rechte und Pflichten eines Handelsmaklers.</div>
        </details>
        {mk}
        <img class="vs-underline" src="/assets/img/underline.svg" alt="" width="340" height="20" loading="lazy">
      </div>
      <div class="vs-card reveal reveal-d1">
        <h3>Vertreter</h3>
        <details class="vs-law">
          <summary>Rechtsposition: <strong>§ 84 (1) Satz 1 HGB</strong><img src="/assets/img/caret-down.svg" alt="" width="16" height="16" loading="lazy"></summary>
          <div class="vs-law-body">(1) Handelsvertreter ist, wer als selbständiger Gewerbetreibender ständig damit betraut ist, für einen anderen Unternehmer Geschäfte zu vermitteln oder in dessen Namen abzuschließen.</div>
        </details>
        {vt}
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    <div class="blog-head reveal">
      <h2>Unser Blog</h2>
      <p><strong>Wissenswertes über Versicherungen:</strong><br>Informiere Dich für eine optimale Absicherung</p>
    </div>
    <div class="blog-grid">{blog_cards}</div>
    <div class="cta-mid" style="padding-bottom:0">
      <a href="/blog/" class="btn btn--solid">Alle Blogbeiträge&nbsp;<img src="/assets/img/pfeil-weiss.svg" alt="" width="26" height="26"></a>
    </div>
  </div>
</section>"""
    page(
        path="index.html", active="start",
        title="Schneider & Musil | Unabhängige Versicherungsmakler Nürnberg & Fürth",
        desc="Deine unabhängigen Versicherungsmakler aus der Metropolregion Nürnberg. Persönliche & kostenfreie Beratung – 100% unabhängig, vollständig digital. Jetzt Termin buchen!",
        body=body, extra_ld=[faq_ld_home],
    )

# ================================================================ TERMIN
def build_termin():
    body = f"""
<section class="page-hero">
  <div class="container">
    <h1>Termin vereinbaren</h1>
    <p>Egal, ob Du lieber online, telefonisch oder persönlich beraten werden möchtest – wir passen uns Deinen Präferenzen an. Vereinbare Deinen Termin und erhalte individuelle Lösungen, die zu Dir passen.</p>
    <p><strong style="color:#fff">Termin vereinbaren mit:</strong></p>
    <div class="termin-choose">
      <a href="#max">Max</a><span class="or">oder</span><a href="#marco">Marco</a>
    </div>
  </div>
</section>
<section class="section termin-section">
  <img class="bg-logo" src="/assets/img/hero-bg.svg" alt="" aria-hidden="true">
  <div class="container makler-grid">
    <article class="makler-card reveal" id="max">
      <img src="/assets/img/makler-max-500.webp" srcset="/assets/img/makler-max-500.webp 500w, /assets/img/makler-max-800.webp 800w" sizes="(min-width: 900px) 357px, 86vw" width="357" height="446" alt="Maximilian Schneider, Versicherungsfachmann (IHK)">
      <div class="makler-card-info">
        <h2>Max Schneider</h2>
        <p class="role">Versicherungsfachmann (IHK)</p>
        <p class="sub">Freier Makler nach §93 HGB</p>
        <a class="tel" href="tel:+4917680185940">0176 80 18 59 40</a>
        <a class="mail" href="mailto:schneider@sum-makler.de">schneider@sum-makler.de</a>
        <div><a href="https://calendly.com/sum-schneider/beratung" target="_blank" rel="noopener" class="btn">{ARROW_BTN}Termin online buchen</a></div>
      </div>
    </article>
    <img class="makler-logo" src="/assets/img/logo-full.svg" alt="" width="300" height="120" loading="lazy">
    <article class="makler-card reveal reveal-d1" id="marco">
      <img src="/assets/img/makler-marco-500.webp" srcset="/assets/img/makler-marco-500.webp 500w, /assets/img/makler-marco-800.webp 800w" sizes="(min-width: 900px) 357px, 86vw" width="357" height="446" loading="lazy" alt="Marco Musil, Diplom Betriebswirt (FH)">
      <div class="makler-card-info">
        <h2>Marco Musil</h2>
        <p class="role">Diplom Betriebswirt (FH)</p>
        <p class="sub">Freier Makler nach §93 HGB</p>
        <a class="tel" href="tel:+491792936633">0179 29 36 63 3</a>
        <a class="mail" href="mailto:musil@sum-makler.de">musil@sum-makler.de</a>
        <div><a href="https://calendly.com/musil/60min" target="_blank" rel="noopener" class="btn">{ARROW_BTN}Termin online buchen</a></div>
      </div>
    </article>
  </div>
</section>"""
    page(
        path="termin/index.html",
        title="Beratungstermin buchen | Schneider & Musil Versicherungsmakler",
        desc="Vereinbare jetzt Deinen unverbindlichen Beratungstermin – online, telefonisch oder persönlich. Kostenfreie Versicherungsberatung mit Max Schneider oder Marco Musil.",
        body=body, og_image="/assets/img/og-image.jpg",
    )

# ================================================================ SPARTEN
def breadcrumb_ld(items):
    lis = ",".join(
        f'{{"@type":"ListItem","position":{i + 1},"name":"{n}","item":"{u}"}}'
        for i, (n, u) in enumerate(items)
    )
    return f'{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{lis}]}}'

def build_sparten_index():
    sections = ""
    for csvcat, disp, anchor, icon in CATS:
        cards = "".join(f"""<a class="sparte-card" href="/sparten/{s['Slug']}/">
  <h3>{e(s['Name'])}</h3><p>{e(s['Headline'])}</p>
</a>""" for s in by_cat[csvcat])
        sections += f"""<section class="sparten-section section" id="{anchor}">
  <div class="container">
    <h2><img src="/assets/img/{icon}" alt="" width="44" height="44" loading="lazy">{e(disp)}</h2>
    <div class="sparten-grid">{cards}</div>
  </div>
</section>"""
    body = f"""
<section class="page-hero">
  <div class="container">
    <nav class="breadcrumbs" aria-label="Brotkrumen"><a href="/">Start</a> / <span aria-current="page">Sparten</span></nav>
    <h1>Versicherungssparten</h1>
    <p>Von Autoversicherungen bis zur Altersvorsorge – wir haben alles abgedeckt. Wir helfen Dir gerne bei der richtigen Auswahl. Finde jetzt die passende Absicherung für Dich.</p>
  </div>
</section>
{sections}
{kontakt_section()}"""
    page(
        path="sparten/index.html",
        title="Versicherungssparten im Überblick | Schneider & Musil",
        desc="Alle Versicherungssparten im Überblick: Sach & KFZ, Wohnung & Haus, Pflege & Krankheit, Rente & Vorsorge. Unabhängige Beratung von Schneider & Musil aus Fürth.",
        body=body,
        extra_ld=[breadcrumb_ld([("Start", BASE + "/"), ("Sparten", BASE + "/sparten/")])],
    )

def build_sparte_detail(s):
    slug = s["Slug"]
    name = s["Name"]
    cat = next((c for c in CATS if c[0] == s["Kategorie"]), CATS[0])
    faqs, faq_ld_items = "", []
    for i in range(1, 5):
        q, a = s.get(f"FAQ Frage {i}", "").strip(), s.get(f"FAQ Antwort {i}", "").strip()
        if not q or not a:
            continue
        faqs += f"""<details class="faq-item"{' open' if i == 1 else ''}>
  <summary>{e(q)}<img src="/assets/img/caret-down.svg" alt="" width="16" height="16" loading="lazy"></summary>
  <div class="faq-body">{e(a)}</div>
</details>"""
        faq_ld_items.append(f'{{"@type":"Question","name":{jstr(q)},"acceptedAnswer":{{"@type":"Answer","text":{jstr(a)}}}}}')
    faq_ld = f'{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{",".join(faq_ld_items)}]}}'
    related = "".join(f'<a class="sparte-card" href="/sparten/{r["Slug"]}/"><h3>{e(r["Name"])}</h3><p>{e(r["Headline"])}</p></a>'
                      for r in by_cat[cat[0]] if r["Slug"] != slug)
    body = f"""
<section class="page-hero">
  <div class="container">
    <nav class="breadcrumbs" aria-label="Brotkrumen"><a href="/">Start</a> / <a href="/sparten/">Sparten</a> / <span aria-current="page">{e(name)}</span></nav>
    <p class="hero-label">{e(cat[1])}</p>
    <h1>{e(name)}</h1>
    <p><strong style="color:#fff">{e(s['Headline'])}</strong></p>
    <p>{e(s['Einleitung Hero'])}</p>
    <div class="cta-row" style="justify-content:center;margin-top:28px;margin-bottom:0">
      <a href="/termin/" class="btn">{ARROW_BTN}Kostenfreie Beratung</a>
      <a href="tel:+4991137758430" class="btn btn--ghost">{PHONE_BTN}Jetzt anrufen</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="container detail-content">
    <h2>{e(s['Thema'])}</h2>
    {s['Thema Richtext']}
  </div>
</section>
<section class="faq-section section">
  <div class="container">
    <div class="blog-head"><h2>Häufige Fragen zur {e(name)}</h2></div>
    <div class="faq-list">{faqs}</div>
  </div>
</section>
{kontakt_section(name)}
<section class="section" style="padding-top:0">
  <div class="container">
    <h2 class="split-head">Weitere Sparten: {e(cat[1])}</h2>
    <div class="sparten-grid">{related}</div>
  </div>
</section>"""
    page(
        path=f"sparten/{slug}/index.html",
        title=f"{name} | Unabhängige Beratung – Schneider & Musil",
        desc=(s["Einleitung Hero"][:155] + "…") if len(s["Einleitung Hero"]) > 158 else s["Einleitung Hero"],
        body=body,
        extra_ld=[faq_ld, breadcrumb_ld([("Start", BASE + "/"), ("Sparten", BASE + "/sparten/"), (e(name), f"{BASE}/sparten/{slug}/")])],
    )

def jstr(s):
    import json
    return json.dumps(s, ensure_ascii=False)

# ================================================================ BLOG
def build_blog_index():
    cards = ""
    for b in blogs:
        cat_slug = "wissen" if b["Kategorie"] == "Wissen" else "checkliste"
        cards += f"""<a href="/sum-blog/{b['Slug']}/" class="blog-card" data-cat="{cat_slug}">
  <span class="blog-tag">{e(b['Kategorie'])}</span>
  <h3>{e(b['Name'])}</h3>
  <p>{e(b['Headline'])}</p>
  <span class="blog-more">Mehr erfahren <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5"/></svg></span>
</a>"""
    body = f"""
<section class="page-hero">
  <div class="container">
    <p class="hero-label">Unser Blog</p>
    <h1>Erfahre mehr über die Welt der Versicherungen</h1>
    <p>Wissenswertes und Checklisten für Deinen umfassenden Versicherungsschutz.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="blog-filter" role="group" aria-label="Beiträge filtern">
      <button class="active" data-cat="alle">Alle</button>
      <button data-cat="wissen">Wissen</button>
      <button data-cat="checkliste">Checklisten</button>
    </div>
    <div class="blog-grid">{cards}</div>
  </div>
</section>"""
    page(
        path="blog/index.html", active="blog",
        title="Blog: Wissenswertes & Checklisten zu Versicherungen | Schneider & Musil",
        desc="Unser Versicherungs-Blog: Wissenswertes, Mythen-Checks und Checklisten für Deinen optimalen Versicherungsschutz – von Deinen unabhängigen Maklern aus Fürth.",
        body=body,
        extra_ld=[breadcrumb_ld([("Start", BASE + "/"), ("Blog", BASE + "/blog/")])],
    )

def build_blog_detail(b):
    slug = b["Slug"]
    sections = f"""<div class="container detail-content">
  <p style="font-size:1.1rem">{e(b['Einleitungstext'])}</p>"""
    # Checkliste items
    items = ""
    for i in range(1, 11):
        t = b.get(f"Titel Versicherung {i}", "").strip()
        d = b.get(f"Beschreibung Versicherung {i}", "").strip()
        if t and d:
            items += f'<div class="vorteil-card" style="margin-bottom:16px"><h3><img src="/assets/img/check-blau.svg" alt="" width="20" height="20" loading="lazy" style="vertical-align:-3px"> {e(t)}</h3><p style="margin:0">{e(d)}</p></div>'
    if items:
        sections += f"<h2>Diese Versicherungen solltest Du kennen:</h2>{items}"
        if b.get("CTA Beschreibung Checkliste", "").strip():
            sections += f'<p>{e(b["CTA Beschreibung Checkliste"])}</p>'
    # Mythos / Realität
    if b.get("Mythos Titel", "").strip():
        sections += f"<h2>{e(b['Mythos Titel'])}</h2><p>{e(b['Mythos Beschreibung'])}</p>"
    if b.get("Aufklärung / Realität Titel", "").strip():
        sections += f"<h2>{e(b['Aufklärung / Realität Titel'])}</h2><p>{e(b['Realität Beschreibung'])}</p>"
    if b.get("Beispiel Titel 1", "").strip():
        sections += f"<h2>{e(b.get('Beispiel Section Überschrift', 'Beispiele aus dem Leben:'))}</h2>"
        for i in range(1, 4):
            t = b.get(f"Beispiel Titel {i}", "").strip().rstrip("|").strip()
            d = b.get(f"Beispiel Beschreibung {i}", "").strip()
            if t and d:
                sections += f'<div class="vorteil-card" style="margin-bottom:16px"><h3>{e(t)}</h3><p style="margin:0">{e(d)}</p></div>'
    if b.get("Fazit Titel", "").strip():
        sections += f"<h2>{e(b['Fazit Titel'])}</h2><p>{e(b['Fazit Beschreibung'])}</p>"
    sections += "</div>"

    iso = ""
    m = re.search(r"\w+ (\w+) (\d+) (\d+)", b.get("Published On", ""))
    months = dict(Jan="01", Feb="02", Mar="03", Apr="04", May="05", Jun="06", Jul="07", Aug="08", Sep="09", Oct="10", Nov="11", Dec="12")
    if m and m.group(1) in months:
        iso = f"{m.group(3)}-{months[m.group(1)]}-{int(m.group(2)):02d}"
    blog_ld = f"""{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": {jstr(b['Name'])},
  "description": {jstr(b['Headline'])},
  "inLanguage": "de",
  {f'"datePublished": "{iso}",' if iso else ''}
  "author": {{"@type": "Organization", "name": "Schneider & Musil Versicherungsmakler GbR"}},
  "publisher": {{"@id": "https://www.sum-makler.de/#organization"}},
  "mainEntityOfPage": "{BASE}/sum-blog/{slug}/"
}}"""
    body = f"""
<article>
<section class="page-hero">
  <div class="container">
    <nav class="breadcrumbs" aria-label="Brotkrumen"><a href="/">Start</a> / <a href="/blog/">Blog</a> / <span aria-current="page">{e(b['Name'])}</span></nav>
    <p class="hero-label">{e(b['Kategorie'])}</p>
    <h1>{e(b['Name'])}</h1>
    <p>{e(b['Headline'])}</p>
  </div>
</section>
<section class="section">
{sections}
</section>
<section class="section" style="padding-top:0">
  <div class="container cta-mid" style="padding-bottom:0">
    <h2>Fragen zu Deiner Absicherung?</h2>
    <p>Wir beraten Dich kostenfrei, unabhängig und unverbindlich.</p>
    <a href="/termin/" class="btn btn--solid">Jetzt Termin vereinbaren&nbsp;<img src="/assets/img/pfeil-weiss.svg" alt="" width="26" height="26"></a>
  </div>
</section>
</article>"""
    page(
        path=f"sum-blog/{slug}/index.html",
        title=f"{b['Name']} | Schneider & Musil Blog",
        desc=b["Headline"],
        body=body, og_type="article",
        extra_ld=[blog_ld, breadcrumb_ld([("Start", BASE + "/"), ("Blog", BASE + "/blog/"), (e(b["Name"]), f"{BASE}/sum-blog/{slug}/")])],
    )

# ================================================================ LEGAL
def build_impressum():
    body = """
<section class="page-hero"><div class="container"><h1>Impressum</h1></div></section>
<section class="section"><div class="container legal-content">
<h2>Angaben gemäß § 5 TMG</h2>
<h3>Firma</h3>
<p>Schneider &amp; Musil Versicherungsmakler GbR<br>Blütenstr. 41<br>90765 Fürth<br>
Telefon: 0911/ 37758430<br>Telefax: 0911/ 37758432<br>
E-Mail: <a href="mailto:info@sum-makler.de">info@sum-makler.de</a><br>
Webseite: <a href="https://www.sum-makler.de">www.sum-makler.de</a></p>
<h3>Zuständige Registrierungsbehörde</h3>
<p>IHK für München und Oberbayern<br>Max-Joseph-Straße 2<br>80333 München<br>
Webseite: <a href="https://www.muenchen.ihk.de" rel="noopener">www.muenchen.ihk.de</a></p>
<p>Tätig als Versicherungsmakler mit Erlaubnispflicht nach § 34d<br>
Registrierungsnummer: D-82GD-K54AB-86 &amp; D-HFNZ-UN9OV-02</p>
<p>Die Eintragung kann bei der folgenden Registerstelle überprüft werden:</p>
<p>Deutscher Industrie- und Handelskammertag (DIHK) e.V.<br>Breite Straße 29<br>10178 Berlin<br>
Telefon: 0180 6005850 (Festnetzpreis 0,20 €/Anruf; Mobilfunkpreise maximal 0,60 €/Anruf)<br>
Internetseite: <a href="https://www.vermittlerregister.info" rel="noopener">www.vermittlerregister.info</a></p>
<h2>Schlichtungsstellen</h2>
<p>Für eventuelle Streitigkeiten zwischen Kunden und Versicherungsvermittlern gibt es unabhängige Schlichtungsstellen, die unter folgenden Kontaktdaten erreicht werden können:</p>
<p>Versicherungsombudsmann e.V.<br>Postfach 080632<br>10006 Berlin<br>
Telefon: +49 30 20 60 58 – 0<br>Telefax: +49 30 20 60 58 – 58<br>
E-Mail: <a href="mailto:beschwerde@versicherungsombudsmann.de">beschwerde@versicherungsombudsmann.de</a><br>
Webseite: <a href="https://www.versicherungsombudsmann.de" rel="noopener">www.versicherungsombudsmann.de</a></p>
<p>Ombudsmann für die Private Kranken- und Pflegeversicherung<br>Postfach 060222<br>10052 Berlin<br>
Telefon: 01802 – 55 04 44 (6 Cent/Anruf aus dem deutschen Festnetz, höchstens 42 Cent/Min aus Mobilfunknetzen)<br>
Telefax: 030 – 20 45 89 31<br>
Webseite: <a href="https://www.pkv-ombudsmann.de" rel="noopener">www.pkv-ombudsmann.de</a></p>
<h2>Berufsrechtliche Regelungen</h2>
<p>Die berufsrechtlichen Regelungen können über die vom Bundesministerium der Justiz und von der juris GmbH betriebene Homepage <a href="https://www.gesetze-im-internet.de" rel="noopener">www.gesetze-im-internet.de</a> eingesehen und abgerufen werden.</p>
<h2>Beteiligungen</h2>
<p>Der Versicherungsvermittler hält keine unmittelbare oder mittelbare Beteiligung von mehr als 10% der Stimmrechte oder des Kapitals an einem Versicherungsunternehmen.</p>
<p>Ein Versicherungsunternehmen hält keine mittelbare oder unmittelbare Beteiligung von mehr als 10% der Stimmrechte oder des Kapitals am Versicherungsvermittler.</p>
<h2>Datenschutz</h2>
<p>Die Nutzung unserer Webseite ist in der Regel ohne Angabe personenbezogener Daten möglich. Soweit auf unseren Seiten personenbezogene Daten (beispielsweise Name, Anschrift oder E-Mail-Adressen) erhoben werden, erfolgt dies, soweit möglich, stets auf freiwilliger Basis. Diese Daten werden ohne Ihre ausdrückliche Zustimmung nicht an Dritte weitergegeben.</p>
<p>Wir weisen darauf hin, dass die Datenübertragung im Internet (z.B. bei der Kommunikation per E-Mail) Sicherheitslücken aufweisen kann. Ein lückenloser Schutz der Daten vor dem Zugriff durch Dritte ist nicht möglich.</p>
<p>Der Nutzung von im Rahmen der Impressumspflicht veröffentlichten Kontaktdaten durch Dritte zur Übersendung von nicht ausdrücklich angeforderter Werbung und Informationsmaterialien wird hiermit ausdrücklich widersprochen. Die Betreiber der Seiten behalten sich ausdrücklich rechtliche Schritte im Falle der unverlangten Zusendung von Werbeinformationen, etwa durch Spam-Mails, vor.</p>
</div></section>"""
    page(path="impressum/index.html", title="Impressum | Schneider & Musil Versicherungsmakler GbR",
         desc="Impressum der Schneider & Musil Versicherungsmakler GbR, Blütenstr. 41, 90765 Fürth. Angaben gemäß § 5 TMG.",
         body=body)

def build_datenschutz():
    body = """
<section class="page-hero"><div class="container"><h1>Datenschutzerklärung</h1></div></section>
<section class="section"><div class="container legal-content">
<h2>1. Name und Kontaktdaten des für die Verarbeitung Verantwortlichen</h2>
<p>Wir freuen uns über Ihren Besuch auf unserer Webseite und Ihr Interesse an Schneider &amp; Musil Versicherungsmakler. Diese Datenschutz-Information gilt für die Datenverarbeitung durch:</p>
<p><strong>Verantwortlicher:</strong><br>Schneider &amp; Musil GbR, Blütenstr. 41, 90765 Fürth<br>
E-Mail: <a href="mailto:info@sum-makler.de">info@sum-makler.de</a><br>
Telefon: +49 (0)911 37 75 84 30<br>Fax: +49 (0)911 37 75 84 32</p>
<h2>2. Erhebung und Speicherung personenbezogener Daten sowie Art und Zweck von deren Verwendung</h2>
<p>Beim Aufrufen unserer Website werden durch den auf Ihrem Endgerät zum Einsatz kommenden Browser automatisch Informationen an den Server unserer Website gesendet. Diese Informationen werden temporär in einem sog. Logfile gespeichert. Folgende Informationen werden dabei ohne Ihr Zutun erfasst und bis zur automatisierten Löschung gespeichert: IP-Adresse des anfragenden Rechners, Datum und Uhrzeit des Zugriffs, Name und URL der abgerufenen Datei, Website, von der aus der Zugriff erfolgt (Referrer-URL), verwendeter Browser und ggf. das Betriebssystem Ihres Rechners sowie der Name Ihres Access-Providers.</p>
<p>Die genannten Daten werden durch uns zu folgenden Zwecken verarbeitet: Gewährleistung eines reibungslosen Verbindungsaufbaus der Website, Gewährleistung einer komfortablen Nutzung unserer Website, Auswertung der Systemsicherheit und -stabilität sowie zu weiteren administrativen Zwecken.</p>
<p>Die Rechtsgrundlage für die Datenverarbeitung ist Art. 6 Abs. 1 S. 1 lit. f DSGVO. Unser berechtigtes Interesse folgt aus oben aufgelisteten Zwecken zur Datenerhebung. In keinem Fall verwenden wir die erhobenen Daten zu dem Zweck, Rückschlüsse auf Ihre Person zu ziehen.</p>
<h2>3. Weitergabe von Daten</h2>
<p>Eine Übermittlung Ihrer persönlichen Daten an Dritte zu anderen als den im Folgenden aufgeführten Zwecken findet nicht statt. Wir geben Ihre persönlichen Daten nur an Dritte weiter, wenn:</p>
<p>Sie Ihre nach Art. 6 Abs. 1 S. 1 lit. a DSGVO ausdrückliche Einwilligung dazu erteilt haben; die Weitergabe nach Art. 6 Abs. 1 S. 1 lit. f DSGVO zur Geltendmachung, Ausübung oder Verteidigung von Rechtsansprüchen erforderlich ist und kein Grund zur Annahme besteht, dass Sie ein überwiegendes schutzwürdiges Interesse an der Nichtweitergabe Ihrer Daten haben; für den Fall, dass für die Weitergabe nach Art. 6 Abs. 1 S. 1 lit. c DSGVO eine gesetzliche Verpflichtung besteht; dies gesetzlich zulässig und nach Art. 6 Abs. 1 S. 1 lit. b DSGVO für die Abwicklung von Vertragsverhältnissen mit Ihnen erforderlich ist.</p>
<h2>4. Cookies</h2>
<p>Wir setzen auf unserer Seite sog. Cookies ein. Hierbei handelt es sich um kleine Dateien, die Ihr Browser automatisch erstellt und die auf Ihrem Endgerät (Notebook, Tablet, Smartphone etc.) gespeichert werden, wenn Sie unsere Seite besuchen. Cookies richten auf Ihrem Endgerät keinen Schaden an, enthalten keine Viren, Trojaner oder sonstige Schadsoftware.</p>
<p>Der Einsatz von Cookies dient einerseits dazu, die Nutzung unseres Angebots für Sie angenehmer zu gestalten. So setzen wir sog. Session-Cookies ein, um zu erkennen, dass Sie einzelne Seiten unserer Website bereits besucht haben. Diese werden nach Verlassen unserer Seite automatisch gelöscht. Dauerhafte Cookies werden nach Ihrer Einwilligung für 6 Monate gespeichert. Danach werden Sie beim Aufrufen unserer Website erneut gefragt, ob Sie mit der Cookie-Setzung (weiterhin) einverstanden sind.</p>
<p>Die durch Cookies verarbeiteten Daten sind für die genannten Zwecke zur Wahrung unserer berechtigten Interessen sowie der Dritter nach Art. 6 Abs. 1 S. 1 lit. f DSGVO erforderlich. Die meisten Browser akzeptieren Cookies automatisch. Sie können Ihren Browser jedoch so konfigurieren, dass keine Cookies auf Ihrem Computer gespeichert werden oder stets ein Hinweis erscheint, bevor ein neuer Cookie angelegt wird.</p>
<h2>5. Google Maps</h2>
<p>Auf unserer Webseite nutzen wir das Angebot von Google Maps. Dadurch können wir Ihnen interaktive Karten direkt in der Website anzeigen und ermöglichen Ihnen die komfortable Nutzung der Karten-Funktion. Durch den Besuch auf der Website erhält Google die Information, dass Sie die entsprechende Unterseite unserer Website aufgerufen haben. Weitere Informationen zu Zweck und Umfang der Datenerhebung und ihrer Verarbeitung durch den Plug-in-Anbieter erhalten Sie in den <a href="https://www.google.de/intl/de/policies/privacy" rel="noopener">Datenschutzerklärungen des Anbieters</a>.</p>
<h2>6. Kontaktformular</h2>
<p>Wenn Sie die von Ihnen im Kontaktformular eingegebenen Daten an uns übersenden, erklären Sie sich damit einverstanden, dass wir Ihre Angaben für die Beantwortung Ihrer Anfrage bzw. Kontaktaufnahme verwenden. Eine Weitergabe an Dritte findet grundsätzlich nicht statt, es sei denn geltende Datenschutzvorschriften rechtfertigen eine Übertragung oder wir sind dazu gesetzlich verpflichtet. Sie können Ihre erteilte Einwilligung jederzeit mit Wirkung für die Zukunft widerrufen. Im Falle des Widerrufs werden Ihre Daten umgehend gelöscht.</p>
<h2>7. Facebook</h2>
<p>Wir haben auf unserer Webseite Komponenten des Unternehmens Facebook integriert. Betreibergesellschaft von Facebook ist die Facebook, Inc., 1 Hacker Way, Menlo Park, CA 94025, USA. Durch jeden Aufruf einer der Einzelseiten dieser Internetseite, auf welcher eine Facebook-Komponente integriert wurde, wird der Internetbrowser automatisch veranlasst, eine Darstellung der entsprechenden Facebook-Komponente herunterzuladen. Die von Facebook veröffentlichte Datenrichtlinie, die unter <a href="https://de-de.facebook.com/about/privacy" rel="noopener">de-de.facebook.com/about/privacy</a> abrufbar ist, gibt Aufschluss über die Erhebung, Verarbeitung und Nutzung personenbezogener Daten durch Facebook.</p>
<h2>8. Datenschutzbestimmungen zu Einsatz und Verwendung von YouTube (und anderen Videodienstleistern)</h2>
<p>Wir haben auf unserer Webseite Komponenten von YouTube und/oder anderen Videodienstleistern integriert. Betreibergesellschaft von YouTube ist die YouTube, LLC, 901 Cherry Ave., San Bruno, CA 94066, USA. Sofern die betroffene Person gleichzeitig bei YouTube eingeloggt ist, erkennt YouTube mit dem Aufruf einer Unterseite, die ein YouTube-Video enthält, welche konkrete Unterseite dieser Internetseite die betroffene Person besucht. Die von YouTube veröffentlichten Datenschutzbestimmungen sind unter <a href="https://www.google.de/intl/de/policies/privacy" rel="noopener">www.google.de/intl/de/policies/privacy</a> abrufbar.</p>
<h2>9. Betroffenenrechte</h2>
<p>Sie haben das Recht:</p>
<p>gemäß Art. 15 DSGVO Auskunft über Ihre von uns verarbeiteten personenbezogenen Daten zu verlangen; gemäß Art. 16 DSGVO unverzüglich die Berichtigung unrichtiger oder Vervollständigung Ihrer bei uns gespeicherten personenbezogenen Daten zu verlangen; gemäß Art. 17 DSGVO die Löschung Ihrer bei uns gespeicherten personenbezogenen Daten zu verlangen; gemäß Art. 18 DSGVO die Einschränkung der Verarbeitung Ihrer personenbezogenen Daten zu verlangen; gemäß Art. 20 DSGVO Ihre personenbezogenen Daten, die Sie uns bereitgestellt haben, in einem strukturierten, gängigen und maschinenlesbaren Format zu erhalten; gemäß Art. 7 Abs. 3 DSGVO Ihre einmal erteilte Einwilligung jederzeit zu widerrufen; gemäß Art. 77 DSGVO sich bei einer Aufsichtsbehörde zu beschweren.</p>
<h2>10. Widerspruchsrecht</h2>
<p>Sofern Ihre personenbezogenen Daten auf Grundlage von berechtigten Interessen gemäß Art. 6 Abs. 1 S. 1 lit. f DSGVO verarbeitet werden, haben Sie das Recht, gemäß Art. 21 DSGVO Widerspruch gegen die Verarbeitung Ihrer personenbezogenen Daten einzulegen. Möchten Sie von Ihrem Widerrufs- oder Widerspruchsrecht Gebrauch machen, genügt eine E-Mail an <a href="mailto:info@sum-makler.de">info@sum-makler.de</a>.</p>
<h2>11. Datensicherheit</h2>
<p>Wir bedienen uns geeigneter technischer und organisatorischer Sicherheitsmaßnahmen, um Ihre Daten gegen zufällige oder vorsätzliche Manipulationen, teilweisen oder vollständigen Verlust, Zerstörung oder gegen den unbefugten Zugriff Dritter zu schützen. Unsere Sicherheitsmaßnahmen werden entsprechend der technologischen Entwicklung fortlaufend verbessert.</p>
<h2>12. Aktualität und Änderung dieser Datenschutzerklärung</h2>
<p>Durch die Weiterentwicklung unserer Website und Angebote oder aufgrund geänderter gesetzlicher beziehungsweise behördlicher Vorgaben kann es notwendig werden, diese Datenschutzerklärung zu ändern. Die jeweils aktuelle Datenschutzerklärung kann jederzeit auf dieser Seite von Ihnen abgerufen und ausgedruckt werden.</p>
</div></section>"""
    page(path="datenschutzerklarung/index.html", title="Datenschutzerklärung | Schneider & Musil Versicherungsmakler",
         desc="Datenschutzerklärung der Schneider & Musil Versicherungsmakler GbR – Informationen zur Erhebung und Verarbeitung personenbezogener Daten.",
         body=body)

def build_anfrage():
    body = """
<section class="error-hero">
  <div class="container">
    <h1>Wir freuen uns über Deine Nachricht!</h1>
    <p>Wir werden uns in Kürze bei Dir melden!<br>Viele Grüße<br><strong>Marco &amp; Max</strong></p>
    <a href="/" class="btn btn--solid">Zur Startseite</a>
  </div>
</section>"""
    page(path="anfrage/index.html", title="Danke für Deine Anfrage | Schneider & Musil",
         desc="Vielen Dank für Deine Nachricht – wir melden uns in Kürze bei Dir.", body=body, noindex=True)

def build_404():
    body = """
<section class="error-hero">
  <div class="container">
    <p class="code">404</p>
    <h1>Seite konnte nicht gefunden werden</h1>
    <p>Die Seite, die Du suchst, existiert nicht oder wurde verschoben.</p>
    <a href="/" class="btn btn--solid">Zur Startseite</a>
  </div>
</section>"""
    page(path="404.html", title="Seite nicht gefunden | Schneider & Musil",
         desc="Die angeforderte Seite existiert nicht.", body=body, noindex=True)

# ================================================================ SEO files
def build_seo_files(urls):
    entries = "".join(
        f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")

# ================================================================ main
def main():
    urls = []
    build_index(); urls.append(BASE + "/")
    build_termin(); urls.append(BASE + "/termin/")
    build_sparten_index(); urls.append(BASE + "/sparten/")
    for s in sparten:
        build_sparte_detail(s); urls.append(f"{BASE}/sparten/{s['Slug']}/")
    build_blog_index(); urls.append(BASE + "/blog/")
    for b in blogs:
        build_blog_detail(b); urls.append(f"{BASE}/sum-blog/{b['Slug']}/")
    build_impressum(); urls.append(BASE + "/impressum/")
    build_datenschutz(); urls.append(BASE + "/datenschutzerklarung/")
    build_anfrage()
    build_404()
    build_seo_files(urls)
    print(f"Built {len(urls)} indexable pages (+ anfrage, 404, sitemap, robots).")

if __name__ == "__main__":
    main()
