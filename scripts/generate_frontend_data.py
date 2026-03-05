#!/usr/bin/env python3
"""
Generate optimized frontend data for HoodSafe
Creates a lightweight JSON for instant neighborhood score lookups
"""

import json
from pathlib import Path
from collections import defaultdict

SCORES_DIR = Path(__file__).parent.parent / "data" / "scores"
OUTPUT_DIR = Path(__file__).parent.parent

def main():
    print("Generating frontend data...")
    
    all_cities = {}
    all_grids = []
    
    # Load all score files
    for score_file in SCORES_DIR.glob("*_scores.json"):
        if score_file.name.startswith("_"):
            continue
            
        with open(score_file) as f:
            data = json.load(f)
        
        city_key = score_file.stem.replace("_scores", "")
        city_name = data["city"]
        state = data["state"]
        
        # City summary
        all_cities[city_key] = {
            "name": city_name,
            "state": state,
            "avg": data["city_average_score"],
            "grade": data["city_grade"],
            "crimes": data["total_crimes"],
            "grids": data["grid_cells"],
        }
        
        # Collect all grids with city reference
        for grid_key, grid_data in data["grids"].items():
            lat, lng = grid_data["lat"], grid_data["lng"]
            all_grids.append({
                "c": city_key,  # city
                "la": round(lat, 4),  # latitude
                "lo": round(lng, 4),  # longitude
                "s": grid_data["score"],  # score
                "g": grid_data["grade"],  # grade
                "v": grid_data["violent_count"],  # violent crimes
            })
    
    print(f"Cities: {len(all_cities)}")
    print(f"Total grids: {len(all_grids)}")
    
    # Create the frontend data structure
    frontend_data = {
        "cities": all_cities,
        "grids": all_grids,
    }
    
    # Write as JS module
    output_file = OUTPUT_DIR / "hoodsafe_scores.js"
    with open(output_file, "w") as f:
        f.write("// HoodSafe Score Data - Auto-generated\n")
        f.write(f"// {len(all_cities)} cities, {len(all_grids)} neighborhoods\n")
        f.write("const HOODSAFE_DATA = ")
        json.dump(frontend_data, f, separators=(',', ':'))
        f.write(";\n")
    
    print(f"Output: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Also create a minified version with just lat/lng -> score lookup
    # Format: array of [lat, lng, score, city_idx]
    city_list = list(all_cities.keys())
    city_idx = {k: i for i, k in enumerate(city_list)}
    
    compact_grids = []
    for g in all_grids:
        compact_grids.append([
            g["la"],
            g["lo"], 
            round(g["s"], 1),
            city_idx[g["c"]]
        ])
    
    compact_data = {
        "c": city_list,  # city keys
        "n": {k: v["name"] for k, v in all_cities.items()},  # city names
        "g": compact_grids,  # grids: [lat, lng, score, city_idx]
    }
    
    compact_file = OUTPUT_DIR / "hoodsafe_compact.js"
    with open(compact_file, "w") as f:
        f.write("// HoodSafe Compact - Auto-generated\n")
        f.write("const HS = ")
        json.dump(compact_data, f, separators=(',', ':'))
        f.write(";\n")
        f.write("""
// Lookup function - finds nearest grid to given lat/lng
function findHoodScore(lat, lng) {
    const grids = HS.g;
    let nearest = null;
    let minDist = Infinity;
    
    for (const g of grids) {
        const d = Math.pow(g[0] - lat, 2) + Math.pow(g[1] - lng, 2);
        if (d < minDist) {
            minDist = d;
            nearest = g;
        }
    }
    
    if (!nearest || minDist > 0.001) return null; // ~1km threshold
    
    return {
        score: nearest[2],
        grade: scoreToGrade(nearest[2]),
        city: HS.n[HS.c[nearest[3]]],
        distance: Math.sqrt(minDist) * 111 // rough km
    };
}

function scoreToGrade(s) {
    if (s >= 90) return 'A+';
    if (s >= 85) return 'A';
    if (s >= 80) return 'A-';
    if (s >= 75) return 'B+';
    if (s >= 70) return 'B';
    if (s >= 65) return 'B-';
    if (s >= 60) return 'C+';
    if (s >= 55) return 'C';
    if (s >= 50) return 'C-';
    if (s >= 45) return 'D+';
    if (s >= 40) return 'D';
    if (s >= 35) return 'D-';
    return 'F';
}
""")
    
    print(f"Compact: {compact_file}")
    print(f"Size: {compact_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
