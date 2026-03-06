#!/usr/bin/env python3
"""Generate missing state ranking pages."""
import json
import os
import re

with open('data/fbi/cities_crime_2024.json') as f:
    cities = json.load(f)

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

STATE_NAMES = {v: k.title() for k, v in STATE_ABBREVS.items()}

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

# Missing states to generate
missing = ['minnesota', 'hawaii', 'florida']

for state_slug in missing:
    state_name = state_slug.replace('-', ' ').title()
    state_upper = state_name.upper()
    state_abbr = STATE_ABBREVS.get(state_upper, state_slug[:2].upper())
    
    # Filter cities for this state
    state_cities = [c for c in cities if c['state'].strip().upper() == state_upper]
    
    if not state_cities:
        print(f"⚠️ {state_name}: No cities in FBI data - skipping")
        continue
    
    # Sort by safety score
    state_cities.sort(key=lambda x: x.get('safety_score', 0), reverse=True)
    
    # Build HTML
    safest_20 = state_cities[:20]
    dangerous_10 = list(reversed(state_cities[-10:])) if len(state_cities) >= 10 else []
    
    safest_rows = '\n'.join([
        f'<tr><td>{i+1}</td><td>{c["city"]}</td><td><span style="color:{get_color(c.get("safety_score",50))}">{c.get("safety_score",50)}</span></td><td>{get_grade(c.get("safety_score",50))}</td></tr>'
        for i, c in enumerate(safest_20)
    ])
    
    dangerous_rows = '\n'.join([
        f'<tr><td>{i+1}</td><td>{c["city"]}</td><td><span style="color:{get_color(c.get("safety_score",50))}">{c.get("safety_score",50)}</span></td><td>{get_grade(c.get("safety_score",50))}</td></tr>'
        for i, c in enumerate(dangerous_10)
    ]) if dangerous_10 else ''
    
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Safest Cities in {state_name} 2024 | Crime Rankings | HoodSafe</title>
<meta name="description" content="Safest cities in {state_name} ranked by crime rate. See the top 20 safest and most dangerous cities in {state_abbr}. Latest FBI data.">
<link rel="icon" href="/favicon.ico">
<style>:root{{--primary:#0d9488;--bg:#f8fafc;--card:#fff;--text:#1e293b;--muted:#64748b;--border:#e2e8f0}}*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}.container{{max-width:1000px;margin:0 auto;padding:1rem}}header{{background:var(--card);border-bottom:1px solid var(--border);padding:1rem 0}}.logo{{font-weight:700;font-size:1.25rem;color:var(--primary);text-decoration:none}}h1{{font-size:1.5rem;margin-bottom:0.5rem}}h2{{font-size:1.25rem;margin:2rem 0 1rem}}.section{{background:var(--card);padding:1.5rem;border-radius:1rem;margin:1.5rem 0}}table{{width:100%;border-collapse:collapse}}th,td{{padding:0.75rem;text-align:left;border-bottom:1px solid var(--border)}}th{{font-weight:600;color:var(--muted)}}footer{{text-align:center;padding:2rem;color:var(--muted)}}a{{color:var(--primary)}}</style>
</head><body>
<header><div class="container"><a href="/" class="logo"><svg width="22" height="22" viewBox="0 0 512 512" style="vertical-align:middle;margin-right:6px"><path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="#0d9488" opacity="0.15"/><path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="none" stroke="#0d9488" stroke-width="24"/><path d="M256 196l-60 48v64h40v-36h40v36h40v-64l-60-48z" fill="#0d9488"/></svg>HoodSafe</a></div></header><div class="container" style="font-size:0.875rem;color:var(--muted);padding-top:0.5rem"><a href="/" style="color:var(--primary);text-decoration:none">Home</a> → <a href="/#states-section" style="color:var(--primary);text-decoration:none">States</a> → <span>{state_name}</span></div>
<main class="container">
<h1>Safest Cities in {state_name} - Crime Rankings</h1>
<p>Crime rate rankings for {len(state_cities)} cities • Latest FBI Data</p>
<p style="margin-top:1rem">This ranking includes {len(state_cities)} cities in {state_name} with crime data from the FBI's Uniform Crime Reporting (UCR) program. Safety scores are calculated using violent crime rates, property crime rates, and population data.</p>

<div class="section">
<h2>🏆 Top 20 Safest Cities in {state_name}</h2>
<table><thead><tr><th>Rank</th><th>City</th><th>Score</th><th>Grade</th></tr></thead>
<tbody>{safest_rows}</tbody></table>
</div>

{f'''<div class="section">
<h2>⚠️ 10 Most Dangerous Cities in {state_name}</h2>
<table><thead><tr><th>Rank</th><th>City</th><th>Score</th><th>Grade</th></tr></thead>
<tbody>{dangerous_rows}</tbody></table>
</div>''' if dangerous_rows else ''}

</main>
<footer>© 2026 HoodSafe.org • <a href="/">Home</a> • <a href="/#states-section">States</a></footer>
</body></html>'''
    
    # Write file
    folder = f'safest-cities/{state_slug}'
    os.makedirs(folder, exist_ok=True)
    with open(f'{folder}/index.html', 'w') as f:
        f.write(html)
    
    print(f"✓ {state_name}: {len(state_cities)} cities")

print("\n✅ Done!")
