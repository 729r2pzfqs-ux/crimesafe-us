import os, re
GA = '<script async src="https://www.googletagmanager.com/gtag/js?id=G-0G79LDD6JD"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-0G79LDD6JD");</script>'
for root, dirs, files in os.walk('.'):
    if '.git' in root: continue
    for f in files:
        if not f.endswith('.html'): continue
        p = os.path.join(root, f)
        with open(p) as fh: c = fh.read()
        if 'cookie-consent' not in c: continue
        idx = c.find('<div id="cookie-consent"')
        if idx != -1:
            end = c.find('</div>', idx)
            if end != -1:
                end += 6
                if end < len(c) and c[end] == '
': end += 1
                c = c[:idx] + c[end:]
        idx = c.find('function loadGA()')
        if idx != -1:
            s = c.rfind('<script>', 0, idx)
            if s != -1:
                e = c.find('</script>', idx)
                if e != -1:
                    e += 9
                    if e < len(c) and c[e] == '
': e += 1
                    c = c[:s] + c[e:]
        if 'googletagmanager.com/gtag/js?id=G-' not in c:
            c = c.replace('<head>', '<head>
' + GA, 1)
        with open(p, 'w') as fh: fh.write(c)
