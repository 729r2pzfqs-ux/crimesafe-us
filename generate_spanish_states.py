#!/usr/bin/env python3
"""Generate Spanish versions of all state pages."""
import os

REPLACEMENTS = [
    ('lang="en"', 'lang="es"'),
    ('>Home<', '>Inicio<'),
    ('Home</a> →', 'Inicio</a> →'),
    ('>States<', '>Estados<'),
    ('States</a>', 'Estados</a>'),
    ('→ States →', '→ Estados →'),
    ('Crime Rate & Safety', 'Tasa de Crimen y Seguridad'),
    ('Crime rate rankings for', 'Clasificaciones de tasa de crimen para'),
    ('Latest FBI Data', 'Datos del FBI'),
    ('Safety Score', 'Puntuación de Seguridad'),
    ('Avg Score', 'Punt. Prom'),
    ('A-Rated', 'Calif. A'),
    ('>Cities<', '>Ciudades<'),
    ('Cities in', 'Ciudades en'),
    ('Counties in', 'Condados en'),
    ('Crime Statistics', 'Estadísticas de Crimen'),
    ('>City<', '>Ciudad<'),
    ('>Score<', '>Puntuación<'),
    ('>Grade<', '>Calificación<'),
    ('Población', 'Población'),
    ('Population', 'Población'),
    ('Violent/100k', 'Violento/100k'),
    ('Violent Crime', 'Crimen Violento'),
    ('Property Crime', 'Crimen contra la Propiedad'),
    ('per 100K', 'por cada 100K'),
    ('View Details', 'Ver Detalles'),
    ('Safest Cities in', 'Ciudades Más Seguras en'),
    ('Safest Ciudades en', 'Ciudades Más Seguras en'),
    ('Top 20 Safest Ciudades en', 'Top 20 Ciudades Más Seguras en'),
    ('Top 20 Safest', 'Top 20 Más Seguras'),
    ('Safest Cities', 'Ciudades Más Seguras'),
    ('Most Dangerous', 'Más Peligrosas'),
    ('State Overview', 'Resumen del Estado'),
    ('Click any city to explore', 'Haz clic en cualquier ciudad para explorar'),
    ('its safety data', 'sus datos de seguridad'),
    (' cities', ' ciudades'),
    ('About ', 'Acerca de '),
    (' Crime Data', ' Datos de Crimen'),
    ('This ranking includes', 'Esta clasificación incluye'),
    ('with crime data from the FBI', 'con datos de crimen del FBI'),
    ("'s Uniform Crime Reporting (UCR) program for", 'del programa UCR para'),
    ('Safety scores are calculated using', 'Las puntuaciones de seguridad se calculan usando'),
    ('violent crime rates', 'tasas de crimen violento'),
    ('property crime rates', 'tasas de crimen contra la propiedad'),
    ('and population data', 'y datos de población'),
    ('All State Rankings', 'Todas las Clasificaciones'),
    ('© 2026 HoodSafe.org', '© 2026 HoodSafe.org'),
    ('Safest ciudades in', 'Ciudades más seguras en'),
    ('ranked by crime rate', 'clasificadas por tasa de crimen'),
    ('See the top 20 safest and most dangerous', 'Ver las 20 ciudades más seguras y peligrosas'),
    ('ciudades in', 'ciudades en'),
    ('safest and most dangerous ciudades', 'ciudades más seguras y peligrosas'),
    # Fix links
    ('href="/"', 'href="/es/"'),
    ('href="/safest-cities/', 'href="/es/safest-cities/'),
    ('href="/city/', 'href="/es/city/'),
]

def translate_state_page(html):
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

def generate_spanish_states():
    state_dirs = [d for d in os.listdir('safest-cities') if os.path.isdir(f'safest-cities/{d}')]
    print(f"Generating Spanish versions for {len(state_dirs)} states...")
    
    os.makedirs('es/safest-cities', exist_ok=True)
    
    generated = 0
    for slug in state_dirs:
        en_path = f'safest-cities/{slug}/index.html'
        es_dir = f'es/safest-cities/{slug}'
        es_path = f'{es_dir}/index.html'
        
        if not os.path.exists(en_path):
            continue
        
        with open(en_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        html = translate_state_page(html)
        html = html.replace(f'href="https://hoodsafe.org/safest-cities/{slug}/"', 
                           f'href="https://hoodsafe.org/es/safest-cities/{slug}/"')
        
        en_url = f'https://hoodsafe.org/safest-cities/{slug}/'
        es_url = f'https://hoodsafe.org/es/safest-cities/{slug}/'
        html = add_hreflang(html, en_url, es_url)
        
        html = html.replace('href="/"', 'href="/es/"')
        
        os.makedirs(es_dir, exist_ok=True)
        with open(es_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated += 1
    
    print(f"✅ Generated {generated} Spanish state pages")

if __name__ == '__main__':
    generate_spanish_states()
