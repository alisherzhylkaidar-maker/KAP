#!/usr/bin/env python3
"""
Generates a premium black & gold hero illustration for the KEA homepage:
a stylised Kazakhstan map made of glowing gold lines/nodes, a Baiterek
silhouette, a soft skyline, a fine dot-mesh, and scattered gold particles.
Pure SVG (vector) -> crisp at any size, loads instantly, no raster assets.
"""
import random, math

random.seed(7)

W, H = 1600, 900

# ---------- Stylised Kazakhstan outline (decorative, not cartographically exact) ----------
# Positioned in the right ~60% of the canvas, west (Caspian) on the left of the shape,
# east (Altai) on the right, oriented roughly like the real country's silhouette.
COUNTRY = [
    (660, 260), (760, 190), (900, 165), (1030, 140), (1160, 120), (1280, 145),
    (1380, 200), (1455, 230), (1500, 300), (1470, 360), (1520, 410), (1500, 470),
    (1430, 510), (1400, 580), (1320, 630), (1230, 650), (1150, 700), (1040, 720),
    (950, 690), (880, 710), (800, 670), (740, 690), (680, 630), (700, 560),
    (640, 500), (660, 430), (610, 380), (630, 320), (660, 260),
]

# ---------- City nodes (approximate relative placement, matches the regions map) ----------
CITIES = [
    {"name": "Astana",   "x": 1080, "y": 330, "r": 7, "hub": True},
    {"name": "Almaty",   "x": 1190, "y": 600, "r": 5.5},
    {"name": "Shymkent",  "x": 980, "y": 640, "r": 4.5},
    {"name": "Atyrau",   "x": 730,  "y": 360, "r": 4.5},
    {"name": "Karaganda", "x": 1040, "y": 430, "r": 4.5},
    {"name": "Aktobe",   "x": 800,  "y": 270, "r": 4.5},
]
HUB = next(c for c in CITIES if c.get("hub"))
LINKS = [(HUB, c) for c in CITIES if c is not HUB]
LINKS += [
    (next(c for c in CITIES if c["name"] == "Almaty"), next(c for c in CITIES if c["name"] == "Shymkent")),
    (next(c for c in CITIES if c["name"] == "Atyrau"), next(c for c in CITIES if c["name"] == "Aktobe")),
    (next(c for c in CITIES if c["name"] == "Karaganda"), next(c for c in CITIES if c["name"] == "Shymkent")),
]

def point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside

def poly_path(points):
    d = f"M {points[0][0]:.1f} {points[0][1]:.1f} "
    for x, y in points[1:]:
        d += f"L {x:.1f} {y:.1f} "
    d += "Z"
    return d

svg_parts = []
svg_parts.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">')

# ---------- DEFS ----------
svg_parts.append('''
<defs>
  <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="60%">
    <stop offset="0%" stop-color="#0a0a0a"/>
    <stop offset="42%" stop-color="#0b0b0a"/>
    <stop offset="100%" stop-color="#171206"/>
  </linearGradient>
  <radialGradient id="ambientGlow" cx="72%" cy="45%" r="55%">
    <stop offset="0%" stop-color="#d4af37" stop-opacity="0.16"/>
    <stop offset="55%" stop-color="#d4af37" stop-opacity="0.05"/>
    <stop offset="100%" stop-color="#d4af37" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="nodeGlow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#f5e6a8" stop-opacity="0.95"/>
    <stop offset="40%" stop-color="#d4af37" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="#d4af37" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="hubGlow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#fff7d6" stop-opacity="1"/>
    <stop offset="35%" stop-color="#f5e6a8" stop-opacity="0.7"/>
    <stop offset="100%" stop-color="#d4af37" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="countryStroke" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#8a6a17" stop-opacity="0.55"/>
    <stop offset="50%" stop-color="#d4af37" stop-opacity="0.85"/>
    <stop offset="100%" stop-color="#f5e6a8" stop-opacity="0.55"/>
  </linearGradient>
  <linearGradient id="towerGrad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#f5e6a8"/>
    <stop offset="100%" stop-color="#9a7a22"/>
  </linearGradient>
  <filter id="blurSoft" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <filter id="blurStrong" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="38"/>
  </filter>
  <filter id="blurTiny" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="1.2"/>
  </filter>
  <clipPath id="countryClip">
    <path d="''' + poly_path(COUNTRY) + '''"/>
  </clipPath>
</defs>
''')

