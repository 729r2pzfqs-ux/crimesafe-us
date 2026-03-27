#!/usr/bin/env python3
"""Enrich ZIP code pages with FAQ schema"""
import os, re, json

count = 0

def process_zip(filepath):
    global count
    with open(filepath, "r") as f:
        html = f.read()
    
    if "FAQPage" in html:
        return
    
    # Extract data
    zip_match = re.search(r'ZIP Code (\d+)', html)
    city_match = re.search(r'<p style="color:var\(--muted\)">([^•]+)•', html)
    score_match = re.search(r'<div class="score"[^>]*>(\d+)</div>', html)
    grade_match = re.search(r'Grade: ([^<]+)</div>', html)
    
    if not zip_match:
        return
    
    zipcode = zip_match.group(1)
    city = city_match.group(1).strip() if city_match else "this area"
    score = score_match.group(1) if score_match else "N/A"
    grade = grade_match.group(1) if grade_match else ""
    
    faqs = [
        (f"Is ZIP code {zipcode} safe?",
         f"ZIP code {zipcode} ({city}) has a safety score of {score}/100, earning a grade of {grade}. This score is based on FBI crime data for the primary city covering this ZIP code."),
        (f"What is the crime rate in ZIP code {zipcode}?",
         f"Crime rates for ZIP {zipcode} are based on data from {city}. Check the violent and property crime rates above for specific numbers per 100,000 residents."),
        (f"How is the safety score calculated?",
         f"Safety scores combine violent crime rates, property crime rates, and population data from the FBI Uniform Crime Report. Scores range from 0-100, with higher scores indicating safer areas."),
    ]
    
    faq_html = '\n<div style="background:var(--card);padding:1.5rem;border-radius:1rem;margin:1rem 0">\n'
    faq_html += '<h2>Frequently Asked Questions</h2>\n'
    for q, a in faqs:
        faq_html += f'<details style="border-bottom:1px solid var(--border)">'
        faq_html += f'<summary style="padding:0.75rem 0;cursor:pointer;font-weight:500">{q}</summary>'
        faq_html += f'<p style="padding:0 0 0.75rem;color:var(--muted);font-size:0.875rem;line-height:1.6">{a}</p>'
        faq_html += '</details>\n'
    faq_html += '</div>\n'
    
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]
    })
    
    html = html.replace('</main>', faq_html + '</main>')
    html = html.replace('</head>', f'<script type="application/ld+json">{schema}</script></head>')
    
    with open(filepath, "w") as f:
        f.write(html)
    count += 1

print("📮 Enriching ZIP pages...")
for d in sorted(os.listdir("zip")):
    p = f"zip/{d}/index.html"
    if os.path.isfile(p):
        process_zip(p)

# ES ZIP pages
if os.path.isdir("es/zip"):
    for d in sorted(os.listdir("es/zip")):
        p = f"es/zip/{d}/index.html"
        if os.path.isfile(p):
            process_zip(p)

print(f"✅ {count} ZIP pages enriched")
