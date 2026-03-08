#!/usr/bin/env python3
"""Generate Spanish versions of all ZIP code pages."""
import os

REPLACEMENTS = [
    ('lang="en"', 'lang="es"'),
    ('>Home<', '>Inicio<'),
    ('Home</a> →', 'Inicio</a> →'),
    ('ZIP Codes</a>', 'Códigos Postales</a>'),
    ('ZIP Code', 'Código Postal'),
    ('Zip Code', 'Código Postal'),
    ('Safety Score', 'Puntuación de Seguridad'),
    ('Crime Data', 'Datos de Crimen'),
    ('Crime Statistics', 'Estadísticas de Crimen'),
    ('Located in', 'Ubicado en'),
    ('Based on city data', 'Basado en datos de la ciudad'),
    ('This score is based on crime data for', 'Esta puntuación se basa en datos de crimen de'),
    ('the primary city for ZIP code', 'la ciudad principal del código postal'),
    ('Individual neighborhoods within this ZIP may vary', 'Los vecindarios individuales dentro de este código postal pueden variar'),
    ('Violent Crime', 'Crimen Violento'),
    ('Violento Rate', 'Tasa de Crimen Violento'),
    ('Property Crime', 'Crimen contra la Propiedad'),
    ('Propiedad Rate', 'Tasa de Crimen contra la Propiedad'),
    ('City Population', 'Población de la Ciudad'),
    ('City Población', 'Población de la Ciudad'),
    ('Population', 'Población'),
    ('per 100K', 'por cada 100K'),
    ('View City Details', 'Ver Detalles de la Ciudad'),
    ('>View Full ', '>Ver Detalles de '),
    (' Details →<', ' →<'),
    ('About ZIP Code', 'Acerca del Código Postal'),
    ('About Código Postal', 'Acerca del Código Postal'),
    ('is located in', 'está ubicado en'),
    ('Based on FBI crime data', 'Basado en datos de crimen del FBI'),
    ('this area has a safety score of', 'esta área tiene una puntuación de seguridad de'),
    ('earning a grade of', 'obteniendo una calificación de'),
    ('Crime rates in this area are', 'Las tasas de crimen en esta área están'),
    ('around the national average', 'alrededor del promedio nacional'),
    ('above the national average', 'por encima del promedio nacional'),
    ('below the national average', 'por debajo del promedio nacional'),
    ('Crimen Tasa de Crimen', 'Tasa de Crimen'),
    ('Grade: A — Very Safe', 'Calificación: A — Muy Seguro'),
    ('Grade: B — Safe', 'Calificación: B — Seguro'),
    ('Grade: C — Moderate', 'Calificación: C — Moderado'),
    ('Grade: D — Below Average', 'Calificación: D — Por Debajo del Promedio'),
    ('Grade: F — High Risk', 'Calificación: F — Alto Riesgo'),
    ('Grade: A', 'Calificación: A'),
    ('Grade: B', 'Calificación: B'),
    ('Grade: C', 'Calificación: C'),
    ('Grade: D', 'Calificación: D'),
    ('Grade: F', 'Calificación: F'),
    ('Very Safe', 'Muy Seguro'),
    ('Safe', 'Seguro'),
    ('Moderate', 'Moderado'),
    ('Below Average', 'Por Debajo del Promedio'),
    ('High Risk', 'Alto Riesgo'),
    ('Is ZIP code', '¿Es el código postal'),
    ('safe?', 'seguro?'),
    ('has a safety score of', 'tiene una puntuación de seguridad de'),
    ('View crime rates and safety data', 'Ver tasas de crimen y datos de seguridad'),
    ('© 2026 HoodSafe.org', '© 2026 HoodSafe.org'),
    # Fix links to use /es/ prefix
    ('href="/zip/', 'href="/es/zip/'),
    ('href="/city/', 'href="/es/city/'),
    ('href="/"', 'href="/es/"'),
]

def translate_zip_page(html):
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)
    return html

def add_hreflang(html, en_url, es_url):
    hreflang = f'''
<link rel="alternate" hreflang="en" href="{en_url}" />
<link rel="alternate" hreflang="es" href="{es_url}" />
<link rel="alternate" hreflang="x-default" href="{en_url}" />
'''
    html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + hreflang)
    return html

def generate_spanish_zips():
    zip_dirs = [d for d in os.listdir('zip') if os.path.isdir(f'zip/{d}')]
    print(f"Generating Spanish versions for {len(zip_dirs)} ZIP codes...")
    
    os.makedirs('es/zip', exist_ok=True)
    
    generated = 0
    for slug in zip_dirs:
        en_path = f'zip/{slug}/index.html'
        es_dir = f'es/zip/{slug}'
        es_path = f'{es_dir}/index.html'
        
        if not os.path.exists(en_path):
            continue
        
        with open(en_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        html = translate_zip_page(html)
        html = html.replace(f'href="https://hoodsafe.org/zip/{slug}/"', 
                           f'href="https://hoodsafe.org/es/zip/{slug}/"')
        
        en_url = f'https://hoodsafe.org/zip/{slug}/'
        es_url = f'https://hoodsafe.org/es/zip/{slug}/'
        html = add_hreflang(html, en_url, es_url)
        
        html = html.replace('href="/"', 'href="/es/"')
        
        os.makedirs(es_dir, exist_ok=True)
        with open(es_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated += 1
        if generated % 2000 == 0:
            print(f"  Generated {generated}...")
    
    print(f"\n✅ Generated {generated} Spanish ZIP pages")

if __name__ == '__main__':
    generate_spanish_zips()
