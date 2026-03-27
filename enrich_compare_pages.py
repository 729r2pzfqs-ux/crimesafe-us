#!/usr/bin/env python3
"""
Enrich CrimeSafe compare pages with FAQ section + Schema.org markup.
Target: compare/*/index.html (125,977 pages) + es/compare/*/index.html
"""
import os, re, json

count = 0
errors = 0

def extract_data(html):
    """Extract city names, scores, and crime data from compare page"""
    # City names from h2 tags
    cities = re.findall(r'<h2>([^<]+)</h2>', html)
    if len(cities) < 2:
        return None
    
    # Scores
    scores = re.findall(r'<div class="score"[^>]*>(\d+)</div>', html)
    
    # Grades
    grades = re.findall(r'<div class="grade">Grade: ([^<]+)</div>', html)
    
    # Violent rates
    violent = re.findall(r'Violent Rate</span><span>([\d,.]+)/100k</span>', html)
    
    # Property rates
    prop = re.findall(r'Property Rate</span><span>([\d,.]+)/100k</span>', html)
    
    # Winner
    winner_match = re.search(r'🏆 ([^<]+) is Safer', html)
    winner = winner_match.group(1) if winner_match else None
    
    # Points diff
    diff_match = re.search(r'by (\d+) points', html)
    diff = diff_match.group(1) if diff_match else None
    
    return {
        "city_a": cities[0], "city_b": cities[1],
        "score_a": scores[0] if len(scores) > 0 else "N/A",
        "score_b": scores[1] if len(scores) > 1 else "N/A",
        "grade_a": grades[0] if len(grades) > 0 else "",
        "grade_b": grades[1] if len(grades) > 1 else "",
        "violent_a": violent[0] if len(violent) > 0 else "N/A",
        "violent_b": violent[1] if len(violent) > 1 else "N/A",
        "prop_a": prop[0] if len(prop) > 0 else "N/A",
        "prop_b": prop[1] if len(prop) > 1 else "N/A",
        "winner": winner, "diff": diff
    }

def build_faq_and_schema(d, lang="en"):
    """Build FAQ HTML and schema for a compare page"""
    a, b = d["city_a"], d["city_b"]
    sa, sb = d["score_a"], d["score_b"]
    w = d["winner"] or a
    diff = d["diff"] or "several"
    
    if lang == "es":
        faqs = [
            (f"¿Es {a} o {b} más seguro?",
             f"{w} es más seguro con una puntuación de seguridad más alta por {diff} puntos. {a} tiene una puntuación de {sa}/100 mientras que {b} tiene {sb}/100."),
            (f"¿Cuál es la tasa de criminalidad violenta en {a} vs {b}?",
             f"{a} tiene una tasa de crimen violento de {d['violent_a']}/100k habitantes, mientras que {b} tiene {d['violent_b']}/100k. Las tasas más bajas indican comunidades más seguras."),
            (f"¿Cuál es la tasa de delitos contra la propiedad en {a} vs {b}?",
             f"{a} tiene una tasa de delitos contra la propiedad de {d['prop_a']}/100k, comparado con {d['prop_b']}/100k en {b}."),
        ]
    else:
        faqs = [
            (f"Is {a} or {b} safer?",
             f"{w} is safer with a higher safety score by {diff} points. {a} has a safety score of {sa}/100 while {b} has {sb}/100, based on FBI Uniform Crime Report data."),
            (f"What is the violent crime rate in {a} vs {b}?",
             f"{a} has a violent crime rate of {d['violent_a']} per 100,000 residents, while {b} has {d['violent_b']} per 100,000. Lower rates indicate safer communities. The national average is approximately 380 per 100,000."),
            (f"What is the property crime rate in {a} vs {b}?",
             f"{a} has a property crime rate of {d['prop_a']} per 100,000, compared to {d['prop_b']} per 100,000 in {b}. Property crimes include burglary, theft, and motor vehicle theft."),
            (f"How are CrimeSafe safety scores calculated?",
             f"Safety scores range from 0-100, combining violent crime rates, property crime rates, and population data from the FBI UCR. Higher scores mean safer cities. Grades: A (80+), B (70-79), C (60-69), D (50-59), F (below 50)."),
            (f"Should I move to {a} or {b}?",
             f"Based on crime data alone, {w} is safer. However, safety is just one factor — also consider cost of living, job market, schools, and quality of life. Visit our city pages for more details on each."),
        ]
    
    # FAQ HTML
    faq_html = '\n<div class="card" style="margin-top:1.5rem;text-align:left">\n'
    faq_html += '<h2 style="font-size:1rem;margin-bottom:0.75rem">Frequently Asked Questions</h2>\n'
    for q, ans in faqs:
        faq_html += f'<details style="border-bottom:1px solid var(--border)">'
        faq_html += f'<summary style="padding:0.75rem 0;cursor:pointer;font-weight:500">{q}</summary>'
        faq_html += f'<p style="padding:0 0 0.75rem;color:var(--muted);font-size:0.875rem;line-height:1.6">{ans}</p>'
        faq_html += '</details>\n'
    faq_html += '</div>\n'
    
    # Schema
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]
    })
    
    return faq_html, faq_schema

def process_file(filepath, lang="en"):
    global count, errors
    
    with open(filepath, "r") as f:
        html = f.read()
    
    if "FAQPage" in html:
        return  # Already enriched
    
    data = extract_data(html)
    if not data:
        errors += 1
        return
    
    faq_html, faq_schema = build_faq_and_schema(data, lang)
    
    # Inject FAQ before </main>
    html = html.replace('</main>', faq_html + '</main>')
    
    # Inject schema before </head>
    schema_tag = f'<script type="application/ld+json">{faq_schema}</script>'
    html = html.replace('</head>', schema_tag + '</head>')
    
    with open(filepath, "w") as f:
        f.write(html)
    
    count += 1

# Process EN compare pages
print("🔍 Enriching EN compare pages...")
compare_dir = "compare"
dirs = sorted(os.listdir(compare_dir))
total = len(dirs)
for i, d in enumerate(dirs):
    p = os.path.join(compare_dir, d, "index.html")
    if os.path.isfile(p):
        process_file(p, "en")
    if (i + 1) % 10000 == 0:
        print(f"  ... {i+1}/{total} ({count} enriched)")

print(f"  ✅ EN: {count} enriched ({errors} errors)")

# Process ES compare pages
es_count_before = count
print("\n🔍 Enriching ES compare pages...")
es_dir = "es/compare"
if os.path.isdir(es_dir):
    dirs = sorted(os.listdir(es_dir))
    total = len(dirs)
    for i, d in enumerate(dirs):
        p = os.path.join(es_dir, d, "index.html")
        if os.path.isfile(p):
            process_file(p, "es")
        if (i + 1) % 10000 == 0:
            print(f"  ... {i+1}/{total}")

es_enriched = count - es_count_before
print(f"  ✅ ES: {es_enriched} enriched")

print(f"\n✅ Total: {count} pages enriched ({errors} errors)")