# ---------- Background ----------
svg_parts.append(f'<rect width="{W}" height="{H}" fill="url(#bgGrad)"/>')
svg_parts.append(f'<rect width="{W}" height="{H}" fill="url(#ambientGlow)"/>')
svg_parts.append(f'<circle cx="1150" cy="420" r="420" fill="#d4af37" opacity="0.05" filter="url(#blurStrong)"/>')
svg_parts.append(f'<circle cx="{HUB["x"]}" cy="{HUB["y"]-60}" r="260" fill="#f5e6a8" opacity="0.06" filter="url(#blurStrong)"/>')
svg_parts.append(f'<circle cx="780" cy="700" r="180" fill="#d4af37" opacity="0.045" filter="url(#blurStrong)"/>')

# ---------- Fine dot-mesh clipped inside the country silhouette ----------
svg_parts.append(f'<g clip-path="url(#countryClip)">')
minx = min(p[0] for p in COUNTRY); maxx = max(p[0] for p in COUNTRY)
miny = min(p[1] for p in COUNTRY); maxy = max(p[1] for p in COUNTRY)
step = 26
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        jitterx = x + random.uniform(-4, 4)
        jittery = y + random.uniform(-4, 4)
        if point_in_polygon(jitterx, jittery, COUNTRY):
            r = random.uniform(0.8, 1.8)
            op = random.uniform(0.10, 0.32)
            svg_parts.append(f'<circle cx="{jitterx:.1f}" cy="{jittery:.1f}" r="{r:.2f}" fill="#d4af37" opacity="{op:.2f}"/>')
        y += step
    x += step
# subtle inner gradient wash for depth
svg_parts.append(f'<rect x="{minx}" y="{miny}" width="{maxx-minx}" height="{maxy-miny}" fill="#d4af37" opacity="0.03"/>')
svg_parts.append('</g>')

# ---------- Country outline ----------
svg_parts.append(f'<path d="{poly_path(COUNTRY)}" fill="none" stroke="url(#countryStroke)" stroke-width="1.6" opacity="0.8"/>')
svg_parts.append(f'<path d="{poly_path(COUNTRY)}" fill="none" stroke="#d4af37" stroke-width="3.5" opacity="0.10" filter="url(#blurSoft)"/>')

# ---------- Connection network ----------
for a, b in LINKS:
    mx, my = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2 - random.uniform(15, 35)
    path = f'M {a["x"]} {a["y"]} Q {mx:.1f} {my:.1f} {b["x"]} {b["y"]}'
    svg_parts.append(f'<path d="{path}" fill="none" stroke="#d4af37" stroke-width="1.1" opacity="0.55"/>')
    svg_parts.append(f'<path d="{path}" fill="none" stroke="#f5e6a8" stroke-width="2.6" opacity="0.16" filter="url(#blurSoft)"/>')
    # a small traveling dot to suggest data/flow
    t = random.uniform(0.2, 0.8)
    fx = (1 - t) ** 2 * a["x"] + 2 * (1 - t) * t * mx + t ** 2 * b["x"]
    fy = (1 - t) ** 2 * a["y"] + 2 * (1 - t) * t * my + t ** 2 * b["y"]
    svg_parts.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="2.1" fill="#f5e6a8" opacity="0.85"/>')

# ---------- City nodes ----------
for c in CITIES:
    glow = "hubGlow" if c.get("hub") else "nodeGlow"
    glow_r = c["r"] * (7 if c.get("hub") else 5)
    svg_parts.append(f'<circle cx="{c["x"]}" cy="{c["y"]}" r="{glow_r:.1f}" fill="url(#{glow})"/>')
    svg_parts.append(f'<circle cx="{c["x"]}" cy="{c["y"]}" r="{c["r"]:.1f}" fill="#fff7d6"/>')
    svg_parts.append(f'<circle cx="{c["x"]}" cy="{c["y"]}" r="{c["r"]+2.2:.1f}" fill="none" stroke="#d4af37" stroke-width="0.8" opacity="0.6"/>')

