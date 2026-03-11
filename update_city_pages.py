#!/usr/bin/env python3
"""Update city pages with 2025 in title and FAQ schema"""
import os
import re
from glob import glob

def update_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract score from meta description
    score_match = re.search(r'Safety Score: (\d+)/100', content)
    if not score_match:
        return False
    score = score_match.group(1)
    
    # Update title: "X Crime Rate & Safety Score | HoodSafe" -> "X Crime Rate 2025 — Safety Score {score}/100 | HoodSafe"
    old_title_pattern = r'<title>(.+?) Crime Rate & Safety Score \| HoodSafe</title>'
    new_title = rf'<title>\1 Crime Rate 2025 — Safety Score {score}/100 | HoodSafe</title>'
    content = re.sub(old_title_pattern, new_title, content)
    
    # Check if FAQ schema already exists
    if '"@type": "FAQPage"' in content:
        # Just update title
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    
    # Extract city name and grade for FAQ schema
    city_match = re.search(r'<h1>(.+?) Crime Rate</h1>', content)
    grade_match = re.search(r'Safety Score: \d+/100 \(([A-F])\)', content)
    
    if city_match and grade_match:
        city = city_match.group(1)
        grade = grade_match.group(1)
        
        # Add FAQ schema before </head>
        faq_schema = f'''
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
            }}
        ]
    }}
    </script>
</head>'''
        content = content.replace('</head>', faq_schema)
    
    with open(filepath, 'w') as f:
        f.write(content)
    return True

# Process all city pages
files = glob('city/*/index.html')
updated = 0
for f in files:
    if update_file(f):
        updated += 1
    if updated % 1000 == 0:
        print(f"Updated {updated}/{len(files)}...")

print(f"\n✅ Updated {updated} city pages")
