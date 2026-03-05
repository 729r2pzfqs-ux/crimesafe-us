#!/usr/bin/env python3
"""
HoodSafe Safety Scoring Algorithm
Calculates neighborhood safety scores from crime data
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data" / "cities"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "scores"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# CRIME SEVERITY WEIGHTS
# Higher weight = more impact on safety score (worse)
# =============================================================================

CRIME_WEIGHTS = {
    # Violent crimes (highest weight)
    "homicide": 100,
    "murder": 100,
    "manslaughter": 90,
    "rape": 85,
    "sexual assault": 85,
    "kidnapping": 80,
    "aggravated assault": 70,
    "armed robbery": 70,
    "robbery": 60,
    "assault": 50,
    "battery": 45,
    
    # Property crimes (medium weight)
    "burglary": 40,
    "breaking and entering": 40,
    "home invasion": 45,
    "arson": 50,
    "vehicle theft": 35,
    "auto theft": 35,
    "motor vehicle theft": 35,
    "grand theft": 30,
    "larceny": 25,
    "theft": 20,
    "shoplifting": 10,
    "vandalism": 15,
    "criminal mischief": 15,
    
    # Other crimes (lower weight)
    "drug": 20,
    "narcotics": 20,
    "weapons": 30,
    "firearm": 35,
    "fraud": 15,
    "forgery": 15,
    "identity theft": 15,
    "trespass": 10,
    "disorderly": 5,
    "prostitution": 10,
    "gambling": 5,
    "dui": 15,
    "dwi": 15,
}

# Category fallback weights
CATEGORY_WEIGHTS = {
    "violent": 60,
    "property": 25,
    "other": 15,
}


def get_crime_weight(crime_type, category=None):
    """Get weight for a crime based on type or category"""
    if not crime_type:
        return CATEGORY_WEIGHTS.get(category, 15)
    
    crime_lower = crime_type.lower()
    
    # Check for exact or partial matches
    for keyword, weight in CRIME_WEIGHTS.items():
        if keyword in crime_lower:
            return weight
    
    # Fall back to category
    return CATEGORY_WEIGHTS.get(category, 15)


def parse_date(date_str):
    """Parse various date formats"""
    if not date_str:
        return None
    
    # Handle epoch milliseconds
    if isinstance(date_str, (int, float)):
        try:
            return datetime.fromtimestamp(date_str / 1000)
        except:
            return None
    
    # Handle string formats
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str)[:26], fmt)
        except:
            continue
    
    return None


def get_recency_weight(crime_date, max_days=365):
    """Weight crimes by recency (recent = higher weight)"""
    if not crime_date:
        return 0.5  # Unknown date = half weight
    
    now = datetime.now()
    days_ago = (now - crime_date).days
    
    if days_ago < 0:
        days_ago = 0
    if days_ago > max_days:
        return 0.1  # Old crimes still count a little
    
    # Linear decay from 1.0 (today) to 0.3 (max_days ago)
    return 1.0 - (0.7 * days_ago / max_days)


def lat_lng_to_grid(lat, lng, grid_size=0.005):
    """Convert lat/lng to grid cell (roughly 500m x 500m at mid-latitudes)"""
    if lat is None or lng is None:
        return None
    
    try:
        lat = float(lat)
        lng = float(lng)
        grid_lat = round(lat / grid_size) * grid_size
        grid_lng = round(lng / grid_size) * grid_size
        return (grid_lat, grid_lng)
    except:
        return None


def calculate_grid_scores(records, grid_size=0.005):
    """Calculate safety scores for each grid cell"""
    # Aggregate crime weights by grid cell
    grid_crimes = defaultdict(lambda: {"total_weight": 0, "count": 0, "violent": 0, "property": 0})
    
    for record in records:
        lat = record.get("lat")
        lng = record.get("lng")
        grid = lat_lng_to_grid(lat, lng, grid_size)
        
        if not grid:
            continue
        
        # Get crime weight
        crime_type = record.get("type") or record.get("description") or ""
        category = record.get("category", "other")
        base_weight = get_crime_weight(crime_type, category)
        
        # Apply recency weight
        crime_date = parse_date(record.get("date"))
        recency = get_recency_weight(crime_date)
        
        weighted_score = base_weight * recency
        
        grid_crimes[grid]["total_weight"] += weighted_score
        grid_crimes[grid]["count"] += 1
        
        if category == "violent":
            grid_crimes[grid]["violent"] += 1
        elif category == "property":
            grid_crimes[grid]["property"] += 1
    
    return grid_crimes


def normalize_scores(grid_crimes, city_population=None):
    """Convert raw weights to 0-100 safety scores using percentile ranking"""
    if not grid_crimes:
        return {}
    
    # Get all weights and sort for percentile calculation
    weights = [(g, g_data["total_weight"]) for g, g_data in grid_crimes.items()]
    weights.sort(key=lambda x: x[1])
    
    # Create percentile ranks (0 = lowest crime, 100 = highest crime)
    n = len(weights)
    percentiles = {}
    for rank, (grid, weight) in enumerate(weights):
        percentile = (rank / (n - 1)) * 100 if n > 1 else 50
        percentiles[grid] = percentile
    
    # Convert to safety scores (invert so low crime = high score)
    scores = {}
    for grid, data in grid_crimes.items():
        crime_percentile = percentiles[grid]
        
        # Invert: high crime percentile = low safety score
        # Scale from 20-95 range (no perfect scores)
        safety_score = 95 - (crime_percentile * 0.75)
        
        # Adjust based on violent crime ratio
        if data["count"] > 0:
            violent_ratio = data["violent"] / data["count"]
            # Penalize areas with high violent crime ratio
            safety_score -= violent_ratio * 15
        
        # Clamp to valid range
        safety_score = max(15, min(95, safety_score))
        
        # Use string key for JSON compatibility
        grid_key = f"{grid[0]:.4f},{grid[1]:.4f}"
        scores[grid_key] = {
            "score": round(safety_score, 1),
            "grade": score_to_grade(safety_score),
            "crime_count": data["count"],
            "violent_count": data["violent"],
            "property_count": data["property"],
            "lat": grid[0],
            "lng": grid[1],
        }
    
    return scores


def score_to_grade(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    elif score >= 45:
        return "D+"
    elif score >= 40:
        return "D"
    elif score >= 35:
        return "D-"
    else:
        return "F"


def process_city(city_file):
    """Process a single city's crime data"""
    print(f"\nProcessing: {city_file.name}")
    
    with open(city_file) as f:
        data = json.load(f)
    
    city_name = data.get("city", "Unknown")
    state = data.get("state", "")
    records = data.get("records", [])
    
    print(f"  City: {city_name}, {state}")
    print(f"  Records: {len(records)}")
    
    if not records:
        print("  No records to process")
        return None
    
    # Calculate grid scores
    grid_crimes = calculate_grid_scores(records)
    print(f"  Grid cells: {len(grid_crimes)}")
    
    # Normalize to 0-100 scores
    scores = normalize_scores(grid_crimes, data.get("population"))
    
    # Calculate city-wide statistics
    all_scores = [s["score"] for s in scores.values()]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 50
    
    result = {
        "city": city_name,
        "state": state,
        "population": data.get("population"),
        "processed_at": datetime.now().isoformat(),
        "total_crimes": len(records),
        "grid_cells": len(scores),
        "city_average_score": round(avg_score, 1),
        "city_grade": score_to_grade(avg_score),
        "score_distribution": {
            "A": len([s for s in all_scores if s >= 80]),
            "B": len([s for s in all_scores if 65 <= s < 80]),
            "C": len([s for s in all_scores if 50 <= s < 65]),
            "D": len([s for s in all_scores if 35 <= s < 50]),
            "F": len([s for s in all_scores if s < 35]),
        },
        "grids": scores,
    }
    
    print(f"  Average Score: {avg_score:.1f} ({score_to_grade(avg_score)})")
    
    return result


