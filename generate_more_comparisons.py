#!/usr/bin/env python3
"""Generate comparison pages for top 200 cities."""
import json
import os
import re

# Load city data
with open('data/fbi/cities_crime_2024.json') as f:
    cities = json.load(f)

# Sort by population (largest first)
cities_sorted = sorted(cities, key=lambda x: x.get('population', 0), reverse=True)
top_cities = cities_sorted[:200]

print(f"Generating comparisons for top {len(top_cities)} cities...")

def slugify(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def get_grade(score):
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'

def get_color(score):
    if score >= 70: return '#16a34a'
    if score >= 50: return '#f59e0b'
    return '#dc2626'

STATE_ABBREVS = {
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA',
    'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
    'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA',
    'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO',
    'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH',
    'OKLAHOMA': 'OK', 'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT',
    'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY'
}

def get_state_abbrev(state):
    return STATE_ABBREVS.get(state.upper().strip(), state[:2].upper())

# Build expected folder names first to check what we need
folders_needed = {}
for i, city1 in enumerate(top_cities):
    for city2 in top_cities[i+1:]:
        slug1 = slugify(f"{city1['city']}-{get_state_abbrev(city1['state'])}")
        slug2 = slugify(f"{city2['city']}-{get_state_abbrev(city2['state'])}")
        if slug1 > slug2:
            slug1, slug2 = slug2, slug1
            c1, c2 = city2, city1
        else:
            c1, c2 = city1, city2
        folder = f"{slug1}-vs-{slug2}"
        folders_needed[folder] = (c1, c2)

# Get existing comparisons to skip
existing = set()
if os.path.exists('compare'):
    for d in os.listdir('compare'):
        if d != 'index.html' and os.path.isdir(f'compare/{d}'):
            existing.add(d)

to_create = {k: v for k, v in folders_needed.items() if k not in existing}
print(f"Need {len(to_create)} new comparisons ({len(existing)} existing, {len(folders_needed)} total)")

generated = 0

for folder, (city1, city2) in to_create.items():
        name1 = city1['city']
        name2 = city2['city']
        state1 = get_state_abbrev(city1['state'])
        state2 = get_state_abbrev(city2['state'])
        
        slug1 = slugify(f"{name1}-{state1}")
        slug2 = slugify(f"{name2}-{state2}")
        
        score1 = city1.get('safety_score', 50)
        score2 = city2.get('safety_score', 50)
        vrate1 = city1.get('violent_rate', 0)
        vrate2 = city2.get('violent_rate', 0)
        prate1 = city1.get('property_rate', 0)
        prate2 = city2.get('property_rate', 0)
        pop1 = city1.get('population', 0)
        pop2 = city2.get('population', 0)
        
        winner = name1 if score1 > score2 else name2 if score2 > score1 else "Tie"
        diff = abs(score1 - score2)
        
        html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name1} vs {name2} Crime Comparison | HoodSafe</title>
<meta name="description" content="Compare crime rates: {name1}, {state1} (Score: {score1}) vs {name2}, {state2} (Score: {score2}). See which city is safer.">
<link rel="icon" href="/favicon.ico">
<style>:root{{--primary:#0d9488;--bg:#f8fafc;--card:#fff;--text:#1e293b;--muted:#64748b;--border:#e2e8f0}}*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}.container{{max-width:900px;margin:0 auto;padding:1rem}}header{{background:var(--card);border-bottom:1px solid var(--border);padding:1rem 0}}.logo{{font-weight:700;font-size:1.25rem;color:var(--primary);text-decoration:none}}h1{{font-size:1.25rem;margin-bottom:1rem}}h2{{font-size:1rem;margin:1.5rem 0 1rem}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}.card{{background:var(--card);padding:1.25rem;border-radius:0.75rem;text-align:center}}.score{{font-size:2.5rem;font-weight:700}}.grade{{font-size:1rem;margin-top:0.25rem}}.stat{{display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid var(--border)}}.winner{{background:linear-gradient(135deg,#0d9488,#14b8a6);color:#fff;padding:1.5rem;border-radius:0.75rem;text-align:center;margin:1.5rem 0}}.winner h2{{color:#fff;margin:0}}footer{{text-align:center;padding:2rem;color:var(--muted)}}a{{color:var(--primary)}}@media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}</style>
</head><body>
<header><div class="container"><a href="/" class="logo"><svg width="22" height="22" viewBox="0 0 512 512" style="vertical-align:middle;margin-right:6px"><path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="#0d9488" opacity="0.15"/><path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="none" stroke="#0d9488" stroke-width="24"/><path d="M256 196l-60 48v64h40v-36h40v36h40v-64l-60-48z" fill="#0d9488"/></svg>HoodSafe</a></div></header>
<div class="container" style="font-size:0.875rem;color:var(--muted);padding-top:0.5rem"><a href="/">Home</a> → <a href="/compare/">Compare</a> → {name1} vs {name2}</div>
<main class="container">
<h1>{name1}, {state1} vs {name2}, {state2}</h1>
<div class="grid">
<div class="card"><h2>{name1}, {state1}</h2><div class="score" style="color:{get_color(score1)}">{score1}</div><div class="grade">Grade: {get_grade(score1)}</div>
<div class="stat"><span>Violent Rate</span><span>{vrate1:.1f}/100k</span></div>
<div class="stat"><span>Property Rate</span><span>{prate1:.1f}/100k</span></div>
<div class="stat"><span>Population</span><span>{pop1:,}</span></div>
<a href="/city/{slug1}/" style="display:block;margin-top:1rem">View Details →</a></div>
<div class="card"><h2>{name2}, {state2}</h2><div class="score" style="color:{get_color(score2)}">{score2}</div><div class="grade">Grade: {get_grade(score2)}</div>
<div class="stat"><span>Violent Rate</span><span>{vrate2:.1f}/100k</span></div>
<div class="stat"><span>Property Rate</span><span>{prate2:.1f}/100k</span></div>
<div class="stat"><span>Population</span><span>{pop2:,}</span></div>
<a href="/city/{slug2}/" style="display:block;margin-top:1rem">View Details →</a></div>
</div>
<div class="winner"><h2>{"🏆 " + winner + " is Safer" if winner != "Tie" else "🤝 It's a Tie!"}</h2><p style="margin-top:0.5rem;opacity:0.9">{f"by {diff} points" if diff > 0 else "Same safety score"}</p></div>
</main>
<footer>© 2026 HoodSafe.org • <a href="/">Home</a> • <a href="/compare/">Compare Cities</a></footer>
</body></html>'''
        
        os.makedirs(f'compare/{folder}', exist_ok=True)
        with open(f'compare/{folder}/index.html', 'w') as f:
            f.write(html)
        
        generated += 1
        if generated % 1000 == 0:
            print(f"  Generated {generated}...")

print(f"\n✅ Generated {generated} new comparisons")
print(f"Total comparisons: {generated + len(existing) + 1}")
