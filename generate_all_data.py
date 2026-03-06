#!/usr/bin/env python3
"""Generate front page data files from FBI data - honest 2024 only."""
import json

# Load FBI data
with open('data/fbi/cities_crime_2024.json') as f:
    cities = json.load(f)

print(f"Loaded {len(cities)} cities from FBI data")

# State abbrevs
STATE_ABBREVS = {
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
    'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID',
    'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
    'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
    'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
    'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
    'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
    'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
    'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
    'WISCONSIN': 'WI', 'WYOMING': 'WY', 'DISTRICT OF COLUMBIA': 'DC'
}

def slugify(name):
    """Convert city name to URL slug."""
    import re
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def shorten_name(name):
    """Shorten long department names for display."""
    replacements = {
        'Las Vegas Metropolitan Police Department': 'Las Vegas',
        'Metropolitan Nashville Police Department': 'Nashville',
        'Charlotte-Mecklenburg': 'Charlotte',
        'Louisville Metro': 'Louisville',
        'Honolulu Police Department': 'Honolulu',
    }
    return replacements.get(name, name)

def get_state_abbrev(state):
    return STATE_ABBREVS.get(state.strip().upper(), state[:2].upper())

# City coordinates (approximate)
COORDS = {
    'New York': (40.7128, -74.006), 'Los Angeles': (34.0522, -118.2437),
    'Chicago': (41.8781, -87.6298), 'Houston': (29.7604, -95.3698),
    'Phoenix': (33.4484, -112.074), 'Philadelphia': (39.9526, -75.1652),
    'San Antonio': (29.4241, -98.4936), 'San Diego': (32.7157, -117.1611),
    'Dallas': (32.7767, -96.797), 'San Jose': (37.3382, -121.8863),
    'Austin': (30.2672, -97.7431), 'Jacksonville': (30.3322, -81.6557),
    'Fort Worth': (32.7555, -97.3308), 'Columbus': (39.9612, -82.9988),
    'Indianapolis': (39.7684, -86.1581), 'Charlotte-Mecklenburg': (35.2271, -80.8431),
    'San Francisco': (37.7749, -122.4194), 'Seattle': (47.6062, -122.3321),
    'Denver': (39.7392, -104.9903), 'Washington': (38.9072, -77.0369),
    'Metropolitan Nashville Police Department': (36.1627, -86.7816),
    'Oklahoma City': (35.4676, -97.5164), 'El Paso': (31.7619, -106.485),
    'Boston': (42.3601, -71.0589), 'Portland': (45.5155, -122.6789),
    'Las Vegas Metropolitan Police Department': (36.1699, -115.1398),
    'Detroit': (42.3314, -83.0458), 'Memphis': (35.1495, -90.049),
    'Louisville Metro': (38.2527, -85.7585), 'Baltimore': (39.2904, -76.6122),
    'Milwaukee': (43.0389, -87.9065), 'Albuquerque': (35.0844, -106.6504),
    'Tucson': (32.2226, -110.9747), 'Fresno': (36.7378, -119.7871),
    'Sacramento': (38.5816, -121.4944), 'Mesa': (33.4152, -111.8315),
    'Kansas City': (39.0997, -94.5786), 'Atlanta': (33.749, -84.388),
    'Omaha': (41.2565, -95.9345), 'Colorado Springs': (38.8339, -104.8214),
    'Raleigh': (35.7796, -78.6382), 'Long Beach': (33.7701, -118.1937),
    'Virginia Beach': (36.8529, -75.978), 'Miami': (25.7617, -80.1918),
    'Oakland': (37.8044, -122.2712), 'Minneapolis': (44.9778, -93.265),
    'Tulsa': (36.154, -95.9928), 'Tampa': (27.9506, -82.4572),
    'Arlington': (32.7357, -97.1081), 'Aurora': (39.7294, -104.8319),
    'Honolulu': (21.3069, -157.8583), 'Bakersfield': (35.3733, -119.0187),
    'St. Louis': (38.627, -90.1994), 'Pittsburgh': (40.4406, -79.9959),
    'Wichita': (37.6872, -97.3301), 'Stockton': (37.9577, -121.2908),
    'Anchorage': (61.2181, -149.9003), 'New Orleans': (29.9511, -90.0715),
    'Cincinnati': (39.1031, -84.512), 'Cleveland': (41.4993, -81.6944),
    'Honolulu Police Department': (21.3069, -157.8583),
}

