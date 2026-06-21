#!/usr/bin/env python3
"""
Static site generator for Kazakhstan Entrepreneurs Association.
Reads /locales/<lang>.json and renders /<lang>/index.html for kk, ru, en.
Produces clean separate URLs (site.kz/kk, /ru, /en) with hreflang + SEO,
without requiring any JS framework or build toolchain at runtime.

To add a new language later:
  1. Create /locales/<code>.json with the same keys as ru.json
  2. Add the code to LANGS below
  3. Re-run: python3 build.py
"""
import json, os, html, time

ROOT = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(ROOT, "locales")
OUT_ROOT = ROOT

LANGS = ["kk", "ru", "en"]          # active languages, kk = default
DEFAULT_LANG = "kk"
SITE_NAME = "site.kz"               # placeholder domain, replace with real domain on deploy
BASE_URL = "https://site.kz"        # placeholder absolute base for canonical/hreflang/schema
BUILD_VERSION = str(int(time.time()))  # changes every build -> guarantees fresh CSS/JS, bypasses any stale CDN/browser cache

FUTURE_LANGS = ["tr", "zh", "ar", "de", "fr", "ky", "uz"]  # reserved, not yet active


def load(lang):
    with open(os.path.join(LOCALES_DIR, f"{lang}.json"), encoding="utf-8") as f:
        return json.load(f)


def e(s):
    """HTML-escape plain text content (not used for hand-authored markup)."""
    return html.escape(s, quote=True)


def hreflang_tags(current_lang):
    tags = []
    for l in LANGS:
        tags.append(f'<link rel="alternate" hreflang="{l}" href="{BASE_URL}/{l}/" />')
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}/{DEFAULT_LANG}/" />')
    return "\n  ".join(tags)


def lang_switch_html(current_lang, mobile=False):
    cls = "lang-switch" if not mobile else "lang-switch"
    items = []
    for l in LANGS:
        active = " active" if l == current_lang else ""
        items.append(f'<a href="/{l}/" data-lang-link="{l}" class="{active.strip()}">{e(load(l)["langSwitcher"][l])}</a>')
    return f'<div class="{cls}">' + "".join(items) + "</div>"


def footer_lang_html(current_lang):
    items = []
    for l in LANGS:
        active = " active" if l == current_lang else ""
        items.append(f'<a href="/{l}/" class="{active.strip()}">{e(load(l)["langSwitcher"][l])}</a>')
    return "".join(items)


def get_nav_links(lang, d):
    """Single source of truth for the main navigation, used on every page."""
    return [
        ("#about", d["nav"]["about"]),
        ("#structure", d["nav"]["structure"]),
        ("#membership", d["nav"]["membership"]),
        ("#regions", d["nav"]["regions"]),
        (f"/{lang}/news/", d["nav"]["news"]),
        (f"/{lang}/events/", d["nav"]["events"]),
        ("#partners", d["nav"]["partners"]),
        ("#ai", d["nav"]["ai"]),
        ("#cabinet", d["nav"]["cabinet"]),
        ("#contacts", d["nav"]["contacts"]),
    ]


MODAL_HREFS = {"#ai": "ai", "#cabinet": "cabinet"}


def nav_link_html(href, label, extra_class=""):
    if href in MODAL_HREFS:
        cls = ("nav-link-btn " + extra_class).strip()
        return f'<button type="button" class="{cls}" data-modal-trigger="{MODAL_HREFS[href]}">{e(label)}</button>'
    return f'<a href="{href}" class="{extra_class}">{e(label)}</a>'


