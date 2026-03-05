#!/usr/bin/env python3
"""
HoodSafe Crime Data Ingestion Script
Fetches crime data from 50 US city open data portals
"""

import json
import os
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Output directory
DATA_DIR = Path(__file__).parent.parent / "data" / "cities"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Standard crime categories mapping
CRIME_CATEGORIES = {
    "violent": ["homicide", "murder", "assault", "robbery", "rape", "kidnapping", "manslaughter"],
    "property": ["burglary", "theft", "larceny", "vehicle theft", "auto theft", "arson", "vandalism"],
    "other": ["fraud", "forgery", "drugs", "weapons", "prostitution", "gambling", "dui", "disorderly"]
}

def categorize_crime(description):
    """Map crime description to category"""
    desc_lower = description.lower()
    for category, keywords in CRIME_CATEGORIES.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "other"

# ============================================================
# CITY CONFIGURATIONS
# ============================================================

CITIES = {
    # TIER 1: Socrata API cities (easiest)
    "chicago": {
        "name": "Chicago",
        "state": "IL",
        "population": 2700000,
        "api": "https://data.cityofchicago.org/resource/ijzp-q8t2.json",
        "type": "socrata",
        "fields": {
            "date": "date",
            "type": "primary_type",
            "description": "description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "block",
            "district": "district"
        }
    },
    "los_angeles": {
        "name": "Los Angeles",
        "state": "CA",
        "population": 3900000,
        "api": "https://data.lacity.org/resource/2nrs-mtv8.json",
        "type": "socrata",
        "fields": {
            "date": "date_occ",
            "type": "crm_cd_desc",
            "description": "crm_cd_desc",
            "lat": "lat",
            "lng": "lon",
            "location": "location",
            "district": "area_name"
        }
    },
    "new_york": {
        "name": "New York",
        "state": "NY",
        "population": 8300000,
        "api": "https://data.cityofnewyork.us/resource/qgea-i56i.json",
        "type": "socrata",
        "fields": {
            "date": "cmplnt_fr_dt",
            "type": "ofns_desc",
            "description": "pd_desc",
            "lat": "latitude",
            "lng": "longitude",
            "location": "boro_nm",
            "district": "addr_pct_cd"
        }
    },
    "san_francisco": {
        "name": "San Francisco",
        "state": "CA",
        "population": 870000,
        "api": "https://data.sfgov.org/resource/wg3w-h783.json",
        "type": "socrata",
        "fields": {
            "date": "incident_datetime",
            "type": "incident_category",
            "description": "incident_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "intersection",
            "district": "police_district"
        }
    },
    "seattle": {
        "name": "Seattle",
        "state": "WA",
        "population": 750000,
        "api": "https://data.seattle.gov/resource/tazs-3rd5.json",
        "type": "socrata",
        "fields": {
            "date": "offense_start_datetime",
            "type": "offense_parent_group",
            "description": "offense",
            "lat": "latitude",
            "lng": "longitude",
            "location": "mcpp",
            "district": "precinct"
        }
    },
    "austin": {
        "name": "Austin",
        "state": "TX",
        "population": 1000000,
        "api": "https://data.austintexas.gov/resource/fdj4-gpfu.json",
        "type": "socrata",
        "fields": {
            "date": "occ_date_time",
            "type": "crime_type",
            "description": "ucr_category",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "council_district"
        }
    },
    "denver": {
        "name": "Denver",
        "state": "CO",
        "population": 715000,
        "api": "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/ODC_CRIME_OFFENSE_CURRENT/FeatureServer/0/query",
        "type": "arcgis",
        "fields": {
            "date": "FIRST_OCCURRENCE_DATE",
            "type": "OFFENSE_CATEGORY_ID",
            "description": "OFFENSE_TYPE_ID",
            "lat": "GEO_LAT",
            "lng": "GEO_LON",
            "location": "INCIDENT_ADDRESS",
            "district": "DISTRICT_ID"
        }
    },
    "boston": {
        "name": "Boston",
        "state": "MA",
        "population": 675000,
        "api": "https://data.boston.gov/api/3/action/datastore_search",
        "resource_id": "12cb3883-56f5-47de-afa5-3b1cf61b257b",
        "type": "ckan",
        "fields": {
            "date": "OCCURRED_ON_DATE",
            "type": "OFFENSE_CODE_GROUP",
            "description": "OFFENSE_DESCRIPTION",
            "lat": "Lat",
            "lng": "Long",
            "location": "STREET",
            "district": "DISTRICT"
        }
    },
    "baltimore": {
        "name": "Baltimore",
        "state": "MD",
        "population": 570000,
        "api": "https://data.baltimorecity.gov/resource/wsfq-mvij.json",
        "type": "socrata",
        "fields": {
            "date": "crimedate",
            "type": "description",
            "description": "description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "location",
            "district": "district"
        }
    },
    "nashville": {
        "name": "Nashville",
        "state": "TN",
        "population": 690000,
        "api": "https://data.nashville.gov/resource/2u6v-ujjs.json",
        "type": "socrata",
        "fields": {
            "date": "incident_occurred",
            "type": "offense_description",
            "description": "offense_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "incident_location",
            "district": "precinct"
        }
    },
    "louisville": {
        "name": "Louisville",
        "state": "KY",
        "population": 620000,
        "api": "https://data.louisvilleky.gov/resource/iqs4-7w2j.json",
        "type": "socrata",
        "fields": {
            "date": "date_occured",
            "type": "crime_type",
            "description": "crime_type",
            "lat": "latitude",
            "lng": "longitude",
            "location": "block_address",
            "district": "badge_id"
        }
    },
    "portland": {
        "name": "Portland",
        "state": "OR",
        "population": 650000,
        "api": "https://public.tableau.com/views/PPBOpenDataDownloads/CrimeData.csv",
        "type": "csv",
        "fields": {
            "date": "OccurDate",
            "type": "OffenseType",
            "description": "OffenseType",
            "lat": "OpenDataLat",
            "lng": "OpenDataLon",
            "location": "Address",
            "district": "Neighborhood"
        }
    },
    "detroit": {
        "name": "Detroit",
        "state": "MI",
        "population": 640000,
        "api": "https://data.detroitmi.gov/resource/6gdg-y3kf.json",
        "type": "socrata",
        "fields": {
            "date": "incident_timestamp",
            "type": "offense_description",
            "description": "offense_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "precinct"
        }
    },
    "memphis": {
        "name": "Memphis",
        "state": "TN",
        "population": 630000,
        "api": "https://data.memphistn.gov/resource/ybsi-jur4.json",
        "type": "socrata",
        "fields": {
            "date": "offense_date",
            "type": "category",
            "description": "offense",
            "lat": "coord1",
            "lng": "coord2",
            "location": "agency_crimestoppers",
            "district": "beat"
        }
    },
    "kansas_city": {
        "name": "Kansas City",
        "state": "MO",
        "population": 500000,
        "api": "https://data.kcmo.org/resource/98is-shjt.json",
        "type": "socrata",
        "fields": {
            "date": "reported_date",
            "type": "description",
            "description": "description",
            "lat": "location_1.latitude",
            "lng": "location_1.longitude",
            "location": "address",
            "district": "area"
        }
    },
    "atlanta": {
        "name": "Atlanta",
        "state": "GA",
        "population": 500000,
        "api": "https://services3.arcgis.com/Et5Qfajgiyosiw4d/arcgis/rest/services/CrimeDataExport/FeatureServer/0/query",
        "type": "arcgis",
        "fields": {
            "date": "occur_date",
            "type": "UC2_Literal",
            "description": "UC2_Literal",
            "lat": "lat",
            "lng": "long",
            "location": "location",
            "district": "beat"
        }
    },
    "sacramento": {
        "name": "Sacramento",
        "state": "CA",
        "population": 525000,
        "api": "https://data.cityofsacramento.org/resource/m36a-rmkz.json",
        "type": "socrata",
        "fields": {
            "date": "datetime",
            "type": "offense",
            "description": "offense",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "district"
        }
    },
    "new_orleans": {
        "name": "New Orleans",
        "state": "LA",
        "population": 385000,
        "api": "https://data.nola.gov/resource/wgrp-d3ma.json",
        "type": "socrata",
        "fields": {
            "date": "occurred_date",
            "type": "offense_description",
            "description": "offense_description",
            "lat": "location.latitude",
            "lng": "location.longitude",
            "location": "block_address",
            "district": "district"
        }
    },
    "minneapolis": {
        "name": "Minneapolis",
        "state": "MN",
        "population": 425000,
        "api": "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/Reported_Crime_2021/FeatureServer/0/query",
        "type": "arcgis",
        "fields": {
            "date": "reportedDate",
            "type": "offense",
            "description": "description",
            "lat": "centerLat",
            "lng": "centerLong",
            "location": "address",
            "district": "precinct"
        }
    },
    "raleigh": {
        "name": "Raleigh",
        "state": "NC",
        "population": 475000,
        "api": "https://data.raleighnc.gov/resource/dwjm-cait.json",
        "type": "socrata",
        "fields": {
            "date": "reported_date",
            "type": "lcr_desc",
            "description": "lcr_desc",
            "lat": "latitude",
            "lng": "longitude",
            "location": "reported_block_address",
            "district": "district"
        }
    },
    "oakland": {
        "name": "Oakland",
        "state": "CA",
        "population": 430000,
        "api": "https://data.oaklandca.gov/resource/3xav-7geq.json",
        "type": "socrata",
        "fields": {
            "date": "datetime",
            "type": "crimetype",
            "description": "description",
            "lat": "location_1.coordinates.1",
            "lng": "location_1.coordinates.0",
            "location": "address",
            "district": "policebeat"
        }
    },
    "tucson": {
        "name": "Tucson",
        "state": "AZ",
        "population": 545000,
        "api": "https://gisdata.tucsonaz.gov/arcgis/rest/services/Public/PublicSafety/MapServer/1/query",
        "type": "arcgis",
        "fields": {
            "date": "OCCURDATE",
            "type": "STATUTDESC",
            "description": "STATUTDESC",
            "lat": "POINT_Y",
            "lng": "POINT_X",
            "location": "HUNDREDBLOCKADDRESS",
            "district": "DIVISION"
        }
    },
    "charlotte": {
        "name": "Charlotte",
        "state": "NC",
        "population": 875000,
        "api": "https://data.charlottenc.gov/resource/va7s-nik5.json",
        "type": "socrata",
        "fields": {
            "date": "date_incident_began",
            "type": "highest_nibrs_description",
            "description": "highest_nibrs_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "division_id"
        }
    },
    "indianapolis": {
        "name": "Indianapolis",
        "state": "IN",
        "population": 880000,
        "api": "https://data.indy.gov/resource/2tisn-hcbv.json",
        "type": "socrata",
        "fields": {
            "date": "occurred_dt",
            "type": "ucr_description",
            "description": "ucr_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "dist"
        }
    },
    "columbus": {
        "name": "Columbus",
        "state": "OH",
        "population": 905000,
        "api": "https://data.columbus.gov/resource/v9qi-rqcp.json",
        "type": "socrata",
        "fields": {
            "date": "report_datetime",
            "type": "crime",
            "description": "crime",
            "lat": "lat",
            "lng": "lng",
            "location": "location",
            "district": "cpd_boundary"
        }
    },
    "fort_worth": {
        "name": "Fort Worth",
        "state": "TX",
        "population": 935000,
        "api": "https://data.fortworthtexas.gov/resource/k6ic-7kp7.json",
        "type": "socrata",
        "fields": {
            "date": "from_date",
            "type": "nature_of_call",
            "description": "nature_of_call",
            "lat": "location_1.latitude",
            "lng": "location_1.longitude",
            "location": "block_address",
            "district": "beat"
        }
    },
    "jacksonville": {
        "name": "Jacksonville",
        "state": "FL",
        "population": 950000,
        "api": "https://data.coj.net/resource/7g3g-y27s.json",
        "type": "socrata",
        "fields": {
            "date": "incidentdate",
            "type": "incidenttype",
            "description": "incidenttype",
            "lat": "latitude",
            "lng": "longitude",
            "location": "blockaddress",
            "district": "zone"
        }
    },
    "phoenix": {
        "name": "Phoenix",
        "state": "AZ",
        "population": 1600000,
        "api": "https://www.phoenixopendata.com/api/id/b4ky-tjgq.json",
        "type": "socrata",
        "fields": {
            "date": "occurred_on",
            "type": "ucr_crime_category",
            "description": "ucr_crime_category",
            "lat": "latitude",
            "lng": "longitude",
            "location": "100_block_addr",
            "district": "grid"
        }
    },
    "houston": {
        "name": "Houston",
        "state": "TX",
        "population": 2300000,
        "api": "https://data.houstontx.gov/resource/djrf-bgxe.json",
        "type": "socrata",
        "fields": {
            "date": "date",
            "type": "offense_type",
            "description": "offense_type",
            "lat": "geolocation.latitude",
            "lng": "geolocation.longitude",
            "location": "block_range",
            "district": "beat"
        }
    },
    "san_antonio": {
        "name": "San Antonio",
        "state": "TX",
        "population": 1500000,
        "api": "https://data.sanantonio.gov/resource/eb79-yi6d.json",
        "type": "socrata",
        "fields": {
            "date": "occured_date_time",
            "type": "category",
            "description": "category",
            "lat": "location_1.latitude",
            "lng": "location_1.longitude",
            "location": "address",
            "district": "district"
        }
    },
    "san_diego": {
        "name": "San Diego",
        "state": "CA",
        "population": 1400000,
        "api": "https://seshat.datasd.org/pd/pd_calls_for_service_2024_datasd.csv",
        "type": "csv_url",
        "fields": {
            "date": "date_time",
            "type": "call_type",
            "description": "call_type",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "beat"
        }
    },
    "dallas": {
        "name": "Dallas",
        "state": "TX",
        "population": 1300000,
        "api": "https://www.dallasopendata.com/resource/qv6i-rri7.json",
        "type": "socrata",
        "fields": {
            "date": "date1",
            "type": "offincident",
            "description": "offincident",
            "lat": "geocoded_column.latitude",
            "lng": "geocoded_column.longitude",
            "location": "incidentaddress",
            "district": "division"
        }
    },
    "san_jose": {
        "name": "San Jose",
        "state": "CA",
        "population": 1000000,
        "api": "https://data.sanjoseca.gov/resource/7m4f-n9e9.json",
        "type": "socrata",
        "fields": {
            "date": "cdts",
            "type": "calltype_description",
            "description": "calltype_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "location_1",
            "district": "district"
        }
    },
    "philadelphia": {
        "name": "Philadelphia",
        "state": "PA",
        "population": 1600000,
        "api": "https://phl.carto.com/api/v2/sql",
        "type": "carto",
        "fields": {
            "date": "dispatch_date",
            "type": "text_general_code",
            "description": "text_general_code",
            "lat": "point_y",
            "lng": "point_x",
            "location": "location_block",
            "district": "dc_dist"
        }
    },
    "las_vegas": {
        "name": "Las Vegas",
        "state": "NV",
        "population": 640000,
        "api": "https://services.arcgis.com/aJt2tjqpCvm6b5KC/arcgis/rest/services/Crime_Dispatch_Incidents/FeatureServer/0/query",
        "type": "arcgis",
        "fields": {
            "date": "IncidentDate",
            "type": "IncidentType",
            "description": "IncidentType",
            "lat": "Latitude",
            "lng": "Longitude",
            "location": "Address",
            "district": "AreaCommand"
        }
    },
    "cleveland": {
        "name": "Cleveland",
        "state": "OH",
        "population": 370000,
        "api": "https://data.clevelandohio.gov/resource/c7jm-5bpj.json",
        "type": "socrata",
        "fields": {
            "date": "date",
            "type": "offense",
            "description": "offense",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "district"
        }
    },
    "miami": {
        "name": "Miami",
        "state": "FL",
        "population": 440000,
        "api": "https://gis-mdc.opendata.arcgis.com/api/download/v1/items/a10c35e3f7a7429abfc2d3065abf4f16/csv",
        "type": "csv_url",
        "fields": {
            "date": "DateOccurred",
            "type": "CrimeType",
            "description": "CrimeType",
            "lat": "Latitude",
            "lng": "Longitude",
            "location": "Address",
            "district": "Zone"
        }
    },
    "tampa": {
        "name": "Tampa",
        "state": "FL",
        "population": 395000,
        "api": "https://data.tampagov.net/resource/rqgd-42ne.json",
        "type": "socrata",
        "fields": {
            "date": "occurred_datetime",
            "type": "offense_description",
            "description": "offense_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "district"
        }
    },
    "albuquerque": {
        "name": "Albuquerque",
        "state": "NM",
        "population": 565000,
        "api": "https://data.cabq.gov/resource/bc4a-ysrz.json",
        "type": "socrata",
        "fields": {
            "date": "date",
            "type": "crime_type",
            "description": "crime_type",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address",
            "district": "zone"
        }
    },
    "omaha": {
        "name": "Omaha",
        "state": "NE",
        "population": 485000,
        "api": "https://opendata.arcgis.com/datasets/57a37fafb7974e51bb8f5f4d41b5d0d8_0.geojson",
        "type": "geojson",
        "fields": {
            "date": "DATE_OCCURRED",
            "type": "OFFENSE",
            "description": "OFFENSE",
            "lat": "lat",
            "lng": "lon",
            "location": "ADDRESS",
            "district": "SECTOR"
        }
    },
    "baton_rouge": {
        "name": "Baton Rouge",
        "state": "LA",
        "population": 225000,
        "api": "https://data.brla.gov/resource/fabb-cnnu.json",
        "type": "socrata",
        "fields": {
            "date": "offense_date",
            "type": "crime",
            "description": "offense_desc",
            "lat": "geolocation.latitude",
            "lng": "geolocation.longitude",
            "location": "address",
            "district": "district"
        }
    },
    "cincinnati": {
        "name": "Cincinnati",
        "state": "OH",
        "population": 310000,
        "api": "https://data.cincinnati-oh.gov/resource/k59e-2pvf.json",
        "type": "socrata",
        "fields": {
            "date": "date_reported",
            "type": "offense",
            "description": "offense",
            "lat": "latitude_x",
            "lng": "longitude_x",
            "location": "address_x",
            "district": "cpd_neighborhood"
        }
    },
    "buffalo": {
        "name": "Buffalo",
        "state": "NY",
        "population": 280000,
        "api": "https://data.buffalony.gov/resource/d6g9-xbgu.json",
        "type": "socrata",
        "fields": {
            "date": "incident_datetime",
            "type": "incident_type_primary",
            "description": "incident_description",
            "lat": "latitude",
            "lng": "longitude",
            "location": "address_1",
            "district": "neighborhood"
        }
    }
}

