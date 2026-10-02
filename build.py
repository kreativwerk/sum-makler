# -*- coding: utf-8 -*-
"""Static site generator for sum-makler.de rebuild.

Reads _cms/sparten.csv and _cms/blogs.csv, writes the finished site to www/.
English version: translations in _cms/sparten_en.json and _cms/blogs_en.json
(keyed by slug), UI strings inline via T("deutsch", "english"); output in www/en/.
Run:  python3 build.py
"""
import csv
import html
import json
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

def read_json(name):
    path = os.path.join(ROOT, "_cms", name)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

SPARTEN_DE = read_csv("sparten.csv")
BLOGS_DE = read_csv("blogs.csv")
SPARTEN_EN_TX = read_json("sparten_en.json")
BLOGS_EN_TX = read_json("blogs_en.json")

# ---------------------------------------------------------------- i18n
LANG = "de"

def T(de, en):
    """Pick the UI string for the language currently being built."""
    return en if LANG == "en" else de

def U(p):
    """Absolute URL of a site path in the current language."""
    return BASE + ("/en" if LANG == "en" else "") + p

def overlay(rows, tx):
    out = []
    for row in rows:
        r2 = dict(row)
        r2.update({k: v for k, v in tx.get(row["Slug"], {}).items() if v is not None})
        out.append(r2)
    return out

CATS_DE = [  # (csv value, display, anchor id, icon)
    ("Sach und Kfz", "Sach & KFZ", "kfz", "icon-sach-kfz.svg"),
    ("Wohnung & Haus", "Wohnung & Haus", "haus", "icon-haus.svg"),
    ("Pflege & Krankheit", "Pflege & Krankheit", "pflege", "icon-pflege.svg"),
    ("Rente & Vorsorge", "Rente & Vorsorge", "rente", "icon-rente.svg"),
]
CAT_EN = {"kfz": "Property & Motor", "haus": "Home & House", "pflege": "Care & Health", "rente": "Pension & Retirement"}

def set_lang(lang):
    """Switch all content globals to the given language."""
    global LANG, sparten, blogs, CATS, by_cat
    LANG = lang
    sparten = overlay(SPARTEN_DE, SPARTEN_EN_TX) if lang == "en" else SPARTEN_DE
    blogs = overlay(BLOGS_DE, BLOGS_EN_TX) if lang == "en" else BLOGS_DE
    CATS = [(c, CAT_EN[a] if lang == "en" else d, a, i) for c, d, a, i in CATS_DE]
    by_cat = {c[0]: sorted([s for s in sparten if s["Kategorie"] == c[0]], key=lambda r: r["Name"]) for c in CATS}

set_lang("de")

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

def lang_switch(url_de, url_en):
    # __ROOT__ keeps these links from being rewritten to /en/ in page()
    de_cur = ' aria-current="true"' if LANG == "de" else ""
    en_cur = ' aria-current="true"' if LANG == "en" else ""
    return f"""<div class="lang-switch" role="group" aria-label="{T('Sprache wählen', 'Choose language')}">
      <a href="__ROOT__{url_de}" hreflang="de" lang="de"{de_cur} title="Deutsch">DE</a>
      <a href="__ROOT__{url_en}" hreflang="en" lang="en"{en_cur} title="English">EN</a>
    </div>"""

def header(active="", url_de="/", url_en="/en/"):
    def cur(k):
        return ' aria-current="page"' if k == active else ""
    return f"""<a class="skip-link" href="#main">{T('Zum Inhalt springen', 'Skip to content')}</a>
<header class="site-header">
  <nav class="nav" aria-label="{T('Hauptnavigation', 'Main navigation')}">
    <a href="/" class="nav-logo" aria-label="Schneider &amp; Musil – {T('Startseite', 'Home')}">
      <img src="/assets/img/logo-text.svg" alt="Schneider &amp; Musil {T('Versicherungsmakler', 'Insurance Brokers')}" width="180" height="40">
    </a>
    <div class="nav-socials">
      <a href="https://www.instagram.com/summakler/" rel="noopener" aria-label="Instagram"><img src="/assets/img/icon-instagram.svg" alt="" width="24" height="24" loading="lazy"></a>
      <a href="https://www.facebook.com/schneidermusilmakler/" rel="noopener" aria-label="Facebook"><img src="/assets/img/icon-facebook.svg" alt="" width="24" height="24" loading="lazy"></a>
      <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" aria-label="WhatsApp"><img src="/assets/img/icon-wa-round.svg" alt="" width="24" height="24" loading="lazy"></a>
    </div>
    <div class="nav-menu" id="nav-menu">
      <a href="/" class="nav-link"{cur('start')}>{T('Start', 'Home')}</a>
      <a href="/blog/" class="nav-link"{cur('blog')}>Blog</a>
      <a href="/#service" class="nav-link">Service</a>
      <div class="mega">
        <button aria-expanded="false" aria-haspopup="true">{T('Sparten', 'Insurance')} {CARET}</button>
        <div class="mega-panel">{mega_menu()}</div>
      </div>
      <div class="nav-cta">
        <a href="https://login.simplr.de/#/login" class="nav-portal" rel="noopener">{T('Kundenportal', 'Customer portal')}</a>
        <a href="/termin/" class="nav-book">{T('Termin buchen', 'Book appointment')}</a>
      </div>
      <div class="nav-social">
        <a href="https://www.instagram.com/summakler/" rel="noopener" aria-label="Instagram"><img src="/assets/img/icon-instagram.svg" alt="" width="28" height="28" loading="lazy"></a>
        <a href="https://www.facebook.com/schneidermusilmakler/" rel="noopener" aria-label="Facebook"><img src="/assets/img/icon-facebook.svg" alt="" width="28" height="28" loading="lazy"></a>
        <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" aria-label="WhatsApp"><img src="/assets/img/icon-wa-round.svg" alt="" width="28" height="28" loading="lazy"></a>
      </div>
    </div>
    {lang_switch(url_de, url_en)}
  </nav>
</header>"""

def fab_dock():
    """Floating dock: menu button (mobile only) + WhatsApp button."""
    return f"""<div class="fab-dock">
  <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="{T('Menü', 'Menu')}"><span class="nav-toggle-icon" aria-hidden="true"></span><span class="nav-toggle-label">{T('Menü', 'Menu')}</span></button>
  <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" class="wa-fab" aria-label="{T('Per WhatsApp schreiben', 'Message us on WhatsApp')}">
    <span class="wa-fab-icon"><img src="/assets/img/icon-whatsapp.svg" alt="" width="28" height="28"></span>
    <span class="wa-fab-text"><strong>WhatsApp</strong><span>{T('Jetzt direkt schreiben', 'Message us now')}</span></span>
  </a>
</div>"""

def footer():
    return f"""<footer class="site-footer">
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
      <nav class="footer-links" aria-label="{T('Footer Navigation', 'Footer navigation')}">
        <h3>Navigation</h3>
        <a href="/">{T('Start', 'Home')}</a>
        <a href="/blog/">Blog</a>
        <a href="/#service">Service</a>
        <a href="/#app">{T('Unsere App', 'Our app')}</a>
        <a href="/termin/">{T('Termin buchen', 'Book appointment')}</a>
      </nav>
      <nav class="footer-links" aria-label="{T('Sparten', 'Insurance')}">
        <h3><a href="/sparten/">{T('Sparten', 'Insurance')}</a></h3>
        {"".join(f'<a href="/sparten/#{a}">{e(d)}</a>' for _, d, a, _ in CATS)}
      </nav>
    </div>
    <div class="footer-bottom">
      <span>© {date.today().year} www.sum-makler.de</span>
      <div class="footer-legal">
        <a href="/impressum/">{T('Impressum', 'Legal notice')}</a>
        <a href="/datenschutzerklarung/">{T('Datenschutzerklärung', 'Privacy policy')}</a>
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
  "description": "__ORG_DESC__",
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
  "areaServed": ["Nürnberg", "Fürth", "Erlangen", "Metropolregion Nürnberg"],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+49 911 37758430",
    "email": "info@sum-makler.de",
    "contactType": "customer service",
    "availableLanguage": ["German", "English"]
  },
  "knowsAbout": [
    "Private Krankenversicherung", "Berufsunfähigkeitsversicherung", "Haftpflichtversicherung",
    "Hausratversicherung", "KFZ-Versicherung", "Rechtsschutzversicherung",
    "Altersvorsorge", "Wohngebäudeversicherung", "Beamtenversicherung"
  ],
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
         extra_ld=None, og_type="website", noindex=False, extra_head="", extra_js="", body_class=""):
    """Write a full HTML page. path is relative to www/, e.g. 'termin/index.html'
    (German); in English mode it is written to www/en/<path> automatically."""
    base_path = path
    if base_path.endswith("index.html"):
        url_de = "/" + os.path.dirname(base_path).replace(os.sep, "/")
        url_de = url_de.rstrip("/") + "/"
    else:
        url_de = "/"
    url_en = "/en" + url_de
    if LANG == "en":
        path = "en/" + path
    canonical = BASE + "/" + os.path.dirname(path).replace(os.sep, "/")
    canonical = canonical.rstrip("/") + "/" if os.path.dirname(path) else BASE + "/"
    if base_path == "404.html":
        canonical = BASE + ("/en" if LANG == "en" else "") + "/404.html"
    alternates = "" if noindex else (
        f'\n<link rel="alternate" hreflang="de" href="{BASE}{url_de}">'
        f'\n<link rel="alternate" hreflang="en" href="{BASE}{url_en}">'
        f'\n<link rel="alternate" hreflang="x-default" href="{BASE}{url_de}">')
    org_ld = ORG_LD.replace("__ORG_DESC__", T(
        "Unabhängige Versicherungsmakler aus der Metropolregion Nürnberg – persönliche und kostenfreie Beratung, 100% unabhängig, vollständig digital.",
        "Independent insurance brokers in the Nuremberg metropolitan region – personal and free advice in German and English, 100% independent, fully digital."))
    lds = [org_ld] + (extra_ld or [])
    ld_tags = "".join(f'<script type="application/ld+json">{ld}</script>' for ld in lds)
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    doc = f"""<!DOCTYPE html>
<html lang="{LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">{alternates}{robots}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Schneider &amp; Musil {T('Versicherungsmakler', 'Insurance Brokers')}">
<meta property="og:locale" content="{T('de_DE', 'en_GB')}">
<meta property="og:locale:alternate" content="{T('en_GB', 'de_DE')}">
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
{extra_head}
</head>
<body{f' class="{body_class}"' if body_class else ''}>
{header(active, url_de, url_en)}
<main id="main">
{body}
</main>
{footer()}{extra_js}
{fab_dock()}
</body>
</html>"""
    if LANG == "en":
        # interne Seiten-Links auf die englische Version umbiegen (Assets bleiben)
        doc = re.sub(r'\bhref="/(?!/|assets/|en/)', 'href="/en/', doc)
    doc = doc.replace('href="__ROOT__/', 'href="/')
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
    if topic:
        sub = T(f"Wir finden die passende {e(topic)} für Dich – kostenfrei, unabhängig und unverbindlich.",
                f"We will find the right {e(topic)} for you – free of charge, independent and without obligation.")
    else:
        sub = T("Wir beraten Dich kostenfrei, unabhängig und unverbindlich.",
                "We advise you free of charge, independently and without obligation.")
    return f"""<section class="section" aria-label="{T('Kontakt', 'Contact')}">
  <div class="container">
    <div class="kontakt-banner">
      <div class="kontakt-banner-left">
        <img src="/assets/img/logo-full.svg" alt="Schneider &amp; Musil {T('Versicherungsmakler', 'Insurance Brokers')}" width="240" height="117" loading="lazy">
        <p>Schneider &amp; Musil Versicherungsmakler GbR<br>Blütenstr. 41, 90765 Fürth</p>
      </div>
      <div class="kontakt-banner-right">
        <h2>{T('Wir freuen uns auf Deine Nachricht.', 'We look forward to hearing from you.')}</h2>
        <p>{sub}</p>
        <div class="kontakt-tiles">
          <a href="/termin/" class="kontakt-tile">
            <img src="/assets/img/arrow.svg" alt="" width="20" height="20" loading="lazy">
            <strong>{T('Termin buchen', 'Book appointment')}</strong><span>{T('online &amp; kostenfrei', 'online &amp; free of charge')}</span>
          </a>
          <a href="tel:+4991137758430" class="kontakt-tile">
            <img src="/assets/img/icon-tel.svg" alt="" width="20" height="20" loading="lazy">
            <strong>{T('Anrufen', 'Call us')}</strong><span>+49 (911) 37758430</span>
          </a>
          <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" class="kontakt-tile kontakt-tile--wa">
            <img src="/assets/img/icon-whatsapp.svg" alt="" width="20" height="20" loading="lazy">
            <strong>WhatsApp</strong><span>{T('direkt schreiben', 'message us directly')}</span>
          </a>
          <a href="mailto:info@sum-makler.de?subject={T('Unverbindliche%20Anfrage', 'Enquiry')}" class="kontakt-tile">
            <img src="/assets/img/icon-mail.svg" alt="" width="20" height="20" loading="lazy">
            <strong>E-Mail</strong><span>info@sum-makler.de</span>
          </a>
        </div>
        <div class="cta-checks kontakt-checks">{CHECKS()}</div>
      </div>
    </div>
  </div>