def build_header_chrome(lang, d):
    """Header + mobile drawer + persistent AI widget bubble.
    Identical on every page (home, news, events, ...) so the person is always
    one click away from any section, the member area, and the AI assistant.

    Layout: brand (left) — News/Events as plain centered links (always visible,
    middle) — language switch + member-area icon + hamburger (right).
    The hamburger drawer only holds the remaining secondary sections
    (About, Structure, Membership, Regions, Partners, Contacts); News, Events,
    the AI assistant and the member area each already have their own direct,
    always-visible entry point, so duplicating them in the drawer would be
    redundant clutter.
    """
    nav_links = get_nav_links(lang, d)
    drawer_hrefs_to_skip = {"#ai", "#cabinet", f"/{lang}/news/", f"/{lang}/events/"}
    drawer_links = [(href, label) for href, label in nav_links if href not in drawer_hrefs_to_skip]
    mobile_nav = "".join(nav_link_html(href, label) for href, label in drawer_links)

    center_nav = (
        f'<a href="/{lang}/news/">{e(d["nav"]["news"])}</a>'
        f'<a href="/{lang}/events/">{e(d["nav"]["events"])}</a>'
    )

    cabinet_icon = (
        '<svg viewBox="0 0 24 24" fill="none">'
        '<circle cx="12" cy="8" r="3.5" stroke="currentColor" stroke-width="1.6"/>'
        '<path d="M4.5 20c0-3.9 3.3-6.6 7.5-6.6s7.5 2.7 7.5 6.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
        '</svg>'
    )

    return f"""
<header class="site-header">
  <div class="container header-inner">
    <a href="/{lang}/" class="brand">
      <span class="brand-mark">KEA</span>
      <span class="brand-text"><strong>Kazakhstan Entrepreneurs</strong><span>Association</span></span>
    </a>
    <nav class="center-nav">{center_nav}</nav>
    <div class="header-actions">
      {lang_switch_html(lang)}
      <button type="button" class="cabinet-icon-btn" data-modal-trigger="cabinet" aria-label="{e(d['nav']['cabinet'])}" title="{e(d['nav']['cabinet'])}">{cabinet_icon}</button>
      <button class="burger" aria-label="menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-nav">
  <div class="mobile-nav-inner">
    {mobile_nav}
    <button type="button" class="btn btn-gold" style="margin-top:18px;" data-modal-trigger="cabinet">{e(d['topbar']['join'])}</button>
  </div>
</div>
"""


def build_ai_widget(d):
    """Persistent bottom-right AI assistant chat bubble. Same on every page."""
    return f"""
<div class="ai-widget" id="ai-widget">
  <div class="ai-widget-panel" id="ai-widget-panel">
    <div class="ai-widget-head">
      <span class="dot-live"></span>
      <strong>{e(d['ai']['eyebrow'])}</strong>
      <button type="button" class="ai-widget-close" aria-label="close">&times;</button>
    </div>
    <div class="chat-body" id="ai-chat-body">
      <div class="chat-bubble bot">{e(d['ai']['demoReply'])}</div>
    </div>
    <form id="ai-chat-form" class="chat-input-row" data-demo-reply="{e(d['ai']['demoReply'])}">
      <input id="ai-chat-input" type="text" placeholder="{e(d['ai']['placeholder'])}" autocomplete="off" />
      <button type="submit" class="btn btn-gold btn-sm">{e(d['ai']['send'])}</button>
    </form>
    <div class="ai-disclaimer">{e(d['ai']['disclaimer'])}</div>
  </div>
  <button type="button" class="ai-widget-bubble" id="ai-widget-bubble" aria-label="AI assistant">
    <svg class="ico-chat" viewBox="0 0 24 24" fill="none"><path d="M4 12c0-4.4 3.6-8 8-8s8 3.6 8 8-3.6 8-8 8c-1.1 0-2.1-.2-3-.6L4 20l1-4.3C4.4 14.6 4 13.3 4 12Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><circle cx="8.6" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="15.4" cy="12" r="1" fill="currentColor"/></svg>
    <svg class="ico-close" viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
  </button>
</div>
"""


