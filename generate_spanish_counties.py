#!/usr/bin/env python3
"""Generate Spanish versions of all county pages."""
import os
import re

REPLACEMENTS = [
    ('lang="en"', 'lang="es"'),
    ('>Home<', '>Inicio<'),
    ('Home</a> →', 'Inicio</a> →'),
    ('crime stats. Score:', 'estadísticas de crimen. Puntuación:'),
    ('Latest FBI data.', 'Datos del FBI.'),
    ('County Crime Rate', 'Tasa de Crimen del Condado'),
    ('Safety Score', 'Puntuación de Seguridad'),
    ('Cities in this County', 'Ciudades en este Condado'),
    ('Cities in', 'Ciudades en'),
    ('Crime Statistics', 'Estadísticas de Crimen'),
    ('Population', 'Población'),
    ('Violent Crime', 'Crimen Violento'),
    ('Property Crime', 'Crimen contra la Propiedad'),
    ('per 100K', 'por cada 100K'),
    ('View Details', 'Ver Detalles'),
    ('County', 'Condado'),
    ('© 2026 HoodSafe.org', '© 2026 HoodSafe.org'),
    ('Loading...', 'Cargando...'),
]

def translate_county_page(html):
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

def generate_spanish_counties():
    county_dirs = [d for d in os.listdir('county') if os.path.isdir(f'county/{d}')]
    print(f"Generating Spanish versions for {len(county_dirs)} counties...")
    
    os.makedirs('es/county', exist_ok=True)
    
    generated = 0
    for slug in county_dirs:
        en_path = f'county/{slug}/index.html'
        es_dir = f'es/county/{slug}'
        es_path = f'{es_dir}/index.html'
        
        if not os.path.exists(en_path):
            continue
        
        with open(en_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        html = translate_county_page(html)
        html = html.replace(f'href="https://hoodsafe.org/county/{slug}/"', 
                           f'href="https://hoodsafe.org/es/county/{slug}/"')
        
        en_url = f'https://hoodsafe.org/county/{slug}/'
        es_url = f'https://hoodsafe.org/es/county/{slug}/'
        html = add_hreflang(html, en_url, es_url)
        
        html = html.replace('href="/"', 'href="/es/"')
        
        os.makedirs(es_dir, exist_ok=True)
        with open(es_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated += 1
        if generated % 500 == 0:
            print(f"  Generated {generated}...")
    
    print(f"\n✅ Generated {generated} Spanish county pages")

if __name__ == '__main__':
    generate_spanish_counties()