# ============================================================
# FETCH FUNCTIONS
# ============================================================

def fetch_socrata(city_config, limit=50000, days_back=365):
    """Fetch data from Socrata API"""
    url = city_config["api"]
    date_field = city_config["fields"]["date"]
    
    # First try without date filter (more reliable)
    params = {
        "$limit": limit,
        "$order": f"{date_field} DESC"
    }
    
    print(f"  Fetching from: {url}")
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Fallback: try without ordering
        print(f"  Retrying without order...")
        params = {"$limit": limit}
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()


def fetch_arcgis(city_config, limit=50000):
    """Fetch data from ArcGIS FeatureServer"""
    url = city_config["api"]
    
    params = {
        "where": "1=1",
        "outFields": "*",
        "resultRecordCount": limit,
        "f": "json",
        "returnGeometry": "true"
    }
    
    print(f"  Fetching from: {url}")
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    
    # Extract features
    if "features" in data:
        return [f.get("attributes", {}) for f in data["features"]]
    return []


def fetch_ckan(city_config, limit=50000):
    """Fetch data from CKAN API (Boston style)"""
    url = city_config["api"]
    
    params = {
        "resource_id": city_config.get("resource_id", ""),
        "limit": limit
    }
    
    print(f"  Fetching from: {url}")
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    
    if data.get("success") and "result" in data:
        return data["result"].get("records", [])
    return []


