#!/usr/bin/env python3
"""Generate Spanish versions of all comparison pages."""
import os

REPLACEMENTS = [
    ('lang="en"', 'lang="es"'),
    ('>Home<', '>Inicio<'),
    ('Home</a> →', 'Inicio</a> →'),
    ('Compare</a> →', 'Comparar</a> →'),
    (' vs ', ' vs '),
    ('Crime Rate Comparison', 'Comparación de Tasas de Crimen'),
    ('Safety Comparison', 'Comparación de Seguridad'),
    ('Which city is safer', 'Cuál ciudad es más segura'),
    ('is Safer', 'es Más Seguro'),
    ('is safer by', 'es más seguro por'),
    ('is safer than', 'es más seguro que'),
    ('Safety Score', 'Puntuación de Seguridad'),
    ('Violent Rate', 'Tasa de Violencia'),
    ('Property Rate', 'Tasa de Propiedad'),
    ('Violent Crime', 'Crimen Violento'),
    ('Property Crime', 'Crimen contra la Propiedad'),
    ('Population', 'Población'),
    ('per 100K', 'por cada 100K'),
    ('Grade: A', 'Calificación: A'),
    ('Grade: B', 'Calificación: B'),
    ('Grade: C', 'Calificación: C'),
    ('Grade: D', 'Calificación: D'),
    ('Grade: F', 'Calificación: F'),
    ('Winner', 'Ganador'),
    ('View Details', 'Ver Detalles'),
    ('>Ver Detalles →<', '>Ver Detalles →<'),
    ('Related Comparisons', 'Comparaciones Relacionadas'),
    ('Compare More Cities', 'Comparar Más Ciudades'),
    ('points', 'puntos'),
    ('by ', 'por '),
    ('© 2026 HoodSafe.org', '© 2026 HoodSafe.org'),
    # Fix links
    ('href="/"', 'href="/es/"'),
    ('href="/compare/"', 'href="/es/compare/"'),
    ('href="/compare/', 'href="/es/compare/'),
    ('href="/city/', 'href="/es/city/'),
]

def translate_comparison_page(html):
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

def generate_spanish_comparisons():
    compare_dirs = [d for d in os.listdir('compare') if os.path.isdir(f'compare/{d}') and '-vs-' in d]
    print(f"Generating Spanish versions for {len(compare_dirs)} comparisons...")
    
    os.makedirs('es/compare', exist_ok=True)
    
    generated = 0
    for slug in compare_dirs:
        en_path = f'compare/{slug}/index.html'
        es_dir = f'es/compare/{slug}'
        es_path = f'{es_dir}/index.html'
        
        if not os.path.exists(en_path):
            continue
        
        with open(en_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        html = translate_comparison_page(html)
        html = html.replace(f'href="https://hoodsafe.org/compare/{slug}/"', 
                           f'href="https://hoodsafe.org/es/compare/{slug}/"')
        
        en_url = f'https://hoodsafe.org/compare/{slug}/'
        es_url = f'https://hoodsafe.org/es/compare/{slug}/'
        html = add_hreflang(html, en_url, es_url)
        
        html = html.replace('href="/"', 'href="/es/"')
        html = html.replace('href="/compare/"', 'href="/es/compare/"')
        
        os.makedirs(es_dir, exist_ok=True)
        with open(es_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated += 1
        if generated % 10000 == 0:
            print(f"  Generated {generated}...")
    
    print(f"\n✅ Generated {generated} Spanish comparison pages")

if __name__ == '__main__':
    generate_spanish_comparisons()