def build_cabinet_modal(d):
    """Member-area modal (login/register/dashboard). Same on every page."""
    cab = d["cabinet"]
    features_grid = "".join(f'<div class="glass card" style="padding:18px;"><p>{e(f)}</p></div>' for f in cab["features"])
    return f"""
<div class="modal-overlay" id="modal-cabinet">
  <div class="modal glass modal-lg">
    <button class="modal-close" aria-label="close">&times;</button>
    <div class="cabinet-wrap">
      <div class="glass auth-panel" id="cabinet-auth" style="padding:30px;">
        <div id="cabinet-forms">
          <div class="auth-tabs">
            <button class="auth-tab active" data-tab="login">{e(cab['loginTab'])}</button>
            <button class="auth-tab" data-tab="register">{e(cab['registerTab'])}</button>
          </div>
          <form id="login-form" style="display:flex; flex-direction:column;">
            <div class="field"><label>{e(cab['email'])}</label><input type="email" required /></div>
            <div class="field"><label>{e(cab['password'])}</label><input type="password" required /></div>
            <a href="#" class="auth-forgot">{e(cab['forgot'])}</a>
            <button type="submit" class="btn btn-gold btn-block">{e(cab['submitLogin'])}</button>
          </form>
          <form id="register-form" style="display:none; flex-direction:column;">
            <div class="field"><label>{e(cab['name'])}</label><input type="text" name="name" required /></div>
            <div class="field"><label>{e(cab['email'])}</label><input type="email" required /></div>
            <div class="field"><label>{e(cab['phone'])}</label><input type="tel" required /></div>
            <div class="field"><label>{e(cab['password'])}</label><input type="password" required /></div>
            <button type="submit" class="btn btn-gold btn-block">{e(cab['submitRegister'])}</button>
          </form>
          <p class="cabinet-demo-note">{e(cab['demoNote'])}</p>
        </div>
        <div class="dashboard" id="cabinet-dashboard">
          <div class="dashboard-head">
            <h3>{e(cab['welcomeBack'])}, <span id="cabinet-username">Member</span></h3>
            <button class="btn btn-ghost btn-sm" id="cabinet-logout">{e(cab.get('logout','Sign out'))}</button>
          </div>
          <p class="lead">{e(cab['subtitle'])}</p>
          <p class="cabinet-demo-note">{e(cab['demoNote'])}</p>
        </div>
      </div>
      <div>
        <div class="eyebrow">{e(cab['eyebrow'])}</div>
        <h2 style="font-size:28px;">{e(cab['title'])}</h2>
        <p class="lead" style="margin:14px 0 22px; font-size:15px;">{e(cab['subtitle'])}</p>
        <div class="grid cabinet-feature-grid">{features_grid}</div>
      </div>
    </div>
  </div>
</div>
"""


def build_footer(lang, d, nav_links):
    dept_footer_links = "".join(f'<li>{e(dep["name"])}</li>' for dep in d["departments"][:6])
    nav_footer_links = "".join(f'<li><a href="{href}">{e(label)}</a></li>' for href, label in nav_links[:6])
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="brand" style="margin-bottom:14px;"><span class="brand-mark">KEA</span><span class="brand-text"><strong>Kazakhstan Entrepreneurs</strong><span>Association</span></span></div>
        <p style="color:var(--c-muted); font-size:14px; max-width:300px;">{e(d['footer']['aboutShort'])}</p>
      </div>
      <div>
        <h4>{e(d['footer']['quickLinksTitle'])}</h4>
        <ul>{nav_footer_links}</ul>
      </div>
      <div>
        <h4>{e(d['footer']['departmentsTitle'])}</h4>
        <ul>{dept_footer_links}</ul>
      </div>
      <div>
        <h4>{e(d['footer']['languagesTitle'])}</h4>
        <div class="footer-lang">{footer_lang_html(lang)}</div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span id="year"></span> Kazakhstan Entrepreneurs Association. {e(d['footer']['rights'])}</span>
      <span>{SITE_NAME}/{lang}</span>
    </div>
  </div>
</footer>
"""


def build_scripts():
    return f"""