def fetch_carto(city_config, limit=50000):
    """Fetch data from Carto SQL API (Philadelphia)"""
    url = city_config["api"]
    # Simple query without date filter
    query = f"SELECT * FROM incidents_part1_part2 ORDER BY dispatch_date DESC LIMIT {limit}"
    
    params = {
        "q": query,
        "format": "json"
    }
    
    print(f"  Fetching from: {url}")
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    
    return data.get("rows", [])


def fetch_csv_url(city_config, limit=50000):
    """Fetch and parse CSV from URL"""
    import csv
    from io import StringIO
    
    url = city_config["api"]
    print(f"  Fetching CSV from: {url}")
    
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    
    reader = csv.DictReader(StringIO(response.text))
    rows = []
    for i, row in enumerate(reader):
        if i >= limit:
            break
        rows.append(row)
    return rows


def fetch_geojson(city_config, limit=50000):
    """Fetch GeoJSON data"""
    url = city_config["api"]
    print(f"  Fetching GeoJSON from: {url}")
    
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()
    
    features = data.get("features", [])[:limit]
    return [f.get("properties", {}) for f in features]


# ============================================================
# NORMALIZATION
# ============================================================

def get_nested_value(obj, key):
    """Get value from nested dict using dot notation (supports array indices)"""
    if not key:
        return None
    
    parts = key.split(".")
    value = obj
    for part in parts:
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list):
            try:
                idx = int(part)
                value = value[idx] if idx < len(value) else None
            except (ValueError, IndexError):
                return None
        else:
            return None
    return value


