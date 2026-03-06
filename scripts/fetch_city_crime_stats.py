#!/usr/bin/env python3
"""
Fetch aggregated crime statistics from major city APIs.
Calculates yearly totals for violent/property crime rates.
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import time

DATA_DIR = Path(__file__).parent.parent / "data" / "cities_stats"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# City Socrata APIs with crime data
CITY_APIS = {
    "chicago": {
        "name": "Chicago, IL",
        "population": 2696555,
        "state": "IL",
        "api": "https://data.cityofchicago.org/resource/ijzp-q8t2.json",
        "date_field": "date",
        "type_field": "primary_type"
    },
    "los_angeles": {
        "name": "Los Angeles, CA",
        "population": 3898747,
        "state": "CA",
        "api": "https://data.lacity.org/resource/2nrs-mtv8.json",
        "date_field": "date_occ",
        "type_field": "crm_cd_desc"
    },
    "new_york": {
        "name": "New York, NY",
        "population": 8336817,
        "state": "NY",
        "api": "https://data.cityofnewyork.us/resource/5uac-w243.json",
        "date_field": "cmplnt_fr_dt",
        "type_field": "ofns_desc"
    },
    "philadelphia": {
        "name": "Philadelphia, PA",
        "population": 1603797,
        "state": "PA",
        "api": "https://phl.carto.com/api/v2/sql",
        "query": "SELECT dispatch_date, text_general_code FROM incidents_part1_part2 WHERE dispatch_date >= '2020-01-01' ORDER BY dispatch_date DESC LIMIT 100000"
    },
    "houston": {
        "name": "Houston, TX",
        "population": 2304580,
        "state": "TX",
        "api": "https://data.houstontx.gov/resource/w867-pqaw.json",
        "date_field": "date",
        "type_field": "offense_type"
    },
    "phoenix": {
        "name": "Phoenix, AZ",
        "population": 1608139,
        "state": "AZ",
        "api": "https://www.phoenixopendata.com/resource/m4ub-ciud.json",
        "date_field": "occurred_on",
        "type_field": "ucr_crime_category"
    },
    "san_antonio": {
        "name": "San Antonio, TX",
        "population": 1434625,
        "state": "TX",
        "api": "https://data.sanantonio.gov/resource/yy7q-b6dp.json",
        "date_field": "date_occurred",
        "type_field": "category"
    },
    "san_diego": {
        "name": "San Diego, CA",
        "population": 1386932,
        "state": "CA",
        "api": "https://seshat.datasd.org/pd/pd_calls_for_service_2024_datasd.csv",
        "format": "csv",
        "skip": True  # CSV format needs different handling
    },
    "dallas": {
        "name": "Dallas, TX",
        "population": 1304379,
        "state": "TX",
        "api": "https://www.dallasopendata.com/resource/qv6i-rri7.json",
        "date_field": "date1",
        "type_field": "offincident"
    },
    "san_jose": {
        "name": "San Jose, CA",
        "population": 1013240,
        "state": "CA",
        "api": "https://data.sanjoseca.gov/resource/59rk-uqaa.json",
        "date_field": "cdts",
        "type_field": "category"
    },
    "austin": {
        "name": "Austin, TX",
        "population": 978908,
        "state": "TX",
        "api": "https://data.austintexas.gov/resource/fdj4-gpfu.json",
        "date_field": "occurred_date",
        "type_field": "crime_type"
    },
    "seattle": {
        "name": "Seattle, WA",
        "population": 737015,
        "state": "WA",
        "api": "https://data.seattle.gov/resource/tazs-3rd5.json",
        "date_field": "offense_start_datetime",
        "type_field": "offense_parent_group"
    },
    "denver": {
        "name": "Denver, CO",
        "population": 715522,
        "state": "CO",
        "api": "https://data.denvergov.org/resource/5du2-yg8q.json",
        "date_field": "incident_reported_date",
        "type_field": "offense_category_id"
    },
    "boston": {
        "name": "Boston, MA",
        "population": 675647,
        "state": "MA",
        "api": "https://data.boston.gov/resource/63da-xbyk.json",
        "date_field": "occurred_on_date",
        "type_field": "offense_code_group"
    },
    "detroit": {
        "name": "Detroit, MI",
        "population": 639111,
        "state": "MI",
        "api": "https://services2.arcgis.com/RQcpPaCpMAXzUI5g/arcgis/rest/services/RMS_Crime_Incidents_View/FeatureServer/0/query",
        "type": "arcgis"
    },
    "san_francisco": {
        "name": "San Francisco, CA",
        "population": 873965,
        "state": "CA",
        "api": "https://data.sfgov.org/resource/wg3w-h783.json",
        "date_field": "incident_date",
        "type_field": "incident_category"
    },
    "new_orleans": {
        "name": "New Orleans, LA",
        "population": 383997,
        "state": "LA",
        "api": "https://data.nola.gov/resource/wgrp-d3ma.json",
        "date_field": "occurdate",
        "type_field": "type_"
    },
    "minneapolis": {
        "name": "Minneapolis, MN",
        "population": 429954,
        "state": "MN",
        "api": "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/Crime_Data/FeatureServer/0/query",
        "type": "arcgis"
    },
    "kansas_city": {
        "name": "Kansas City, MO",
        "population": 508090,
        "state": "MO",
        "api": "https://data.kcmo.org/resource/98is-shjt.json",
        "date_field": "from_date",
        "type_field": "ibrs_category"
    },
    "baltimore": {
        "name": "Baltimore, MD",
        "population": 585708,
        "state": "MD",
        "api": "https://data.baltimorecity.gov/resource/wsfq-mvij.json",
        "date_field": "crimedate",
        "type_field": "description"
    },
    "portland": {
        "name": "Portland, OR",
        "population": 652503,
        "state": "OR",
        "api": "https://public.tableau.com/views/",
        "skip": True  # No easy API
    },
    "charlotte": {
        "name": "Charlotte, NC",
        "population": 874579,
        "state": "NC",
        "api": "https://gis.charlottenc.gov/arcgis/rest/services/CMPD/CMPDIncidents/MapServer/0/query",
        "type": "arcgis"
    },
    "cincinnati": {
        "name": "Cincinnati, OH",
        "population": 309317,
        "state": "OH",
        "api": "https://data.cincinnati-oh.gov/resource/k59e-2pvf.json",
        "date_field": "date_reported",
        "type_field": "offense"
    },
    "oakland": {
        "name": "Oakland, CA",
        "population": 433031,
        "state": "CA",
        "api": "https://data.oaklandca.gov/resource/3xav-7geq.json",
        "date_field": "datetime",
        "type_field": "crimetype"
    }
}

# Crime type mapping to categories
VIOLENT_CRIMES = [
    "homicide", "murder", "assault", "robbery", "rape", "battery",
    "aggravated", "kidnapping", "manslaughter", "shooting", "weapon",
    "arson", "sex offense", "criminal sexual"
]

PROPERTY_CRIMES = [
    "theft", "burglary", "larceny", "vehicle", "auto", "motor vehicle",
    "robbery", "breaking", "shoplifting", "fraud", "forgery", "vandalism",
    "trespass", "stolen"
]


def classify_crime(crime_type):
    """Classify a crime as violent, property, or other."""
    if not crime_type:
        return "other"
    crime_lower = crime_type.lower()
    for v in VIOLENT_CRIMES:
        if v in crime_lower:
            return "violent"
    for p in PROPERTY_CRIMES:
        if p in crime_lower:
            return "property"
    return "other"


def fetch_socrata(city_key, config, limit=50000):
    """Fetch crime data from a Socrata API."""
    url = config["api"]
    params = {"$limit": limit, "$order": f"{config['date_field']} DESC"}
    
    try:
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Aggregate by year
        stats = {}
        for row in data:
            date_val = row.get(config["date_field"], "")
            if not date_val:
                continue
            year = date_val[:4]
            if not year.isdigit() or int(year) < 2015:
                continue
            
            crime_type = row.get(config["type_field"], "")
            category = classify_crime(crime_type)
            
            if year not in stats:
                stats[year] = {"violent": 0, "property": 0, "other": 0, "total": 0}
            stats[year][category] += 1
            stats[year]["total"] += 1
        
        return stats
    except Exception as e:
        print(f"  Error: {e}")
        return None


def fetch_arcgis(city_key, config, limit=50000):
    """Fetch crime data from an ArcGIS API."""
    url = config["api"]
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "json",
        "resultRecordCount": min(limit, 2000),
        "resultOffset": 0
    }
    
    all_data = []
    try:
        while len(all_data) < limit:
            resp = requests.get(url, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            features = data.get("features", [])
            if not features:
                break
            all_data.extend(features)
            params["resultOffset"] += len(features)
            if len(features) < params["resultRecordCount"]:
                break
            time.sleep(0.5)
        
        print(f"  Fetched {len(all_data)} records")
        return {"records": len(all_data)}
    except Exception as e:
        print(f"  Error: {e}")
        return None


def main():
    results = {}
    
    for city_key, config in CITY_APIS.items():
        if config.get("skip"):
            continue
            
        print(f"Fetching {config['name']}...")
        
        if config.get("type") == "arcgis":
            stats = fetch_arcgis(city_key, config)
        elif "query" in config:
            # Carto SQL API
            try:
                resp = requests.get(config["api"], params={"q": config["query"]}, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                stats = {"records": len(data.get("rows", []))}
            except Exception as e:
                print(f"  Error: {e}")
                stats = None
        elif "date_field" in config:
            stats = fetch_socrata(city_key, config)
        else:
            print(f"  Skipping - no handler")
            stats = None
        
        if stats:
            results[city_key] = {
                "name": config["name"],
                "state": config["state"],
                "population": config["population"],
                "stats": stats
            }
            print(f"  ✓ {config['name']}: {stats}")
    
    # Save results
    output_file = DATA_DIR / "city_crime_stats.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Saved to {output_file}")
    print(f"Cities processed: {len(results)}")


if __name__ == "__main__":
    main()
