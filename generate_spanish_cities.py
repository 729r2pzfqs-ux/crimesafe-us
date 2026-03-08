#!/usr/bin/env python3
"""Generate Spanish versions of all city pages."""
import os
import re

# Spanish translations for city pages
REPLACEMENTS = [
    # HTML lang
    ('lang="en"', 'lang="es"'),
    
    # Page titles and meta
    ('Crime Rate & Safety Score', 'Tasa de Crimen y Puntuación de Seguridad'),
    ('Crime Rate', 'Tasa de Crimen'),
    ('crime data, safety score', 'datos de crimen, puntuación de seguridad'),
    ('safety rankings', 'clasificaciones de seguridad'),
    ('Latest FBI Data', 'Datos del FBI'),
    
    # Navigation
    ('>Home<', '>Inicio<'),
    ('Home</a> →', 'Inicio</a> →'),
    
    # Section headers
    ('Safety Overview', 'Resumen de Seguridad'),
    ('Safety Score', 'Puntuación de Seguridad'),
    ('Average Safety', 'Seguridad Promedio'),
    ('Crime Breakdown', 'Desglose del Crimen'),
    ('Crime Statistics', 'Estadísticas de Crimen'),
    ('Detailed Statistics', 'Estadísticas Detalladas'),
    ('Crime Trends', 'Tendencias de Crimen'),
    ('Safety Tips', 'Consejos de Seguridad'),
    ('Nearby Cities', 'Ciudades Cercanas'),
    ('Related Comparisons', 'Comparaciones Relacionadas'),
    ('About This Data', 'Acerca de Estos Datos'),
    ('Frequently Asked Questions', 'Preguntas Frecuentes'),
    ('Total Incidents', 'Incidentes Totales'),
    ('per 100k residents', 'por cada 100k residentes'),
    ('residents', 'residentes'),
    
    # FAQ questions
    ('What is', '¿Cuál es'),
    ("'s crime rate?", ' la tasa de crimen?'),
    ('Is ', '¿Es '),
    (' safe?', ' seguro?'),
    (' safe to live?', ' seguro para vivir?'),
    ('How does ', '¿Cómo se compara '),
    (' compare to', ' con'),
    ('the national average', 'el promedio nacional'),
    ('above average', 'por encima del promedio'),
    ('below average', 'por debajo del promedio'),
    ('which is', 'que es'),
    
    # Paragraphs
    (' has a safety score of ', ' tiene una puntuación de seguridad de '),
    ('The city reported', 'La ciudad reportó'),
    ('violent crimes and', 'crímenes violentos y'),
    ('property crimes according to the latest FBI data', 'crímenes contra la propiedad según los datos más recientes del FBI'),
    ('With a violent crime rate of', 'Con una tasa de crimen violento de'),
    
    # Stats labels
    ('Violent Crime Rate', 'Tasa de Crimen Violento'),
    ('Property Crime Rate', 'Tasa de Crimen contra la Propiedad'),
    ('Violent Crime', 'Crimen Violento'),
    ('Property Crime', 'Crimen contra la Propiedad'),
    ('Population', 'Población'),
    ('per 100,000', 'por cada 100,000'),
    ('per 100K', 'por cada 100K'),
    ('National Average', 'Promedio Nacional'),
    ('National Avg', 'Promedio Nacional'),
    ('vs national avg', 'vs promedio nacional'),
    
    # Grades
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
    
    # Crime types
    ('Murder', 'Homicidio'),
    ('Rape', 'Violación'),
    ('Robbery', 'Robo con Violencia'),
    ('Assault', 'Agresión'),
    ('Aggravated Assault', 'Agresión Agravada'),
    ('Burglary', 'Allanamiento'),
    ('Theft', 'Robo'),
    ('Larceny', 'Hurto'),
    ('Motor Vehicle Theft', 'Robo de Vehículos'),
    ('Vehicle Theft', 'Robo de Vehículos'),
    ('Arson', 'Incendio Provocado'),
    
    # Comparisons and CTAs
    ('Compare', 'Comparar'),
    ('View Details', 'Ver Detalles'),
    ('See how', 'Mira cómo'),
    ('stacks up against other major cities', 'se compara con otras ciudades importantes'),
    ('Compare Cities →', 'Comparar Ciudades →'),
    
    # Footer
    ('City Rankings', 'Clasificaciones de Ciudades'),
    ('© 2026 HoodSafe.org', '© 2026 HoodSafe.org'),
    
    # Data source
    ('Source: FBI UCR', 'Fuente: FBI UCR'),
    ('FBI Uniform Crime Report', 'Informe Uniforme de Crimen del FBI'),
    ('Based on FBI', 'Basado en datos del FBI'),
    ('Latest available data', 'Datos más recientes disponibles'),
    
    # Misc
    ('Loading...', 'Cargando...'),
    ('incidents', 'incidentes'),
    ('lower than', 'menor que'),
    ('higher than', 'mayor que'),
    ('below', 'por debajo'),
    ('above', 'por encima'),
]

def translate_city_page(html):
    """Apply Spanish translations to city page HTML."""
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)
    return html

def add_hreflang(html, en_url, es_url):
    """Add hreflang tags to page."""
    hreflang = f'''
<link rel="alternate" hreflang="en" href="{en_url}" />
<link rel="alternate" hreflang="es" href="{es_url}" />
<link rel="alternate" hreflang="x-default" href="{en_url}" />
'''
    html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + hreflang)
    return html

def generate_spanish_cities():
    """Generate Spanish versions of all city pages."""
    city_dirs = [d for d in os.listdir('city') if os.path.isdir(f'city/{d}')]
    print(f"Generating Spanish versions for {len(city_dirs)} cities...")
    
    os.makedirs('es/city', exist_ok=True)
    
    generated = 0
    for i, slug in enumerate(city_dirs):
        en_path = f'city/{slug}/index.html'
        es_dir = f'es/city/{slug}'
        es_path = f'{es_dir}/index.html'
        
        if not os.path.exists(en_path):
            continue
        
        with open(en_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Apply translations
        html = translate_city_page(html)
        
        # Update canonical URL
        html = html.replace(f'href="https://hoodsafe.org/city/{slug}/"', 
                           f'href="https://hoodsafe.org/es/city/{slug}/"')
        
        # Add hreflang
        en_url = f'https://hoodsafe.org/city/{slug}/'
        es_url = f'https://hoodsafe.org/es/city/{slug}/'
        html = add_hreflang(html, en_url, es_url)
        
        # Update internal links to Spanish versions
        html = html.replace('href="/"', 'href="/es/"')
        html = html.replace('href="/compare/"', 'href="/es/compare/"')
        
        os.makedirs(es_dir, exist_ok=True)
        with open(es_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated += 1
        if generated % 1000 == 0:
            print(f"  Generated {generated}...")
    
    print(f"\n✅ Generated {generated} Spanish city pages")

if __name__ == '__main__':
    generate_spanish_cities()