def normalize_record(record, city_config):
    """Normalize a crime record to standard format"""
    fields = city_config["fields"]
    
    return {
        "date": get_nested_value(record, fields.get("date")),
        "type": get_nested_value(record, fields.get("type")),
        "description": get_nested_value(record, fields.get("description")),
        "lat": get_nested_value(record, fields.get("lat")),
        "lng": get_nested_value(record, fields.get("lng")),
        "location": get_nested_value(record, fields.get("location")),
        "district": get_nested_value(record, fields.get("district")),
        "category": categorize_crime(str(get_nested_value(record, fields.get("type")) or ""))
    }


# ============================================================
# MAIN
# ============================================================

def fetch_city(city_key, limit=50000):
    """Fetch and normalize data for a single city"""
    if city_key not in CITIES:
        print(f"Unknown city: {city_key}")
        return None
    
    config = CITIES[city_key]
    api_type = config.get("type", "socrata")
    
    print(f"\n{'='*60}")
    print(f"Fetching: {config['name']}, {config['state']} ({api_type})")
    print(f"{'='*60}")
    
    try:
        # Fetch based on API type
        if api_type == "socrata":
            raw_data = fetch_socrata(config, limit)
        elif api_type == "arcgis":
            raw_data = fetch_arcgis(config, limit)
        elif api_type == "ckan":
            raw_data = fetch_ckan(config, limit)
        elif api_type == "carto":
            raw_data = fetch_carto(config, limit)
        elif api_type == "csv_url" or api_type == "csv":
            raw_data = fetch_csv_url(config, limit)
        elif api_type == "geojson":
            raw_data = fetch_geojson(config, limit)
        else:
            print(f"  Unknown API type: {api_type}")
            return None
        
        print(f"  Raw records: {len(raw_data)}")
        
        # Normalize records
        normalized = [normalize_record(r, config) for r in raw_data]
        
        # Filter out records without coordinates
        with_coords = [r for r in normalized if r.get("lat") and r.get("lng")]
        print(f"  With coordinates: {len(with_coords)}")
        
        # Build output
        output = {
            "city": config["name"],
            "state": config["state"],
            "population": config["population"],
            "fetched_at": datetime.now().isoformat(),
            "record_count": len(with_coords),
            "records": with_coords
        }
        
        # Save to file
        output_file = DATA_DIR / f"{city_key}.json"
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"  Saved to: {output_file}")
        return output
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def fetch_all_cities(limit=50000, delay=2):
    """Fetch data for all configured cities"""
    results = {}
    
    for city_key in CITIES:
        result = fetch_city(city_key, limit)
        if result:
            results[city_key] = {
                "city": result["city"],
                "state": result["state"],
                "records": result["record_count"]
            }
        time.sleep(delay)  # Be nice to the APIs
    
    # Save summary
    summary_file = DATA_DIR / "_summary.json"
    with open(summary_file, "w") as f:
        json.dump({
            "fetched_at": datetime.now().isoformat(),
            "cities": results
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: Fetched {len(results)} cities")
    print(f"{'='*60}")
    for city, info in sorted(results.items(), key=lambda x: x[1]["records"], reverse=True):
        print(f"  {info['city']}, {info['state']}: {info['records']:,} records")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Fetch specific city
        city_key = sys.argv[1].lower().replace(" ", "_")
        fetch_city(city_key)
    else:
        # Fetch all cities
        print("Usage: python fetch_crime_data.py [city_name]")
        print("       python fetch_crime_data.py --all")
        print("\nAvailable cities:")
        for key, config in sorted(CITIES.items()):
            print(f"  {key}: {config['name']}, {config['state']}")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--all":
            fetch_all_cities()
