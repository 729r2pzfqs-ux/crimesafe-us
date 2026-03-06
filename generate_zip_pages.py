#!/usr/bin/env python3
"""Generate ZIP code pages by mapping to city safety scores."""
import json
import csv
import os
import re

# Load our FBI cities
with open('data/fbi/cities_crime_2024.json') as f:
    fbi_cities = json.load(f)

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

def normalize(s):
    s = s.lower().strip()
    s = re.sub(r'\s+(city|town|village|borough|township|cdp)$', '', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

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

def get_grade_text(score):
    if score >= 80: return 'Very Safe'
    if score >= 70: return 'Safe'
    if score >= 60: return 'Moderate'
    if score >= 50: return 'Below Average'
    return 'High Crime'

# Create lookups
city_lookup = {}
for c in fbi_cities:
    state_upper = c['state'].strip().upper()
    abbr = STATE_ABBREVS.get(state_upper, state_upper[:2])
    key1 = (c['city'].lower().strip(), abbr)
    city_lookup[key1] = c
    key2 = (normalize(c['city']), abbr)
    city_lookup[key2] = c

# Load ZIP data and match
matched_zips = []
with open('/tmp/zip_city.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        city = row['city'].strip()
        state = row['state_abbr'].strip().upper()
        zipcode = row['zipcode'].strip()
        county = row.get('county', '').strip()
        
        key1 = (city.lower(), state)
        if key1 in city_lookup:
            matched_zips.append((zipcode, city, state, county, city_lookup[key1]))
            continue
        
        key2 = (normalize(city), state)
        if key2 in city_lookup:
            matched_zips.append((zipcode, city, state, county, city_lookup[key2]))

print(f"Generating {len(matched_zips)} ZIP code pages...")

os.makedirs('zip', exist_ok=True)

for i, (zipcode, city, state, county, data) in enumerate(matched_zips):
    score = data.get('safety_score', 50)
    grade = get_grade(score)
    color = get_color(score)
    grade_text = get_grade_text(score)
    vrate = data.get('violent_rate', 0)
    prate = data.get('property_rate', 0)
    pop = data.get('population', 0)
    city_name = data['city']
    city_slug = slugify(f"{city_name}-{state}")
    state_name = STATE_NAMES.get(state, state)
    
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZIP Code {zipcode} Crime Rate &amp; Safety | {city}, {state} | HoodSafe</title>
<meta name="description" content="Is ZIP code {zipcode} safe? {city}, {state} has a safety score of {score}/100 ({grade_text}). View crime rates and safety data.">
<link rel="canonical" href="https://hoodsafe.org/zip/{zipcode}/">
<link rel="icon" href="/favicon.ico">
<style>:root{{--primary:#0d9488;--bg:#f8fafc;--card:#fff;--text:#1e293b;--muted:#64748b;--border:#e2e8f0}}*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}.container{{max-width:800px;margin:0 auto;padding:1rem}}header{{background:var(--card);border-bottom:1px solid var(--border);padding:1rem 0}}.logo{{font-weight:700;font-size:1.25rem;color:var(--primary);text-decoration:none}}h1{{font-size:1.5rem;margin-bottom:0.5rem}}h2{{font-size:1.125rem;margin:1.5rem 0 1rem;color:var(--muted)}}.card{{background:var(--card);padding:1.5rem;border-radius:1rem;margin:1rem 0}}.score-box{{text-align:center;padding:2rem}}.score{{font-size:4rem;font-weight:700}}.grade{{font-size:1.5rem;margin-top:0.5rem}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin:1rem 0}}.stat{{text-align:center;padding:1rem;background:#f1f5f9;border-radius:0.5rem}}.stat-value{{font-size:1.5rem;font-weight:600}}.stat-label{{font-size:0.875rem;color:var(--muted)}}.note{{background:#fef3c7;padding:1rem;border-radius:0.5rem;font-size:0.875rem;margin:1rem 0}}.btn{{display:inline-block;background:var(--primary);color:#fff;padding:0.75rem 1.5rem;border-radius:0.5rem;text-decoration:none;margin-top:1rem}}footer{{text-align:center;padding:2rem;color:var(--muted)}}a{{color:var(--primary)}}</style>
</head><body>
<header><div class="container"><a href="/" class="logo"><svg width="22" height="22" viewBox="0 0 512 512" style="vertical-align:middle;margin-right:6px"><path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="#0d9488" opacity="0.15"/><path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="none" stroke="#0d9488" stroke-width="24"/><path d="M256 196l-60 48v64h40v-36h40v36h40v-64l-60-48z" fill="#0d9488"/></svg>HoodSafe</a></div></header>
<div class="container" style="font-size:0.875rem;color:var(--muted);padding-top:0.5rem"><a href="/">Home</a> → <a href="/zip/">ZIP Codes</a> → {zipcode}</div>
<main class="container">
<h1>ZIP Code {zipcode} Safety Score</h1>
<p style="color:var(--muted)">{city}, {state_name}{f" • {county} County" if county else ""}</p>

<div class="card score-box">
<div class="score" style="color:{color}">{score}</div>
<div class="grade">Grade: {grade} — {grade_text}</div>
</div>

<div class="note">
📍 This score is based on crime data for <strong>{city_name}, {state}</strong>, the primary city for ZIP code {zipcode}. Individual neighborhoods within this ZIP may vary.
</div>

<h2>Crime Statistics</h2>
<div class="stats">
<div class="stat"><div class="stat-value">{vrate:.0f}</div><div class="stat-label">Violent Crime Rate<br>(per 100K)</div></div>
<div class="stat"><div class="stat-value">{prate:.0f}</div><div class="stat-label">Property Crime Rate<br>(per 100K)</div></div>
<div class="stat"><div class="stat-value">{pop:,}</div><div class="stat-label">City Population</div></div>
</div>

<a href="/city/{city_slug}/" class="btn">View Full {city_name} Details →</a>

<h2>About ZIP Code {zipcode}</h2>
<p>ZIP code {zipcode} is located in <strong>{city}, {state_name}</strong>. Based on FBI crime data, this area has a safety score of <strong>{score}/100</strong>, earning a grade of <strong>{grade}</strong>.</p>

<p>{'This is considered a safe area with crime rates below the national average.' if score >= 70 else 'Crime rates in this area are around the national average.' if score >= 50 else 'This area has higher than average crime rates. Exercise normal precautions.'}</p>

</main>
<footer>© 2026 HoodSafe.org • <a href="/">Home</a> • <a href="/zip/">ZIP Codes</a> • Data: FBI UCR</footer>
</body></html>'''
    
    os.makedirs(f'zip/{zipcode}', exist_ok=True)
    with open(f'zip/{zipcode}/index.html', 'w') as f:
        f.write(html)
    
    if (i + 1) % 1000 == 0:
        print(f"  Generated {i + 1}...")

print(f"\n✅ Generated {len(matched_zips)} ZIP code pages!")
