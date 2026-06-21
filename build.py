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
import json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(ROOT, "locales")
OUT_ROOT = ROOT

LANGS = ["kk", "ru", "en"]          # active languages, kk = default
DEFAULT_LANG = "kk"
SITE_NAME = "site.kz"               # placeholder domain, replace with real domain on deploy
BASE_URL = "https://site.kz"        # placeholder absolute base for canonical/hreflang/schema

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


def render_page(lang):
    d = load(lang)
    other = [l for l in LANGS if l != lang]

    # ---------- HEAD ----------
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

    head = f"""<!doctype html>
<html lang="{lang}" dir="{d.get('dir','ltr')}">
<head>
<script>document.documentElement.classList.add('js');</script>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(d['meta']['title'])}</title>
<meta name="description" content="{e(d['meta']['description'])}" />
<link rel="canonical" href="{BASE_URL}/{lang}/" />
{hreflang_tags(lang)}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Kazakhstan Entrepreneurs Association" />
<meta property="og:title" content="{e(d['meta']['title'])}" />
<meta property="og:description" content="{e(d['meta']['description'])}" />
<meta property="og:url" content="{BASE_URL}/{lang}/" />
<meta property="og:locale" content="{lang}" />
<meta property="og:image" content="{BASE_URL}/assets/og-cover.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="robots" content="index, follow" />
<link rel="icon" type="image/png" href="/assets/favicon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="/css/style.css" />
<script defer src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
"""

    # ---------- HEADER ----------
    nav_links = [
        ("#about", d["nav"]["about"]),
        ("#structure", d["nav"]["structure"]),
        ("#membership", d["nav"]["membership"]),
        ("#regions", d["nav"]["regions"]),
        ("#news", d["nav"]["news"]),
        ("#events", d["nav"]["events"]),
        ("#partners", d["nav"]["partners"]),
        ("#ai", d["nav"]["ai"]),
        ("#cabinet", d["nav"]["cabinet"]),
        ("#contacts", d["nav"]["contacts"]),
    ]
    main_nav = "".join(f'<a href="{href}">{e(label)}</a>' for href, label in nav_links)
    mobile_nav = "".join(f'<a href="{href}">{e(label)}</a>' for href, label in nav_links)

    header = f"""
<header class="site-header">
  <div class="container header-inner">
    <a href="/{lang}/" class="brand">
      <span class="brand-mark">KEA</span>
      <span class="brand-text"><strong>Kazakhstan Entrepreneurs</strong><span>Association</span></span>
    </a>
    <nav class="main-nav">{main_nav}</nav>
    <div class="header-actions">
      {lang_switch_html(lang)}
      <a href="#cabinet" class="btn btn-gold btn-sm">{e(d['topbar']['join'])}</a>
    </div>
    <button class="burger" aria-label="menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="mobile-nav">
  {mobile_nav}
  <a href="#cabinet" class="btn btn-gold" style="margin-top:8px;">{e(d['topbar']['join'])}</a>
  {lang_switch_html(lang, mobile=True)}
</div>
"""

    # ---------- HERO ----------
    hero = f"""
<section class="hero">
  <div class="hero-bg"><div class="hero-grid"></div></div>
  <div class="container hero-content">
    <div class="eyebrow">{e(d['hero']['eyebrow'])}</div>
    <h1>{e(d['hero']['title'])}</h1>
    <p class="lead">{e(d['hero']['subtitle'])}</p>
    <div class="hero-ctas">
      <a href="#membership" class="btn btn-gold">{e(d['hero']['cta1'])}</a>
      <a href="#contacts" class="btn btn-ghost">{e(d['hero']['cta2'])}</a>
      <a href="#cabinet" class="btn btn-ghost">{e(d['hero']['cta3'])}</a>
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

    # ---------- NEWS ----------
    news_tabs = "".join(f'<button class="tab-pill">{e(c)}</button>' for c in d["news"]["categories"])
    news_section = f"""
<section class="section" id="news">
  <div class="container">
    <div class="section-head">
      <div class="eyebrow">{e(d['news']['eyebrow'])}</div>
      <h2>{e(d['news']['title'])}</h2>
      <p class="lead" style="margin-top:14px;">{e(d['news']['subtitle'])}</p>
    </div>
    <div class="tabs-row">{news_tabs}</div>
    <div class="empty-panel">{e(d['news']['empty'])}</div>
  </div>