</section>"""

ARROW_BTN = '<span class="btn-icon"><img src="/assets/img/arrow.svg" alt="" width="16" height="16"></span>'
PHONE_BTN = '<span class="btn-icon btn-icon--phone"><img src="/assets/img/icon-phone-call.svg" alt="" width="16" height="16"></span>'

def CHECKS(sep=""):
    return sep.join(f"<span>✔ {x}</span>" for x in (T("kostenfrei", "free of charge"), T("unverbindlich", "no obligation"), T("unkompliziert", "hassle-free")))

def cta_buttons():
    return f"""<div class="cta-row">
  <a href="/termin/" class="btn">{ARROW_BTN}{T('Termin buchen', 'Book appointment')}</a>
  <a href="tel:+4991137758430" class="btn btn--ghost">{PHONE_BTN}{T('Jetzt anrufen', 'Call now')}</a>
</div>"""

CHECK_SVG = ('<svg class="check-circle" viewBox="0 0 40 40" aria-hidden="true">'
             '<circle class="halo" cx="20" cy="20" r="20"/>'
             '<circle class="ring" cx="20" cy="20" r="12.5"/>'
             '<path class="tick" d="M14 20.5l4.5 4.5 9.5-10.5"/></svg>')

TESTIMONIALS_EN = [  # translated from the German originals on Google
    "Great advice with flexible communication. A customer for several years – I can be sure I always get the best offer – a partner I trust!",
    "Trust, outstanding expertise and individual service for the client are top priorities here! 5 stars are not enough!",
    "I can only speak very positively! Both gentlemen have helped me quickly and easily in every situation so far. I never felt like anyone was trying to talk me into something.",
    "Really very satisfied! Everyone is incredibly friendly! Always reachable by phone. I feel well advised and in good hands. Highly recommended.",
    "Absolutely recommended, always friendly and helpful, even when things need to move quickly. Modern and straightforward processes, clear explanations for every question.",
    "The car damage claim was settled promptly and to my complete satisfaction. Great to get exactly the support you'd hope for in a situation like that!",
]

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
        if LANG == "en":
            text = TESTIMONIALS_EN[i]
        slides += f"""<article class="slide{' active' if i == 0 else ''}">
  <div class="slide-head">
    <img class="g-logo" src="/assets/img/google-g.svg" alt="Google" width="20" height="20" loading="lazy">
    <img class="stars" src="/assets/img/sterne-5.svg" alt="{T('5 von 5 Sternen', '5 out of 5 stars')}" width="110" height="18" loading="lazy">
    <span class="slide-verified">{T('von Google verifiziert', 'verified by Google · translated')}</span>
  </div>
  <p class="slide-text">{e(text)}</p>
  <div class="slide-person">
    <img src="/assets/img/{img}" alt="" width="38" height="38" loading="lazy">
    <span>{e(name)}</span>
  </div>
</article>"""
    chev_l = '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4l-8 8 8 8"/></svg>'
    chev_r = '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 4l8 8-8 8"/></svg>'
    return f"""<div class="slider" data-slider aria-label="{T('Google Bewertungen', 'Google reviews')}">
  <button class="slider-arrow slider-arrow--prev" data-prev aria-label="{T('Vorherige Bewertung', 'Previous review')}">{chev_l}</button>
  <div class="slide-track">{slides}</div>
  <button class="slider-arrow slider-arrow--next" data-next aria-label="{T('Nächste Bewertung', 'Next review')}">{chev_r}</button>
  <div class="slider-dots"></div>