<div class="toast" id="toast"></div>
<script>document.getElementById('year').textContent = new Date().getFullYear();</script>
<script defer src="/js/main.js?v={BUILD_VERSION}"></script>
</body>
</html>
"""


def build_head(lang, d, url_path="", title=None, description=None):
    """url_path is the slug after the language code, e.g. '' for home, 'news/' for the news page."""
    page_url = f"{BASE_URL}/{lang}/{url_path}"
    page_title = title or d["meta"]["title"]
    page_desc = description or d["meta"]["description"]
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Kazakhstan Entrepreneurs Association",
        "alternateName": d["meta"]["title"],
        "url": f"{BASE_URL}/{lang}/",
        "logo": f"{BASE_URL}/assets/logo.png",
        "description": d["meta"]["description"],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": d["contacts"]["phoneValue"],
            "email": d["contacts"]["emailValue"],
            "contactType": "customer service"
        },
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Astana",
            "addressCountry": "KZ",
            "streetAddress": d["contacts"]["addressValue"]
        }
    }
    hreflang = "\n  ".join(
        [f'<link rel="alternate" hreflang="{l}" href="{BASE_URL}/{l}/{url_path}" />' for l in LANGS] +
        [f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}/{DEFAULT_LANG}/{url_path}" />']
    )
    return f"""<!doctype html>
<html lang="{lang}" dir="{d.get('dir','ltr')}">
<head>
<script>document.documentElement.classList.add('js');</script>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(page_title)}</title>
<meta name="description" content="{e(page_desc)}" />
<link rel="canonical" href="{page_url}" />
{hreflang}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Kazakhstan Entrepreneurs Association" />
<meta property="og:title" content="{e(page_title)}" />
<meta property="og:description" content="{e(page_desc)}" />
<meta property="og:url" content="{page_url}" />
<meta property="og:locale" content="{lang}" />
<meta property="og:image" content="{BASE_URL}/assets/og-cover.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="robots" content="index, follow" />
<link rel="icon" type="image/png" href="/assets/favicon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="/css/style.css?v={BUILD_VERSION}" />
<script defer src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
"""


def render_page(lang):
    d = load(lang)
    nav_links = get_nav_links(lang, d)

    head = build_head(lang, d, url_path="")
    header = build_header_chrome(lang, d)

    # ---------- HERO ----------
    hero = f"""
<section class="hero">
  <div class="hero-bg"><img src="/assets/hero-illustration.svg" alt="" class="hero-illustration" /></div>
  <div class="container hero-content">
    <div class="eyebrow">{e(d['hero']['eyebrow'])}</div>
    <h1>{e(d['hero']['title'])}</h1>
    <p class="lead">{e(d['hero']['subtitle'])}</p>
    <div class="hero-ctas">
      <a href="#membership" class="btn btn-gold">{e(d['hero']['cta1'])}</a>
      <a href="#contacts" class="btn btn-ghost">{e(d['hero']['cta2'])}</a>
      <button type="button" class="btn btn-ghost" data-modal-trigger="cabinet">{e(d['hero']['cta3'])}</button>
      <a href="#contacts" class="btn btn-ghost">{e(d['hero']['cta4'])}</a>
    </div>
  </div>
  <div class="scroll-cue"><span class="line"></span>{e(d['hero']['scroll'])}</div>
</section>
"""

    # ---------- ABOUT ----------
    about = d["about"]
    benefits_li = "".join(f"<li>{e(b)}</li>" for b in about["benefits"])
    about_section = f"""
<section class="section" id="about">
  <div class="container about-grid">
    <div>
      <div class="eyebrow">{e(about['eyebrow'])}</div>
      <h2 class="reveal">{e(about['title'])}</h2>
      <p class="lead reveal" style="margin-top:18px;">{e(about['who'])}</p>
      <div class="about-list">
        <div class="reveal"><div class="item-label">{e(about['historyTitle'])}</div><p>{e(about['history'])}</p></div>
        <div class="reveal"><div class="item-label">{e(about['goalsTitle'])}</div><p>{e(about['goals'])}</p></div>
        <div class="reveal"><div class="item-label">{e(about['tasksTitle'])}</div><p>{e(about['tasks'])}</p></div>
      </div>
    </div>
    <div class="glass benefits-panel reveal">
      <h3 style="margin-bottom:18px;">{e(about['benefitsTitle'])}</h3>
      <ul>{benefits_li}</ul>
    </div>
  </div>
