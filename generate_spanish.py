#!/usr/bin/env python3
"""Generate Spanish language version of HoodSafe pages."""
import os
import re
import json

# Load translations
with open('translations/es.json', 'r', encoding='utf-8') as f:
    T = json.load(f)

def t(key):
    """Get translation by dot notation key."""
    keys = key.split('.')
    val = T
    for k in keys:
        val = val.get(k, key)
    return val

# Text replacements for homepage (order matters - longer strings first)
REPLACEMENTS = [
    # Longer strings first to avoid partial matches
    ('2,300 counties, 10,000+ ZIP codes. Free FBI crime data and safety scores', '2,300 condados, más de 10,000 códigos postales. Datos de crimen del FBI y puntuaciones de seguridad gratis'),
    ('2,300 counties, 10,000+ ZIP codes with FBI crime data', '2,300 condados, más de 10,000 códigos postales con datos de crimen del FBI'),
    ('ZIP codes', 'códigos postales'),
    ('ZIP code', 'código postal'),
    ('counties', 'condados'),
    ('county', 'condado'),
    # HTML lang
    ('lang="en"', 'lang="es"'),
    
    # Title and meta
    ('HoodSafe — Neighborhood Safety Explorer', 'HoodSafe — Explorador de Seguridad de Vecindarios'),
    ('Find your safest neighborhood. Search 9,000+ cities', 'Encuentra tu vecindario más seguro. Busca más de 9,000 ciudades'),
    ('Free safety scores, comparisons, and rankings', 'Puntuaciones de seguridad, comparaciones y clasificaciones gratis'),
    ('US Crime Safety Data for 9,000+ Cities', 'Datos de Seguridad y Crimen para más de 9,000 Ciudades de EE.UU.'),
    
    # Hero section
    ('Find Your Safest Neighborhood', 'Encuentra tu Vecindario Más Seguro'),
    ('9,000+ cities · 2,300 counties · 10,000 ZIPs · 125K comparisons', '9,000+ ciudades · 2,300 condados · 10,000 códigos postales · 125K comparaciones'),
    ('Search city, county, or ZIP code...', 'Buscar ciudad, condado o código postal...'),
    ('🔍 Search', '🔍 Buscar'),
    ('⚔️ Compare', '⚔️ Comparar'),
    ('First city...', 'Primera ciudad...'),
    ('Second city...', 'Segunda ciudad...'),
    ('>Compare<', '>Comparar<'),
    
    # Stats
    ('Safety Score', 'Puntuación de Seguridad'),
    ('Violent Crime', 'Crimen Violento'),
    ('Property Crime', 'Crimen contra la Propiedad'),
    ('Population', 'Población'),
    ('Violent Rate', 'Tasa de Crimen Violento'),
    ('Property Rate', 'Tasa de Crimen contra la Propiedad'),
    ('per 100K', 'por cada 100K'),
    ('National Avg', 'Promedio Nacional'),
    
    # Rankings section  
    ('City Safety Rankings', 'Clasificaciones de Seguridad por Ciudad'),
    ('Filter cities...', 'Filtrar ciudades...'),
    ('Showing', 'Mostrando'),
    (' of ', ' de '),
    (' cities', ' ciudades'),
    ('← Prev', '← Anterior'),
    ('Next →', 'Siguiente →'),
    
    # Map section
    ('Interactive Safety Map', 'Mapa Interactivo de Seguridad'),
    ('50 largest cities', '50 ciudades más grandes'),
    
    # Table headers
    ('>City<', '>Ciudad<'),
    ('>State<', '>Estado<'),
    ('Browse by State', 'Explorar por Estado'),
    ('>Rankings<', '>Clasificaciones<'),
    ('>States<', '>Estados<'),
    ('National Crime Trends', 'Tendencias Nacionales de Crimen'),
    ('Crime Trends 2019–2025', 'Tendencias de Crimen 2019–2025'),
    ('Crime Breakdown (2025)', 'Desglose del Crimen (2025)'),
    ('City Comparison', 'Comparación de Ciudades'),
    
    # Grades
    ('Grade: A', 'Calificación: A'),
    ('Grade: B', 'Calificación: B'),
    ('Grade: C', 'Calificación: C'),
    ('Grade: D', 'Calificación: D'),
    ('Grade: F', 'Calificación: F'),
    
    # KPI cards
    ('Safest Large City', 'Ciudad Grande Más Segura'),
    ('Highest Crime Risk', 'Mayor Riesgo de Crimen'),
    ('Cities Analyzed', 'Ciudades Analizadas'),
    
    # Trends section
    ('Average violent crime rate across major US cities', 'Tasa promedio de crimen violento en las principales ciudades de EE.UU.'),
    
    # Footer
    ('Based on FBI Uniform Crime Reporting (UCR) data', 'Basado en datos del Informe Uniforme de Crimen (UCR) del FBI'),
    ('Safety scores are for informational purposes', 'Las puntuaciones de seguridad son solo para fines informativos'),
    ('verify with official sources for important decisions', 'verifique con fuentes oficiales para decisiones importantes'),
    ('About & Methodology', 'Acerca de y Metodología'),
    ('FAQ', 'Preguntas Frecuentes'),
    ('Contact', 'Contacto'),
    ('>Home<', '>Inicio<'),
    
    # Misc
    ('View Details', 'Ver Detalles'),
    ('Compare Cities', 'Comparar Ciudades'),
    ('Loading...', 'Cargando...'),
    ('No results found', 'No se encontraron resultados'),
    
    # Buttons and modals
    ('>Close<', '>Cerrar<'),
    ('aria-label="Close"', 'aria-label="Cerrar"'),
    ('Quick explore:', 'Exploración rápida:'),
    ('Score:', 'Puntuación:'),
    ('See details', 'Ver detalles'),
    ('View All', 'Ver Todo'),
    ('// Close', '// Cerrar'),
    
    # Error messages
    ('City not found', 'Ciudad no encontrada'),
    ('Something went wrong', 'Algo salió mal'),
]

def generate_spanish_homepage():
    """Generate Spanish version of homepage."""
    print("Generating Spanish homepage...")
    
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Apply all replacements
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)
    
    # Update canonical URL
    html = html.replace('href="https://hoodsafe.org/"', 'href="https://hoodsafe.org/es/"')
    html = html.replace('og:url" content="https://hoodsafe.org/"', 'og:url" content="https://hoodsafe.org/es/"')
    
    # Add hreflang tags after <head>
    hreflang = '''
<link rel="alternate" hreflang="en" href="https://hoodsafe.org/" />
<link rel="alternate" hreflang="es" href="https://hoodsafe.org/es/" />
<link rel="alternate" hreflang="x-default" href="https://hoodsafe.org/" />
'''
    html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + hreflang)
    
    # Update internal links to Spanish versions
    html = html.replace('href="/about/"', 'href="/es/about/"')
    html = html.replace('href="/faq/"', 'href="/es/faq/"')
    html = html.replace('href="/contact/"', 'href="/es/contact/"')
    html = html.replace('href="/compare/"', 'href="/es/compare/"')
    
    # Keep city/county/state/zip links pointing to English versions for now
    # (Spanish versions will be generated later)
    
    os.makedirs('es', exist_ok=True)
    with open('es/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Created es/index.html")

if __name__ == '__main__':
    generate_spanish_homepage()
