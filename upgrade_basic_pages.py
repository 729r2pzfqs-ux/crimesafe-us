#!/usr/bin/env python3
"""Upgrade basic city pages with FAQ and Compare CTA."""
import json
import os
import re

# Load city data
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

def get_state_abbrev(state):
    return STATE_ABBREVS.get(state.upper().strip(), state[:2].upper())

# Create city lookup by slug
city_lookup = {}
for c in cities:
    state_abbr = get_state_abbrev(c['state'])
    slug = slugify(f"{c['city']}-{state_abbr}")
    city_lookup[slug] = c

# Find basic pages (no FAQ)
basic_pages = []
for folder in os.listdir('city'):
    filepath = f'city/{folder}/index.html'
    if os.path.isfile(filepath):
        with open(filepath) as f:
            content = f.read()
        if 'faq-item' not in content:
            basic_pages.append((folder, filepath))

print(f"Found {len(basic_pages)} basic pages to upgrade...")

upgraded = 0
for folder, filepath in basic_pages:
    # Get city data
    city_data = city_lookup.get(folder)
    if not city_data:
        continue
    
    city_name = city_data['city']
    state_abbr = get_state_abbrev(city_data['state'])
    state_name = STATE_NAMES.get(state_abbr, state_abbr)
    state_slug = slugify(state_name)
    
    score = city_data.get('safety_score', 50)
    vrate = city_data.get('violent_rate', 0)
    prate = city_data.get('property_rate', 0)
    total_rate = vrate + prate
    
    # Generate FAQ + CTA HTML
    faq_cta = f'''
        <div class="section" style="margin-top:1.5rem">
            <h2 style="font-size:1.125rem;margin-bottom:1rem">Frequently Asked Questions</h2>
            <div class="faq" style="font-size:0.9rem">
                <div class="faq-item" style="border-bottom:1px solid var(--border);padding:0.75rem 0">
                    <div style="font-weight:600;margin-bottom:0.25rem">What is {city_name}'s crime rate?</div>
                    <div style="color:var(--muted)">{city_name} has a total crime rate of {total_rate:.1f} per 100,000 residents, with {vrate:.1f} violent crimes and {prate:.1f} property crimes per 100k.</div>
                </div>
                <div class="faq-item" style="padding:0.75rem 0">
                    <div style="font-weight:600;margin-bottom:0.25rem">How does {city_name} compare to the national average?</div>
                    <div style="color:var(--muted)">{"Violent crime is below" if vrate < 380 else "Violent crime is above"} the US average of 380 per 100k. {"Property crime is below" if prate < 2000 else "Property crime is above"} the national average of 2,000 per 100k.</div>
                </div>
            </div>
        </div>
        
        <div style="background:linear-gradient(135deg,#0d9488,#14b8a6);color:#fff;padding:1.5rem;border-radius:0.75rem;text-align:center;margin-top:1.5rem">
            <h3 style="margin-bottom:0.5rem">Compare {city_name} with Other Cities</h3>
            <p style="opacity:0.9;margin-bottom:1rem">See how {city_name} ranks against other cities in {state_name}</p>
            <a href="/safest-cities/{state_slug}/" style="display:inline-block;background:#fff;color:#0d9488;padding:0.5rem 1rem;border-radius:0.5rem;text-decoration:none;font-weight:600">View {state_name} Rankings →</a>
        </div>
'''
    
    # Read current content
    with open(filepath) as f:
        content = f.read()
    
    # Insert before </main>
    if '</main>' in content:
        content = content.replace('</main>', faq_cta + '\n    </main>')
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        upgraded += 1
        if upgraded % 1000 == 0:
            print(f"  Upgraded {upgraded}...")

print(f"\n✅ Upgraded {upgraded} basic pages with FAQ + Compare CTA!")
