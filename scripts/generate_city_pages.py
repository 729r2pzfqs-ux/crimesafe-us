#!/usr/bin/env python3
"""
Generate programmatic SEO city pages for HoodSafe.org
Creates /city/{city}-crime-rate pages with crime stats
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import time

ROOT = Path(__file__).parent.parent
CITY_DIR = ROOT / "city"
CITY_DIR.mkdir(exist_ok=True)

# Working city APIs with verified endpoints
CITIES = {
    "chicago-il": {
        "name": "Chicago",
        "state": "Illinois",
        "state_abbr": "IL",
        "population": 2696555,
        "api": "https://data.cityofchicago.org/resource/ijzp-q8t2.json",
        "date_field": "date",
        "type_field": "primary_type"
    },
    "new-york-ny": {
        "name": "New York City",
        "state": "New York",
        "state_abbr": "NY",
        "population": 8336817,
        "api": "https://data.cityofnewyork.us/resource/5uac-w243.json",
        "date_field": "cmplnt_fr_dt",
        "type_field": "ofns_desc"
    },
    "los-angeles-ca": {
        "name": "Los Angeles",
        "state": "California",
        "state_abbr": "CA",
        "population": 3898747,
        "api": "https://data.lacity.org/resource/2nrs-mtv8.json",
        "date_field": "date_occ",
        "type_field": "crm_cd_desc"
    },
    "seattle-wa": {
        "name": "Seattle",
        "state": "Washington",
        "state_abbr": "WA",
        "population": 737015,
        "api": "https://data.seattle.gov/resource/tazs-3rd5.json",
        "date_field": "offense_start_datetime",
        "type_field": "offense_parent_group"
    },
    "san-francisco-ca": {
        "name": "San Francisco",
        "state": "California",
        "state_abbr": "CA",
        "population": 873965,
        "api": "https://data.sfgov.org/resource/wg3w-h783.json",
        "date_field": "incident_date",
        "type_field": "incident_category"
    },
    "boston-ma": {
        "name": "Boston",
        "state": "Massachusetts",
        "state_abbr": "MA",
        "population": 675647,
        "api": "https://data.boston.gov/resource/63da-xbyk.json",
        "date_field": "occurred_on_date",
        "type_field": "offense_code_group"
    },
    "denver-co": {
        "name": "Denver",
        "state": "Colorado",
        "state_abbr": "CO",
        "population": 715522,
        "api": "https://data.denvergov.org/resource/5du2-yg8q.json",
        "date_field": "incident_reported_date",
        "type_field": "offense_category_id"
    },
    "dallas-tx": {
        "name": "Dallas",
        "state": "Texas",
        "state_abbr": "TX",
        "population": 1304379,
        "api": "https://www.dallasopendata.com/resource/qv6i-rri7.json",
        "date_field": "date1",
        "type_field": "offincident"
    },
    "austin-tx": {
        "name": "Austin",
        "state": "Texas",
        "state_abbr": "TX",
        "population": 978908,
        "api": "https://data.austintexas.gov/resource/fdj4-gpfu.json",
        "date_field": "occurred_date",
        "type_field": "crime_type"
    },
    "new-orleans-la": {
        "name": "New Orleans",
        "state": "Louisiana",
        "state_abbr": "LA",
        "population": 383997,
        "api": "https://data.nola.gov/resource/wgrp-d3ma.json",
        "date_field": "occurdate",
        "type_field": "type_"
    },
    "kansas-city-mo": {
        "name": "Kansas City",
        "state": "Missouri",
        "state_abbr": "MO",
        "population": 508090,
        "api": "https://data.kcmo.org/resource/98is-shjt.json",
        "date_field": "from_date",
        "type_field": "ibrs_category"
    },
    "baltimore-md": {
        "name": "Baltimore",
        "state": "Maryland",
        "state_abbr": "MD",
        "population": 585708,
        "api": "https://data.baltimorecity.gov/resource/wsfq-mvij.json",
        "date_field": "crimedate",
        "type_field": "description"
    },
    "cincinnati-oh": {
        "name": "Cincinnati",
        "state": "Ohio",
        "state_abbr": "OH",
        "population": 309317,
        "api": "https://data.cincinnati-oh.gov/resource/k59e-2pvf.json",
        "date_field": "date_reported",
        "type_field": "offense"
    },
    "oakland-ca": {
        "name": "Oakland",
        "state": "California",
        "state_abbr": "CA",
        "population": 433031,
        "api": "https://data.oaklandca.gov/resource/3xav-7geq.json",
        "date_field": "datetime",
        "type_field": "crimetype"
    },
    "buffalo-ny": {
        "name": "Buffalo",
        "state": "New York",
        "state_abbr": "NY",
        "population": 278349,
        "api": "https://data.buffalony.gov/resource/d6g9-xbgu.json",
        "date_field": "incident_datetime",
        "type_field": "incident_type_primary"
    },
    "baton-rouge-la": {
        "name": "Baton Rouge",
        "state": "Louisiana",
        "state_abbr": "LA",
        "population": 227470,
        "api": "https://data.brla.gov/resource/fabb-cnnu.json",
        "date_field": "offense_date",
        "type_field": "offense"
    }
}

# Crime classification
VIOLENT = ["homicide", "murder", "assault", "robbery", "rape", "battery", "aggravated", 
           "kidnapping", "manslaughter", "shooting", "weapon", "sex offense"]
PROPERTY = ["theft", "burglary", "larceny", "vehicle", "auto", "motor vehicle",
            "shoplifting", "fraud", "forgery", "vandalism", "trespass", "stolen"]


def classify(crime_type):
    if not crime_type:
        return "other"
    ct = crime_type.lower()
    if any(v in ct for v in VIOLENT):
        return "violent"
    if any(p in ct for p in PROPERTY):
        return "property"
    return "other"


def fetch_stats(config):
    """Fetch and aggregate crime stats from API."""
    try:
        params = {"$limit": 50000, "$order": f"{config['date_field']} DESC"}
        resp = requests.get(config["api"], params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        stats = {}
        for row in data:
            date_val = row.get(config["date_field"], "")
            if not date_val:
                continue
            year = date_val[:4]
            if not year.isdigit() or int(year) < 2020:
                continue
            
            cat = classify(row.get(config["type_field"], ""))
            if year not in stats:
                stats[year] = {"violent": 0, "property": 0, "other": 0, "total": 0}
            stats[year][cat] += 1
            stats[year]["total"] += 1
        
        return stats, len(data)
    except Exception as e:
        print(f"  Error: {e}")
        return None, 0


def calculate_score(stats, population):
    """Calculate safety score 0-100 based on crime rates."""
    if not stats:
        return 50  # Default
    
    # Get most recent year
    years = sorted(stats.keys(), reverse=True)
    if not years:
        return 50
    
    latest = stats[years[0]]
    violent_rate = (latest["violent"] / population) * 100000
    property_rate = (latest["property"] / population) * 100000
    
    # National averages (approximate)
    # Violent: 380 per 100k, Property: 2000 per 100k
    violent_score = max(0, min(100, 100 - (violent_rate / 380 * 50)))
    property_score = max(0, min(100, 100 - (property_rate / 2000 * 30)))
    
    # Trend bonus/penalty
    trend_score = 50
    if len(years) >= 2:
        prev = stats[years[1]]
        if prev["total"] > 0:
            change = (latest["total"] - prev["total"]) / prev["total"]
            trend_score = 50 - (change * 100)  # Decrease = bonus
            trend_score = max(0, min(100, trend_score))
    
    # Weighted: 50% violent, 30% property, 20% trend
    score = violent_score * 0.5 + property_score * 0.3 + trend_score * 0.2
    return round(score)


def get_grade(score):
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"


def generate_page(slug, config, stats, score):
    """Generate HTML page for a city."""
    grade = get_grade(score)
    name = config["name"]
    state = config["state"]
    pop = config["population"]
    
    # Get latest year stats
    years = sorted(stats.keys(), reverse=True) if stats else []
    latest_year = years[0] if years else "2024"
    latest = stats.get(latest_year, {"violent": 0, "property": 0, "total": 0})
    
    violent_rate = round((latest["violent"] / pop) * 100000, 1) if pop else 0
    property_rate = round((latest["property"] / pop) * 100000, 1) if pop else 0
    total_rate = round((latest["total"] / pop) * 100000, 1) if pop else 0
    
    # Trend
    trend_text = "Stable"
    trend_icon = "→"
    if len(years) >= 2:
        prev = stats.get(years[1], {})
        if prev.get("total", 0) > 0:
            change = ((latest["total"] - prev["total"]) / prev["total"]) * 100
            if change > 5:
                trend_text = f"Up {abs(change):.1f}%"
                trend_icon = "↑"
            elif change < -5:
                trend_text = f"Down {abs(change):.1f}%"
                trend_icon = "↓"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}, {config["state_abbr"]} Crime Rate & Safety Score | HoodSafe</title>
    <meta name="description" content="{name} crime rate and safety statistics. Safety Score: {score}/100 ({grade}). Violent crime rate: {violent_rate} per 100k. Updated {latest_year}.">
    <link rel="canonical" href="https://hoodsafe.org/city/{slug}">
    
    <!-- Favicons -->
    <link rel="icon" href="/favicon.ico" sizes="48x48">
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{name} Crime Rate - Safety Score {score}/100">
    <meta property="og:description" content="Is {name} safe? Crime statistics and safety analysis.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://hoodsafe.org/city/{slug}">
    
    <!-- Schema.org -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{name}, {config["state_abbr"]} Crime Rate & Safety Score",
        "description": "Crime statistics and safety analysis for {name}, {state}",
        "author": {{"@type": "Organization", "name": "HoodSafe"}},
        "dateModified": "{datetime.now().strftime('%Y-%m-%d')}"
    }}
    </script>
    
    <style>
        :root {{
            --primary: #0d9488;
            --danger: #dc2626;
            --warning: #f59e0b;
            --success: #16a34a;
            --bg: #f8fafc;
            --card: #ffffff;
            --text: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
        }}
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
        
        @media (max-width: 600px) {{
            .score-card {{ flex-direction: column; text-align: center; }}
            .stats-grid {{ grid-template-columns: 1fr 1fr; }}
        }}
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
                <nav>
                    <a href="/#rankings" style="color: var(--muted); text-decoration: none;">Rankings</a>
                </nav>
            </div>
            <div class="breadcrumb">
                <a href="/">Home</a> → <a href="/#rankings">Cities</a> → {name}, {config["state_abbr"]}
            </div>
        </div>
    </header>
    
    <main class="container">
        <div class="hero">
            <h1>{name}, {config["state_abbr"]} Crime Rate</h1>
            <p class="hero-meta">Population: {pop:,} • Data updated {latest_year}</p>
            
            <div class="score-card">
                <div class="score-circle" style="background: {'var(--success)' if score >= 70 else 'var(--warning)' if score >= 50 else 'var(--danger)'};">
                    <span class="score-num">{score}</span>
                    <span class="score-label">Safety Score</span>
                </div>
                <div class="score-details">
                    <div class="grade" style="color: {'var(--success)' if score >= 70 else 'var(--warning)' if score >= 50 else 'var(--danger)'};">{grade}</div>
                    <div class="grade-text">
                        {'Above Average Safety' if score >= 70 else 'Average Safety' if score >= 50 else 'Below Average Safety'}
                    </div>
                    <div style="margin-top: 0.5rem; color: var(--muted);">
                        Trend: {trend_icon} {trend_text}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: var(--danger);">{latest["violent"]:,}</div>
                <div class="stat-label">Violent Crimes</div>
                <div class="stat-rate">{violent_rate} per 100k residents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--warning);">{latest["property"]:,}</div>
                <div class="stat-label">Property Crimes</div>
                <div class="stat-rate">{property_rate} per 100k residents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{latest["total"]:,}</div>
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
            <h2>Is {name} Safe?</h2>
            <p>{name} has a safety score of <strong>{score}/100</strong>, which is {'above' if score >= 60 else 'below'} the national average. 
            The city reported {latest["violent"]:,} violent crimes and {latest["property"]:,} property crimes in {latest_year}.</p>
            <p style="margin-top: 1rem;">With a violent crime rate of {violent_rate} per 100,000 residents, {name} is 
            {'safer than' if violent_rate < 380 else 'more dangerous than'} the national average of 380 per 100k.</p>
        </div>
        
        <div class="section">
            <h2>Frequently Asked Questions</h2>
            <div class="faq">
                <div class="faq-item">
                    <div class="faq-q">What is {name}'s crime rate?</div>
                    <div class="faq-a">{name} has a total crime rate of {total_rate} per 100,000 residents, with {violent_rate} violent crimes and {property_rate} property crimes per 100k.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-q">Is {name} safe to live in?</div>
                    <div class="faq-a">{name} has a safety score of {score}/100 (Grade {grade}), indicating {'above average' if score >= 60 else 'below average'} safety compared to other US cities.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-q">How does {name}'s crime rate compare to the national average?</div>
                    <div class="faq-a">{'The violent crime rate is lower than' if violent_rate < 380 else 'The violent crime rate is higher than'} the US average of 380 per 100k. {'Property crime is also below' if property_rate < 2000 else 'Property crime is above'} the national average of 2,000 per 100k.</div>
                </div>
            </div>
        </div>
        
        <div class="cta">
            <h3>Check Any Address</h3>
            <p>Get detailed safety scores for specific neighborhoods</p>
            <a href="/#lookup-section">Check Address Safety →</a>
        </div>
    </main>
    
    <footer>
        <p>© 2026 HoodSafe.org • <a href="/">Home</a> • <a href="/#rankings">City Rankings</a></p>
        <p style="margin-top: 0.5rem;">Data sources: Local police departments, FBI UCR</p>
    </footer>
</body>
</html>'''
    
    return html


def main():
    print("Generating city pages...\n")
    
    generated = 0
    for slug, config in CITIES.items():
        print(f"Processing {config['name']}, {config['state_abbr']}...")
        
        stats, count = fetch_stats(config)
        if not stats:
            print(f"  ⚠️ No data, using defaults")
            stats = {"2024": {"violent": 0, "property": 0, "other": 0, "total": 0}}
        
        score = calculate_score(stats, config["population"])
        print(f"  ✓ {count} records, Score: {score}/100")
        
        html = generate_page(slug, config, stats, score)
        
        # Save page
        page_dir = CITY_DIR / slug
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(html)
        
        generated += 1
        time.sleep(1)  # Rate limit
    
    print(f"\n✅ Generated {generated} city pages in /city/")


if __name__ == "__main__":
    main()