# ========== 1. TOP 50 FOR TABLE (crime_data_embedded.js) ==========
top_50 = sorted(cities, key=lambda x: x.get('population', 0), reverse=True)[:50]
top_50_sorted = sorted(top_50, key=lambda x: x.get('safety_score', 0), reverse=True)

table_data = []
for rank, c in enumerate(top_50_sorted, 1):
    state_abbrev = get_state_abbrev(c['state'])
    coords = COORDS.get(c['city'], (39.5, -98.5))  # Default to US center
    display_name = shorten_name(c['city'])
    table_data.append({
        'city': display_name,
        'state': state_abbrev,
        'lat': coords[0],
        'lng': coords[1],
        'population': c['population'],
        'violent_rate': round(c.get('violent_rate', 0), 1),
        'property_rate': round(c.get('property_rate', 0), 1),
        'safety_score': c.get('safety_score', 50),
        'grade': c.get('grade', 'C'),
        'slug': slugify(c['city']) + '-' + state_abbrev.lower(),
        'rank': rank
    })

with open('crime_data_embedded.js', 'w') as f:
    f.write(f"const CRIME_DATA = {json.dumps(table_data)};")

print(f"Generated crime_data_embedded.js: {len(table_data)} cities for table")

# ========== 2. ALL CITIES FOR SEARCH (cities_search.js) ==========
# Light format: [name, state, score, slug]
search_data = []
for c in cities:
    state_abbrev = get_state_abbrev(c['state'])
    slug = slugify(c['city']) + '-' + state_abbrev.lower()
    search_data.append([
        c['city'],
        state_abbrev,
        c.get('safety_score', 50),
        slug
    ])

# Sort by population (biggest first for search relevance)
cities_with_pop = [(c, cities[i]['population']) for i, c in enumerate(search_data)]
search_data = [c for c, _ in sorted(cities_with_pop, key=lambda x: x[1], reverse=True)]

with open('cities_search.js', 'w') as f:
    f.write(f"const CITIES_SEARCH = {json.dumps(search_data)};")

print(f"Generated cities_search.js: {len(search_data)} cities for search")

# ========== 3. CITY COORDINATES FOR MAP (cities_map.js) ==========
# Get coordinates from existing data or use state centroids
# For now, we'll skip map markers and just do search

# Show stats
print("\nTop 5 safest (table):")
for c in table_data[:5]:
    print(f"  {c['rank']}. {c['city']}, {c['state']}: {c['safety_score']} ({c['grade']})")

# ========== 3. ALL COUNTIES FOR SEARCH (counties_search.js) ==========
try:
    with open('data/fbi/counties_with_population.json') as f:
        # File is one big array without opening bracket
        content = f.read().strip()
        if not content.startswith('['):
            content = '[' + content + ']'
        counties = json.loads(content)
    
    counties_search = []
    for c in counties:
        county_name = c.get('county_clean', c.get('county', ''))
        state_abbrev = c.get('state_abbr', '')
        score = c.get('safety_score', 50)
        slug = slugify(county_name) + '-county-' + state_abbrev.lower()
        counties_search.append([
            county_name + ' County',
            state_abbrev,
            score,
            slug
        ])
    
    with open('counties_search.js', 'w') as f:
        f.write(f"const COUNTIES_SEARCH = {json.dumps(counties_search)};")
    
    print(f"Generated counties_search.js: {len(counties_search)} counties for search")
except Exception as e:
    print(f"Counties search skipped: {e}")

print("\nFile sizes:")
import os
for f in ['crime_data_embedded.js', 'cities_search.js', 'counties_search.js']:
    if os.path.exists(f):
        size = os.path.getsize(f) / 1024
        print(f"  {f}: {size:.1f} KB")