</section>
"""

    # ---------- EVENTS ----------
    event_tabs = "".join(f'<button class="tab-pill">{e(c)}</button>' for c in d["events"]["types"])
    events_section = f"""
<section class="section section-tight" id="events">
  <div class="container">
    <div class="section-head">
      <div class="eyebrow">{e(d['events']['eyebrow'])}</div>
      <h2>{e(d['events']['title'])}</h2>
      <p class="lead" style="margin-top:14px;">{e(d['events']['subtitle'])}</p>
    </div>
    <div class="tabs-row">{event_tabs}</div>
    <div class="empty-panel">{e(d['events']['empty'])}</div>
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

    # ---------- AI ASSISTANT ----------
    ai_features = "".join(f'<div class="ai-feature"><span class="dot"></span>{e(f)}</div>' for f in d["ai"]["features"])
    ai_section = f"""
<section class="section" id="ai">
  <div class="container ai-wrap">
    <div class="reveal">
      <div class="eyebrow">{e(d['ai']['eyebrow'])}</div>
      <h2>{e(d['ai']['title'])}</h2>
      <p class="lead" style="margin:16px 0 26px;">{e(d['ai']['subtitle'])}</p>
      {ai_features}
    </div>
    <div class="glass chat-panel reveal">
      <div class="chat-head"><span class="dot-live"></span><strong>AI Assistant</strong></div>
      <div class="chat-body" id="ai-chat-body">
        <div class="chat-bubble bot">{e(d['ai']['demoReply'])}</div>
      </div>
      <form id="ai-chat-form" class="chat-input-row" data-demo-reply="{e(d['ai']['demoReply'])}">
        <input id="ai-chat-input" type="text" placeholder="{e(d['ai']['placeholder'])}" autocomplete="off" />
        <button type="submit" class="btn btn-gold btn-sm">{e(d['ai']['send'])}</button>
      </form>
      <div class="ai-disclaimer">{e(d['ai']['disclaimer'])}</div>
    </div>
  </div>
</section>
"""

    # ---------- CABINET ----------
    cab = d["cabinet"]
    features_grid = "".join(f'<div class="glass card" style="padding:20px;"><p>{e(f)}</p></div>' for f in cab["features"])
    cabinet_section = f"""
<section class="section section-tight" id="cabinet">
  <div class="container cabinet-wrap">
    <div class="glass auth-panel reveal" id="cabinet-auth">
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
    <div class="reveal">
      <div class="eyebrow">{e(cab['eyebrow'])}</div>
      <h2>{e(cab['title'])}</h2>
      <p class="lead" style="margin:16px 0 28px;">{e(cab['subtitle'])}</p>
      <div class="grid cabinet-feature-grid">{features_grid}</div>
    </div>
  </div>
</section>
"""

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

    # ---------- FOOTER ----------
    dept_footer_links = "".join(f'<li>{e(dep["name"])}</li>' for dep in d["departments"][:6])
    nav_footer_links = "".join(f'<li><a href="{href}">{e(label)}</a></li>' for href, label in nav_links[:6])
    footer = f"""
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

    toast_and_scripts = """
<div class="toast" id="toast"></div>
<script>document.getElementById('year').textContent = new Date().getFullYear();</script>
<script defer src="/js/main.js"></script>
</body>
</html>
"""

    return (
        head + header + hero + about_section + mission + values_section + directions_section +
        stats_section + structure_section + practical_section + membership_section +
        regions_section + news_section + events_section + partners_section + ai_section +
        cabinet_section + contacts_section + footer + toast_and_scripts
    )


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
    for l in LANGS:
        urls.append(f"""  <url>
    <loc>{BASE_URL}/{l}/</loc>
    {''.join(f'<xhtml:link rel="alternate" hreflang="{ol}" href="{BASE_URL}/{ol}/" />' for ol in LANGS)}
    <changefreq>weekly</changefreq>
    <priority>{'1.0' if l == DEFAULT_LANG else '0.9'}</priority>
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