def main():
    """Process all cities and generate scores"""
    print("=" * 60)
    print("HoodSafe Safety Score Generator")
    print("=" * 60)
    
    # Find all city data files
    city_files = list(DATA_DIR.glob("*.json"))
    city_files = [f for f in city_files if not f.name.startswith("_")]
    
    print(f"Found {len(city_files)} city data files")
    
    all_results = {}
    
    for city_file in sorted(city_files):
        result = process_city(city_file)
        if result:
            city_key = city_file.stem
            all_results[city_key] = result
            
            # Save individual city file
            output_file = OUTPUT_DIR / f"{city_key}_scores.json"
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
    
    # Save summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "cities": len(all_results),
        "total_grid_cells": sum(r["grid_cells"] for r in all_results.values()),
        "city_scores": {
            k: {
                "score": v["city_average_score"],
                "grade": v["city_grade"],
                "crimes": v["total_crimes"],
            }
            for k, v in all_results.items()
        }
    }
    
    with open(OUTPUT_DIR / "_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print("CITY RANKINGS (by average safety score)")
    print("=" * 60)
    
    ranked = sorted(all_results.items(), key=lambda x: x[1]["city_average_score"], reverse=True)
    for i, (key, data) in enumerate(ranked, 1):
        print(f"  {i:2}. {data['city']}, {data['state']}: {data['city_average_score']:.1f} ({data['city_grade']})")
    
    print(f"\nOutput saved to: {OUTPUT_DIR}")
    return all_results


if __name__ == "__main__":
    main()
