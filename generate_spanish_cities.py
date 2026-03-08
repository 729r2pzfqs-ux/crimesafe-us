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
    ('Latest FBI data', 'Datos del FBI'),
    ('crime rate and safety statistics', 'tasa de crimen y estadísticas de seguridad'),
    ('Violent crime rate:', 'Tasa de crimen violento:'),
    
    # Navigation
    ('>Home<', '>Inicio<'),
    ('Home</a> →', 'Inicio</a> →'),
    
    # Section headers - IMPORTANT: More specific strings must come BEFORE general ones!
    ('Safety Overview', 'Resumen de Seguridad'),
    ('Safety Score', 'Puntuación de Seguridad'),
    ('.score-label { font-size: 0.75rem; opacity: 0.9; }', '.score-label { font-size: 0.75rem; opacity: 0.9; text-align: center; }'),
    ('Below Average Safety', 'Seguridad Por Debajo del Promedio'),
    ('Above Average Safety', 'Seguridad Por Encima del Promedio'),
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
    ('Very Safe', 'Muy Seguro'),
    ('is below average', 'está por debajo del promedio'),
    ('is above average', 'está por encima del promedio'),
    ('above the national average of', 'por encima del promedio nacional de'),
    ('below the national average of', 'por debajo del promedio nacional de'),
    ('the national average', 'el promedio nacional'),
    ('national average', 'promedio nacional'),
    ('per 100k', 'por cada 100k'),
    ('per 100K', 'por cada 100K'),
    ('Violent Crimes', 'Crímenes Violentos'),
    ('Property Crimes', 'Crímenes contra la Propiedad'),
    ('>Score<', '>Puntuación<'),
    ('Score</span>', 'Puntuación</span>'),
    ('HoodSeguro', 'HoodSafe'),
    ('>Rankings<', '>Clasificaciones<'),
    ('View ', 'Ver '),
    (' Rankings', ' Clasificaciones'),
    ('ranks against other cities in', 'se compara con otras ciudades en'),
    ('with Other Cities', 'con Otras Ciudades'),
    ('has a total crime rate of', 'tiene una tasa de crimen total de'),
    ('has a total crime rate de', 'tiene una tasa de crimen total de'),
    (', with ', ', con '),
    ('property crimes per', 'crímenes contra la propiedad por'),
    ('property crimes por', 'crímenes contra la propiedad por'),
    ('Violent crime is por', 'El crimen violento está por'),
    ('Robberies', 'Robos'),
    ('Burglaries', 'Allanamientos'),
    ('Assaults', 'Agresiones'),
    ('Homicides', 'Homicidios'),
    ('Larceny', 'Hurtos'),
    ('Motor Vehicle Theft', 'Robo de Vehículos'),
    ('The violent crime rate is', 'La tasa de crimen violento es'),
    ('Property crime rate is', 'La tasa de crimen contra la propiedad es'),
    ('Total Incidents', 'Incidentes Totales'),
    ('How does', 'Cómo se compara'),
    ("'s crime rate compare to", ' en comparación con'),
    ('The violent crime rate is above', 'La tasa de crimen violento está por encima de'),
    ('The violent crime rate is below', 'La tasa de crimen violento está por debajo de'),
    ('Property crime is above', 'El crimen contra la propiedad está por encima de'),
    ('Property crime is below', 'El crimen contra la propiedad está por debajo de'),
    ('the US average of', 'el promedio de EE.UU. de'),
    ("'s crime rate compare to the national average", ' en comparación con el promedio nacional'),
    ("'s crime rate", ' tasa de crimen'),
    (' of ', ' de '),
    
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
    ('— Safe<', '— Seguro<'),
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
        html = html.replace('href="/city/', 'href="/es/city/')
        html = html.replace('href="/#rankings"', 'href="/es/#rankings"')
        html = html.replace('>Cities<', '>Ciudades<')
        html = html.replace('Comparar Cities', 'Comparar Ciudades')
        
        os.makedirs(es_dir, exist_ok=True)
        with open(es_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated += 1
        if generated % 1000 == 0:
            print(f"  Generated {generated}...")
    
    print(f"\n✅ Generated {generated} Spanish city pages")

if __name__ == '__main__':
    generate_spanish_cities()