</section>
"""

    # ---------- MISSION ----------
    mission = f"""
<section class="mission">
  <div class="container">
    <div class="eyebrow" style="justify-content:center;">{e(d['mission']['eyebrow'])}</div>
    <blockquote class="reveal">&ldquo;{e(d['mission']['text'])}&rdquo;</blockquote>
  </div>
</section>
"""

    # ---------- VALUES ----------
    values_cards = "".join(
        f'''<div class="glass card value-card reveal"><span class="value-num">0{i+1}</span><h3 style="margin-top:14px;">{e(v['name'])}</h3><p>{e(v['desc'])}</p></div>'''
        for i, v in enumerate(d["values"]["items"])
    )
    values_section = f"""
<section class="section" id="values">
  <div class="container">
    <div class="section-head center">
      <div class="eyebrow">{e(d['values']['eyebrow'])}</div>
      <h2>{e(d['values']['title'])}</h2>
    </div>
    <div class="grid grid-4 stagger">{values_cards}</div>
  </div>
</section>
"""

    # ---------- DIRECTIONS ----------
    dir_cards = "".join(
        f'''<div class="glass card reveal"><div class="card-icon">{i+1}</div><h3>{e(it['name'])}</h3><p>{e(it['desc'])}</p></div>'''
        for i, it in enumerate(d["directions"]["items"])
    )
    directions_section = f"""
<section class="section section-tight" id="directions">
  <div class="container">
    <div class="section-head center">
      <div class="eyebrow">{e(d['directions']['eyebrow'])}</div>
      <h2>{e(d['directions']['title'])}</h2>
    </div>
    <div class="grid grid-4 stagger">{dir_cards}</div>
  </div>
</section>
"""

    # ---------- STATS ----------
    stats_html = "".join(
        f'''<div class="stat reveal"><span class="num" data-count="{e(s['value'])}">0</span><span class="label">{e(s['label'])}</span></div>'''
        for s in d["stats"]["items"]
    )
    stats_section = f"""
<section class="stats-strip">
  <div class="container">
    <div class="grid grid-4" style="grid-template-columns:repeat(6,1fr); gap:18px;">{stats_html}</div>
  </div>
</section>
"""

    # ---------- DEPARTMENTS + MODALS ----------
    dept_cards = []
    dept_modals = []
    dm = d["departmentModal"]
    for i, dep in enumerate(d["departments"]):
        idx = str(i + 1).zfill(2)
        tags = "".join(f'<span class="tag">{e(s)}</span>' for s in dep["services"][:4])
        dept_cards.append(f"""
        <div class="glass card dept-card reveal" data-dept-trigger="{dep['id']}">
          <span class="dept-index">{idx}</span>
          <h3>{e(dep['name'])}</h3>
          <p>{e(dep['short'])}</p>
          <div class="tags">{tags}</div>
          <span class="more">{e(d['structure']['viewAll'])} →</span>
        </div>""")
        services_html = "".join(f"<span>{e(s)}</span>" for s in dep["services"])
        dept_modals.append(f"""
        <div class="modal-overlay" id="modal-{dep['id']}">
          <div class="modal glass">
            <button class="modal-close" aria-label="close">&times;</button>
            <h3>{e(dep['name'])}</h3>
            <p class="modal-sub">{e(dep['short'])}</p>
            <div class="modal-section">
              <h4>{e(dm['servicesTitle'])}</h4>
              <div class="service-list">{services_html}</div>
            </div>
            <div class="modal-section">
              <h4>{e(dm['headTitle'])}</h4>
              <p>{e(dep['head'])}</p>
            </div>
            <div class="modal-section">
              <h4>{e(dm['contactTitle'])}</h4>
              <form data-mock-form data-success="{e(d['contacts']['formSuccess'])}">
                <div class="field"><input type="text" placeholder="{e(dm['formName'])}" required /></div>
                <div class="field"><input type="tel" placeholder="{e(dm['formPhone'])}" required /></div>
                <div class="field"><input type="text" placeholder="{e(dm['formMessage'])}" /></div>
                <button type="submit" class="btn btn-gold btn-block">{e(dm['formSubmit'])}</button>
              </form>
            </div>
          </div>
        </div>""")

    structure_section = f"""
