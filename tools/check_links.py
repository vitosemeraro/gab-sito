# Controlla che ogni link interno e ogni immagine del sito generato punti a un file esistente.
import os, re, sys
DIST = sys.argv[1] if len(sys.argv) > 1 else 'src/dist'
bad = []
for r, _, fs in os.walk(DIST):
    for f in fs:
        if not f.endswith('.html'): continue
        p = os.path.join(r, f); s = open(p, encoding='utf-8').read()
        for u in re.findall(r'(?:href|src)="(/[^"#?]*)', s) + [x.split()[0] for x in re.findall(r'srcset="([^"]+)"', s) for x in x.split(',')]:
            if not u.startswith('/') or u.startswith('//'): continue
            t = os.path.join(DIST, u.lstrip('/'))
            if not (os.path.isfile(t) or os.path.isfile(os.path.join(t, 'index.html'))):
                bad.append(f'{os.path.relpath(p, DIST)} -> {u}')
for b in sorted(set(bad)): print('LINK ROTTO', b)
print(len(set(bad)), 'link rotti')
sys.exit(1 if bad else 0)