# ---------- Astana skyline (simple silhouettes behind Baiterek) ----------
sx, sy = HUB["x"], HUB["y"]
buildings = [
    (-225, 42, 100), (-178, 56, 140), (-128, 36, 85),
    (128, 46, 120), (176, 34, 80), (218, 54, 135),
]
skyline = ['<g opacity="0.5">']
for dx, w, h in buildings:
    bx2 = sx + dx
    by2 = sy + 18
    skyline.append(f'<rect x="{bx2:.1f}" y="{by2-h:.1f}" width="{w}" height="{h}" fill="#0a0a09" stroke="#d4af37" stroke-width="0.6" opacity="0.6"/>')
    wcount = max(1, h // 22)
    for wi in range(int(wcount)):
        wy = by2 - 10 - wi * 20
        if random.random() < 0.55:
            skyline.append(f'<rect x="{bx2+6:.1f}" y="{wy:.1f}" width="4" height="6" fill="#f5e6a8" opacity="{random.uniform(0.2,0.5):.2f}"/>')
        if w > 60 and random.random() < 0.5:
            skyline.append(f'<rect x="{bx2+w-16:.1f}" y="{wy:.1f}" width="4" height="6" fill="#f5e6a8" opacity="{random.uniform(0.15,0.4):.2f}"/>')
skyline.append('</g>')
svg_parts.append(''.join(skyline))

# ---------- Baiterek silhouette (stylised) ----------
bx, by = sx, sy + 14   # base anchor (ground level near Astana node)
trunk_top_y = by - 150
ball_cy = trunk_top_y - 18
ball_r = 30
baiterek = f'''
<g opacity="0.95">
  <path d="M {bx-46},{by} C {bx-30},{by-70} {bx-16},{by-120} {bx-7},{trunk_top_y}
           L {bx+7},{trunk_top_y} C {bx+16},{by-120} {bx+30},{by-70} {bx+46},{by}
           Z" fill="#0c0c0a" stroke="url(#towerGrad)" stroke-width="1.4"/>
  <path d="M {bx-46},{by} C {bx-30},{by-70} {bx-16},{by-120} {bx-7},{trunk_top_y}" fill="none" stroke="#f5e6a8" stroke-width="0.8" opacity="0.7"/>
  <path d="M {bx+46},{by} C {bx+30},{by-70} {bx+16},{by-120} {bx+7},{trunk_top_y}" fill="none" stroke="#f5e6a8" stroke-width="0.8" opacity="0.7"/>
  <circle cx="{bx}" cy="{ball_cy}" r="{ball_r+10}" fill="url(#hubGlow)"/>
  <circle cx="{bx}" cy="{ball_cy}" r="{ball_r}" fill="#0c0c0a" stroke="url(#towerGrad)" stroke-width="2"/>
  <circle cx="{bx}" cy="{ball_cy}" r="{ball_r-7}" fill="none" stroke="#d4af37" stroke-width="0.8" opacity="0.7"/>
  <path d="M {bx-ball_r},{ball_cy} L {bx+ball_r},{ball_cy} M {bx},{ball_cy-ball_r} L {bx},{ball_cy+ball_r}
           M {bx-ball_r*0.7},{ball_cy-ball_r*0.7} L {bx+ball_r*0.7},{ball_cy+ball_r*0.7}
           M {bx-ball_r*0.7},{ball_cy+ball_r*0.7} L {bx+ball_r*0.7},{ball_cy-ball_r*0.7}"
        stroke="#d4af37" stroke-width="0.6" opacity="0.55"/>
  <line x1="{bx}" y1="{ball_cy-ball_r}" x2="{bx}" y2="{ball_cy-ball_r-26}" stroke="#f5e6a8" stroke-width="1.4" opacity="0.8"/>
  <circle cx="{bx}" cy="{ball_cy-ball_r-26}" r="2.4" fill="#fff7d6"/>
  <line x1="{bx}" y1="{by-6}" x2="{bx}" y2="{trunk_top_y+10}" stroke="#f5e6a8" stroke-width="1" opacity="0.35"/>
</g>
'''
svg_parts.append(baiterek)

# ---------- Scattered gold particles (atmosphere, sparse into the dark left zone too) ----------
particles = ['<g>']
for _ in range(220):
    px = random.uniform(0, W)
    py = random.uniform(0, H)
    # bias density toward the right side; keep the left ~40% very sparse
    if px < W * 0.42 and random.random() > 0.10:
        continue
    r = random.uniform(0.5, 2.6)
    op = random.uniform(0.10, 0.55)
    particles.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" fill="#f5e6a8" opacity="{op:.2f}"/>')
particles.append('</g>')
svg_parts.append(''.join(particles))

# ---------- Soft vignette for depth ----------
svg_parts.append(f'''
<radialGradient id="vignette" cx="50%" cy="50%" r="75%">
  <stop offset="60%" stop-color="#000000" stop-opacity="0"/>
  <stop offset="100%" stop-color="#000000" stop-opacity="0.35"/>
</radialGradient>
<rect width="{W}" height="{H}" fill="url(#vignette)"/>
''')

svg_parts.append('</svg>')

out = '\n'.join(svg_parts)
with open('/home/claude/site/assets/hero-illustration.svg', 'w', encoding='utf-8') as f:
    f.write(out)
print('SVG written:', len(out), 'chars')