<section class="section" id="structure">
  <div class="container">
    <div class="section-head center">
      <div class="eyebrow">{e(d['structure']['eyebrow'])}</div>
      <h2>{e(d['structure']['title'])}</h2>
      <p class="lead" style="margin:18px auto 0;">{e(d['structure']['subtitle'])}</p>
    </div>
    <div class="grid grid-3 stagger">{''.join(dept_cards)}</div>
  </div>
</section>
{''.join(dept_modals)}
"""

    # ---------- PRACTICAL HELP ----------
    practical_items = "".join(
        f'<div class="practical-item reveal"><span class="dot"></span>{e(it)}</div>' for it in d["practical"]["items"]
    )
    practical_section = f"""
<section class="section section-tight" id="practical">
  <div class="container">
    <div class="section-head center">
      <div class="eyebrow">{e(d['practical']['eyebrow'])}</div>
      <h2>{e(d['practical']['title'])}</h2>
    </div>
    <div class="grid practical-grid">{practical_items}</div>
  </div>
</section>
"""

    # ---------- MEMBERSHIP ----------
    plans_html = []
    for i, p in enumerate(d["membership"]["packages"]):
        featured = " featured" if i == 1 else ""
        badge = f'<span class="badge">{e(d["membership"]["popular"])}</span>' if i == 1 else ""
        benefits = "".join(f"<li>{e(b)}</li>" for b in p["benefits"])
        plans_html.append(f"""
        <div class="glass plan{featured} reveal">
          {badge}
          <div class="plan-name">{e(p['name'])}</div>
          <div class="audience">{e(p['audience'])}</div>
          <div class="fee">{e(p['fee'])}</div>
          <ul>{benefits}</ul>
          <a href="#contacts" class="btn {('btn-gold' if i==1 else 'btn-ghost')} btn-block">{e(d['membership']['applyCta'])}</a>
        </div>""")
    membership_section = f"""
<section class="section" id="membership">
  <div class="container">
    <div class="section-head center">
      <div class="eyebrow">{e(d['membership']['eyebrow'])}</div>
      <h2>{e(d['membership']['title'])}</h2>
      <p class="lead" style="margin:18px auto 0;">{e(d['membership']['subtitle'])}</p>
    </div>
    <div class="grid grid-3">{''.join(plans_html)}</div>
  </div>
</section>
"""

    # ---------- REGIONS ----------
    region_rows = "".join(
        f'''<div class="region-row"><span class="city">{e(r['city'])}</span><span class="role">{e(r['role'])}</span></div>'''
        for r in d["regions"]["items"]
    )
    map_points = json.dumps(
        [{"city": r["city"], "role": r["role"], "lat": r["lat"], "lng": r["lng"]} for r in d["regions"]["items"]],
        ensure_ascii=False
    )
    regions_section = f"""
<section class="section section-tight" id="regions">
  <div class="container regions-wrap">
    <div class="reveal">
      <div class="eyebrow">{e(d['regions']['eyebrow'])}</div>
      <h2>{e(d['regions']['title'])}</h2>
      <p class="lead" style="margin-top:16px;">{e(d['regions']['subtitle'])}</p>
      <div class="glass map-frame" style="margin-top:30px;">
        <div id="regions-map" data-points='{map_points}'></div>
        <span class="map-caption">{e(d['regions']['mapNote'])}</span>
      </div>
    </div>
    <div class="glass reveal" style="padding:34px;">{region_rows}</div>
  </div>
