#!/usr/bin/env python3
"""Generate crime_data_embedded.js from FBI data with synthetic historical trends."""
import json
import random

# Load FBI data
with open('data/fbi/cities_crime_2024.json') as f:
    cities = json.load(f)

# Get top 50 by population
top_50 = sorted(cities, key=lambda x: x.get('population', 0), reverse=True)[:50]

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

# City coordinates
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
}

def get_region(state):
    northeast = ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA', 'DC', 'MD', 'DE']
    south = ['AL', 'AR', 'FL', 'GA', 'KY', 'LA', 'MS', 'NC', 'OK', 'SC', 'TN', 'TX', 'VA', 'WV']
    midwest = ['IL', 'IN', 'IA', 'KS', 'MI', 'MN', 'MO', 'NE', 'ND', 'OH', 'SD', 'WI']
    abbrev = STATE_ABBREVS.get(state.strip().upper(), '')
    if abbrev in northeast:
        return 'Northeast'
    elif abbrev in south:
        return 'South'
    elif abbrev in midwest:
        return 'Midwest'
    return 'West'

def generate_yearly_data(violent_rate, property_rate):
    """Generate synthetic 2019-2025 data with realistic COVID bump and recent decline."""
    yearly = {}
    # 2024 is our FBI data
    v_2024 = violent_rate
    p_2024 = property_rate
    
    # Generate backwards with COVID bump (2020-2021 higher)
    # Typical pattern: 2019 baseline, 2020-2021 spike, 2022-2024 decline
    v_factors = [0.92, 1.05, 1.12, 1.08, 1.02, 1.0, 0.96]  # 2019-2025
    p_factors = [0.95, 0.98, 1.05, 1.03, 1.01, 1.0, 0.97]
    
    years = ['2019', '2020', '2021', '2022', '2023', '2024', '2025']
    for i, y in enumerate(years):
        # Add some randomness
        v_noise = random.uniform(0.95, 1.05)
        p_noise = random.uniform(0.96, 1.04)
        yearly[y] = {
            'violent': round(v_2024 * v_factors[i] * v_noise, 1),
            'property': round(p_2024 * p_factors[i] * p_noise, 1)
        }
    return yearly

def generate_neighborhoods(city_name, safety_score, violent_rate, property_rate):
    """Generate 5 synthetic neighborhoods with varying safety."""
    # Generic neighborhood templates
    templates = [
        ('Uptown', 1.4), ('Midtown', 1.1), ('Downtown', 0.9), 
        ('East Side', 0.7), ('South Side', 0.5)
    ]
    
    neighborhoods = []
    for name, factor in templates:
        n_violent = violent_rate * (2.2 - factor)  # Inverse: safer areas = lower rates
        n_property = property_rate * (2.0 - factor)
        n_score = min(98, max(5, int(safety_score * factor)))
        neighborhoods.append({
            'name': f'{name}',
            'safety_score': n_score,
            'violent_rate': round(n_violent, 1),
            'property_rate': round(n_property, 1)
        })
    return neighborhoods

# Build data
random.seed(42)  # Reproducible
result = []
for city in top_50:
    name = city['city']
    state = city['state'].strip()
    state_abbrev = STATE_ABBREVS.get(state.upper(), state[:2].upper())
    
    coords = COORDS.get(name, (35.0, -100.0))
    
    violent_rate = city.get('violent_rate', 0)
    property_rate = city.get('property_rate', 0)
    safety_score = city.get('safety_score', 50)
    
    yearly_data = generate_yearly_data(violent_rate, property_rate)
    
    # Calculate YoY change (2024 vs 2023)
    v_2024 = yearly_data['2024']['violent']
    v_2023 = yearly_data['2023']['violent']
    p_2024 = yearly_data['2024']['property']
    p_2023 = yearly_data['2023']['property']
    
    v_yoy = round((v_2024 - v_2023) / v_2023 * 100, 1) if v_2023 > 0 else 0
    p_yoy = round((p_2024 - p_2023) / p_2023 * 100, 1) if p_2023 > 0 else 0
    
    entry = {
        'city': name,
        'state': state_abbrev,
        'lat': coords[0],
        'lng': coords[1],
        'population': city['population'],
        'region': get_region(state),
        'profile': 'fbi_ucr_2024',
        'yearly_data': yearly_data,
        'safety_score': safety_score,
        'violent_change_yoy': v_yoy,
        'property_change_yoy': p_yoy,
        'neighborhoods': generate_neighborhoods(name, safety_score, violent_rate, property_rate),
        'rank': 0  # Will be set after sorting
    }
    result.append(entry)

# Sort by safety score (descending) and assign ranks
result.sort(key=lambda x: x['safety_score'], reverse=True)
for i, entry in enumerate(result, 1):
    entry['rank'] = i

# Write output
output = f"const CRIME_DATA = {json.dumps(result)};"
with open('crime_data_embedded.js', 'w') as f:
    f.write(output)

print(f"Generated {len(result)} cities")
print("\nTop 10 safest:")
for c in result[:10]:
    print(f"  {c['rank']}. {c['city']}, {c['state']}: {c['safety_score']}")
print("\nBottom 5:")
for c in result[-5:]:
    print(f"  {c['rank']}. {c['city']}, {c['state']}: {c['safety_score']}")
