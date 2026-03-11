#!/usr/bin/env python3
"""Generate premium city pages for top 50 cities."""
import json
import os
import re

# Load FBI data
with open('data/fbi/cities_crime_2024.json') as f:
    cities = json.load(f)

# Get top 100 by population
top_100 = sorted(cities, key=lambda x: x.get('population', 0), reverse=True)[:100]

# State full names
STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia'
}

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
    'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY',
    'DISTRICT OF COLUMBIA': 'DC'
}

def slugify(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def shorten_name(name):
    replacements = {
        'Las Vegas Metropolitan Police Department': 'Las Vegas',
        'Metropolitan Nashville Police Department': 'Nashville',
        'Charlotte-Mecklenburg': 'Charlotte',
        'Louisville Metro': 'Louisville',
        'Honolulu Police Department': 'Honolulu',
    }
    return replacements.get(name, name)

def get_grade(score):
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'

def get_grade_color(score):
    if score >= 70: return 'var(--success)'
    if score >= 50: return 'var(--warning)'
    return 'var(--danger)'

def get_grade_text(score):
    if score >= 80: return 'Above Average Safety'
    if score >= 70: return 'Good Safety'
    if score >= 60: return 'Average Safety'
    if score >= 50: return 'Below Average Safety'
    return 'High Crime Area'

def format_number(n):
    return f"{n:,}"

# Cities with address lookup data (from hoodsafe_compact.js)
CITIES_WITH_LOOKUP = {
    'minneapolis', 'seattle', 'baton rouge', 'san francisco', 'cincinnati',
    'phoenix', 'buffalo', 'charlotte', 'oakland', 'philadelphia',
    'kansas city', 'chicago', 'new york', 'dallas', 'detroit', 'new orleans'
}

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{city}, {state_abbr} Crime Rate 2025 — Safety Score {score}/100 | HoodSafe</title>
    <meta name="description" content="{city} crime rate and safety statistics. Safety Score: {score}/100 ({grade}). Violent crime rate: {violent_rate} per 100k. Latest FBI data.">
    <link rel="canonical" href="https://hoodsafe.org/city/{slug}/">
    
    <!-- Favicons -->
    <link rel="icon" href="/favicon.ico" sizes="48x48">
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{city} Crime Rate - Safety Score {score}/100">
    <meta property="og:description" content="Is {city} safe? Crime statistics and safety analysis.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://hoodsafe.org/city/{slug}/">
    
    <!-- Schema.org -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{city}, {state_abbr} Crime Rate & Safety Score",
        "description": "Crime statistics and safety analysis for {city}, {state_name}",
        "author": {{"@type": "Organization", "name": "HoodSafe"}},
        "dateModified": "2026-03-06"
    }}
    </script>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {{
                "@type": "Question",
                "name": "Is {city} safe to live in?",
                "acceptedAnswer": {{
                    "@type": "Answer",
                    "text": "{city} has a safety score of {score}/100 (Grade {grade}), based on FBI crime data."
                }}
            }},
            {{
                "@type": "Question",
                "name": "What is {city}'s crime rate?",
                "acceptedAnswer": {{
                    "@type": "Answer",
                    "text": "{city} has a total crime rate of {total_rate} per 100,000 residents, with {violent_rate} violent crimes and {property_rate} property crimes per 100k."
                }}
            }}
        ]
    }}
    </script>
    
    <style>
        :root {{ --primary: #0d9488; --danger: #dc2626; --warning: #f59e0b; --success: #16a34a; --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --muted: #64748b; --border: #e2e8f0; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 1rem; }}
        header {{ background: var(--card); border-bottom: 1px solid var(--border); padding: 1rem 0; }}
        .header-inner {{ display: flex; align-items: center; justify-content: space-between; }}
        .logo {{ font-weight: 700; font-size: 1.25rem; color: var(--primary); text-decoration: none; display: flex; align-items: center; gap: 0.5rem; }}
        .breadcrumb {{ font-size: 0.875rem; color: var(--muted); margin-top: 1rem; }}
        .breadcrumb a {{ color: var(--primary); text-decoration: none; }}
        .hero {{ background: var(--card); padding: 2rem; border-radius: 1rem; margin: 1.5rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .hero h1 {{ font-size: 1.75rem; margin-bottom: 0.5rem; }}
        .hero-meta {{ color: var(--muted); margin-bottom: 1.5rem; }}
        .score-card {{ display: flex; gap: 2rem; align-items: center; }}
        .score-circle {{ width: 120px; height: 120px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-weight: 700; }}
        .score-num {{ font-size: 2.5rem; line-height: 1; }}
        .score-label {{ font-size: 0.75rem; opacity: 0.9; }}
        .score-details {{ flex: 1; }}
        .grade {{ font-size: 3rem; font-weight: 700; }}
        .grade-text {{ color: var(--muted); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
        .stat-card {{ background: var(--card); padding: 1.25rem; border-radius: 0.75rem; border: 1px solid var(--border); }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; }}
        .stat-label {{ font-size: 0.875rem; color: var(--muted); }}
        .stat-rate {{ font-size: 0.75rem; color: var(--muted); }}
        .section {{ background: var(--card); padding: 1.5rem; border-radius: 1rem; margin: 1.5rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .section h2 {{ font-size: 1.25rem; margin-bottom: 1rem; }}
        .faq {{ margin-top: 1rem; }}
        .faq-item {{ border-bottom: 1px solid var(--border); padding: 1rem 0; }}
        .faq-q {{ font-weight: 600; margin-bottom: 0.5rem; }}
        .faq-a {{ color: var(--muted); }}
        .cta {{ background: linear-gradient(135deg, var(--primary), #0f766e); color: white; text-align: center; padding: 2rem; border-radius: 1rem; margin: 2rem 0; }}
        .cta h3 {{ margin-bottom: 0.5rem; }}
        .cta a {{ display: inline-block; background: white; color: var(--primary); padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; margin-top: 1rem; }}
        footer {{ text-align: center; padding: 2rem; color: var(--muted); font-size: 0.875rem; }}
        footer a {{ color: var(--primary); }}
        @media (max-width: 600px) {{ .score-card {{ flex-direction: column; text-align: center; }} .stats-grid {{ grid-template-columns: 1fr 1fr; }} }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-inner">
                <a href="/" class="logo">
                    <svg width="28" height="28" viewBox="0 0 512 512" fill="none">
                        <path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="currentColor" opacity="0.15"/>
                        <path d="M256 52L88 140v120c0 104 72 192 168 224 96-32 168-120 168-224V140L256 52z" fill="none" stroke="currentColor" stroke-width="20" stroke-linejoin="round"/>
                        <path d="M256 196l-60 48v64h40v-36h40v36h40v-64l-60-48z" fill="currentColor"/>
                    </svg>
                    HoodSafe
                </a>
                <nav><a href="/#rankings" style="color: var(--muted); text-decoration: none;">Rankings</a></nav>
            </div>
            <div class="breadcrumb"><a href="/">Home</a> → <a href="/#rankings">Cities</a> → {city}, {state_abbr}</div>
        </div>
    </header>
    
    <main class="container">
        <div class="hero">
            <h1>{city}, {state_abbr} Crime Rate</h1>
            <p class="hero-meta">Population: {population} • Latest FBI Data</p>
            <div class="score-card">
                <div class="score-circle" style="background: {grade_color};">
                    <span class="score-num">{score}</span>
                    <span class="score-label">Safety Score</span>
                </div>
                <div class="score-details">
                    <div class="grade" style="color: {grade_color};">{grade}</div>
                    <div class="grade-text">{grade_text}</div>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: var(--danger);">{violent_crime}</div>
                <div class="stat-label">Violent Crimes</div>
                <div class="stat-rate">{violent_rate} per 100k residents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--warning);">{property_crime}</div>
                <div class="stat-label">Property Crimes</div>
                <div class="stat-rate">{property_rate} per 100k residents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_crime}</div>
                <div class="stat-label">Total Incidents</div>
                <div class="stat-rate">{total_rate} per 100k residents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{score}/100</div>
                <div class="stat-label">Safety Score</div>
                <div class="stat-rate">Grade: {grade}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Is {city} Safe?</h2>
            <p>{city} has a safety score of <strong>{score}/100</strong>, which is {safety_comparison}. 
            The city reported {violent_crime} violent crimes and {property_crime} property crimes according to the latest FBI data.</p>
            <p style="margin-top: 1rem;">With a violent crime rate of {violent_rate} per 100,000 residents, {city} is 
            {violent_comparison} the national average of 380 per 100k.</p>
        </div>
        
        <div class="section">
            <h2>Frequently Asked Questions</h2>
            <div class="faq">
                <div class="faq-item">
                    <div class="faq-q">What is {city}'s crime rate?</div>
                    <div class="faq-a">{city} has a total crime rate of {total_rate} per 100,000 residents, with {violent_rate} violent crimes and {property_rate} property crimes per 100k.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-q">Is {city} safe to live in?</div>
                    <div class="faq-a">{city} has a safety score of {score}/100 (Grade {grade}), indicating {grade_text_lower} compared to other US cities.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-q">How does {city}'s crime rate compare to the national average?</div>
                    <div class="faq-a">The violent crime rate is {violent_comparison} the US average of 380 per 100k. Property crime is {property_comparison} the national average of 2,000 per 100k.</div>
                </div>
            </div>
        </div>
        
        {cta_section}
    </main>
    
    <footer>
        <p>© 2026 HoodSafe.org • <a href="/">Home</a> • <a href="/#rankings">City Rankings</a></p>
        <p style="margin-top: 0.5rem;">Data source: FBI Uniform Crime Reporting (UCR)</p>
    </footer>
</body>
</html>'''

# Generate pages
for c in top_100:
    city_name = shorten_name(c['city'])
    state = c['state'].strip()
    state_abbr = STATE_ABBREVS.get(state.upper(), state[:2].upper())
    state_name = STATE_NAMES.get(state_abbr, state)
    
    slug = slugify(city_name) + '-' + state_abbr.lower()
    
    score = c.get('safety_score', 50)
    grade = get_grade(score)
    violent_rate = round(c.get('violent_rate', 0), 1)
    property_rate = round(c.get('property_rate', 0), 1)
    violent_crime = c.get('violent_crime', 0)
    property_crime = c.get('property_crime', 0)
    total_crime = violent_crime + property_crime
    total_rate = round(violent_rate + property_rate, 1)
    
    # Comparisons
    safety_comparison = "above average" if score >= 60 else "below average"
    violent_comparison = "below" if violent_rate < 380 else "above"
    property_comparison = "below" if property_rate < 2000 else "above"
    
    # CTA - different for cities with/without address lookup
    has_lookup = city_name.lower() in CITIES_WITH_LOOKUP
    if has_lookup:
        cta_section = '''<div class="cta">
            <h3>Check Any Address in ''' + city_name + '''</h3>
            <p>Get detailed safety scores for specific neighborhoods</p>
            <a href="/#lookup-section">Check Address Safety →</a>
        </div>'''
    else:
        state_slug = state_name.lower().replace(' ', '-')
        cta_section = f'''<div class="cta">
            <h3>Compare {city_name} with Other Cities</h3>
            <p>See how {city_name} ranks against other cities in {state_name}</p>
            <a href="/safest-cities/{state_slug}/">View {state_name} Rankings →</a>
        </div>'''
    
    html = TEMPLATE.format(
        city=city_name,
        state_abbr=state_abbr,
        state_name=state_name,
        slug=slug,
        score=score,
        grade=grade,
        grade_color=get_grade_color(score),
        grade_text=get_grade_text(score),
        grade_text_lower=get_grade_text(score).lower(),
        population=format_number(c['population']),
        violent_crime=format_number(violent_crime),
        property_crime=format_number(property_crime),
        total_crime=format_number(total_crime),
        violent_rate=violent_rate,
        property_rate=property_rate,
        total_rate=total_rate,
        safety_comparison=safety_comparison,
        violent_comparison=violent_comparison,
        property_comparison=property_comparison,
        cta_section=cta_section,
    )
    
    # Write file
    folder = f'city/{slug}'
    os.makedirs(folder, exist_ok=True)
    with open(f'{folder}/index.html', 'w') as f:
        f.write(html)
    
    print(f"✓ {city_name}, {state_abbr} ({score} - {grade})")

print(f"\n✅ Generated {len(top_100)} premium city pages!")
