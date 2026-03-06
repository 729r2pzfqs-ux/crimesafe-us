import os

# Read existing sitemap
with open('sitemap.xml', 'r') as f:
    content = f.read()

# Remove closing tag
content = content.replace('</urlset>', '')

# Add ZIP index page
content += '<url><loc>https://hoodsafe.org/zip/</loc><priority>0.8</priority></url>\n'

# Add all ZIP pages
for zipcode in sorted(os.listdir('zip')):
    if zipcode.isdigit() and os.path.isdir(f'zip/{zipcode}'):
        content += f'<url><loc>https://hoodsafe.org/zip/{zipcode}/</loc><priority>0.5</priority></url>\n'

content += '</urlset>\n'

with open('sitemap.xml', 'w') as f:
    f.write(content)

print("Sitemap updated!")