</section>
"""

    # ---------- PARTNERS ----------
    partner_tags = "".join(f'<div class="glass partner-tag reveal">{e(c)}</div>' for c in d["partners"]["categories"])
    partners_section = f"""
<section class="section section-tight" id="partners">
  <div class="container">
    <div class="section-head center">
      <div class="eyebrow">{e(d['partners']['eyebrow'])}</div>
      <h2>{e(d['partners']['title'])}</h2>
      <p class="lead" style="margin:14px auto 0;">{e(d['partners']['subtitle'])}</p>
    </div>
    <div class="grid grid-4 stagger" style="grid-template-columns:repeat(7,1fr);">{partner_tags}</div>
  </div>
</section>
"""

    # ---------- AI ASSISTANT + CABINET (shared widgets, same on every page) ----------
    ai_section = build_ai_widget(d)
    cabinet_section = build_cabinet_modal(d)

    # ---------- CONTACTS ----------
    ct = d["contacts"]
    contacts_section = f"""
<section class="section" id="contacts">
  <div class="container contacts-wrap">
    <div class="reveal">
      <div class="eyebrow">{e(ct['eyebrow'])}</div>
      <h2 style="margin-bottom:30px;">{e(ct['title'])}</h2>
      <div class="contact-row"><span class="ico">@</span><div><div class="lbl">{e(ct['phoneLabel'])}</div><div class="val">{e(ct['phoneValue'])}</div></div></div>
      <div class="contact-row"><span class="ico">✉</span><div><div class="lbl">{e(ct['emailLabel'])}</div><div class="val">{e(ct['emailValue'])}</div></div></div>
      <div class="contact-row"><span class="ico">⚲</span><div><div class="lbl">{e(ct['addressLabel'])}</div><div class="val">{e(ct['addressValue'])}</div></div></div>
      <div class="lbl" style="margin-top:10px;">{e(ct['socialTitle'])}</div>
      <div class="social-row">
        <a href="#" aria-label="Instagram">IG</a>
        <a href="#" aria-label="LinkedIn">in</a>
        <a href="#" aria-label="Telegram">TG</a>
        <a href="#" aria-label="Facebook">FB</a>
      </div>
    </div>
    <div class="glass contact-form reveal">
      <h3 style="margin-bottom:20px;">{e(ct['formTitle'])}</h3>
      <form data-mock-form data-success="{e(ct['formSuccess'])}" style="display:flex; flex-direction:column; gap:16px;">
        <div class="field"><input type="text" placeholder="{e(ct['formName'])}" required /></div>
        <div class="field"><input type="email" placeholder="{e(ct['formEmail'])}" required /></div>
        <textarea placeholder="{e(ct['formMessage'])}" required></textarea>
        <button type="submit" class="btn btn-gold btn-block">{e(ct['formSubmit'])}</button>
      </form>
    </div>
  </div>
</section>
"""

    # ---------- FOOTER + SCRIPTS ----------
    footer = build_footer(lang, d, nav_links)
    toast_and_scripts = build_scripts()

    return (
        head + header + hero + about_section + mission + values_section + directions_section +
        stats_section + structure_section + practical_section + membership_section +
        regions_section + partners_section + ai_section +
        cabinet_section + contacts_section + footer + toast_and_scripts
    )


def render_listing_page(lang, section_key, types_key):
    """Shared renderer for the dedicated News and Events pages — same chrome
    (header, AI widget, member-area modal, footer) as the homepage, full-width
    content area instead of a teaser, with category tabs and an empty state
    ready for real content."""
    d = load(lang)
    nav_links = get_nav_links(lang, d)
    sec = d[section_key]

    head = build_head(
        lang, d, url_path=f"{section_key}/",
        title=f"{sec.get('pageTitle', sec['title'])} — Kazakhstan Entrepreneurs Association",
        description=sec["subtitle"]
    )
    header = build_header_chrome(lang, d)

    tabs = "".join(f'<button class="tab-pill">{e(c)}</button>' for c in sec[types_key])
    page_body = f"""
