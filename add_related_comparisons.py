#!/usr/bin/env python3
"""Add related comparisons section to all comparison pages."""
import os
import re
import json
from collections import defaultdict

# Load city data
with open('data/fbi/cities_crime_2024.json') as f:
    cities = json.load(f)

# Sort by population and get top 500
cities_sorted = sorted(cities, key=lambda x: x.get('population', 0), reverse=True)[:500]

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

def slugify(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def get_state_abbrev(state):
    return STATE_ABBREVS.get(state.upper().strip(), state[:2].upper())

# Build city slug map
city_slugs = {}
city_names = {}
for c in cities_sorted:
    slug = slugify(f"{c['city']}-{get_state_abbrev(c['state'])}")
    city_slugs[slug] = c
    city_names[slug] = f"{c['city']}, {get_state_abbrev(c['state'])}"

# Build comparison links for each city (top 4 most popular comparisons)
# Using largest cities as default comparison targets
popular_slugs = [slugify(f"{c['city']}-{get_state_abbrev(c['state'])}") for c in cities_sorted[:20]]

def get_related_comparisons(city1_slug, city2_slug, limit=4):
    """Get related comparison links for both cities."""
    links = []
    
    # For city1, find comparisons with other popular cities
    for other in popular_slugs[:10]:
        if other != city1_slug and other != city2_slug:
            slugs = sorted([city1_slug, other])
            url = f"/compare/{slugs[0]}-vs-{slugs[1]}/"
            city1_name = city_names.get(city1_slug, city1_slug)
            other_name = city_names.get(other, other)
            links.append((city1_name.split(',')[0], other_name.split(',')[0], url))
            if len(links) >= limit // 2:
                break
    
    # For city2, find comparisons with other popular cities
    for other in popular_slugs[:10]:
        if other != city1_slug and other != city2_slug:
            slugs = sorted([city2_slug, other])
            url = f"/compare/{slugs[0]}-vs-{slugs[1]}/"
            city2_name = city_names.get(city2_slug, city2_slug)
            other_name = city_names.get(other, other)
            links.append((city2_name.split(',')[0], other_name.split(',')[0], url))
            if len(links) >= limit:
                break
    
    return links[:limit]

# Process all comparison folders
compare_dir = 'compare'
folders = [d for d in os.listdir(compare_dir) if os.path.isdir(f'{compare_dir}/{d}')]
print(f"Processing {len(folders)} comparison pages...")

updated = 0
for i, folder in enumerate(folders):
    if '-vs-' not in folder:
        continue
    
    filepath = f'{compare_dir}/{folder}/index.html'
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r') as f:
        html = f.read()
    
    # Skip if already has related comparisons
    if 'Related Comparisons' in html:
        continue
    
    # Extract city slugs from folder name
    parts = folder.split('-vs-')
    if len(parts) != 2:
        continue
    city1_slug, city2_slug = parts
    
    # Get related comparison links
    related = get_related_comparisons(city1_slug, city2_slug)
    if not related:
        continue
    
    # Build related section HTML
    links_html = ''.join([f'<a href="{url}" class="rel-link">{c1} vs {c2}</a>' for c1, c2, url in related])
    related_section = f'''
<div class="related" style="background:var(--card);padding:1.25rem;border-radius:0.75rem;margin-top:1.5rem">
<h2 style="font-size:1rem;margin-bottom:0.75rem">Related Comparisons</h2>
<div style="display:flex;flex-wrap:wrap;gap:0.5rem">{links_html}</div>
</div>
<style>.rel-link{{display:inline-block;padding:0.5rem 1rem;background:var(--bg);border-radius:0.5rem;text-decoration:none;color:var(--text);font-size:0.875rem;transition:background 0.2s}}.rel-link:hover{{background:var(--border)}}</style>'''
    
    # Insert before </main>
    html = html.replace('</main>', f'{related_section}\n</main>')
    
    with open(filepath, 'w') as f:
        f.write(html)
    
    updated += 1
    if updated % 5000 == 0:
        print(f"  Updated {updated}...")

print(f"\n✅ Updated {updated} comparison pages with related links")