</div>"""

# ================================================================ INDEX
faq_ld_home_de = """{
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

faq_ld_home_en = """{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "How much does advice from Schneider & Musil cost?",
     "acceptedAnswer": {"@type": "Answer", "text": "Our advice is 100% free of charge and without obligation. Based on your current situation and your individual needs, we present suitable options to you."}},
    {"@type": "Question", "name": "What is the difference between an insurance broker and an insurance agent?",
     "acceptedAnswer": {"@type": "Answer", "text": "An insurance broker (§ 93 HGB) acts independently on behalf of the customer and can freely choose products from all insurers. An insurance agent (§ 84 HGB) acts on behalf of an insurer and is bound by its instructions and products."}},
    {"@type": "Question", "name": "What happens in the first consultation?",
     "acceptedAnswer": {"@type": "Answer", "text": "1. Introduction: we explain who we are and how we work. 2. Analysis: together we get an overview of your wishes and goals. 3. Discussing the options: we present recommendations and offers. 4. We give you security: we take care of everything from then on, right through to claims handling."}}
  ]
}"""

HGB93_DE = '(1) Wer gewerbsmäßig für andere Personen, ohne von ihnen auf Grund eines Vertragsverhältnisses ständig damit betraut zu sein, die Vermittlung von Verträgen über Anschaffung oder Veräußerung von Waren oder Wertpapieren, über Versicherungen, Güterbeförderungen, Schiffsmiete oder sonstige Gegenstände des Handelsverkehrs übernimmt, hat die Rechte und Pflichten eines Handelsmaklers.'
HGB93_EN = '(1) Anyone who, on a commercial basis and without being permanently engaged to do so under a contractual relationship, undertakes for other persons the brokering of contracts for the purchase or sale of goods or securities, insurance, the carriage of goods, ship chartering or other objects of commercial trade has the rights and obligations of a commercial broker. <em>(Unofficial translation of the German Commercial Code.)</em>'

MORE = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5"/></svg>'

def build_index():
    latest = blogs[:3]
    blog_cards = ""
    for b in latest:
        blog_cards += f"""<a href="/sum-blog/{b['Slug']}/" class="blog-card reveal">
  <span class="blog-tag">{e(b['Kategorie'])}</span>
  <h3>{e(b['Name'])}</h3>
  <p>{e(b['Headline'])}</p>
  <span class="blog-more">{T('Mehr erfahren', 'Read more')} {MORE}</span>
</a>"""

    timeline_steps = [
        (T("1. Vorstellung", "1. Introduction"), "service-1.svg", T("Wir stellen uns vor und erklären Dir genau, wer wir sind und wie wir arbeiten. Wir erklären Dir den Unterschied zwischen einem Versicherungsvertreter und einem Versicherungsmakler, aber auch den Unterschied zu anderen Maklerkollegen und was uns ausmacht.",
            "We introduce ourselves and explain exactly who we are and how we work. We explain the difference between an insurance agent and an insurance broker, as well as how we differ from other brokers and what sets us apart.")),
        (T("2. Analyse", "2. Analysis"), "service-2.svg", T("Wir verschaffen uns einen gemeinsamen Überblick, sprechen über Deine individuellen Wünsche und Ziele, aber auch darüber, was Dir besonders wichtig ist.",
            "Together we get an overview, talk about your individual wishes and goals, and about what matters most to you.")),
        (T("3. Besprechung der Möglichkeiten", "3. Discussing your options"), "service-3.svg", T("Wir besprechen unsere erarbeitete Analyse. Wir stellen Dir unsere Empfehlungen und Angebote vor, geben Dir Tipps für Deine optimale und sinnvolle Absicherung.",
            "We go through our analysis with you, present our recommendations and offers, and give you tips for optimal, sensible cover.")),
        (T("4. Wir geben Sicherheit", "4. We give you security"), "service-4.svg", T("Ab jetzt heißt es für Dich zurücklehnen. Um alles Weitere kümmern wir uns – von der zukünftigen Betreuung bis hin zur kompletten Schadenabwicklung.",
            "From now on you can sit back and relax. We take care of everything else – from ongoing support right through to handling your claims.")),
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

    makler_points = T(["Handelt für den Mandanten", "Ist im Auftrag des Kunden tätig", "Ungebunden / Unabhängig",
                       "Versicherer hat kein Weisungsrecht", "Freie Produktwahl"],
                      ["Acts for the client", "Works on the customer's behalf", "Unbound / independent",
                       "Insurer cannot give instructions", "Free choice of products"])
    vertreter_points = T(["Handelt für den Versicherer", "Im Auftrag des Versicherers tätig", "Gebunden / Abhängig",
                          "Weisung des Versicherers", "Produktauswahl des Versicherers"],
                         ["Acts for the insurer", "Works on the insurer's behalf", "Bound / dependent",
                          "Follows the insurer's instructions", "Insurer's product range only"])
    mk = "".join(f'<div class="vs-point"><img src="/assets/img/check-blau.svg" alt="{T("Vorteil:", "Advantage:")}" width="22" height="22" loading="lazy">{e(p)}</div>' for p in makler_points)
    vt = "".join(f'<div class="vs-point"><img src="/assets/img/x-circle.svg" alt="{T("Nachteil:", "Disadvantage:")}" width="22" height="22" loading="lazy">{e(p)}</div>' for p in vertreter_points)

    vorteile_en = [
        ("Free & without obligation", "Our advice is 100% free of charge and without obligation. Based on your current situation and your individual needs, we present suitable options to you.", ["Personal advice", "Completely free of charge"]),
        ("Independent experts", "Whether it's private health insurance or cover for civil servants – we are 100% independent and only recommend insurers we are convinced of ourselves.", ["Specialised brokers", "100% independent"]),
        ("One direct contact", "With us there's no hotline and no changing contacts – our team is always there for all your questions and concerns.", ["No annoying hotline", "Simple and convenient"]),
        ("Advice from anywhere", "Wherever you are and whatever cover you need – we help you get properly insured. In person, online or by phone.", ["Fully digital", "Saves you time"]),
    ]
    vorteile = [
        ("Kostenfrei & unverbindlich", "Unsere Beratung ist zu 100% kostenlos und unverbindlich. Ausgehend von Deiner aktuellen Situation und Deinen individuellen Bedürfnissen stellen wir Dir passende Möglichkeiten vor.", ["Persönlich beraten", "Vollkommen kostenfrei"]),
        ("Unabhängige Experten", "Egal ob es um die private Krankenversicherung oder z. B. Beamte geht. Wir sind zu 100% unabhängig und empfehlen Dir nur Versicherer, von welchen wir selbst überzeugt sind.", ["Spezialisierte Makler", "Zu 100% unabhängig"]),
        ("Direkter Ansprechpartner", "Bei uns gibt es keine Hotline und keine wechselnden Gesprächspartner – unser Team steht Dir für alle Anliegen und Fragen jederzeit zur Verfügung.", ["Keine nervige Hotline", "Einfach und bequem"]),
        ("Ortsunabhängige Beratung", "Egal wo Du Dich gerade befindest und welche Absicherung Du Dir wünschst – wir helfen Dir, Dich richtig abzusichern. Egal ob persönlich, online oder telefonisch.", ["Vollständig digital", "Zeitersparnis"]),
    ]
    if LANG == "en":
        vorteile = vorteile_en
    vorteile_html = ""
    for i, (t, txt, points) in enumerate(vorteile):
        pts = "".join(f'<div class="vorteil-point"><img src="/assets/img/check-ring.svg" alt="" width="24" height="24" loading="lazy">{e(p)}</div>' for p in points)
        vorteile_html += f'<div class="vorteil-card" style="--i:{i}"><h3>{e(t)}</h3><p>{e(txt)}</p><div class="vorteil-points">{pts}</div></div>'

    body = f"""
<div class="preloader" id="preloader" aria-hidden="true"><div class="preloader-anim" id="preloaderAnim"><div class="preloader-dot"></div></div></div>
<section class="hero" id="start">
  <div class="container hero-grid">
    <div>
      <p class="hero-label">{T('Persönlich versichert', 'Personally insured')}</p>
      <h1>{T('Wir sind Deine <strong>unabhängigen</strong> Versicherungsmakler aus der Metropolregion Nürnberg', 'We are your <strong>independent</strong> insurance brokers in the Nuremberg metropolitan region')}</h1>
      <p class="hero-sub">{T('Buche jetzt einen Termin für eine <strong>persönliche &amp; kostenfreie</strong> Beratung!', 'Book an appointment now for <strong>personal &amp; free</strong> advice!')}</p>
      {cta_buttons()}
      <div class="rating" data-rating-celebrate>
        <strong>{T('5,0', '5.0')}</strong>
        <img class="stars" src="/assets/img/sterne-5.svg" alt="{T('5 von 5 Sternen bei Google', '5 out of 5 stars on Google')}" width="110" height="20">
        <span class="rating-count"><span class="rating-num" data-count-to="200">200</span> {T('Google Rezensionen', 'Google reviews')}</span>
        <img class="badge" src="/assets/img/google-badge-160.webp" srcset="/assets/img/google-badge-160.webp 1x, /assets/img/google-badge-320.webp 2x" alt="Google" width="66" height="44" loading="lazy">
      </div>
    </div>
    <div class="hero-visual">
      <div class="photo-wrap">
        <img class="pattern" src="/assets/img/grosse-auswahl.svg" alt="" aria-hidden="true">
        <img class="hero-photo" src="/assets/img/hero-team-800.webp"
             srcset="/assets/img/hero-team-480.webp 480w, /assets/img/hero-team-800.webp 800w, /assets/img/hero-team-1035.webp 1035w"
             sizes="(min-width: 992px) 45vw, 90vw" width="723" height="669" fetchpriority="high"
             alt="{T('Marco Musil und Maximilian Schneider – unabhängige Versicherungsmakler aus der Metropolregion Nürnberg', 'Marco Musil and Maximilian Schneider – independent insurance brokers in the Nuremberg metropolitan region')}">
        {slider_html()}
      </div>
    </div>
  </div>
</section>

<section class="feature-bar" aria-label="{T('Unsere Versprechen', 'Our promises')}">
  <div class="container feature-bar-inner">
    <div class="feature-item">{CHECK_SVG}<span>{T('100% unabhängig', '100% independent')}</span></div>
    <div class="feature-item">{CHECK_SVG}<span>{T('Vollkommen kostenfrei', 'Completely free of charge')}</span></div>
    <div class="feature-item">{CHECK_SVG}<span>{T('Vollständig digital', 'Fully digital')}</span></div>
  </div>
</section>

<section class="video-section">
  <video data-lazy autoplay muted loop playsinline preload="none" poster="/assets/video/hero-desktop-poster.jpg" aria-hidden="true" tabindex="-1">
    <source data-src="/assets/video/hero-desktop.webm" type="video/webm">
    <source data-src="/assets/video/hero-desktop.mp4" type="video/mp4">
  </video>
  <div class="container video-content">
    <div class="video-text">
      <h2>{T('Wir versichern Dich.<br><strong>persönlich &amp; digital</strong>', 'We insure you.<br><strong>personal &amp; digital</strong>')}</h2>
      <p>{T('Buche jetzt einen Termin für eine<br><strong>persönliche &amp; kostenfreie</strong> Beratung!', 'Book an appointment now for<br><strong>personal &amp; free</strong> advice!')}</p>
      <div class="cta-row">
        <a href="/termin/" class="btn">{ARROW_BTN}{T('Termin buchen', 'Book appointment')}</a>
        <a href="#app" class="btn btn--ghost">{ARROW_BTN}{T('Unsere App', 'Our app')}</a>
      </div>
    </div>
  </div>
</section>

<section class="timeline-section" id="service">
  <div class="container">
    <div class="timeline-head reveal">
      <p class="eyebrow"><strong>{T('Unser Beratungsservice', 'Our advisory service')}</strong></p>
      <h2>{T('Das erwartet Dich in unserem ersten kostenlosen und unverbindlichen Beratungsgespräch', 'What to expect in your first free, no-obligation consultation')}</h2>
    </div>
  </div>
  {timeline_html}
  <div class="timeline-cta reveal">
    <div class="container">
      <h2>{T('Wir freuen uns auf Deine Anfrage.', 'We look forward to your enquiry.')}</h2>
      <p>{T('Ganz bequem per Telefon, E-Mail, WhatsApp oder Social Media', 'Conveniently by phone, email, WhatsApp or social media')}</p>
      <a href="/termin/" class="btn btn--solid">{T('Jetzt Termin vereinbaren', 'Book an appointment now')}&nbsp;<img src="/assets/img/pfeil-weiss.svg" alt="" width="26" height="26"></a>
      <div class="cta-checks">{CHECKS(" ")}</div>
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
      <h2>{T('Verwaltungschaos?', 'Paperwork chaos?')}</h2>
      <p>{T('… wir <strong>digitalisieren</strong> Deinen Versicherungsordner!', '… we <strong>digitalise</strong> your insurance folder!')}</p>
    </div>
    <div class="app-grid">
      <div class="app-phone reveal">
        <img src="/assets/img/app-05-400.webp" srcset="/assets/img/app-05-400.webp 400w, /assets/img/app-05-800.webp 800w" sizes="250px" width="250" height="507" loading="lazy" alt="{T('Versicherungsapp von Schneider und Musil – Übersicht Deiner Verträge', 'Schneider & Musil insurance app – overview of your contracts')}">
        <div class="app-feature">
          <h3><img src="/assets/img/check-blau.svg" alt="" width="26" height="26" loading="lazy">{T('Überall dabei.', 'Always with you.')}</h3>
          <p>{T('Nie mehr einen Versicherungsschein suchen, wenn man diesen braucht. Mit unserer App hast Du alle Deine wichtigen Daten immer griffbereit.', 'Never search for an insurance policy again when you need it. With our app, all your important data is always at hand.')}</p>
        </div>
      </div>
      <div class="app-phone reveal reveal-d1">
        <img src="/assets/img/app-06-400.webp" srcset="/assets/img/app-06-400.webp 400w, /assets/img/app-06-800.webp 800w" sizes="250px" width="250" height="507" loading="lazy" alt="{T('Versicherungsapp von Schneider und Musil – Police-Vorschau', 'Schneider & Musil insurance app – policy preview')}">
        <div class="app-feature">
          <h3><img src="/assets/img/check-blau.svg" alt="" width="26" height="26" loading="lazy">{T('Dein Schutz.', 'Your protection.')}</h3>
          <p>{T('Der Schutz Deiner Daten ist uns besonders wichtig! Deshalb werden Deine Daten ausschließlich verschlüsselt übertragen.', 'Protecting your data is especially important to us! That is why your data is only ever transmitted encrypted.')}</p>
        </div>
      </div>
      <div class="app-phone reveal reveal-d2">
        <img src="/assets/img/app-07-400.webp" srcset="/assets/img/app-07-400.webp 400w, /assets/img/app-07-800.webp 800w" sizes="250px" width="250" height="507" loading="lazy" alt="{T('Versicherungsapp von Schneider und Musil – direkter Kontakt', 'Schneider & Musil insurance app – direct contact')}">
        <div class="app-feature">
          <h3><img src="/assets/img/check-blau.svg" alt="" width="26" height="26" loading="lazy">{T('Persönlich.', 'Personal.')}</h3>
          <p>{T('Wir stehen Dir mit Rat und Tat auch vor Ort und nicht nur per Telefon, E-Mail oder SMS zur Seite. Online muss nicht anonym sein.', 'We support you with advice and action in person too – not just by phone, email or text. Online doesn’t have to mean anonymous.')}</p>
        </div>
      </div>
    </div>
    <div class="app-cta reveal">
      <h2>{T('Du möchtest Deinen Versicherungsordner auch digitalisieren?', 'Would you like to digitalise your insurance folder too?')}</h2>
      <p>{T('Du kannst uns per Telefon, E-Mail, WhatsApp oder Social Media erreichen.', 'You can reach us by phone, email, WhatsApp or social media.')}</p>
      <div class="cta-row" style="justify-content:center">
        <a href="/termin/" class="btn">{ARROW_BTN}{T('Termin buchen', 'Book appointment')}</a>
        <a href="tel:+4991137758430" class="btn btn--ghost">{PHONE_BTN}{T('Jetzt anrufen', 'Call now')}</a>
      </div>
    </div>
  </div>
</section>

<section class="section team-section" id="team">
  <div class="container team-vorteile">
    <div class="team-col">
      <h2 class="split-head">{T('Unser Team', 'Our team')}</h2>
      <div class="team-list">
      <div class="team-member reveal">
        <img src="/assets/img/team-max-400.webp" width="128" height="128" loading="lazy" alt="Maximilian Schneider, {T('Versicherungsfachmann (IHK)', 'Certified Insurance Specialist (IHK)')}">
        <div><h3>Maximilian Schneider</h3><p>{T('Versicherungsfachmann (IHK)', 'Certified Insurance Specialist (IHK)')}</p></div>
      </div>
      <div class="team-member reveal reveal-d1">
        <img src="/assets/img/team-marco-400.webp" width="128" height="128" loading="lazy" alt="Marco Musil, {T('Diplom Betriebswirt (FH)', 'Graduate in Business Administration (FH)')}">
        <div><h3>Marco Musil</h3><p>{T('Diplom Betriebswirt (FH)', 'Graduate in Business Administration (FH)')}</p></div>
      </div>
      <div class="team-member reveal reveal-d2">
        <img src="/assets/img/team-justin-400.webp" width="128" height="128" loading="lazy" alt="Justin Duensing, Office Manager">
        <div><h3>Justin Duensing</h3><p>Office Manager</p></div>
      </div>
      </div>
    </div>
    <div class="vorteile-col">
      <h2 class="split-head">{T('Deine Vorteile', 'Your benefits')}</h2>
      <div class="vorteile-grid">
        {vorteile_html}
        <div class="vorteil-card kontakt-card" style="--i:4">
          <h3>{T('Termin vereinbaren', 'Book an appointment')}</h3>
          <p>{T('Wie Du uns erreichen kannst:', 'How to reach us:')}</p>
          <div class="kontakt-links">
            <a href="tel:+4991137758430"><img src="/assets/img/icon-tel.svg" alt="" width="24" height="24" loading="lazy">{T('Telefon', 'Phone')}</a>
            <a href="https://wa.me/message/N5OLZTL577ELP1" rel="noopener" class="kontakt-link--wa"><img src="/assets/img/icon-whatsapp.svg" alt="" width="24" height="24" loading="lazy">WhatsApp</a>
            <a href="mailto:info@sum-makler.de?subject={T('Unverbindliche%20Anfrage', 'Enquiry')}"><img src="/assets/img/icon-mail.svg" alt="" width="24" height="24" loading="lazy">E-Mail</a>
          </div>
          <a href="/termin/" class="btn">{ARROW_BTN}{T('Termin buchen', 'Book appointment')}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="vs-section section">
  <div class="container">
    <div class="vs-head reveal">
      <h2>{T('Verwechslungsgefahr…', 'Easily confused…')}</h2>
      <p>{T('Wichtige Unterscheidung zwischen „<strong>Versicherungsmakler</strong>“ und „<strong>Versicherungsvertreter</strong>“:<br><strong>Wir klären Euch auf:</strong>', 'An important distinction between an “<strong>insurance broker</strong>” and an “<strong>insurance agent</strong>”:<br><strong>Here’s the difference:</strong>')}</p>
    </div>
    <div class="vs-grid">
      <div class="vs-badge" aria-hidden="true">vs</div>
      <div class="vs-card makler reveal">
        <h3>{T('Makler', 'Broker')}</h3>
        <details class="vs-law">
          <summary>{T('Rechtsposition', 'Legal basis')}: <strong>§ 93 (1) {T('Satz 1', 'sentence 1')} HGB</strong><img src="/assets/img/caret-down.svg" alt="" width="16" height="16" loading="lazy"></summary>
          <div class="vs-law-body">{T(HGB93_DE, HGB93_EN)}</div>
        </details>
        {mk}
        <img class="vs-underline" src="/assets/img/underline.svg" alt="" width="340" height="20" loading="lazy">
      </div>
      <div class="vs-card reveal reveal-d1">
        <h3>{T('Vertreter', 'Agent')}</h3>
        <details class="vs-law">
          <summary>{T('Rechtsposition', 'Legal basis')}: <strong>§ 84 (1) {T('Satz 1', 'sentence 1')} HGB</strong><img src="/assets/img/caret-down.svg" alt="" width="16" height="16" loading="lazy"></summary>
          <div class="vs-law-body">{T('(1) Handelsvertreter ist, wer als selbständiger Gewerbetreibender ständig damit betraut ist, für einen anderen Unternehmer Geschäfte zu vermitteln oder in dessen Namen abzuschließen.', '(1) A commercial agent is a self-employed trader who is permanently engaged to broker transactions for another business or to conclude them in its name. <em>(Unofficial translation of the German Commercial Code.)</em>')}</div>
        </details>
        {vt}
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    <div class="blog-head reveal">
      <h2>{T('Unser Blog', 'Our blog')}</h2>
      <p>{T('<strong>Wissenswertes über Versicherungen:</strong><br>Informiere Dich für eine optimale Absicherung', '<strong>Useful insights on insurance:</strong><br>Get informed for optimal cover')}</p>
    </div>
    <div class="blog-grid">{blog_cards}</div>
    <div class="cta-mid" style="padding-bottom:0">
      <a href="/blog/" class="btn btn--solid">{T('Alle Blogbeiträge', 'All blog posts')}&nbsp;<img src="/assets/img/pfeil-weiss.svg" alt="" width="26" height="26"></a>
    </div>
  </div>
</section>"""
    page(
        path="index.html", active="start",
        title=T("Schneider & Musil | Unabhängige Versicherungsmakler Nürnberg & Fürth", "Schneider & Musil | Independent Insurance Brokers Nuremberg & Fürth"),
        desc=T("Deine unabhängigen Versicherungsmakler aus Nürnberg & Fürth. Persönliche, kostenfreie Beratung – 100% unabhängig & digital. Jetzt Termin buchen!",
               "Your independent insurance brokers in Nuremberg & Fürth. Personal, free advice in English – 100% independent & digital. Book an appointment now!"),
        body=body, extra_ld=[T(faq_ld_home_de, faq_ld_home_en)],
    )

# ================================================================ TERMIN
def build_termin():
    # Schritt 1: Sprache des Termins wählen (Deutsch → Max oder Marco, Englisch → nur Marco).
    # Ohne JavaScript wird die Auswahl übersprungen und beide Makler werden angezeigt.
    body = f"""
<div class="termin-flow" data-termin-flow>
<section class="page-hero">
  <div class="container">
    <h1>{T('Termin vereinbaren', 'Book an appointment')}</h1>
    <p>{T('Egal, ob Du lieber online, telefonisch oder persönlich beraten werden möchtest – wir passen uns Deinen Präferenzen an. Vereinbare Deinen Termin und erhalte individuelle Lösungen, die zu Dir passen.',
          'Whether you prefer advice online, by phone or in person – we adapt to your preferences. Book your appointment and get individual solutions that suit you.')}</p>
    <div class="termin-lang">
      <p><strong style="color:#fff">{T('In welcher Sprache möchtest Du Deinen Termin wahrnehmen?', 'In which language would you like your appointment?')}</strong></p>
      <div class="termin-choose" role="group" aria-label="{T('Sprache des Termins', 'Appointment language')}">
        <button type="button" data-termin-lang="de" aria-pressed="false">Deutsch</button><span class="or">{T('oder', 'or')}</span><button type="button" data-termin-lang="en" aria-pressed="false">English</button>
      </div>
    </div>
    <div class="termin-step2">
      <p><strong style="color:#fff">{T('Termin vereinbaren mit:', 'Book your appointment with:')}</strong></p>
      <div class="termin-choose">
        <a href="#max" class="only-de">Max</a><span class="or only-de">{T('oder', 'or')}</span><a href="#marco">Marco</a>
      </div>
      <p class="termin-en-note only-en">{T('Beratungen auf Englisch führt Marco Musil für Dich durch.', 'Marco Musil will advise you in English.')}</p>
    </div>
  </div>
</section>
<section class="section termin-section">
  <img class="bg-logo" src="/assets/img/hero-bg.svg" alt="" aria-hidden="true">
  <div class="container makler-grid">
    <article class="makler-card reveal only-de" id="max">
      <img src="/assets/img/makler-max-500.webp" srcset="/assets/img/makler-max-500.webp 500w, /assets/img/makler-max-800.webp 800w" sizes="(min-width: 900px) 357px, 86vw" width="357" height="446" alt="Maximilian Schneider, {T('Versicherungsfachmann (IHK)', 'Certified Insurance Specialist (IHK)')}">
      <div class="makler-card-info">
        <h2>Max Schneider</h2>
        <p class="role">{T('Versicherungsfachmann (IHK)', 'Certified Insurance Specialist (IHK)')}</p>
        <p class="sub">{T('Freier Makler nach §93 HGB', 'Independent broker under §93 HGB')}</p>
        <a class="tel" href="tel:+4917680185940">0176 80 18 59 40</a>
        <a class="mail" href="mailto:schneider@sum-makler.de">schneider@sum-makler.de</a>
        <div><a href="https://calendly.com/sum-schneider/beratung" target="_blank" rel="noopener" class="btn">{ARROW_BTN}{T('Termin online buchen', 'Book online')}</a></div>
      </div>
    </article>
    <img class="makler-logo only-de" src="/assets/img/logo-full.svg" alt="" width="300" height="120" loading="lazy">
    <article class="makler-card reveal reveal-d1" id="marco">
      <img src="/assets/img/makler-marco-500.webp" srcset="/assets/img/makler-marco-500.webp 500w, /assets/img/makler-marco-800.webp 800w" sizes="(min-width: 900px) 357px, 86vw" width="357" height="446" loading="lazy" alt="Marco Musil, {T('Diplom Betriebswirt (FH)', 'Graduate in Business Administration (FH)')}">
      <div class="makler-card-info">
        <h2>Marco Musil</h2>
        <p class="role">{T('Diplom Betriebswirt (FH)', 'Graduate in Business Administration (FH)')}</p>
        <p class="sub">{T('Freier Makler nach §93 HGB', 'Independent broker under §93 HGB')}</p>
        <p class="sub langs">{T('Beratung auf Deutsch &amp; Englisch', 'Advice in German &amp; English')}</p>
        <a class="tel" href="tel:+491792936633">0179 29 36 63 3</a>
        <a class="mail" href="mailto:musil@sum-makler.de">musil@sum-makler.de</a>
        <div><a href="https://calendly.com/musil/60min" target="_blank" rel="noopener" class="btn">{ARROW_BTN}{T('Termin online buchen', 'Book online')}</a></div>
      </div>
    </article>
  </div>
</section>
</div>"""
    page(
        path="termin/index.html",
        title=T("Beratungstermin buchen | Schneider & Musil Versicherungsmakler", "Book a consultation | Schneider & Musil Insurance Brokers"),
        desc=T("Vereinbare jetzt Deinen unverbindlichen Beratungstermin – online, telefonisch oder persönlich. Kostenfreie Versicherungsberatung mit Max Schneider oder Marco Musil.",
               "Book your free, no-obligation consultation now – online, by phone or in person. Insurance advice in English with Marco Musil."),
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
    <nav class="breadcrumbs" aria-label="{T('Brotkrumen', 'Breadcrumb')}"><a href="/">{T('Start', 'Home')}</a> / <span aria-current="page">{T('Sparten', 'Insurance')}</span></nav>
    <h1>{T('Versicherungssparten', 'Types of insurance')}</h1>
    <p>{T('Von Autoversicherungen bis zur Altersvorsorge – wir haben alles abgedeckt. Wir helfen Dir gerne bei der richtigen Auswahl. Finde jetzt die passende Absicherung für Dich.', 'From car insurance to retirement planning – we have everything covered. We are happy to help you make the right choice. Find the right cover for you now.')}</p>
  </div>
</section>
{sections}
{kontakt_section()}"""
    page(
        path="sparten/index.html",
        title=T("Versicherungssparten im Überblick | Schneider & Musil", "Types of insurance at a glance | Schneider & Musil"),
        desc=T("Alle Versicherungssparten im Überblick: Sach & KFZ, Wohnung & Haus, Pflege & Krankheit, Rente & Vorsorge. Unabhängige Beratung aus Nürnberg & Fürth.",
               "All types of insurance at a glance: property & motor, home, care & health, pension & retirement. Independent advice in English from Nuremberg & Fürth."),
        body=body,
        extra_ld=[breadcrumb_ld([(T("Start", "Home"), U("/")), (T("Sparten", "Insurance"), U("/sparten/"))])],
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
    <nav class="breadcrumbs" aria-label="{T('Brotkrumen', 'Breadcrumb')}"><a href="/">{T('Start', 'Home')}</a> / <a href="/sparten/">{T('Sparten', 'Insurance')}</a> / <span aria-current="page">{e(name)}</span></nav>
    <p class="hero-label">{e(cat[1])}</p>
    <h1>{e(name)}</h1>
    <p><strong style="color:#fff">{e(s['Headline'])}</strong></p>
    <p>{e(s['Einleitung Hero'])}</p>
    <div class="cta-row" style="justify-content:center;margin-top:28px;margin-bottom:0">
      <a href="/termin/" class="btn">{ARROW_BTN}{T('Kostenfreie Beratung', 'Free consultation')}</a>
      <a href="tel:+4991137758430" class="btn btn--ghost">{PHONE_BTN}{T('Jetzt anrufen', 'Call now')}</a>
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
    <div class="blog-head"><h2>{T(f'Häufige Fragen zur {e(name)}', f'Frequently asked questions: {e(name)}')}</h2></div>
    <div class="faq-list">{faqs}</div>
  </div>
</section>
{kontakt_section(name)}
<section class="section" style="padding-top:0">
  <div class="container">
    <h2 class="split-head">{T('Weitere Sparten', 'More insurance')}: {e(cat[1])}</h2>
    <div class="sparten-grid">{related}</div>
  </div>
</section>"""
    page(
        path=f"sparten/{slug}/index.html",
        title=T(f"{name} in Nürnberg & Fürth | Schneider & Musil", f"{name} in Nuremberg & Fürth | Schneider & Musil"),
        desc=(s["Einleitung Hero"][:155] + "…") if len(s["Einleitung Hero"]) > 158 else s["Einleitung Hero"],
        body=body,
        extra_ld=[faq_ld, breadcrumb_ld([(T("Start", "Home"), U("/")), (T("Sparten", "Insurance"), U("/sparten/")), (e(name), U(f"/sparten/{slug}/"))])],
    )

def jstr(s):
    import json
    return json.dumps(s, ensure_ascii=False)

# ================================================================ BLOG
def build_blog_index():
    cards = ""
    for b in blogs:
        cat_slug = "wissen" if b["Kategorie"] in ("Wissen", "Knowledge") else "checkliste"
        cards += f"""<a href="/sum-blog/{b['Slug']}/" class="blog-card" data-cat="{cat_slug}">
  <span class="blog-tag">{e(b['Kategorie'])}</span>
  <h3>{e(b['Name'])}</h3>
  <p>{e(b['Headline'])}</p>
  <span class="blog-more">{T('Mehr erfahren', 'Read more')} {MORE}</span>
</a>"""
    body = f"""
<section class="page-hero">
  <div class="container">
    <p class="hero-label">{T('Unser Blog', 'Our blog')}</p>
    <h1>{T('Erfahre mehr über die Welt der Versicherungen', 'Learn more about the world of insurance')}</h1>
    <p>{T('Wissenswertes und Checklisten für Deinen umfassenden Versicherungsschutz.', 'Useful knowledge and checklists for comprehensive insurance cover.')}</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="blog-filter" role="group" aria-label="{T('Beiträge filtern', 'Filter posts')}">
      <button class="active" data-cat="alle">{T('Alle', 'All')}</button>
      <button data-cat="wissen">{T('Wissen', 'Knowledge')}</button>
      <button data-cat="checkliste">{T('Checklisten', 'Checklists')}</button>
    </div>
    <div class="blog-grid">{cards}</div>
  </div>
</section>"""
    page(
        path="blog/index.html", active="blog",
        title=T("Blog: Wissenswertes & Checklisten zu Versicherungen | Schneider & Musil", "Blog: insurance insights & checklists | Schneider & Musil"),
        desc=T("Unser Versicherungs-Blog: Wissenswertes, Mythen-Checks und Checklisten für Deinen optimalen Versicherungsschutz – von Deinen unabhängigen Maklern aus Fürth.",
               "Our insurance blog: useful knowledge, myth checks and checklists for optimal cover – from your independent brokers in Fürth."),
        body=body,
        extra_ld=[breadcrumb_ld([(T("Start", "Home"), U("/")), ("Blog", U("/blog/"))])],
    )

def related_articles_html(current):
    others = [x for x in blogs if x["Slug"] != current["Slug"]]
    same_cat = [x for x in others if x["Kategorie"] == current["Kategorie"]]
    rest = [x for x in others if x["Kategorie"] != current["Kategorie"]]
    picks = (same_cat + rest)[:3]
    if not picks:
        return ""
    cards = ""
    for x in picks:
        cards += f"""<a href="/sum-blog/{x['Slug']}/" class="blog-card">
  <span class="blog-tag">{e(x['Kategorie'])}</span>
  <h3>{e(x['Name'])}</h3>
  <p>{e(x['Headline'])}</p>
  <span class="blog-more">{T('Mehr erfahren', 'Read more')} {MORE}</span>
</a>"""
    return f"""<section class="section related-articles" style="padding-top:0">
  <div class="container">
    <h2 style="text-align:center;margin-bottom:32px">{T('Weitere Artikel aus unserem Blog', 'More articles from our blog')}</h2>
    <div class="blog-grid">{cards}</div>
  </div>
</section>"""

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
            items += f'<div class="check-item"><h3><img src="/assets/img/check-blau.svg" alt="" width="20" height="20" loading="lazy" style="vertical-align:-3px"> {e(t)}</h3><p style="margin:0">{e(d)}</p></div>'
    if items:
        sections += f"<h2>{T('Diese Versicherungen solltest Du kennen:', 'Insurance you should know about:')}</h2>{items}"
        if b.get("CTA Beschreibung Checkliste", "").strip():
            sections += f'<p>{e(b["CTA Beschreibung Checkliste"])}</p>'
    # Mythos / Realität
    if b.get("Mythos Titel", "").strip():
        sections += f"<h2>{e(b['Mythos Titel'])}</h2><p>{e(b['Mythos Beschreibung'])}</p>"
    if b.get("Aufklärung / Realität Titel", "").strip():
        sections += f"<h2>{e(b['Aufklärung / Realität Titel'])}</h2><p>{e(b['Realität Beschreibung'])}</p>"
    if b.get("Beispiel Titel 1", "").strip():
        sections += f"<h2>{e(b.get('Beispiel Section Überschrift') or T('Beispiele aus dem Leben:', 'Real-life examples:'))}</h2>"
        for i in range(1, 4):
            t = b.get(f"Beispiel Titel {i}", "").strip().rstrip("|").strip()
            d = b.get(f"Beispiel Beschreibung {i}", "").strip()
            if t and d:
                sections += f'<div class="check-item"><h3>{e(t)}</h3><p style="margin:0">{e(d)}</p></div>'
    if b.get("Fazit Titel", "").strip():
        sections += f"<h2>{e(b['Fazit Titel'])}</h2><p>{e(b['Fazit Beschreibung'])}</p>"
    sections += "</div>"

    def parse_webflow_date(raw):
        m = re.search(r"\w+ (\w+) (\d+) (\d+)", raw or "")
        months = dict(Jan="01", Feb="02", Mar="03", Apr="04", May="05", Jun="06", Jul="07", Aug="08", Sep="09", Oct="10", Nov="11", Dec="12")
        if m and m.group(1) in months:
            return f"{m.group(3)}-{months[m.group(1)]}-{int(m.group(2)):02d}"
        return ""
    iso = parse_webflow_date(b.get("Published On", ""))
    iso_mod = parse_webflow_date(b.get("Updated On", "")) or iso
    blog_ld = f"""{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": {jstr(b['Name'])},
  "description": {jstr(b['Headline'])},
  "inLanguage": "{LANG}",
  "image": "{BASE}/assets/img/og-home.jpg",
  {f'"datePublished": "{iso}",' if iso else ''}
  {f'"dateModified": "{iso_mod}",' if iso_mod else ''}
  "author": {{"@type": "Organization", "name": "Schneider & Musil Versicherungsmakler GbR", "url": "{BASE}/"}},
  "publisher": {{"@id": "https://www.sum-makler.de/#organization"}},
  "mainEntityOfPage": "{U(f'/sum-blog/{slug}/')}"
}}"""
    body = f"""
<article>
<section class="page-hero">
  <div class="container">
    <nav class="breadcrumbs" aria-label="{T('Brotkrumen', 'Breadcrumb')}"><a href="/">{T('Start', 'Home')}</a> / <a href="/blog/">Blog</a> / <span aria-current="page">{e(b['Name'])}</span></nav>
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
    <h2>{T('Fragen zu Deiner Absicherung?', 'Questions about your cover?')}</h2>
    <p>{T('Wir beraten Dich kostenfrei, unabhängig und unverbindlich.', 'We advise you free of charge, independently and without obligation.')}</p>
    <a href="/termin/" class="btn btn--solid">{T('Jetzt Termin vereinbaren', 'Book an appointment now')}&nbsp;<img src="/assets/img/pfeil-weiss.svg" alt="" width="26" height="26"></a>
  </div>
</section>
{related_articles_html(b)}
</article>"""
    page(
        path=f"sum-blog/{slug}/index.html",
        title=f"{b['Name']} | Schneider & Musil Blog",
        desc=b["Headline"],
        body=body, og_type="article",
        extra_ld=[blog_ld, breadcrumb_ld([(T("Start", "Home"), U("/")), ("Blog", U("/blog/")), (e(b["Name"]), U(f"/sum-blog/{slug}/"))])],
    )

# ================================================================ LEGAL
IMPRESSUM_EN = """
<section class="page-hero"><div class="container"><h1>Legal notice</h1></div></section>
<section class="section"><div class="container legal-content">
<p><em>This is a courtesy translation. Only the <a href="/impressum/" hreflang="de">German version</a> is legally binding.</em></p>
<h2>Information pursuant to § 5 TMG (German Telemedia Act)</h2>
<h3>Company</h3>
<p>Schneider &amp; Musil Versicherungsmakler GbR<br>Blütenstr. 41<br>90765 Fürth<br>Germany<br>
Phone: +49 911 37758430<br>Fax: +49 911 37758432<br>
Email: <a href="mailto:info@sum-makler.de">info@sum-makler.de</a><br>
Website: <a href="https://www.sum-makler.de">www.sum-makler.de</a></p>
<h3>Competent registration authority</h3>
<p>IHK für München und Oberbayern (Chamber of Industry and Commerce for Munich and Upper Bavaria)<br>Max-Joseph-Straße 2<br>80333 München<br>
Website: <a href="https://www.muenchen.ihk.de" rel="noopener">www.muenchen.ihk.de</a></p>
<p>Operating as insurance brokers licensed under § 34d of the German Trade Regulation Act (GewO)<br>
Registration numbers: D-82GD-K54AB-86 &amp; D-HFNZ-UN9OV-02</p>
<p>The registration can be verified with the following register:</p>
<p>Deutscher Industrie- und Handelskammertag (DIHK) e.V.<br>Breite Straße 29<br>10178 Berlin<br>
Phone: 0180 6005850 (landline €0.20/call; mobile max. €0.60/call)<br>
Website: <a href="https://www.vermittlerregister.info" rel="noopener">www.vermittlerregister.info</a></p>
<h2>Arbitration boards</h2>
<p>For any disputes between customers and insurance intermediaries, there are independent arbitration boards that can be contacted as follows:</p>
<p>Versicherungsombudsmann e.V.<br>Postfach 080632<br>10006 Berlin<br>
Phone: +49 30 20 60 58 – 0<br>Fax: +49 30 20 60 58 – 58<br>
Email: <a href="mailto:beschwerde@versicherungsombudsmann.de">beschwerde@versicherungsombudsmann.de</a><br>
Website: <a href="https://www.versicherungsombudsmann.de" rel="noopener">www.versicherungsombudsmann.de</a></p>
<p>Ombudsmann für die Private Kranken- und Pflegeversicherung (Ombudsman for private health and long-term care insurance)<br>Postfach 060222<br>10052 Berlin<br>
Phone: 01802 – 55 04 44 (6 cents/call from German landlines, max. 42 cents/min from mobile networks)<br>
Fax: 030 – 20 45 89 31<br>
Website: <a href="https://www.pkv-ombudsmann.de" rel="noopener">www.pkv-ombudsmann.de</a></p>
<h2>Professional regulations</h2>
<p>The professional regulations can be viewed and accessed on the website operated by the German Federal Ministry of Justice and juris GmbH at <a href="https://www.gesetze-im-internet.de" rel="noopener">www.gesetze-im-internet.de</a>.</p>
<h2>Shareholdings</h2>
<p>The insurance intermediary does not hold a direct or indirect interest of more than 10% of the voting rights or capital of an insurance company.</p>
<p>No insurance company holds a direct or indirect interest of more than 10% of the voting rights or capital of the insurance intermediary.</p>
<h2>Data protection</h2>
<p>Our website can generally be used without providing personal data. Where personal data (such as name, address or email addresses) is collected on our pages, this is always done on a voluntary basis wherever possible. This data will not be passed on to third parties without your express consent.</p>
<p>Please note that data transmission over the internet (e.g. when communicating by email) may be subject to security vulnerabilities. Complete protection of data against access by third parties is not possible.</p>
<p>We hereby expressly object to the use of contact data published within the scope of the legal notice obligation by third parties for sending unsolicited advertising and information material. The operators of these pages expressly reserve the right to take legal action in the event of unsolicited advertising, such as spam emails.</p>
</div></section>"""

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
    page(path="impressum/index.html", title=T("Impressum | Schneider & Musil Versicherungsmakler GbR", "Legal notice | Schneider & Musil Versicherungsmakler GbR"),
         desc=T("Impressum der Schneider & Musil Versicherungsmakler GbR, Blütenstr. 41, 90765 Fürth. Angaben gemäß § 5 TMG.",
                "Legal notice of Schneider & Musil Versicherungsmakler GbR, Blütenstr. 41, 90765 Fürth, Germany. Information pursuant to § 5 TMG."),
         body=T(body, IMPRESSUM_EN))

DATENSCHUTZ_EN = """
<section class="page-hero"><div class="container"><h1>Privacy policy</h1></div></section>
<section class="section"><div class="container legal-content">
<p><em>This is a courtesy translation. Only the <a href="/datenschutzerklarung/" hreflang="de">German version</a> is legally binding.</em></p>
<h2>1. Name and contact details of the controller</h2>
<p>Thank you for visiting our website and for your interest in Schneider &amp; Musil Versicherungsmakler. This privacy information applies to data processing by:</p>
<p><strong>Controller:</strong><br>Schneider &amp; Musil GbR, Blütenstr. 41, 90765 Fürth, Germany<br>
Email: <a href="mailto:info@sum-makler.de">info@sum-makler.de</a><br>
Phone: +49 (0)911 37 75 84 30<br>Fax: +49 (0)911 37 75 84 32</p>
<h2>2. Collection and storage of personal data and the nature and purpose of its use</h2>
<p>When you visit our website, the browser on your device automatically sends information to our website's server. This information is temporarily stored in a so-called log file. The following information is collected without any action on your part and stored until it is automatically deleted: IP address of the requesting computer, date and time of access, name and URL of the file accessed, the website from which access was made (referrer URL), the browser used and, if applicable, your computer's operating system and the name of your access provider.</p>
<p>We process this data for the following purposes: ensuring a smooth connection to the website, ensuring convenient use of our website, evaluating system security and stability, and other administrative purposes.</p>
<p>The legal basis for this data processing is Art. 6 (1) sentence 1 lit. f GDPR. Our legitimate interest follows from the purposes of data collection listed above. Under no circumstances do we use the collected data to draw conclusions about you personally.</p>
<h2>3. Disclosure of data</h2>
<p>Your personal data will not be transferred to third parties for purposes other than those listed below. We only pass on your personal data to third parties if:</p>
<p>you have given your express consent in accordance with Art. 6 (1) sentence 1 lit. a GDPR; disclosure pursuant to Art. 6 (1) sentence 1 lit. f GDPR is necessary for the establishment, exercise or defence of legal claims and there is no reason to assume that you have an overriding legitimate interest in your data not being disclosed; there is a legal obligation to disclose pursuant to Art. 6 (1) sentence 1 lit. c GDPR; or this is legally permissible and necessary for the performance of contractual relationships with you pursuant to Art. 6 (1) sentence 1 lit. b GDPR.</p>
<h2>4. Cookies</h2>
<p>We use so-called cookies on our site. These are small files that your browser creates automatically and that are stored on your device (laptop, tablet, smartphone, etc.) when you visit our site. Cookies do not cause any damage to your device and do not contain viruses, Trojans or other malware.</p>
<p>On the one hand, cookies are used to make our website more convenient for you. For example, we use session cookies to recognise that you have already visited individual pages of our website. These are automatically deleted when you leave our site. Persistent cookies are stored for 6 months after your consent. After that, you will be asked again when you visit our website whether you (still) agree to cookies being set.</p>
<p>The data processed by cookies is necessary for the purposes mentioned to safeguard our legitimate interests and those of third parties pursuant to Art. 6 (1) sentence 1 lit. f GDPR. Most browsers accept cookies automatically. However, you can configure your browser so that no cookies are stored on your computer or so that a notice always appears before a new cookie is created.</p>
<h2>5. Google Maps</h2>
<p>We use Google Maps on our website. This allows us to show you interactive maps directly on the website and enables you to use the map function conveniently. By visiting the website, Google receives the information that you have accessed the corresponding subpage of our website. Further information on the purpose and scope of data collection and its processing by the plug-in provider can be found in the <a href="https://policies.google.com/privacy" rel="noopener">provider's privacy policy</a>.</p>
<h2>6. Contact form</h2>
<p>When you send us the data you have entered in the contact form, you agree that we may use your details to answer your enquiry or to contact you. As a rule, data is not passed on to third parties unless applicable data protection regulations justify a transfer or we are legally obliged to do so. You can revoke your consent at any time with effect for the future. In the event of revocation, your data will be deleted immediately.</p>
<h2>7. Facebook</h2>
<p>We have integrated components of Facebook on our website. The operating company of Facebook is Facebook, Inc., 1 Hacker Way, Menlo Park, CA 94025, USA. Each time one of the individual pages of this website on which a Facebook component has been integrated is accessed, the internet browser is automatically prompted to download a representation of the corresponding Facebook component. Facebook's data policy, available at <a href="https://www.facebook.com/about/privacy" rel="noopener">facebook.com/about/privacy</a>, provides information about the collection, processing and use of personal data by Facebook.</p>
<h2>8. Data protection provisions on the use of YouTube (and other video service providers)</h2>
<p>We have integrated components of YouTube and/or other video service providers on our website. The operating company of YouTube is YouTube, LLC, 901 Cherry Ave., San Bruno, CA 94066, USA. If the data subject is logged in to YouTube at the same time, YouTube recognises which specific subpage of this website the data subject is visiting when a subpage containing a YouTube video is accessed. YouTube's privacy policy is available at <a href="https://policies.google.com/privacy" rel="noopener">policies.google.com/privacy</a>.</p>
<h2>9. Rights of data subjects</h2>
<p>You have the right:</p>
<p>pursuant to Art. 15 GDPR, to request information about your personal data processed by us; pursuant to Art. 16 GDPR, to request without delay the correction of inaccurate or the completion of your personal data stored by us; pursuant to Art. 17 GDPR, to request the erasure of your personal data stored by us; pursuant to Art. 18 GDPR, to request the restriction of the processing of your personal data; pursuant to Art. 20 GDPR, to receive the personal data you have provided to us in a structured, commonly used and machine-readable format; pursuant to Art. 7 (3) GDPR, to withdraw your consent at any time; pursuant to Art. 77 GDPR, to lodge a complaint with a supervisory authority.</p>
<h2>10. Right to object</h2>
<p>If your personal data is processed on the basis of legitimate interests pursuant to Art. 6 (1) sentence 1 lit. f GDPR, you have the right to object to the processing of your personal data pursuant to Art. 21 GDPR. If you wish to exercise your right of revocation or objection, simply send an email to <a href="mailto:info@sum-makler.de">info@sum-makler.de</a>.</p>
<h2>11. Data security</h2>
<p>We use appropriate technical and organisational security measures to protect your data against accidental or intentional manipulation, partial or complete loss, destruction or unauthorised access by third parties. Our security measures are continuously improved in line with technological developments.</p>
<h2>12. Validity and changes to this privacy policy</h2>
<p>As our website and services evolve, or due to changes in legal or regulatory requirements, it may become necessary to amend this privacy policy. You can access and print the current privacy policy at any time on this page.</p>
</div></section>"""

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
    page(path="datenschutzerklarung/index.html", title=T("Datenschutzerklärung | Schneider & Musil Versicherungsmakler", "Privacy policy | Schneider & Musil Insurance Brokers"),
         desc=T("Datenschutzerklärung der Schneider & Musil Versicherungsmakler GbR – Informationen zur Erhebung und Verarbeitung personenbezogener Daten.",
                "Privacy policy of Schneider & Musil Versicherungsmakler GbR – information on the collection and processing of personal data."),
         body=T(body, DATENSCHUTZ_EN))

# ================================================================ AMAZON DSP (nur per Link erreichbar, noindex)
WA_URL = "https://wa.me/message/N5OLZTL577ELP1"

def build_dsp():
    # Transporter (Seitenansicht, Sprinter-Silhouette) – kein Lkw
    van = """<g class="dsp-van-shape">
      <path d="M-48 -36 H14 Q20 -36 23 -31 L34 -16 Q37 -12 42 -11 L46 -10 Q50 -9 50 -4 V2 H-48 Z" fill="#fff" stroke="#101828" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M17 -31 L28 -16 H12 V-31 Z" fill="#245eed"/>
      <rect x="-42" y="-24" width="46" height="5" rx="2.5" fill="#245eed"/>
      <circle cx="-30" cy="3" r="7.5" fill="#101828"/><circle cx="-30" cy="3" r="2.5" fill="#fff"/>
      <circle cx="30" cy="3" r="7.5" fill="#101828"/><circle cx="30" cy="3" r="2.5" fill="#fff"/>
    </g>"""
    steps = [
        (T("Transporter wählen", "Choose van"), "FÜ-SM 104 · Sprinter", T("bereits hinterlegt", "already on file")),
        (T("Fahrer wählen", "Choose driver"), "Daniel K.", T("aus CoDriver übernommen", "synced from CoDriver")),
        (T("Fotos &amp; Ort", "Photos &amp; location"), T("3 Fotos · GPS erkannt", "3 photos · GPS detected"), T("direkt aus der Kamera", "straight from the camera")),
        (T("Gemeldet", "Reported"), T("Schaden #2024-117", "Claim #2024-117"), T("an den Versicherer übermittelt", "sent to the insurer")),
    ]
    step_html = "".join(f"""<div class="ph-step" style="--s:{i}">
          <span class="ph-step-no">{i + 1}</span>
          <div><strong>{t}</strong><span>{v}</span><em>{h}</em></div>
        </div>""" for i, (t, v, h) in enumerate(steps))
    months = T(["Jan", "Feb", "Mär", "Apr", "Mai", "Jun"], ["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
    quota = [42, 38, 31, 27, 22, 18]
    bars = "".join(f'<div class="q-bar" style="--h:{q};--i:{i}"><span class="q-val">{q}%</span><span class="q-mon">{m}</span></div>'
                   for i, (q, m) in enumerate(zip(quota, months)))
    wa_btn = lambda label: (f'<a href="{WA_URL}" rel="noopener" class="btn dsp-btn-wa"><span class="btn-icon">'
                            f'<img src="/assets/img/icon-whatsapp.svg" alt="" width="18" height="18"></span>{label}</a>')
    defleet = [
        (T("Rückgabe planen", "Plan the return"), T("Wir stimmen mit Dir ab, welche Transporter wann zurückgehen, und bereiten die Unterlagen vor.", "We agree with you which vans go back when and prepare the paperwork.")),
        (T("Unabhängiges Gutachten", "Independent appraisal"), T("Unsere unabhängigen Gutachter dokumentieren den Zustand jedes Fahrzeugs – neutral und nachvollziehbar.", "Our independent appraisers document the condition of every vehicle – neutral and traceable.")),
        (T("Schäden abgrenzen", "Separate the damage"), T("Wir prüfen, was normale Abnutzung ist und welche Schäden über die Versicherung laufen.", "We check what is normal wear and which damage is covered by insurance.")),
        (T("Abwicklung", "Settlement"), T("Wir kümmern uns um die Abwicklung mit dem Versicherer – Du konzentrierst Dich auf Deine Touren.", "We handle the settlement with the insurer – you focus on your routes.")),
    ]
    defleet_html = "".join(f'<li class="m-up" style="--d:{i}"><span class="df-no">{i + 1}</span><h3>{t}</h3><p>{p}</p></li>'
                           for i, (t, p) in enumerate(defleet))
    body = f"""
<section class="dsp-hero">
  <div class="container">
    <p class="dsp-eyebrow m-up">{T('Für Amazon DSP Partner', 'For Amazon DSP partners')}</p>
    <h1 class="m-up" style="--d:1">{T('Versicherung für Deine Transporter&shy;flotte.', 'Insurance for your van fleet.')}<br><span class="dsp-accent">{T('Einfach. Digital. Persönlich.', 'Simple. Digital. Personal.')}</span></h1>
    <p class="dsp-lead m-up" style="--d:2">{T('Wir betreuen Delivery Service Partner seit Jahren – digital angebunden an Deine Tools, mit starken Flottenversicherern und immer persönlich erreichbar.',
                                              'We have been supporting Delivery Service Partners for years – digitally connected to your tools, with strong fleet insurers and always personally reachable.')}</p>
    <div class="cta-row m-up" style="--d:3">
      <a href="/termin/" class="btn">{ARROW_BTN}{T('Erstgespräch vereinbaren', 'Book an intro call')}</a>
      {wa_btn('WhatsApp')}
    </div>
    <div class="dsp-hero-visual m-up" style="--d:4" aria-hidden="true">
      <svg viewBox="0 0 1000 220" class="dsp-route">
        <path id="dspRoute" class="dsp-route-base" d="M20 170 C 180 170, 220 70, 380 80 S 600 180, 760 120 S 900 50, 980 50"/>
        <path class="dsp-route-line" d="M20 170 C 180 170, 220 70, 380 80 S 600 180, 760 120 S 900 50, 980 50"/>
        <g class="dsp-stop" transform="translate(380 80)"><circle r="7"/></g>
        <g class="dsp-stop" transform="translate(760 120)"><circle r="7"/></g>
        <g class="dsp-stop dsp-stop--end" transform="translate(980 50)"><circle r="9"/></g>
        <g class="dsp-van">{van}
          <animateMotion dur="12s" repeatCount="indefinite" rotate="auto"><mpath href="#dspRoute"/></animateMotion>
        </g>
      </svg>
    </div>
  </div>
</section>

<section class="dsp-stats">
  <div class="container dsp-stats-grid">
    <div class="m-up"><strong><span data-count="3500">{T('3.500', '3,500')}</span>+</strong><span>{T('Kunden insgesamt', 'customers in total')}</span></div>
    <div class="m-up" style="--d:1"><strong>{T('Jahrelang', 'Years')}</strong><span>{T('DSP-Partner betreut', 'supporting DSP partners')}</span></div>
    <div class="m-up" style="--d:2"><strong>100%</strong><span>{T('unabhängig', 'independent')}</span></div>
  </div>
</section>

<section class="dsp-section">
  <div class="container">
    <div class="dsp-head">
      <p class="dsp-eyebrow m-up">{T('Warum wir', 'Why us')}</p>
      <h2 class="m-up" style="--d:1">{T('Wir kennen das DSP-Programm.', 'We know the DSP programme.')}</h2>
    </div>
    <div class="dsp-grid3">
      <article class="dsp-card m-up" style="--d:1">
        <h3>{T('Tiefes DSP-Verständnis', 'Deep DSP understanding')}</h3>
        <p>{T('Durch die jahrelange Betreuung von DSP-Partnern kennen wir die Abläufe, Anforderungen und typischen Schadenfälle im Programm genau.', 'Years of supporting DSP partners mean we know the processes, requirements and typical claims in the programme inside out.')}</p>
      </article>
      <article class="dsp-card m-up" style="--d:2">
        <h3>{T('Über 3.500 Kunden', 'Over 3,500 customers')}</h3>
        <p>{T('Insgesamt vertrauen uns mehr als 3.500 Kunden – privat und gewerblich.', 'More than 3,500 customers trust us in total – private and commercial.')}</p>
      </article>
      <article class="dsp-card m-up" style="--d:3">
        <h3>{T('Unabhängige Gutachter an Bord', 'Independent appraisers on board')}</h3>
        <p>{T('Für das Defleeting arbeiten wir mit unabhängigen Gutachtern zusammen.', 'For defleeting we work with independent appraisers.')}</p>
      </article>
    </div>
  </div>
</section>

<section class="dsp-section dsp-alt">
  <div class="container">
    <div class="dsp-head">
      <p class="dsp-eyebrow m-up">{T('Direkt angebunden', 'Directly connected')}</p>
      <h2 class="m-up" style="--d:1">{T('Deine Daten sind schon da.', 'Your data is already there.')}</h2>
      <p class="dsp-lead m-up" style="--d:2">{T('Keine doppelte Pflege – Fahrzeuge und Fahrer kommen direkt aus Deinen Systemen.', 'No double entry – vehicles and drivers come straight from your systems.')}</p>
    </div>
    <div class="dsp-flow">
      <article class="dsp-card m-up" style="--d:1">
        <span class="dsp-tag">Cortex</span>
        <h3>Amazon Logistics Portal</h3>
        <p>{T('Einfacher Upload: Export aus Cortex hochladen – Deine Fahrzeuge sind sofort im System.', 'Simple upload: drop in your Cortex export – your vehicles are in the system right away.')}</p>
      </article>
      <div class="dsp-flow-hub m-up" style="--d:2" aria-hidden="true">
        <svg viewBox="0 0 220 60" class="dsp-flow-svg">
          <path id="flL" d="M0 30 H90" class="fl-path"/><path id="flR" d="M220 30 H130" class="fl-path"/>
          <circle r="4" class="fl-dot"><animateMotion dur="2s" repeatCount="indefinite"><mpath href="#flL"/></animateMotion></circle>
          <circle r="4" class="fl-dot"><animateMotion dur="2s" begin="1s" repeatCount="indefinite"><mpath href="#flR"/></animateMotion></circle>
        </svg>
        <img src="/assets/img/fleetsurance-mark.svg" alt="" width="56" height="56">
      </div>
      <article class="dsp-card m-up" style="--d:3">
        <span class="dsp-tag">CoDriver</span>
        <h3>DSP App</h3>
        <p>{T('Direkte Anbindung: Fahrzeug- und Fahrerdaten kommen direkt aus Deiner CoDriver DSP App.', 'Direct integration: vehicle and driver data comes straight from your CoDriver DSP app.')}</p>
      </article>
    </div>
  </div>
</section>

<section class="dsp-section">
  <div class="container dsp-split">
    <div>
      <p class="dsp-eyebrow m-up">{T('Starke Partner', 'Strong partners')}</p>
      <h2 class="m-up" style="--d:1">{T('Enge Zusammenarbeit mit starken Flottenversicherern wie der <span class="dsp-accent">Allianz</span>.', 'Close cooperation with strong fleet insurers such as <span class="dsp-accent">Allianz</span>.')}</h2>
    </div>
    <ul class="dsp-list">
      <li class="m-up" style="--d:1"><strong>{T('Flottentarife für Transporter', 'Fleet rates for vans')}</strong><span>{T('Kfz-Flottenversicherung passend zu Größe und Einsatz Deiner Transporterflotte.', 'Motor fleet insurance tailored to the size and use of your van fleet.')}</span></li>
      <li class="m-up" style="--d:2"><strong>{T('Kurze Wege im Schadenfall', 'Short paths when claims happen')}</strong><span>{T('Wir übergeben Deine Meldung vollständig an den Versicherer und halten nach.', 'We hand your claim to the insurer in full and follow up for you.')}</span></li>
      <li class="m-up" style="--d:3"><strong>{T('Unabhängig vergleichen', 'Independent comparison')}</strong><span>{T('Wir sind Makler, kein Vertreter – wir arbeiten in Deinem Auftrag.', 'We are brokers, not agents – we work on your behalf.')}</span></li>
    </ul>
  </div>
</section>

<section class="dsp-section dsp-alt" id="defleeting">
  <div class="container">
    <div class="dsp-head">
      <p class="dsp-eyebrow m-up">{T('Defleeting-Betreuung', 'Defleeting support')}</p>
      <h2 class="m-up" style="--d:1">{T('Fahrzeugrückgabe ohne Stress.', 'Vehicle returns without the stress.')}</h2>
      <p class="dsp-lead m-up" style="--d:2">{T('Wir begleiten Dich beim Defleeting Deiner Transporter – mit unabhängigen Gutachtern und klarer Abwicklung.', 'We support you when defleeting your vans – with independent appraisers and a clear settlement.')}</p>
    </div>
    <ol class="dsp-steps">{defleet_html}</ol>
  </div>
</section>

<section class="dsp-section dsp-app">
  <div class="container">
    <div class="dsp-head">
      <div class="fs-brand m-up"><img src="/assets/img/fleetsurance-mark.svg" alt="" width="64" height="63"><span>FLEETSURANCE</span></div>
      <h2 class="m-up" style="--d:1">{T('Deine Flotte. Eine App.', 'Your fleet. One app.')}</h2>
    </div>
    <div class="dsp-app-grid">
      <div class="dsp-phone m-up" aria-hidden="true">
        <div class="ph-notch"></div>
        <div class="ph-screen">
          <div class="ph-top fs-brand"><img src="/assets/img/fleetsurance-mark.svg" alt="" width="22" height="22"><span>FLEETSURANCE</span></div>
          <p class="ph-title">{T('Neue Schadensmeldung', 'New claim')}</p>
          {step_html}
          <div class="ph-progress"><span></span></div>
        </div>
      </div>
      <div class="dsp-app-copy">
        <div class="dsp-card m-up" style="--d:1">
          <h3>{T('Schaden in wenigen Klicks melden', 'Report a claim in a few taps')}</h3>
          <p>{T('Schnell und einfach, weil Transporter und Fahrer bereits hinterlegt sind. Foto machen, auswählen, absenden – fertig.', 'Quick and easy, because vans and drivers are already on file. Take a photo, select, send – done.')}</p>
        </div>
        <div class="dsp-card m-up" style="--d:2">
          <h3>{T('Dauer-eVB immer griffbereit', 'Permanent eVB always at hand')}</h3>
          <p>{T('Neuer Transporter in der Flotte? Deine Dauer-eVB für die Zulassung hast Du jederzeit in der App – per Klick kopiert oder geteilt.', 'New van in the fleet? Your permanent eVB for registration is always in the app – copied or shared with one tap.')}</p>
          <div class="evb-card" aria-hidden="true">
            <span class="evb-label">{T('Dauer-eVB', 'Permanent eVB')}</span>
            <span class="evb-code">7XK4P2M</span>
            <span class="evb-copy">{T('Kopiert', 'Copied')}</span>
          </div>
        </div>
        <div class="dsp-card dsp-docs m-up" style="--d:3">
          <h3>{T('Alle Unterlagen zur Anmeldung in der App', 'All registration documents in the app')}</h3>
          <p>{T('Zulassungsvollmacht, SEPA-Mandat für die Kfz-Steuer, Gewerbe- und Registernachweise – alles griffbereit und per Klick geteilt.', 'Registration power of attorney, SEPA mandate for vehicle tax, business and register documents – all at hand and shared in one tap.')}</p>
          <ul class="doc-list" aria-hidden="true">
            <li style="--i:0">eVB</li><li style="--i:1">{T('Zulassungsvollmacht', 'Power of attorney')}</li><li style="--i:2">{T('SEPA-Mandat Kfz-Steuer', 'SEPA mandate vehicle tax')}</li><li style="--i:3">{T('Handelsregisterauszug', 'Commercial register extract')}</li>
            <li class="doc-share" style="--i:4">{T('Teilen', 'Share')}</li>
          </ul>
        </div>
        <div class="dsp-card m-up" style="--d:4">
          <h3>{T('Schadensquote monatlich digital ablesbar', 'Monthly loss ratio at a glance')}</h3>
          <p>{T('Behalte Deine Schadensquote jeden Monat im Blick – die Grundlage für bessere Konditionen.', 'Keep an eye on your loss ratio every month – the basis for better terms.')}</p>
          <div class="q-chart">{bars}</div>
          <p class="q-note">{T('Beispielansicht', 'Sample view')}</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="dsp-section dsp-alt">
  <div class="container dsp-split">
    <div>
      <p class="dsp-eyebrow m-up">{T('Persönlich', 'Personal')}</p>
      <h2 class="m-up" style="--d:1">{T('Immer erreichbar. Über WhatsApp oder Telefon.', 'Always reachable. Via WhatsApp or phone.')}</h2>
      <p class="dsp-lead m-up" style="--d:2">{T('Keine Hotline, keine Warteschleife: Du hast direkte Ansprechpartner, die Deine Flotte kennen.', 'No hotline, no queue: you have direct contacts who know your fleet.')}</p>
      <div class="cta-row m-up" style="--d:3">
        {wa_btn(T('Per WhatsApp schreiben', 'Message on WhatsApp'))}
        <a href="tel:+4991137758430" class="btn btn--ghost">{PHONE_BTN}+49 911 37758430</a>
      </div>
    </div>
    <div class="dsp-team">
      <figure class="m-up" style="--d:1"><img src="/assets/img/team-max-400.webp" width="200" height="200" loading="lazy" alt="Maximilian Schneider"><figcaption>Max Schneider</figcaption></figure>
      <figure class="m-up" style="--d:2"><img src="/assets/img/team-marco-400.webp" width="200" height="200" loading="lazy" alt="Marco Musil"><figcaption>Marco Musil</figcaption></figure>
    </div>
  </div>
</section>

<section class="dsp-section dsp-final">
  <div class="container">
    <h2 class="m-up">{T('Bereit für die nächste Tour?', 'Ready for the next route?')}</h2>
    <p class="dsp-lead m-up" style="--d:1">{T('Kostenfreies Erstgespräch – wir schauen uns Deine aktuelle Flottenversicherung an.', 'Free intro call – we will review your current fleet insurance.')}</p>
    <div class="cta-row m-up" style="--d:2">
      <a href="/termin/" class="btn">{ARROW_BTN}{T('Erstgespräch vereinbaren', 'Book an intro call')}</a>
      {wa_btn('WhatsApp')}
    </div>
  </div>
</section>"""
    page(
        path="amazon-dsp/index.html",
        title=T("Versicherung für Amazon DSP Partner | Schneider & Musil", "Insurance for Amazon DSP partners | Schneider & Musil"),
        desc=T("Transporter-Flottenversicherung für Amazon DSP Partner: CoDriver-Anbindung, Cortex-Upload, Allianz & Co., Defleeting mit unabhängigen Gutachtern und die FLEETSURANCE App.",
               "Van fleet insurance for Amazon DSP partners: CoDriver integration, Cortex upload, Allianz & more, defleeting with independent appraisers and the FLEETSURANCE app."),
        body=body, noindex=True, body_class="dsp-page",
        extra_head='<link rel="stylesheet" href="/assets/css/dsp.css">',
        extra_js='\n<script src="/assets/js/dsp.js" defer></script>',
    )

def build_anfrage():
    body = f"""
<section class="error-hero">
  <div class="container">
    <h1>{T('Wir freuen uns über Deine Nachricht!', 'Thank you for your message!')}</h1>
    <p>{T('Wir werden uns in Kürze bei Dir melden!<br>Viele Grüße', 'We will get back to you shortly!<br>Best regards')}<br><strong>Marco &amp; Max</strong></p>
    <a href="/" class="btn btn--solid">{T('Zur Startseite', 'Back to home')}</a>
  </div>
</section>"""
    page(path="anfrage/index.html", title=T("Danke für Deine Anfrage | Schneider & Musil", "Thank you for your enquiry | Schneider & Musil"),
         desc=T("Vielen Dank für Deine Nachricht – wir melden uns in Kürze bei Dir.", "Thank you for your message – we will get back to you shortly."), body=body, noindex=True)

def build_404():
    body = f"""
<section class="error-hero">
  <div class="container">
    <p class="code">404</p>
    <h1>{T('Seite konnte nicht gefunden werden', 'Page not found')}</h1>
    <p>{T('Die Seite, die Du suchst, existiert nicht oder wurde verschoben.', 'The page you are looking for does not exist or has been moved.')}</p>
    <a href="/" class="btn btn--solid">{T('Zur Startseite', 'Back to home')}</a>
  </div>
</section>"""
    page(path="404.html", title=T("Seite nicht gefunden | Schneider & Musil", "Page not found | Schneider & Musil"),
         desc=T("Die angeforderte Seite existiert nicht.", "The requested page does not exist."), body=body, noindex=True)

# ================================================================ SEO files
def build_seo_files(urls):
    def lastmod_for(u):
        m = re.match(rf"{re.escape(BASE)}(?:/en)?/sum-blog/([^/]+)/", u)
        if m:
            b = next((x for x in blogs if x["Slug"] == m.group(1)), None)
            if b:
                dm = re.search(r"\w+ (\w+) (\d+) (\d+)", b.get("Updated On", "") or b.get("Published On", ""))
                months = dict(Jan="01", Feb="02", Mar="03", Apr="04", May="05", Jun="06", Jul="07", Aug="08", Sep="09", Oct="10", Nov="11", Dec="12")
                if dm and dm.group(1) in months:
                    return f"{dm.group(3)}-{months[dm.group(1)]}-{int(dm.group(2)):02d}"
        return TODAY
    entries = "".join(
        f"<url><loc>{u}</loc><lastmod>{lastmod_for(u)}</lastmod></url>" for u in urls
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")

# ================================================================ main
def build_lang(lang):
    set_lang(lang)
    urls = []
    build_index(); urls.append(U("/"))
    build_termin(); urls.append(U("/termin/"))
    build_sparten_index(); urls.append(U("/sparten/"))
    for s in sparten:
        build_sparte_detail(s); urls.append(U(f"/sparten/{s['Slug']}/"))
    build_blog_index(); urls.append(U("/blog/"))
    for b in blogs:
        build_blog_detail(b); urls.append(U(f"/sum-blog/{b['Slug']}/"))
    build_impressum(); urls.append(U("/impressum/"))
    build_datenschutz(); urls.append(U("/datenschutzerklarung/"))
    build_anfrage()
    build_dsp()  # bewusst nicht in urls/Sitemap und nirgends verlinkt
    build_404()
    return urls

def main():
    missing = [s["Slug"] for s in SPARTEN_DE if s["Slug"] not in SPARTEN_EN_TX] + \
              [b["Slug"] for b in BLOGS_DE if b["Slug"] not in BLOGS_EN_TX]
    if missing:
        print("WARNUNG – keine englische Übersetzung für:", ", ".join(missing))
    urls = build_lang("de") + build_lang("en")
    set_lang("de")
    build_seo_files(urls)
    print(f"Built {len(urls)} indexable pages (+ anfrage, 404, sitemap, robots).")

if __name__ == "__main__":
    main()