<section class="page-hero">
  <div class="container">
    <a href="/{lang}/" class="back-link">&larr; {e(sec.get('backHome', 'Home'))}</a>
    <div class="eyebrow">{e(sec['eyebrow'])}</div>
    <h1>{e(sec.get('pageTitle', sec['title']))}</h1>
    <p class="lead" style="margin-top:16px; max-width:640px;">{e(sec['subtitle'])}</p>
  </div>
</section>
<section class="section section-tight">
  <div class="container">
    <div class="tabs-row">{tabs}</div>
    <div class="empty-panel">{e(sec['empty'])}</div>
  </div>
</section>
"""

    ai_widget = build_ai_widget(d)
    cabinet_modal = build_cabinet_modal(d)
    footer = build_footer(lang, d, nav_links)
    scripts = build_scripts()

    return head + header + page_body + ai_widget + cabinet_modal + footer + scripts


def render_news_page(lang):
    return render_listing_page(lang, "news", "categories")


def render_events_page(lang):
    return render_listing_page(lang, "events", "types")


def render_root_redirect():
    """Root index.html: detect browser language, redirect to /kk/, /ru/ or /en/."""
    links = "".join(f'<a href="/{l}/">{l}</a>' for l in LANGS)
    return f"""<!doctype html>
<html lang="{DEFAULT_LANG}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Kazakhstan Entrepreneurs Association</title>
<meta name="robots" content="index, follow" />
{hreflang_tags(DEFAULT_LANG)}
<script>
(function(){{
  var supported = {json.dumps(LANGS)};
  var saved = null;
  try {{ saved = window.localStorage.getItem('kea_lang'); }} catch(e) {{}}
  var nav = (navigator.language || navigator.userLanguage || '{DEFAULT_LANG}').toLowerCase();
  var browserLang = nav.split('-')[0];
  var target = (saved && supported.indexOf(saved) !== -1) ? saved
             : (supported.indexOf(browserLang) !== -1 ? browserLang : '{DEFAULT_LANG}');
  window.location.replace('/' + target + '/');
}})();
</script>
</head>
<body>
  <noscript>
    <p>Please choose a language / Тілді таңдаңыз / Выберите язык:</p>
    {links}
  </noscript>
</body>
</html>
"""


def render_sitemap():
    urls = []
    sub_pages = ["", "news/", "events/"]
    for sub in sub_pages:
        for l in LANGS:
            if sub == "":
                priority = "1.0" if l == DEFAULT_LANG else "0.9"
            else:
                priority = "0.7"
            urls.append(f"""  <url>
    <loc>{BASE_URL}/{l}/{sub}</loc>
    {''.join(f'<xhtml:link rel="alternate" hreflang="{ol}" href="{BASE_URL}/{ol}/{sub}" />' for ol in LANGS)}
    <changefreq>weekly</changefreq>
    <priority>{priority}</priority>
  </url>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(urls)}
</urlset>
"""


def render_robots():
    return f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""


def main():
    for lang in LANGS:
        out_dir = os.path.join(OUT_ROOT, lang)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(lang)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)
        print(f"built /{lang}/index.html  ({len(html_out)} chars)")

        news_dir = os.path.join(out_dir, "news")
        os.makedirs(news_dir, exist_ok=True)
        news_html = render_news_page(lang)
        with open(os.path.join(news_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(news_html)
        print(f"built /{lang}/news/index.html  ({len(news_html)} chars)")

        events_dir = os.path.join(out_dir, "events")
        os.makedirs(events_dir, exist_ok=True)
        events_html = render_events_page(lang)
        with open(os.path.join(events_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(events_html)
        print(f"built /{lang}/events/index.html  ({len(events_html)} chars)")

    with open(os.path.join(OUT_ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_root_redirect())
    with open(os.path.join(OUT_ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(render_sitemap())
    with open(os.path.join(OUT_ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(render_robots())
    print("built /index.html, /sitemap.xml, /robots.txt")
    print(f"Reserved for future expansion (not active yet): {FUTURE_LANGS}")


if __name__ == "__main__":
    main()
