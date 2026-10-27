# Genera il sito statico GAB in ./dist
import os, json, re, shutil, html
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, 'dist')
SITE = 'https://gestione-affitti-brevi-milano.it'
TODAY = date.today().isoformat()
TEL = '+393290614613'; TEL_H = '329 06 14 613'
MAIL = 'hello@gestione-affitti-brevi-milano.it'
WA = 'https://wa.me/393290614613'
CAL = 'https://calendly.com/vsemeraro/30min'
INDEXNOW_KEY = '5340ac70e4b275ca587b9bcc46cdf271'
CSS = open(os.path.join(HERE, 'base.css')).read()
CSS = re.sub(r'/\*.*?\*/', '', CSS, flags=re.S)
CSS = re.sub(r'\s+', ' ', CSS).replace(' {', '{').replace('{ ', '{').replace('; ', ';').replace(' }', '}').replace(': ', ':')

# AEO: profili esterni dell'attività (solo URL reali e verificati)
SAME_AS = []  # aggiungere il link Maps del profilo Google di GAB quando è verificato (Rent Apartment Milan è un'altra attività)
VITO_SAME_AS = []
CSS += '.inbreve{border-left:4px solid #ff0088;background:#fff5fa;padding:14px 18px;margin:18px 0 26px}.inbreve strong{display:block;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:#c8006b;margin-bottom:4px}.inbreve p{margin:0}'

def inbreve(t): return f'<div class="inbreve"><strong>In breve</strong><p>{t}</p></div>'

# GA4: Analytics caricato solo dopo "Accetta" (nessuna richiesta a Google prima del consenso)
GA_ID = 'G-B77K9RC859'
# CFWA: Cloudflare Web Analytics, senza cookie: conta tutte le visite, anche di chi rifiuta il banner
CFWA = '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token": "84af6820ea6c4d93b3e82df54a69762c"}\'></script>'
CK_HTML = ('<div id="ck" class="ck" role="dialog" aria-label="Preferenze cookie" hidden><p>Usiamo Google Analytics solo se accetti, '
           'per capire quali pagine sono utili. Nessun cookie pubblicitario. <a href="/privacy/#cookie">Privacy e cookie</a></p>'
           '<div><button type="button" class="btn btn-ghost" data-ok>Accetta</button><button type="button" class="btn btn-ghost" data-no>Rifiuta</button></div></div>')
CK_JS = r"""(function(){var K="gab_ck",ID="%s";window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};
gtag("consent","default",{ad_storage:"denied",ad_user_data:"denied",ad_personalization:"denied",analytics_storage:"denied"});
function get(){try{return localStorage.getItem(K)}catch(e){return null}}function put(v){try{localStorage.setItem(K,v)}catch(e){}}
var on=false;function load(){if(on)return;on=true;gtag("consent","update",{analytics_storage:"granted"});gtag("js",new Date());gtag("config",ID);
var s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+ID;document.head.appendChild(s)}
function wipe(){document.cookie.split(";").forEach(function(c){var n=c.split("=")[0].trim();if(n.indexOf("_ga")===0){["",location.hostname,"."+location.hostname].forEach(function(d){document.cookie=n+"=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/"+(d?"; domain="+d:"")})}})}
var b=document.getElementById("ck");if(!b)return;
b.querySelector("[data-ok]").addEventListener("click",function(){put("si");b.hidden=true;load()});
b.querySelector("[data-no]").addEventListener("click",function(){put("no");b.hidden=true;wipe()});
document.querySelectorAll("[data-ck]").forEach(function(a){a.addEventListener("click",function(e){e.preventDefault();b.hidden=false})});
var v=get();if(v==="si")load();else if(v!=="no")b.hidden=false;
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[href]");if(!a)return;var h=a.getAttribute("href"),
m=h.indexOf("tel:")===0?"telefono":h.indexOf("wa.me")>-1?"whatsapp":h.indexOf("calendly.com")>-1?"calendly":h.indexOf("mailto:")===0?"email":"";if(m)gtag("event","contatto",{metodo:m})});
if(location.pathname==="/grazie/")gtag("event","generate_lead",{metodo:"modulo"});})();""" % GA_ID
CSS += '.ck{position:fixed;left:10px;right:10px;bottom:16px;z-index:40;max-width:760px;margin:0 auto;background:var(--paper);border:3px solid var(--ink);padding:14px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}.ck[hidden]{display:none}.ck p{margin:0;font-size:.92rem;flex:1 1 260px}.ck div{display:flex;gap:8px}.ck .btn{padding:10px 16px;font-size:1rem}@media (max-width:700px){.ck{bottom:76px}}'

ZONES = [
    # slug, nome breve, nome lungo, lat, lng, base tariffa monolocale (calibrata sul bilocale Precotto a 1.400 €/mese in medio termine)
    ('porta-venezia', 'Porta Venezia', 'Porta Venezia e Lima', 45.4768, 9.2075, 66),
    ('stazione-centrale', 'Stazione Centrale', 'Stazione Centrale', 45.4855, 9.2040, 62),
    ('loreto-nolo', 'NoLo', 'Loreto, NoLo e Pasteur', 45.4890, 9.2185, 56),
    ('viale-monza', 'Viale Monza', 'Viale Monza, Turro e Gorla', 45.5030, 9.2245, 52),
    ('precotto-greco', 'Precotto', 'Precotto e Greco', 45.5110, 9.2195, 50),
    ('bicocca', 'Bicocca', 'Bicocca', 45.5175, 9.2105, 50),
]

# Recensioni: reviews.json (aggiornato ogni settimana dal job), mostrate dalla più recente
MESI = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic']
REVIEWS = [(r['name'], MESI[int(r['date'][5:7]) - 1] + ' ' + r['date'][:4], r['listing'], r['text'], r.get('lang', ''))
           for r in sorted(json.load(open(os.path.join(HERE, 'reviews.json'))), key=lambda r: r['date'], reverse=True)]

def esc(s): return html.escape(s, quote=True)

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'

ORG = {"@type": "LocalBusiness", "@id": SITE + "/#gab", "name": "GAB Gestione Affitti Brevi", "url": SITE + "/",
       "telephone": TEL, "email": MAIL, "image": SITE + "/img/vito-ritratto-640.webp", "priceRange": "€€",
       "founder": {"@type": "Person", "@id": SITE + "/chi-siamo/#vito", "name": "Vito Semeraro"},
       "logo": SITE + "/favicon.svg", "currenciesAccepted": "EUR", "knowsLanguage": ["it", "en", "fr", "es", "pt"],
       "geo": {"@type": "GeoCoordinates", "latitude": 45.497, "longitude": 9.214},
       "knowsAbout": ["Gestione affitti brevi", "Affitti a medio termine", "Property management Airbnb", "Codice CIN", "Cedolare secca", "Home staging"],
       **({"sameAs": SAME_AS} if SAME_AS else {}),
       "description": "Boutique agency di gestione affitti brevi e a medio termine a Milano, da Porta Venezia a Bicocca.",
       "address": {"@type": "PostalAddress", "addressLocality": "Milano", "addressRegion": "MI", "addressCountry": "IT"},
       "areaServed": [z[2] + ', Milano' for z in ZONES]}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": SITE + u} if u else {})} for i, (n, u) in enumerate(items)]}

def crumbs_html(items):
    parts = [f'<a href="{u}">{esc(n)}</a>' if u else esc(n) for n, u in items]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' › '.join(parts) + '</nav>'

def picture(base, widths, alt, sizes, eager=False, cls=''):
    srcw = ', '.join(f'/img/{base}-{w}.webp {w}w' for w in widths)
    big = widths[0]
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    dims = IMG_DIMS.get(f'{base}-{big}', (big, big))
    return f'<img src="/img/{base}-{big}.webp" srcset="{srcw}" sizes="{sizes}" alt="{esc(alt)}" width="{dims[0]}" height="{dims[1]}" {load}' + (f' class="{cls}"' if cls else '') + '>'

IMG_DIMS = {}

NAV = [('Servizi', '/servizi/'), ('Zone', '/zone/'), ('Prezzi', '/prezzi/'), ('Guide', '/guide/'), ('Chi siamo', '/chi-siamo/'), ('Contatti', '/contatti/')]

CALC_JS = r'''(function(){var RATE={%s};var SIZE={mono:1,bilo:1.3,trilo:1.6};
// breve: occupazione 65%%, poi commissioni portali 15%%, GAB 15%%, maggiore cedolare 5%%, usura 5%%
// medio: tariffa x 30 notti scontata del 15%%, occupazione 95%%, GAB 10%%
var NET={breve:0.65*0.60,medio:0.85*0.95*0.90};
var eur=function(n){return (Math.round(n/10)*10).toLocaleString("it-IT")+" €"};
document.querySelectorAll("form[data-calc]").forEach(function(f){var bx=f.querySelector(".budget");f.querySelectorAll("input[name=stato]").forEach(function(i){i.addEventListener("change",function(){bx.hidden=i.value!=="rinnovo"||!i.checked;});});
f.addEventListener("submit",function(e){e.preventDefault();
var g=(RATE[f.zona.value]||55)*SIZE[f.tipo.value]*30;var k=f.querySelector("input[name=formula]:checked").value;var o=k==="breve"?"medio":"breve";
var r=f.querySelector(".result");var n=g*NET[k];r.querySelector("strong").textContent=eur(n);
var y=f.querySelector(".roi"),rv=f.querySelector("input[name=stato]:checked").value==="rinnovo";y.style.display=rv?"block":"none";
if(rv){var b=f.budget.value.split("-").map(Number),m=function(x){return Math.max(1,Math.round(x/n))};
y.innerHTML="Il budget del restyle rientra "+(b[0]===0?"entro "+m(b[1]):b[1]===0?"in almeno "+m(b[0]):"in "+m(b[0])+"–"+m(b[1]))+" mesi di rendita netta. <a href=\"/servizi/consulenza-home-staging/\">Con la consulenza home staging ti diciamo come spenderlo →</a>";}
r.querySelector(".cmp").textContent=(o==="medio"?"Con il medio periodo: ":"Con l'affitto breve: ")+eur(g*NET[o])+" al mese";r.style.display="block";
var c=document.getElementById("f-zona");if(c&&!c.value)c.value=f.zona.options[f.zona.selectedIndex].text;
if(window.gtag)gtag("event","calcolo_rendita",{zona:f.zona.value,formula:k,stato:rv?"rinnovo":"pronta"});});});})();''' % ','.join(f'"{z[0]}":{z[5]}' for z in ZONES)

MAP_JS = r'''(function(){var el=document.getElementById("zonemap");if(!el)return;
var Z=%s;var M1=[[45.4746,9.2052],[45.48,9.2105],[45.4857,9.216],[45.491,9.219],[45.4965,9.2235],[45.5015,9.225],[45.507,9.2255],[45.5125,9.228]];
function draw(){var m=L.map(el,{scrollWheelZoom:false}).setView([45.497,9.214],14);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:18,className:"tiles-soft",attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(m);
L.polyline(M1,{color:"#ff0088",weight:14,opacity:.15,lineCap:"round"}).addTo(m);L.polyline(M1,{color:"#c8006b",weight:2,dashArray:"4 6"}).addTo(m);
Z.forEach(function(z){L.circle([z[1],z[2]],{radius:420,color:"#ff0088",weight:2,fillColor:"#ff0088",fillOpacity:.18}).addTo(m).bindTooltip(z[0],{permanent:true,direction:"right",className:"zone-tip",offset:[10,0]}).on("click",function(){location.href=z[3]})});
m.fitBounds(L.latLngBounds(Z.map(function(z){return[z[1],z[2]]})),{padding:[40,40]});}
function load(){var c=document.createElement("link");c.rel="stylesheet";c.href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css";document.head.appendChild(c);var s=document.createElement("script");s.src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js";s.onload=draw;document.body.appendChild(s);}
if("IntersectionObserver"in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){io.disconnect();load()}},{rootMargin:"300px"});io.observe(el)}else load();})();''' % json.dumps([[z[2], z[3], z[4], f'/zone/{z[0]}/'] for z in ZONES], ensure_ascii=False)

TABS_JS = r'''document.querySelectorAll(".case-tabs button").forEach(function(b){b.addEventListener("click",function(){var v=b.getAttribute("data-case");document.querySelectorAll(".case-tabs button").forEach(function(x){x.setAttribute("aria-selected",x===b)});document.querySelectorAll("[data-show]").forEach(function(e){e.hidden=e.getAttribute("data-show")!==v})})});'''

EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u2604\u2606-\u2712\u2715-\u27BF\uFE0F]+ ?')

def deslop(body):
    # icone emoji delle card -> numeri di fermata; le altre emoji spariscono
    n = iter(range(1, 100))
    body = re.sub(r'<div class="ico">[^<]*</div>', lambda m: f'<div class="ico" aria-hidden="true">{next(n):02d}</div>', body)
    return EMOJI.sub('', body)

def page(path, title, desc, body, ld_items=(), scripts=(), og_image='/img/vito-hero-1200.webp', robots=None):
    url = SITE + path
    nav = ''.join(f'<a href="{u}"' + (' aria-current="page"' if path.startswith(u) else '') + f'>{n}</a>' for n, u in NAV)
    graph = {"@context": "https://schema.org", "@graph": [ORG] + list(ld_items)}
    js = ''.join(f'<script>{s}</script>' for s in scripts)
    body = deslop(body)
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{f'<meta name="robots" content="{robots}">' if robots else ''}
<meta property="og:type" content="website"><meta property="og:locale" content="it_IT"><meta property="og:site_name" content="GAB Gestione Affitti Brevi">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ff0088">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/archivo-cond-800.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
{ld(graph)}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="/" aria-label="GAB, torna alla home"><span></span><b>GAB</b><span></span></a>
<input type="checkbox" id="mt" class="mt" aria-label="Apri il menu">
<nav class="nav" aria-label="Principale">{nav}</nav>
<a class="tel" href="tel:{TEL}">{TEL_H}</a>
<label for="mt" class="burger" aria-hidden="true"><i></i><i></i><i></i><span>Menu</span></label>
</div></header>
<main>
{body}
</main>
<footer><div class="wrap cols">
<div><a class="logo" href="/" aria-label="GAB"><span></span><b>GAB</b><span></span></a>
<p style="margin-top:14px">GAB Gestione Affitti Brevi<br>Boutique agency di Vito Semeraro<br>Milano, da Porta Venezia a Bicocca<br><a href="tel:{TEL}">{TEL_H}</a><br><a href="mailto:{MAIL}">{MAIL}</a></p></div>
<div><h2>Servizi</h2><ul><li><a href="/servizi/gestione-completa/">Gestione completa</a></li><li><a href="/servizi/medio-termine/">Affitti a medio termine</a></li><li><a href="/property-manager-milano/">Property manager Milano</a></li><li><a href="/gestione-airbnb-milano/">Gestione Airbnb Milano</a></li><li><a href="/servizi/consulenza-home-staging/">Home staging con AI</a></li><li><a href="/servizi/marketing-affitti-brevi/">Marketing e prenotazioni dirette</a></li><li><a href="/prezzi/">Prezzi</a></li></ul></div>
<div><h2>Zone</h2><ul>{''.join(f'<li><a href="/zone/{z[0]}/">{z[2]}</a></li>' for z in ZONES)}</ul></div>
<div><h2>Guide</h2><ul><li><a href="/guide/cedolare-secca-affitti-brevi/">Cedolare secca 2026</a></li><li><a href="/guide/codice-cin-affitti-brevi/">Codice CIN</a></li><li><a href="/guide/affitto-breve-o-medio-termine/">Breve o medio termine?</a></li><li><a href="/calcola-rendita/">Calcola la rendita</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/privacy/#cookie" data-ck>Preferenze cookie</a></li></ul></div>
</div><div class="wrap" style="margin-top:30px;font-size:.8rem;opacity:.7">© {date.today().year} GAB Gestione Affitti Brevi · Recensioni da Airbnb, pubblicate dagli ospiti</div></footer>
{CK_HTML}
<div class="mobilebar"><a class="btn btn-ghost" href="tel:{TEL}">Chiama</a><a class="btn btn-wa" href="{WA}">WhatsApp</a></div>
{js}<script>{CK_JS}</script>{CFWA}
</body>
</html>'''

def calc_form(sel_zone=None, h='h2'):
    opts = ''.join(f'<option value="{z[0]}"' + (' selected' if z[0] == sel_zone else '') + f'>{z[2]}</option>' for z in ZONES)
    return f'''<form class="card" id="calcola" data-calc>
<{h} style="font-size:1.25rem">Quanto rende il tuo appartamento?</{h}>
<p class="small">Stima gratuita in 10 secondi, affitto breve o medio periodo.</p>
<label for="zona">Zona</label><select id="zona" name="zona">{opts}</select>
<label for="tipo">Tipologia</label><select id="tipo" name="tipo"><option value="mono">Monolocale</option><option value="bilo" selected>Bilocale</option><option value="trilo">Trilocale</option></select>
<fieldset class="seg"><legend>Formula</legend>
<label><input type="radio" name="formula" value="breve" checked><span>Affitto breve</span></label>
<label><input type="radio" name="formula" value="medio"><span>Medio periodo (30+ notti)</span></label></fieldset>
<fieldset class="seg"><legend>Stato della casa</legend>
<label><input type="radio" name="stato" value="pronta" checked><span>Pronta da affittare</span></label>
<label><input type="radio" name="stato" value="rinnovo"><span>Da ristrutturare o rinnovare</span></label></fieldset>
<div class="budget" hidden><label for="budget">Budget per il restyle</label><select id="budget" name="budget"><option value="0-5000">Fino a 5.000 €</option><option value="5000-15000" selected>Da 5.000 a 15.000 €</option><option value="15000-30000">Da 15.000 a 30.000 €</option><option value="30000-0">Oltre 30.000 €</option></select></div>
<button class="btn btn-primary" style="width:100%;margin-top:18px">Calcola la stima</button>
<div class="result" aria-live="polite">Netto stimato al mese per te<strong>–</strong><span class="cmp small"></span><span class="roi small"></span><a href="/contatti/?fonte=calcolatore">Ricevi l'analisi dettagliata gratuita →</a></div>
<p class="small" style="margin:10px 0 0">Stima indicativa, dopo commissioni, pulizie e tasse. La analizziamo insieme in consulenza.</p>
</form>'''

def contact_band(zone_text=''):
    return f'''<section class="section" style="padding-top:0"><div class="wrap"><div class="band">
<div><h2>Parliamo del tuo appartamento</h2>
<p>Consulenza gratuita di 30 minuti, senza impegno. Ti rispondo personalmente entro 24 ore lavorative.</p>
<div class="signed">{picture('vito-avatar', [160], 'Vito Semeraro', '56px', cls='')}<div><strong>Vito Semeraro</strong><small style="color:#fff">Fondatore di GAB</small></div></div>
<p style="margin-top:18px"><a class="btn" style="background:#fff;color:var(--brand-dark)" href="{CAL}" rel="noopener">Prenota su Calendly</a></p></div>
<form class="card" action="/contatti.php" method="post">
<input class="hp" name="sito" tabindex="-1" autocomplete="off" aria-hidden="true">
<label for="f-nome">Nome</label><input id="f-nome" name="nome" required autocomplete="name">
<div class="row2"><div><label for="f-tel">Telefono</label><input id="f-tel" name="telefono" type="tel" required autocomplete="tel"></div>
<div><label for="f-zona">Zona immobile</label><input id="f-zona" name="zona" value="{esc(zone_text)}" placeholder="es. NoLo"></div></div>
<label for="f-msg">Messaggio (facoltativo)</label><input id="f-msg" name="messaggio" placeholder="es. bilocale, libero da gennaio">
<p class="form-err" hidden style="color:#b00020;font-weight:600;margin:12px 0 0">Controlla nome e telefono (almeno 6 cifre), oppure chiamami al 329 06 14 613.</p><script>if(/errore=1/.test(location.search))document.querySelectorAll('.form-err').forEach(function(e){{e.hidden=false}})</script>
<button class="btn btn-primary" style="width:100%;margin-top:16px">Richiamatemi</button>
<p class="small" style="margin:10px 0 0">Inviando accetti la <a href="/privacy/">privacy policy</a>.</p>
</form></div></div></section>'''

def linea():
    stops = ''.join(f'<li><a href="/zone/{z[0]}/">{esc(z[1])}' + (f'<small>{esc(z[2])}</small>' if z[2] != z[1] else '') + '</a></li>' for z in ZONES)
    return f'<nav class="linea" aria-label="Zone servite"><p class="cap"><b>M6</b>La linea GAB: {len(ZONES)} fermate, da Porta Venezia a Bicocca <a href="/linea-m6/">Cos’è la linea M6?</a></p><ol>{stops}</ol></nav>'

def reviews_section(title='Cosa dicono gli ospiti dei nostri appartamenti', n=6):
    cards = ''
    for name, when, where, text, tr in REVIEWS[:n]:
        cards += f'''<blockquote class="review" style="margin:0"><div class="stars" aria-label="5 stelle su 5">★★★★★</div><p>{esc(text)}</p><cite>{esc(name)} · {when}<small class="meta" style="display:block;font-weight:400">{esc(where)}{(" · tradotta dal " if tr == "cinese" else " · tradotta dall'") + tr if tr else ""}</small></cite></blockquote>'''
    rl = []  # niente markup Review: le recensioni su sé stessi non sono idonee ai rich result di Google
    _ = [{"@type": "Review", "author": {"@type": "Person", "name": r[0]}, "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": r[3], "itemReviewed": {"@id": SITE + "/#gab"}} for r in REVIEWS[:n]]
    return f'''<section class="section soft"><div class="wrap">
<div class="center"><span class="eyebrow">Recensioni Airbnb a 5 stelle</span><h2>{title}</h2>
<p class="lead">Voto medio 4,9 su 5 sugli appartamenti che gestiamo a Milano. Recensioni reali dei nostri ospiti su Airbnb.</p></div>
<div class="grid3" style="margin-top:30px">{cards}</div></div></section>''', rl

def faq_section(items, title='Domande frequenti'):
    h = ''.join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in items)
    ldf = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in items]}
    return f'<section class="section"><div class="wrap" style="max-width:820px"><h2 class="center">{title}</h2>{h}</div></section>', ldf

CASE = '''<section class="section soft"><div class="wrap">
<span class="eyebrow">I nostri numeri</span>
<h2>Affitto breve o medio periodo? Ecco quanto resta davvero a te</h2>
<p class="lead">Esempio dal nostro report: appartamento a 70 € a notte per 30 notti, al netto delle utenze, con le nostre commissioni incluse.</p>
<div class="case-tabs" role="tablist"><button role="tab" aria-selected="true" data-case="breve">Affitto breve</button><button role="tab" aria-selected="false" data-case="medio">Medio periodo</button></div>
<div class="case" style="margin-top:16px">
<div class="before" style="background:#fff"><span class="small">Incasso lordo del mese</span><span class="big">2.100 €</span>
<ul class="costs" data-show="breve"><li><span>Commissioni portali (OTA)</span><span>−315 €</span></li><li><span>Commissione GAB 15%</span><span>−315 €</span></li><li><span>Maggiore cedolare</span><span>−105 €</span></li><li><span>Usura e manutenzione</span><span>−105 €</span></li></ul>
<ul class="costs" data-show="medio" hidden><li><span>Sconto mensile all'ospite (15%)</span><span>−315 €</span></li><li><span>Commissione GAB 10%</span><span>−179 €</span></li><li><span>Commissioni portali</span><span>0 € con booking diretto</span></li></ul></div>
<div class="after"><span class="small">Netto per te</span>
<span class="big" data-show="breve">1.260 €/mese</span><span class="big" data-show="medio" hidden>1.606 €/mese</span>
<p data-show="breve">Massima flessibilità: usi la casa quando vuoi e approfitti dei picchi di Fashion Week, Salone del Mobile e fiere.</p>
<p data-show="medio" hidden><strong>+346 € al mese</strong> rispetto al breve: occupazione al 95%, meno usura, un solo ospite da gestire. Ideale per trasfertisti e studenti.</p></div></div>
<p class="small" style="margin-top:12px">Spesso conviene alternare le due formule durante l'anno: la scegliamo insieme in base alla tua casa. <a href="/guide/affitto-breve-o-medio-termine/">Leggi il confronto completo</a>.</p>
</div></section>'''

def write(path, content):
    fp = os.path.join(DIST, path.strip('/'), 'index.html') if path.endswith('/') else os.path.join(DIST, path.strip('/'))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(content)

PAGES = []
def add(path, *a, priority='0.7', **k):
    PAGES.append((path, priority)); write(path, page(path, *a, **k))

def build():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    # immagini
    imgsrc = os.path.join(HERE, '..', 'foto2')
    shutil.copytree(os.path.join(HERE, 'fonts'), os.path.join(DIST, 'fonts'))
    os.makedirs(os.path.join(DIST, 'img'))
    from PIL import Image
    for f in os.listdir(imgsrc):
        if f.endswith('.webp'):
            shutil.copy(os.path.join(imgsrc, f), os.path.join(DIST, 'img', f))
            IMG_DIMS[f.rsplit('.', 1)[0]] = Image.open(os.path.join(imgsrc, f)).size

    # ---------------- HOME ----------------
    rev_html, rev_ld = reviews_section()
    faq_html, faq_ld = faq_section([
        ('Quanto costa la gestione degli affitti brevi a Milano?', 'Il 15% sugli incassi per l\'affitto breve e il 10% per il medio termine. Nessun costo fisso: guadagniamo solo se guadagni tu. <a href="/prezzi/">Vedi cosa è incluso</a>.'),
        ('Posso disdire quando voglio?', 'Sì, con 30 giorni di preavviso. Nessun vincolo pluriennale.'),
        ('Meglio affitto breve o medio termine?', 'Dipende da casa, zona e da quanto vuoi usarla. Nel nostro esempio il medio termine rende circa 350 € in più al mese, ma l\'affitto breve è più flessibile. <a href="/guide/affitto-breve-o-medio-termine/">Ecco il confronto</a>.'),
        ('Serve il codice CIN per affittare su Airbnb?', 'Sì, è obbligatorio per tutti gli affitti brevi e va esposto negli annunci. Lo richiediamo noi per te. <a href="/guide/codice-cin-affitti-brevi/">Guida al CIN</a>.'),
        ('In quali zone di Milano lavorate?', 'Porta Venezia, Stazione Centrale, Loreto, NoLo, Pasteur, viale Monza, Turro, Gorla, Precotto, Greco e Bicocca. Ci concentriamo qui per essere sempre a pochi minuti dai nostri appartamenti.'),
    ])
    zl = ''.join(f'<a href="/zone/{z[0]}/">{z[2]}</a>' for z in ZONES)
    body = f'''<section class="hero"><div class="wrap grid"><div>
<span class="eyebrow">Porta Venezia · Centrale · NoLo · viale Monza · Bicocca</span>
<h1>Gestione affitti brevi a Milano, da Porta Venezia a Bicocca. <em>Più rendita, zero pensieri.</em></h1>
<p class="lead">Siamo una boutique agency: pochi appartamenti selezionati, seguiti personalmente. Pensiamo a tutto noi, da annuncio e prezzi a ospiti, pulizie e burocrazia. Tu ricevi l'incasso ogni mese e un report chiaro.</p>
<div class="ctas"><a class="btn btn-primary" href="#calcola">Calcola quanto rende</a><a class="btn btn-wa" href="{WA}?text=Ciao%20GAB%2C%20vorrei%20info%20sulla%20gestione%20del%20mio%20appartamento">WhatsApp</a></div>
<ul class="checks"><li>Un referente diretto, non un call center</li><li>Affitto breve o medio termine: scegliamo la formula che rende di più</li><li>Nessun vincolo: disdici con 30 giorni di preavviso</li></ul>
</div>{calc_form()}</div>{linea()}</section>
<section class="section" style="padding:56px 0"><div class="wrap proof">
<div><strong>9</strong><span>appartamenti seguiti uno per uno</span></div>
<div><strong>4,9★</strong><span>voto medio ospiti su Airbnb</span></div>
<div><strong>95%</strong><span>occupazione nel medio termine</span></div>
<div><strong style="font-size:1.2rem;padding-top:10px">Airbnb · Booking · Vrbo</strong><span>più booking diretto</span></div>
</div></section>
<section class="section"><div class="wrap split">
<div class="photo">{picture('vito-hero', [1200, 700], 'Vito Semeraro, fondatore di GAB', '(max-width:900px) 100vw, 560px')}</div>
<div><span class="eyebrow">Chi c'è dietro GAB</span><h2>Ciao, sono Vito. Gestisco case come se fossero mie</h2>
<p>Sono host su Airbnb da oltre 10 anni e vivo a Milano. Ho iniziato con i miei appartamenti tra Turro e Precotto, oggi seguo 9 case di proprietari che vogliono rendere di più senza perderci tempo.</p>
<p>Lavoro con pochi immobili per scelta: così rispondo io agli ospiti, faccio io i sopralluoghi e conosco ogni casa.</p>
<a href="/chi-siamo/">Scopri come lavoro →</a></div></div></section>
<section class="section soft"><div class="wrap"><div class="center"><span class="eyebrow">Come funziona</span><h2>Dal sopralluogo al primo ospite in 3 passi</h2></div>
<div class="grid3" style="margin-top:36px">
<div class="step card"><div class="n">1</div><h3>Consulenza gratuita</h3><p>Analizziamo zona, concorrenza e potenziale della tua casa e scegliamo insieme: affitto breve, medio termine o un mix.</p></div>
<div class="step card"><div class="n">2</div><h3>Prepariamo la casa</h3><p>Home staging, foto, codice CIN, annunci ottimizzati sui portali e sul nostro sito di booking diretto.</p></div>
<div class="step card"><div class="n">3</div><h3>Gestiamo tutto</h3><p>Prezzi dinamici, ospiti, check-in, pulizie e manutenzioni. Tu ricevi report e incassi ogni mese.</p></div>
</div></div></section>
<section class="section"><div class="wrap"><span class="eyebrow">Servizi</span><h2>Scegli quanto vuoi delegare</h2>
<div class="grid4 cards-link" style="margin-top:28px">
<a class="card service" href="/servizi/gestione-completa/"><div class="ico">🔑</div><h3>Gestione completa</h3><p>Ci occupiamo di tutto, dall'annuncio alle pulizie.</p><span>Scopri →</span></a>
<a class="card service" href="/servizi/medio-termine/"><div class="ico">📅</div><h3>Medio termine</h3><p>Soggiorni da 1 a 18 mesi per trasfertisti e studenti.</p><span>Scopri →</span></a>
<a class="card service" href="/servizi/consulenza-avvio/"><div class="ico">🧭</div><h3>Consulenza avvio</h3><p>Il modello GAB: 3 sessioni per partire da solo, bene.</p><span>Scopri →</span></a>
<a class="card service" href="/servizi/pratiche-cin-burocrazia/"><div class="ico">📄</div><h3>Pratiche e CIN</h3><p>CIN, Alloggiati Web, imposta di soggiorno, cedolare.</p><span>Scopri →</span></a>
</div></div></section>
{CASE}
<section class="section"><div class="wrap zones"><div>
<span class="eyebrow">Zone servite</span><h2>Lavoriamo dove viviamo: l'asse da Porta Venezia a Bicocca</h2>
<p class="lead">Lungo la M1 e viale Monza: sopralluoghi veloci, check-in di persona e interventi in giornata.</p>
<div class="zone-list">{zl}</div></div>
<div id="zonemap" class="map" role="region" aria-label="Mappa delle zone servite"><p class="map-fallback">Mappa delle zone servite lungo la M1: {", ".join(z[2] for z in ZONES)}.</p></div>
</div></section>
<section class="section soft"><div class="wrap grid3">
<div style="grid-column:span 2"><span class="eyebrow">Prezzi trasparenti</span><h2>Paghi solo quando guadagni</h2>
<p class="lead">Una percentuale sugli incassi, nessun costo fisso, disdetta con 30 giorni di preavviso. Pulizie e biancheria sono pagate dall'ospite.</p><a href="/prezzi/">Vedi cosa è incluso →</a></div>
<div class="price"><span class="small">Affitto breve</span><div class="pct">15%</div><p class="small" style="margin:0 0 10px">Medio termine: <strong>10%</strong></p><a class="btn btn-primary" href="/contatti/">Richiedi la proposta</a></div>
</div></section>
{rev_html}
{faq_html}
{contact_band()}'''
    add('/', 'Gestione affitti brevi Milano: Porta Venezia, NoLo, Bicocca',
        'Boutique agency di affitti brevi e medio termine a Milano, da Porta Venezia a Bicocca. Commissione 15%, voto ospiti 4,9. Calcola gratis la rendita.',
        body, ld_items=[faq_ld, {"@type": "WebSite", "@id": SITE + "/#web", "url": SITE + "/", "name": "GAB Gestione Affitti Brevi", "inLanguage": "it-IT"}] + rev_ld,
        scripts=[CALC_JS, TABS_JS, MAP_JS], priority='1.0')

    build_services(); build_zones(); build_misc(); build_guides()
    build_seo_files()


def simple_page(path, crumbs, eyebrow, h1, lead, inner, title, desc, faqs=None, extra_ld=(), scripts=(), band=True, priority='0.7', zone_text=''):
    faq_html, faq_ld = faq_section(faqs) if faqs else ('', None)
    body = f'''<section class="pagehero"><div class="wrap">{crumbs_html(crumbs)}<span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p class="lead">{lead}</p></div></section>
{inner}
{faq_html}
{contact_band(zone_text) if band else ''}'''
    items = [crumbs_ld(crumbs)] + ([faq_ld] if faq_ld else []) + list(extra_ld)
    add(path, title, desc, body, ld_items=items, scripts=scripts, priority=priority)

def service_ld(name, desc, path):
    return {"@type": "Service", "name": name, "description": desc, "serviceType": "Property management", "url": SITE + path,
            "provider": {"@id": SITE + "/#gab"}, "areaServed": {"@type": "City", "name": "Milano"}}

def build_services():
    H = ('Home', '/'); S = ('Servizi', '/servizi/')
    cards = [
        ('/servizi/gestione-completa/', '🔑', 'Gestione completa', 'Annunci, prezzi dinamici, ospiti, check-in, pulizie, manutenzioni e report mensile.'),
        ('/servizi/medio-termine/', '📅', 'Affitti a medio termine', 'Contratti transitori da 1 a 18 mesi per trasfertisti, studenti e famiglie in cura.'),
        ('/servizi/consulenza-avvio/', '🧭', 'Consulenza avvio', 'Il modello GAB: 3 sessioni da un\'ora per avviare la tua casa vacanza da solo.'),
        ('/servizi/home-staging-foto/', '📸', 'Home staging e foto', 'Arredo leggero, foto e testi per annunci che prenotano di più.'),
        ('/servizi/consulenza-home-staging/', '✨', 'Consulenza home staging con AI', 'Il restyle della casa studiato sul tuo budget, con anteprima AI e calcolo del ROI.'),
        ('/servizi/pratiche-cin-burocrazia/', '📄', 'Pratiche e CIN', 'Codice CIN, Alloggiati Web, imposta di soggiorno e dati ISTAT.'),
        ('/servizi/booking-diretto/', '🌐', 'Sito per prenotazioni dirette', 'Un sito per la tua casa per ricevere prenotazioni senza commissioni dei portali.'),
        ('/servizi/marketing-affitti-brevi/', '📣', 'Marketing per affitti brevi', 'SEO, scheda Google, social e campagne per aumentare le prenotazioni dirette.'),
    ]
    inner = '<section class="section" style="padding-top:20px"><div class="wrap grid3 cards-link">' + ''.join(
        f'<a class="card service" href="{u}"><div class="ico">{i}</div><h2 style="font-size:1.25rem">{t}</h2><p>{d}</p><span>Scopri →</span></a>' for u, i, t, d in cards) + '</div></section>'
    simple_page('/servizi/', [H, ('Servizi', None)], 'Servizi', 'Servizi di gestione affitti brevi e medio termine a Milano',
                'Puoi affidarci tutto o solo una parte. In ogni caso parli sempre con me, Vito, e con il mio piccolo team.',
                inner, 'Servizi gestione affitti brevi Milano | GAB',
                'Gestione completa, affitti a medio termine, consulenza, home staging, pratiche CIN e booking diretto per appartamenti a Milano nord-est.', priority='0.9')

    def svc(slug, name, h1, lead, sections, faqs, title, desc):
        inner = f'<section class="section" style="padding-top:10px"><div class="wrap prose">{sections}</div></section>'
        simple_page(f'/servizi/{slug}/', [H, S, (name, None)], 'Servizi', h1, lead, inner, title, desc, faqs, [service_ld(name, desc, f'/servizi/{slug}/')])

    svc('gestione-completa', 'Gestione completa', 'Gestione completa del tuo affitto breve a Milano',
        'Tu metti la casa, noi tutto il resto. Ti resta solo da controllare il report e l\'incasso di fine mese.',
        f'''<h2>Cosa facciamo per te</h2>
<ul class="incl"><li>Sopralluogo e stima di rendita, affitto breve e medio termine a confronto</li><li>Annuncio su Airbnb, Booking e Vrbo: testi in italiano e inglese, foto, regole della casa</li><li>Prezzi dinamici giorno per giorno, con i picchi di Fashion Week, Salone del Mobile e fiere</li><li>Messaggi con gli ospiti 7 giorni su 7, in 5 lingue</li><li>Check-in di persona o self check-in con serratura smart</li><li>Pulizie, biancheria e piccole manutenzioni con fornitori di zona</li><li>Codice CIN, Alloggiati Web, imposta di soggiorno e dati ISTAT</li><li>Report mensile con prenotazioni, incassi e costi</li></ul>
<h2>Quanto costa</h2><p>Il <strong>15% sugli incassi</strong> dell'affitto breve, senza costi fissi. Le pulizie le paga l'ospite. Puoi disdire con 30 giorni di preavviso. <a href="/prezzi/">Tutti i dettagli sui prezzi</a>.</p>
<h2>Perché una boutique agency</h2><p>Seguiamo 9 appartamenti, non 300. Questo significa che conosco ogni casa, rispondo io agli ospiti e posso intervenire in giornata, perché lavoriamo solo tra Porta Venezia e Bicocca. Il risultato si vede nelle recensioni: voto medio 4,9 su Airbnb.</p>
<div class="note">Vuoi sapere quanto può rendere la tua casa? <a href="/calcola-rendita/">Usa il calcolatore</a> o <a href="{CAL}">prenota una call di 30 minuti</a>.</div>''',
        [('Devo essere presente al check-in?', 'No, ce ne occupiamo noi, di persona o con self check-in.'), ('Chi paga le pulizie?', 'L\'ospite, con la tariffa di pulizia indicata nell\'annuncio.'), ('Ricevo io i pagamenti?', 'Sì, gli incassi arrivano sul tuo conto. Ogni mese ti mandiamo il report con incassi, costi e la nostra commissione.')],
        'Gestione completa affitti brevi Milano | GAB', 'Gestione chiavi in mano del tuo affitto breve a Milano: annunci, prezzi dinamici, ospiti, pulizie, CIN e report. Commissione 15%, disdetta con 30 giorni.')

    svc('medio-termine', 'Affitti a medio termine', 'Affitti a medio termine a Milano: più stabilità, meno pensieri',
        'Soggiorni da 1 a 18 mesi per professionisti in trasferta, studenti e famiglie. Nella nostra esperienza l\'occupazione arriva al 95%.',
        f'''<h2>Per chi è adatto</h2><p>Il medio termine conviene se vuoi un reddito stabile con poca usura della casa, o se la tua zona è più richiesta da chi lavora e studia che dai turisti: è il caso di Precotto, Greco e Bicocca, vicine all'università e alle sedi di molte aziende.</p>
<h2>Cosa facciamo</h2><ul class="incl"><li>Selezione e verifica degli inquilini</li><li>Contratto transitorio conforme, registrazione e cedolare secca</li><li>Annunci su portali dedicati e sul nostro booking diretto</li><li>Check-in, inventario e check-out con verifica della casa</li><li>Assistenza agli inquilini e manutenzioni</li></ul>
<h2>Quanto rende</h2><p>Nel nostro esempio con una tariffa di 70 € a notte, il medio termine lascia al proprietario circa <strong>1.606 € al mese contro 1.260 €</strong> dell'affitto breve, già al netto della nostra commissione. La commissione è il <strong>10%</strong>.</p>
<p><a href="/guide/affitto-breve-o-medio-termine/">Leggi il confronto completo tra affitto breve e medio termine</a>.</p>''',
        [('Che contratto si usa?', 'Per soggiorni oltre 30 giorni si usa di solito il contratto transitorio, da 1 a 18 mesi, con esigenza documentata dell\'inquilino.'), ('Posso alternare breve e medio termine?', 'Sì: molti nostri proprietari fanno medio termine in inverno e affitto breve nei mesi di eventi e fiere.')],
        'Affitti a medio termine Milano: gestione e contratti | GAB', 'Gestione affitti a medio termine a Milano (1-18 mesi) per trasfertisti e studenti: occupazione fino al 95%, commissione 10%, contratti e inquilini verificati.')

    svc('consulenza-avvio', 'Consulenza avvio', 'Il modello GAB: avvia da solo il tuo affitto breve, nel modo giusto',
        'Tre sessioni da un\'ora, con aggiornamenti ogni due settimane, per chi vuole gestire la propria casa in autonomia senza errori.',
        '''<h2>Come funziona</h2><ol><li><strong>Analisi</strong>: potenziale della casa, concorrenza in zona, breve o medio termine.</li><li><strong>Preparazione</strong>: arredo, foto, annuncio, pratiche CIN e Alloggiati Web.</li><li><strong>Gestione</strong>: prezzi, messaggi automatici, pulizie, strumenti per lavorare da telefono.</li></ol>
<p>Tra una sessione e l'altra ti seguo ogni due settimane per controllare i risultati. Se poi preferisci delegare, puoi passare alla gestione completa.</p>''',
        [('Quanto costa la consulenza?', 'La prima call di 30 minuti è gratuita: ti faccio una proposta su misura in base a cosa ti serve.')],
        'Consulenza per avviare un affitto breve a Milano | GAB', 'Percorso di 3 sessioni per avviare da solo il tuo affitto breve o casa vacanza a Milano: annuncio, prezzi, CIN e strumenti. Prima call gratuita.')

    svc('home-staging-foto', 'Home staging e foto', 'Home staging e foto per affitti brevi a Milano',
        'Le foto sono la prima cosa che l\'ospite guarda. Un annuncio curato prenota di più e a tariffe più alte.',
        '''<h2>Cosa comprende</h2><ul class="incl"><li>Lista degli acquisti utili: biancheria, cucina, dettagli che fanno la differenza nelle recensioni</li><li>Piccolo allestimento per rendere la casa luminosa e accogliente</li><li>Servizio fotografico professionale</li><li>Testi dell'annuncio in italiano e inglese, ottimizzati per la ricerca su Airbnb</li></ul>
<p>Gli ospiti notano tutto: nelle recensioni dei nostri appartamenti tornano parole come <em>pulito</em>, <em>luminoso</em>, <em>accogliente</em>. È lì che si costruisce il voto medio di 4,9.</p>
<h2>Prima dei lavori, l'anteprima con l'AI</h2><p>Prima di comprare un mobile ti mostriamo come può diventare la casa con <a href="https://home-staged.ai/">home-staged.ai</a>, la piattaforma di home staging virtuale ideata da Vito: da una foto della stanza ottieni la versione arredata, gli interventi consigliati e i costi reali a Milano. Così decidi con le immagini davanti, non a occhio. <a href="/servizi/consulenza-home-staging/">Scopri la consulenza home staging con AI</a>.</p>''',
        None, 'Home staging e foto per Airbnb a Milano | GAB', 'Home staging, foto professionali e testi per annunci Airbnb e Booking a Milano: più prenotazioni e tariffe più alte per il tuo appartamento.')

    svc('consulenza-home-staging', 'Consulenza home staging con AI', 'Consulenza home staging con AI a Milano: il restyle giusto per il tuo budget',
        'Dimmi quanto vuoi investire: con la tecnologia di home-staged.ai progettiamo il restyle del tuo appartamento, ti mostriamo il risultato prima dei lavori e calcoliamo quanto rende.',
        f'''<h2>Come funziona</h2>
<ul class="incl"><li><strong>Partiamo dal budget</strong>: mi dici quanto vuoi spendere, anche poco, e su quello costruiamo il progetto</li><li><strong>Sopralluogo e foto</strong> di ogni stanza</li><li><strong>Anteprima con l'AI</strong>: con <a href="https://home-staged.ai/">home-staged.ai</a> vedi le stanze arredate prima di comprare qualsiasi cosa, in più varianti</li><li><strong>Lista degli interventi con i costi reali a Milano</strong>: arredi, tinteggiatura, luci, tessili, piccoli lavori</li><li><strong>Calcolo del ROI</strong>: quanto può salire la tariffa a notte e l'occupazione, e in quanti mesi rientri dell'investimento</li><li><strong>Se vuoi, ci pensiamo noi</strong>: acquisti, montaggio, foto professionali e annuncio online</li></ul>
<h2>Come calcoliamo il ritorno</h2>
<p>Confrontiamo la tua casa con annunci simili nella stessa zona, prima e dopo un restyle dello stesso livello. Dalla differenza di tariffa e di occupazione ricaviamo il maggiore incasso netto all'anno, dopo commissioni e tasse. Il ROI è il rapporto tra questo incasso in più e il costo del restyle; il tempo di rientro è il numero di mesi necessario per ripagarlo.</p>
<p>Così scegli tra due o tre livelli di intervento guardando i numeri, non solo le foto.</p>
<h2>Per chi è</h2>
<p>Per chi sta per mettere a reddito una casa vuota o datata, per chi ha un annuncio che prenota poco e per chi vuole passare dal medio termine all'affitto breve. Funziona anche se poi la casa la gestisci da solo.</p>
<div class="note">Vuoi vedere subito il potenziale di una stanza? <a href="{CAL}">Prenota una call di 30 minuti</a> e mandami un paio di foto.</div>''',
        [('Cos\'è home-staged.ai?', 'È la piattaforma di home staging virtuale con AI ideata da Vito: da una foto della stanza genera la versione arredata, gli interventi consigliati e i costi reali per città.'),
         ('Le immagini AI corrispondono al risultato finale?', 'Sono un\'anteprima molto fedele dello stile e degli spazi. La lista degli interventi indica gli arredi e i lavori reali con cui ottenerla.'),
         ('Devo affidarvi anche la gestione?', 'No. Puoi chiedere solo la consulenza e poi decidere se gestire la casa da solo o con noi.')],
        'Consulenza home staging con AI a Milano | GAB', 'Restyle del tuo appartamento studiato sul tuo budget con home-staged.ai: anteprima AI delle stanze, costi reali a Milano e calcolo del ROI per affitti brevi.')

    svc('pratiche-cin-burocrazia', 'Pratiche e CIN', 'Pratiche per affitti brevi a Milano: CIN, Alloggiati Web, imposta di soggiorno',
        'La burocrazia degli affitti brevi è cresciuta molto. Ce ne occupiamo noi, così sei sempre in regola.',
        '''<h2>Gli adempimenti che gestiamo</h2><ul class="incl"><li><strong>Codice CIN</strong>: richiesta sulla Banca Dati nazionale e esposizione negli annunci e all'ingresso</li><li><strong>Alloggiati Web</strong>: comunicazione degli ospiti alla Questura entro 24 ore</li><li><strong>Imposta di soggiorno</strong> del Comune di Milano: riscossione, versamento e dichiarazione</li><li><strong>Dati ISTAT</strong> sui flussi turistici</li><li><strong>Sicurezza</strong>: verifica di rilevatori di gas e monossido ed estintori</li><li><strong>Cedolare secca</strong>: dati per la tua dichiarazione o per il tuo commercialista</li></ul>
<p>Approfondisci nelle nostre guide: <a href="/guide/codice-cin-affitti-brevi/">codice CIN</a> e <a href="/guide/cedolare-secca-affitti-brevi/">cedolare secca 2026</a>.</p>''',
        None, 'Pratiche affitti brevi Milano: CIN e Alloggiati Web | GAB', 'Gestiamo CIN, Alloggiati Web, imposta di soggiorno del Comune di Milano e dati ISTAT per il tuo affitto breve. Sempre in regola, senza pensieri.')

    RENTLY_VIDEO = '<figure class="media"><video controls preload="none" playsinline width="640" height="360" poster="/media/rently-poster.webp" aria-label="Video Rently: il potere delle prenotazioni dirette"><source src="/media/rently-video.mp4" type="video/mp4"></video><figcaption>Rently in 15 secondi: meno commissioni, più prenotazioni dirette.</figcaption></figure>'
    video_ld = {"@type": "VideoObject", "name": "Rently: il potere delle prenotazioni dirette", "description": "Come creare un canale di prenotazioni dirette per la tua casa vacanza e smettere di pagare commissioni alte ai portali.",
                "thumbnailUrl": SITE + "/media/rently-poster.webp", "contentUrl": SITE + "/media/rently-video.mp4", "uploadDate": "2024-06-18", "duration": "PT15S", "inLanguage": "it-IT"}

    svc('booking-diretto', 'Sito per prenotazioni dirette', 'Sito web per casa vacanza e affitti brevi, con prenotazioni dirette',
        'Airbnb e Booking trattengono intorno al 15% su ogni prenotazione. Con un sito tuo gli ospiti che tornano, le aziende e chi ti trova su Google prenotano direttamente, senza commissioni.',
        f'''<figure class="media"><img src="/media/rently-siti-demo.webp" alt="Siti web per case vacanza realizzati con Rently, visti da smartphone" width="720" height="332" loading="lazy" decoding="async"><figcaption>Alcuni siti per case vacanza realizzati con Rently.</figcaption></figure>
<h2>Cosa comprende</h2>
<ul class="incl"><li><strong>Logo e immagine coordinata</strong> della tua casa, come un piccolo hotel</li><li><strong>Sito responsive</strong> per smartphone, tablet e computer, veloce e leggero</li><li><strong>Prenotatore</strong> con calendario sincronizzato con Airbnb e Booking, niente doppie prenotazioni</li><li><strong>Più lingue</strong>, con testi professionali scritti per gli ospiti stranieri</li><li><strong>SEO di base</strong> e scheda Google, per farti trovare da chi cerca casa nella tua zona</li><li><strong>Chat e recensioni</strong> in evidenza, per dare fiducia a chi prenota la prima volta</li><li><strong>Dominio e hosting</strong> inclusi</li></ul>
<h2>Perché conviene</h2>
<ul class="checks"><li>Zero commissioni dei portali sulle prenotazioni dirette</li><li>Pagamenti anticipati con le tue regole di caparra e cancellazione</li><li>Le recensioni e i contatti degli ospiti restano tuoi</li><li>Non dipendi dalle decisioni e dagli algoritmi dei portali</li></ul>
<p>Non devi lasciare Airbnb e Booking: il sito si <strong>affianca</strong> ai portali e cresce nel tempo. I portali portano i primi ospiti, il sito li fa tornare.</p>
<figure class="media"><img src="/media/rently-dispositivi.webp" alt="Sito di un trullo in affitto breve visto su computer, tablet e smartphone" width="720" height="304" loading="lazy" decoding="async"></figure>
<h2>Come lo realizziamo</h2>
<ol><li><strong>Questionario</strong>: raccogliamo foto, servizi, regole della casa e cosa rende unica la tua zona.</li><li><strong>Dominio</strong>: ne registriamo uno nuovo o trasferiamo il tuo.</li><li><strong>Anteprima</strong> del sito e fino a due giri di modifiche.</li><li><strong>Messa online</strong> e prenotatore pronto all'uso, con affiancamento.</li><li><strong>Promozione e monitoraggio</strong>: ti diciamo come portare visite al sito e misuriamo i risultati.</li></ol>
<p>Il sito è realizzato con <strong>Rently</strong>, il servizio di siti per case vacanza ideato da Vito. Per far arrivare più ospiti al sito c'è il nostro <a href="/servizi/marketing-affitti-brevi/">marketing per affitti brevi</a>; se vuoi capire prima come funziona, leggi la <a href="/guide/prenotazioni-dirette-affitti-brevi/">guida alle prenotazioni dirette</a>.</p>
<div class="note">Vuoi vedere un sito per una casa come la tua? <a href="{CAL}">Prenota una call di 30 minuti</a>: ti mostro gli esempi e ti faccio un preventivo.</div>''',
        [('Devo togliere la casa da Airbnb e Booking?', 'No. Il sito si affianca ai portali con il calendario sincronizzato: le date prenotate da una parte si bloccano anche dall\'altra.'),
         ('Come arrivano gli ospiti sul sito?', 'All\'inizio soprattutto da chi ha già soggiornato, dalle aziende e dalla scheda Google. Poi dalla ricerca su Google, dai social e dalle campagne. Lo spieghiamo nella pagina sul marketing per affitti brevi.'),
         ('Le tasse cambiano con le prenotazioni dirette?', 'Valgono cedolare secca, imposta di soggiorno e Alloggiati Web come per le prenotazioni dai portali. Senza portale, però, nessuno trattiene la ritenuta del 21%: la cedolare la versi tu in dichiarazione.')],
        'Sito web per casa vacanza e affitti brevi con prenotazioni dirette | GAB', 'Sito web per la tua casa vacanza con prenotatore, calendario sincronizzato con Airbnb e Booking, più lingue e SEO: prenotazioni dirette senza commissioni.')

    inner_mk = f'''<section class="section" style="padding-top:10px"><div class="wrap prose">
{RENTLY_VIDEO}
<h2>Perché le prenotazioni dirette</h2>
<p>Gli host sono stretti tra portali che alzano le commissioni, ospiti sempre più esigenti e più burocrazia. Ogni prenotazione che arriva direttamente, invece che da un portale, lascia in tasca intorno al 15% in più: su un incasso di 2.000 € al mese sono circa 300 €.</p>
<h2>Cosa facciamo</h2>
<ul class="incl"><li><strong>Branding</strong>: nome, logo e immagine coordinata della tua casa</li><li><strong>Sito con prenotatore</strong>: il tuo canale diretto, sincronizzato con i portali. <a href="/servizi/booking-diretto/">Scopri il sito per prenotazioni dirette</a></li><li><strong>SEO</strong>: pagine e articoli per farti trovare su Google da chi cerca casa nella tua città</li><li><strong>Scheda Google</strong> curata, con foto, recensioni e link al sito</li><li><strong>Contenuti social</strong>: post, reel e storie che raccontano la casa e il quartiere</li><li><strong>Campagne a pagamento</strong> su Google, Facebook e Instagram, con budget sotto controllo</li><li><strong>Ospiti che tornano</strong>: messaggi e offerte dirette a chi ha già soggiornato</li></ul>
<h2>Quanto ci vuole</h2>
<table><tr><th>Canale</th><th>Primi risultati</th></tr><tr><td>Campagne su Google e social</td><td>2-3 mesi</td></tr><tr><td>SEO e ricerca su Google</td><td>circa 6 mesi</td></tr><tr><td>Ospiti che tornano e passaparola</td><td>dalla prima stagione</td></tr></table>
<h2>I numeri che misuriamo</h2>
<p>Lavoriamo con i dati, non a sensazione. Nella campagna di lancio di Rently, a novembre 2024, gli annunci hanno avuto un <strong>CTR del 2,2%</strong> e la pagina di atterraggio ha convertito il <strong>4% dei visitatori</strong>: in due settimane, con 224 € di budget, sono arrivate 8 richieste di sito. Per la tua casa misuriamo le stesse cose ogni mese: clic, costo per clic, richieste e prenotazioni.</p>
<figure class="media"><img src="/media/rently-logo.webp" alt="Logo Rently, sviluppa il tuo canale diretto" width="300" height="62" loading="lazy" decoding="async" style="max-width:240px"></figure>
<p>Il marketing è fatto con <strong>Rently</strong>, il servizio per case vacanza ideato da Vito che unisce sito, SEO, campagne e contenuti. Funziona anche se la casa la gestisci da solo.</p>
<div class="note">Vuoi capire quante prenotazioni dirette può portare la tua casa? <a href="{CAL}">Prenota una call di 30 minuti</a>.</div>
</div></section>'''
    mk_desc = 'Marketing per affitti brevi e case vacanza: sito con prenotatore, SEO, scheda Google, social e campagne per aumentare le prenotazioni dirette senza commissioni.'
    simple_page('/servizi/marketing-affitti-brevi/', [H, S, ('Marketing per affitti brevi', None)], 'Servizi', 'Marketing per affitti brevi: più prenotazioni dirette, meno commissioni',
                'Sito, Google, social e campagne per portare ospiti che prenotano direttamente da te. Senza rinunciare ad Airbnb e Booking.',
                inner_mk, 'Marketing per affitti brevi e case vacanza | GAB', mk_desc,
                [('Serve per forza un sito?', 'È il punto di arrivo di tutto il resto: Google, social e campagne portano visite, il sito le trasforma in prenotazioni senza commissioni.'),
                 ('Quanto devo spendere in campagne?', 'Dipende dalla stagione e dalla zona. Si parte con budget piccoli, si misura il costo per prenotazione e si aumenta solo se conviene.'),
                 ('Funziona anche fuori Milano?', 'Sì. La gestione la facciamo solo a Milano, ma sito e marketing li realizziamo per case vacanza in tutta Italia.')],
                [service_ld('Marketing per affitti brevi', mk_desc, '/servizi/marketing-affitti-brevi/'), video_ld], priority='0.8')

    # pagine keyword commerciali
    for path, name, h1, title, desc, angle in [
        ('/property-manager-milano/', 'Property manager Milano', 'Property manager a Milano per affitti brevi e medio termine',
         'Property manager Milano per affitti brevi | GAB', 'Cerchi un property manager a Milano? Boutique agency per appartamenti tra Porta Venezia e Bicocca: gestione completa, 15% di commissione, voto ospiti 4,9.',
         'Un property manager si occupa della tua casa come farebbe un albergatore: prezzi, ospiti, pulizie, manutenzioni e burocrazia. La differenza tra un buon gestore e uno qualsiasi si vede nelle recensioni e nel netto che ti resta a fine mese.'),
        ('/gestione-airbnb-milano/', 'Gestione Airbnb Milano', 'Gestione Airbnb a Milano: affidaci il tuo annuncio',
         'Gestione Airbnb Milano: co-host per il tuo annuncio | GAB', 'Gestione Airbnb a Milano nord-est: annuncio, prezzi dinamici, messaggi, check-in e pulizie. Host da oltre 10 anni, voto medio 4,9. Commissione 15%.',
         'Siamo host su Airbnb da oltre 10 anni. Possiamo prendere in mano il tuo annuncio come co-host, oppure crearne uno nuovo partendo da foto e testi, e portarlo anche su Booking e Vrbo.'),
    ]:
        rev_html, rev_ld = reviews_section('Le recensioni dei nostri ospiti', 3)
        inner = f'''<section class="section" style="padding-top:10px"><div class="wrap split"><div class="prose">
<p>{angle}</p>
<h2>Cosa ottieni</h2><ul class="incl"><li>Un referente unico: Vito, raggiungibile su WhatsApp</li><li>Prezzi aggiornati ogni giorno in base a eventi e domanda</li><li>Check-in, pulizie e manutenzioni con fornitori di zona</li><li>CIN, Alloggiati Web e imposta di soggiorno sempre in regola</li><li>Report mensile chiaro</li></ul>
<h2>Prezzi</h2><p><strong>15%</strong> sugli incassi per l'affitto breve, <strong>10%</strong> per il medio termine. Nessun costo fisso, disdetta con 30 giorni. <a href="/prezzi/">Dettagli</a>.</p>
<h2>Dove lavoriamo</h2><p>{', '.join(f'<a href="/zone/{z[0]}/">{z[2]}</a>' for z in ZONES)}.</p>
</div><div class="photo">{picture('vito-telefono', [640, 400], 'Vito Semeraro gestisce le prenotazioni dal telefono', '(max-width:900px) 100vw, 520px')}</div></div></section>{rev_html}'''
        simple_page(path, [H, (name, None)], name, h1, 'Boutique agency tra Porta Venezia, Centrale, NoLo, viale Monza, Precotto e Bicocca.', inner, title, desc,
                    extra_ld=[service_ld(name, desc, path)] + rev_ld, priority='0.9')

ZONE_TXT = {
 'porta-venezia': dict(
  h1='Gestione affitti brevi a Porta Venezia e Lima',
  lead='Tra corso Buenos Aires, i Giardini Montanelli e il Lazzaretto: una delle zone più richieste di Milano da turisti e viaggiatori d\'affari.',
  why=[('🛍️ Shopping e centro a piedi', 'Corso Buenos Aires è una delle vie dello shopping più lunghe d\'Europa e il Duomo è a 3 fermate di M1.'),
       ('🌳 Liberty e locali', 'Palazzi d\'epoca, i Giardini Montanelli, il Museo di Storia Naturale e la vita serale del Lazzaretto attirano coppie e weekend.'),
       ('🚇 M1 Porta Venezia e Lima', 'Il passante ferroviario a Porta Venezia collega direttamente con Rho Fiera e la Stazione Centrale è a pochi minuti.')],
  tip='Qui le tariffe sono tra le più alte della nostra area: l\'affitto breve rende al massimo nelle settimane di moda, design e fiere.',
  faq=[('Conviene l\'affitto breve a Porta Venezia?', 'Sì: domanda turistica tutto l\'anno e tariffe alte. Il medio termine resta un\'ottima alternativa nei mesi più tranquilli.'),
       ('Ci sono limiti agli affitti brevi a Milano?', 'Oggi no oltre agli obblighi nazionali (CIN, Alloggiati Web, imposta di soggiorno) e alle regole del condominio. Li verifichiamo insieme.')]),
 'stazione-centrale': dict(
  h1='Gestione affitti brevi in zona Stazione Centrale',
  lead='Treni, metro M2 e M3, bus per gli aeroporti: chi arriva a Milano cerca casa qui, anche solo per una o due notti.',
  why=[('✈️ Aeroporti e treni', 'Bus e Malpensa Express per gli aeroporti, Frecce e Italo per tutta Italia: perfetto per soggiorni brevi.'),
       ('💼 Business', 'Porta Nuova, Gioia e Repubblica sono a pochi minuti: tanti professionisti in trasferta di 2-5 notti.'),
       ('🔁 Alta rotazione', 'Molti check-in brevi: servono prezzi aggiornati ogni giorno e check-in senza intoppi, a ogni ora.')],
  tip='Con soggiorni così brevi il self check-in e una pulizia impeccabile fanno la differenza su recensioni e tariffe.',
  faq=[('Le notti brevi convengono?', 'Sì, se la tariffa include bene la pulizia e il check-in è automatizzato. Impostiamo soggiorni minimi diversi per giorni feriali e weekend.'),
       ('La zona è sicura per gli ospiti?', 'Scegliamo con cura le informazioni sul percorso da metro e stazione e le inseriamo nella guida della casa.')]),
 'loreto-nolo': dict(
  h1='Gestione affitti brevi a NoLo e Loreto',
  lead='Tra piazzale Loreto, via Padova e viale Monza: incrocio di M1 e M2, a 10 minuti a piedi dalla Stazione Centrale.',
  why=[('🚆 Vicino a Centrale', 'Loreto, Pasteur e Rovereto sono a una o due fermate da Centrale e dal centro.'),
       ('🎨 Quartiere di tendenza', 'Bistrot, locali e mercati di quartiere: NoLo piace a chi vuole vivere Milano come un milanese.'),
       ('💼 Soggiorni medi', 'Professionisti e studenti cercano soluzioni da 1 a 6 mesi a prezzi più bassi del centro.')],
  tip='NoLo funziona bene in entrambe le formule: affitto breve nei mesi di eventi, medio termine nel resto dell\'anno.',
  faq=[('Meglio affitto breve o medio termine a NoLo?', 'Vicino alle fermate M1 e M2 l\'affitto breve rende di più nei mesi di eventi; il medio termine riempie i periodi più tranquilli.'),
       ('Fate il check-in di persona?', 'Sì, siamo in zona. Offriamo anche il self check-in con serratura smart.')]),
 'viale-monza': dict(
  h1='Gestione affitti brevi in viale Monza, Turro e Gorla',
  lead='Lungo la M1 tra Rovereto, Turro e Gorla, a due passi dal Naviglio Martesana. È la zona dove abbiamo iniziato.',
  why=[('🏠 Il nostro primo appartamento', 'Il nostro monolocale sopra la metro Turro ha recensioni a 5 stelle dal 2023: gli ospiti amano la metro sotto casa e la zona tranquilla.'),
       ('🚴 Martesana', 'La pista ciclopedonale del Naviglio Martesana e i locali lungo l\'acqua sono un plus che citiamo in ogni annuncio.'),
       ('💶 Prezzi accessibili', 'Tariffe più basse del centro con il Duomo a 20 minuti di M1: ideale per famiglie e soggiorni più lunghi.')],
  tip='Qui il medio termine rende molto bene: domanda costante di trasfertisti e prezzi di acquisto ancora accessibili.',
  faq=[('Che risultati avete in zona Turro?', 'Il nostro monolocale sopra la metro Turro ha solo recensioni a 5 stelle su Airbnb. "Zona tranquilla vicinissima alla metro rossa" è il commento più frequente.'),
       ('Gestite anche case da ristrutturare?', 'Ti aiutiamo a capire quali lavori servono davvero e quali hanno un ritorno sulle tariffe.')]),
 'precotto-greco': dict(
  h1='Gestione affitti brevi a Precotto e Greco',
  lead='M1 Precotto e Villa San Giovanni, stazione di Greco Pirelli e tram: collegamenti ottimi a pochi minuti da Bicocca.',
  why=[('🏠 I nostri bilocali', 'Gestiamo appartamenti a 350 metri dalla M1 Precotto: occupazione al 71% tra aprile e luglio 2026 e voto 5 su 5 negli ultimi mesi.'),
       ('🎓 Bicocca e aziende', 'Università, uffici e sedi aziendali portano studenti e trasfertisti tutto l\'anno.'),
       ('🛒 Servizi sotto casa', 'Supermercati, panetterie e tram: gli ospiti lo scrivono spesso nelle recensioni.')],
  tip='A Precotto alterniamo affitto breve e medio termine: un bilocale con balcone è affittato a 1.400 € netti al mese.',
  faq=[('Quanto rende un bilocale a Precotto?', 'Dipende da formula e arredo. Uno dei nostri bilocali in medio termine rende 1.400 € netti al mese; in affitto breve l\'occupazione è arrivata al 71% in primavera.'),
       ('Lavorate anche a Villa San Giovanni?', 'Sì, è dentro la nostra area lungo la M1.')]),
 'bicocca': dict(
  h1='Gestione affitti brevi a Bicocca',
  lead='Università di Milano-Bicocca, Teatro degli Arcimboldi, Pirelli HangarBicocca e tanti uffici: una zona che vive tutto l\'anno.',
  why=[('🎓 Studenti e docenti', 'Visiting professor, dottorandi e famiglie degli studenti cercano soggiorni medi vicino all\'università.'),
       ('🎭 Eventi', 'Concerti e spettacoli agli Arcimboldi e mostre all\'HangarBicocca portano ospiti anche nei weekend.'),
       ('💼 Uffici', 'Le sedi aziendali della zona generano trasferte di settimane o mesi.')],
  tip='Bicocca è la zona ideale per il medio termine: con la M5 e la M1 vicine, le case si affittano in fretta.',
  faq=[('Conviene il medio termine a Bicocca?', 'Sì, la domanda di università e aziende è costante: nel medio termine puntiamo al 95% di occupazione.'),
       ('Gestite anche stanze singole?', 'Valutiamo caso per caso; di solito lavoriamo con appartamenti interi.')]),
}

def build_zones():
    H = ('Home', '/'); Z = ('Zone', '/zone/')
    cards = ''.join(f'<a class="card" href="/zone/{z[0]}/"><h2 style="font-size:1.2rem">{z[2]}</h2><p>{ZONE_TXT[z[0]]["lead"]}</p><span>Scopri la zona →</span></a>' for z in ZONES)
    inner = f'''<section class="section" style="padding-top:10px"><div class="wrap">
<div id="zonemap" class="map" role="region" aria-label="Mappa delle zone servite" style="margin-bottom:30px"><p class="map-fallback">Mappa delle zone servite lungo la M1.</p></div>
<div class="grid3 cards-link">{cards}</div></div></section>'''
    simple_page('/zone/', [H, ('Zone', None)], 'Zone servite', 'Le zone di Milano dove gestiamo affitti brevi',
                'Lavoriamo solo lungo l\'asse della M1 e di viale Monza, da Porta Venezia a Bicocca. Così siamo sempre a pochi minuti da ogni casa.',
                inner, 'Zone servite: Porta Venezia, Centrale, NoLo, Bicocca | GAB',
                'Gestione affitti brevi a Milano in Porta Venezia, Stazione Centrale, Loreto e NoLo, viale Monza, Turro, Gorla, Precotto, Greco e Bicocca.',
                scripts=[MAP_JS], priority='0.9')
    for i, z in enumerate(ZONES):
        t = ZONE_TXT[z[0]]
        why = ''.join(f'<div class="card"><h3>{a}</h3><p>{b}</p></div>' for a, b in t['why'])
        near = ''.join(f'<a href="/zone/{o[0]}/">{o[2]}</a>' for o in ZONES if o[0] != z[0])
        faq_html, faq_ld = faq_section(t['faq'] + [('Quanto costa la gestione?', 'Il 15% sugli incassi per l\'affitto breve e il 10% per il medio termine, senza costi fissi. Disdetta con 30 giorni.')], f'Domande frequenti su {z[2]}')
        rev_html, rev_ld = reviews_section('Le recensioni dei nostri ospiti', 3)
        brief = inbreve(f"GAB gestisce affitti brevi e a medio termine a {z[2]}, Milano: annunci, prezzi, ospiti, check-in di persona, pulizie e pratiche CIN. "
                        "Commissione del 15% sugli incassi per l'affitto breve e del 10% per il medio termine, nessun costo fisso, disdetta con 30 giorni. " + t['tip'])
        body = f'''<section class="hero"><div class="wrap grid"><div>
{crumbs_html([H, Z, (z[2], None)])}
<span class="eyebrow">Zona servita</span>
<h1>{t['h1'].replace(z[2], '<em>' + z[2] + '</em>') if z[2] in t['h1'] else t['h1']}</h1>
<p class="lead">{t['lead']}</p>
<div class="ctas"><a class="btn btn-primary" href="#calcola">Calcola quanto rende</a><a class="btn btn-wa" href="{WA}?text={esc('Ciao GAB, ho un appartamento in zona ' + z[2]).replace(' ', '%20')}">WhatsApp</a></div>
</div>{calc_form(z[0])}</div></section>
<section class="section"><div class="wrap">{brief}<span class="eyebrow">Perché affittare qui</span><h2>Chi cerca casa a {z[2]}</h2>
<div class="grid3" style="margin-top:28px">{why}</div>
<div class="note" style="margin-top:28px">{t['tip']}</div></div></section>
{CASE}
{rev_html}
{faq_html}
<section class="section soft"><div class="wrap"><h2>Zone vicine</h2><div class="zone-list">{near}</div></div></section>
{contact_band(z[2])}'''
        sld = {"@type": "Service", "name": f"Gestione affitti brevi a {z[2]}, Milano", "serviceType": "Property management affitti brevi",
               "provider": {"@id": SITE + "/#gab"}, "areaServed": {"@type": "Place", "name": f"{z[2]}, Milano", "geo": {"@type": "GeoCoordinates", "latitude": z[3], "longitude": z[4]}}}
        add(f'/zone/{z[0]}/', f'Gestione affitti brevi {z[2]}, Milano | GAB',
            f'Gestione affitti brevi e Airbnb a {z[2]}, Milano: ospiti, pulizie e CIN. Commissione 15%, medio termine 10%. Calcola la rendita.',
            body, ld_items=[crumbs_ld([H, Z, (z[2], None)]), faq_ld, sld] + rev_ld, scripts=[CALC_JS, TABS_JS], priority='0.8')

def build_misc():
    H = ('Home', '/')
    # prezzi
    inner = f'''<section class="section" style="padding-top:10px"><div class="wrap">
<div class="price-grid">
<div class="price"><span class="small">Affitto breve</span><div class="pct">15%</div><p class="small">sugli incassi delle prenotazioni</p>
<ul class="incl"><li>Annunci su Airbnb, Booking e Vrbo</li><li>Prezzi dinamici ogni giorno</li><li>Messaggi con gli ospiti 7 giorni su 7</li><li>Check-in di persona o self check-in</li><li>Coordinamento pulizie e biancheria</li><li>CIN, Alloggiati Web, imposta di soggiorno</li><li>Report mensile</li></ul></div>
<div class="price" style="border-color:var(--ink)"><span class="small">Medio termine (30+ notti)</span><div class="pct" style="color:var(--ink)">10%</div><p class="small">sul canone mensile</p>
<ul class="incl"><li>Selezione e verifica degli inquilini</li><li>Contratto transitorio e registrazione</li><li>Check-in, inventario e check-out</li><li>Assistenza e manutenzioni</li><li>Booking diretto senza commissioni dei portali</li><li>Report mensile</li></ul></div>
</div>
<div class="prose" style="margin-top:40px">
<h2>Nessun costo fisso, nessun vincolo</h2><p>Non paghi canoni mensili né costi di attivazione: la nostra commissione è una percentuale di quello che incassi. Puoi interrompere la gestione in qualsiasi momento con <strong>30 giorni di preavviso</strong>.</p>
<h2>Cosa resta a carico del proprietario</h2><ul><li>Utenze, condominio e tasse sull'immobile</li><li>Le commissioni dei portali (Airbnb, Booking) sull'affitto breve</li><li>Eventuali acquisti per l'arredo e le riparazioni, sempre concordati prima</li></ul>
<p>Le pulizie tra un ospite e l'altro sono pagate dall'ospite con la tariffa di pulizia.</p>
<h2>Un esempio concreto</h2><p>Con 70 € a notte per 30 notti, in affitto breve ti restano circa <strong>1.260 €</strong> al mese, nel medio termine circa <strong>1.606 €</strong>. <a href="/guide/affitto-breve-o-medio-termine/">Ecco il calcolo voce per voce</a>.</p>
</div></div></section>'''
    simple_page('/prezzi/', [H, ('Prezzi', None)], 'Prezzi', 'Prezzi della gestione affitti brevi: 15% breve, 10% medio termine',
                'Paghi solo una percentuale su quello che incassi. Nessun costo fisso, disdetta con 30 giorni di preavviso.', inner,
                'Prezzi gestione affitti brevi Milano: 15% e 10% | GAB',
                'Quanto costa la gestione affitti brevi a Milano: 15% sugli incassi per l\'affitto breve, 10% per il medio termine. Nessun costo fisso.',
                faqs=[('Ci sono costi di attivazione?', 'No. Eventuali servizi extra come il servizio fotografico vengono concordati prima.'), ('Su cosa si calcola il 15%?', 'Sugli incassi delle prenotazioni di affitto breve. Ti mandiamo ogni mese il dettaglio nel report.')], priority='0.9')

    # chi siamo
    inner = f'''<section class="section" style="padding-top:10px"><div class="wrap split">
<div class="photo">{picture('vito-ritratto', [640, 400], 'Ritratto di Vito Semeraro, fondatore di GAB', '(max-width:900px) 100vw, 520px', eager=True)}</div>
<div class="prose"><h2>Ciao, sono Vito</h2>
<p>Sono di origini pugliesi e vivo a Milano. Sono su Airbnb da 13 anni, prima come viaggiatore e poi come host: il primo annuncio è stato un trullo in Valle d'Itria, poi sono arrivati i miei appartamenti a Milano tra Turro e Precotto.</p>
<p>Di lavoro sono project manager nell'IT. Ho portato nella gestione degli affitti lo stesso metodo: processi chiari, strumenti digitali, numeri misurati e un report che si capisce.</p>
<p>Dallo stesso lavoro è nato <a href="https://home-staged.ai/">home-staged.ai</a>, la piattaforma di home staging virtuale con AI che ho ideato per mostrare il potenziale di una casa prima dei lavori. Oggi la usano anche agenti immobiliari, home stager e altri property manager.</p>
<p>Oggi GAB segue <strong>9 appartamenti</strong>. Sono pochi per scelta: voglio conoscere ogni casa, rispondere io agli ospiti e poterti dire esattamente come sta andando.</p>
<p>Parlo italiano, inglese, francese, spagnolo e portoghese, e con gli ospiti si sente.</p></div></div></section>
<section class="section soft"><div class="wrap split">
<div class="prose"><h2>Come lavoro</h2>
<ul class="incl"><li><strong>Pochi immobili, tutti in zona</strong>: da Porta Venezia a Bicocca, mai a più di 20 minuti</li><li><strong>Numeri trasparenti</strong>: commissione chiara e report mensile</li><li><strong>La formula giusta</strong>: affitto breve, medio termine o un mix, in base alla tua casa</li><li><strong>Tutto dal telefono</strong>: prezzi, messaggi e calendari sempre sotto controllo</li></ul>
<p><a href="{CAL}">Prenota una call di 30 minuti con me</a></p></div>
<div class="photo">{picture('vito-telefono', [640, 400], 'Vito Semeraro controlla le prenotazioni dal telefono', '(max-width:900px) 100vw, 520px')}</div>
</div></section>'''
    simple_page('/chi-siamo/', [H, ('Chi siamo', None)], 'Chi siamo', 'GAB è una boutique agency di affitti brevi a Milano',
                'Pochi appartamenti, seguiti personalmente da chi li conosce. Ecco chi c\'è dietro.', inner,
                'Chi siamo: Vito Semeraro e la boutique agency GAB | GAB',
                'Vito Semeraro, host Airbnb da oltre 10 anni, guida GAB: boutique agency che segue 9 appartamenti a Milano tra Porta Venezia e Bicocca.',
                extra_ld=[{"@type": "Person", "@id": SITE + "/chi-siamo/#vito", "url": SITE + "/chi-siamo/", **({"sameAs": VITO_SAME_AS} if VITO_SAME_AS else {}),
                           "description": "Fondatore di GAB Gestione Affitti Brevi: gestisce appartamenti in affitto breve e a medio termine a Milano, da Porta Venezia a Bicocca.",
                           "name": "Vito Semeraro", "jobTitle": "Fondatore", "worksFor": {"@id": SITE + "/#gab"}, "image": SITE + "/img/vito-ritratto-640.webp", "knowsLanguage": ["it", "en", "fr", "es", "pt"]}])

    # contatti
    inner = f'''<section class="section" style="padding-top:10px"><div class="wrap grid3">
<div class="card"><h2 style="font-size:1.2rem">📞 Telefono</h2><p><a href="tel:{TEL}">{TEL_H}</a></p></div>
<div class="card"><h2 style="font-size:1.2rem">💬 WhatsApp</h2><p><a href="{WA}">Scrivimi su WhatsApp</a></p></div>
<div class="card"><h2 style="font-size:1.2rem">✉️ Email</h2><p><a href="mailto:{MAIL}">{MAIL}</a></p></div>
</div></section>'''
    simple_page('/contatti/', [H, ('Contatti', None)], 'Contatti', 'Contatta GAB: consulenza gratuita per la tua casa',
                'Scrivimi, chiamami o prenota una call. Ti rispondo personalmente entro 24 ore lavorative.', inner,
                'Contatti e consulenza gratuita | GAB', 'Contatta GAB per una consulenza gratuita sulla gestione del tuo affitto breve o a medio termine a Milano: telefono, WhatsApp, email o Calendly.', priority='0.8')

    # calcolatore
    inner = f'''<section class="section" style="padding-top:10px"><div class="wrap split"><div>{calc_form(None, 'h2')}</div>
<div class="prose"><h2>Come calcoliamo la stima</h2>
<ul><li><strong>Affitto breve</strong>: tariffa media della zona, occupazione al 65%, meno commissioni dei portali (15%), commissione GAB (15%), maggiore cedolare e usura.</li>
<li><strong>Medio periodo</strong>: tariffa mensile scontata del 15%, occupazione al 95%, commissione GAB (10%).</li></ul>
<p>Le tariffe di zona sono calibrate sui nostri appartamenti: per esempio un bilocale a Precotto in medio termine rende 1.400 € netti al mese. È una stima indicativa: per un numero preciso analizziamo la tua casa in consulenza.</p></div></div></section>'''
    simple_page('/calcola-rendita/', [H, ('Calcola la rendita', None)], 'Strumento gratuito', 'Calcola quanto rende il tuo appartamento a Milano',
                'Affitto breve o medio periodo: scopri in 10 secondi il netto stimato al mese nella tua zona.', inner,
                'Calcolatore rendita affitto breve Milano | GAB',
                'Calcola gratis quanto rende il tuo appartamento a Milano con affitto breve o medio termine: netto mensile stimato per zona e tipologia.', scripts=[CALC_JS], priority='0.8')

    # concept grafico: la linea M6
    inner = f'''{linea()}
<section class="section"><div class="wrap prose">
<h2>Perché una linea della metro</h2>
<p>Lavoriamo solo lungo l'asse della M1 e di viale Monza, da Porta Venezia a Bicocca. Ogni zona che seguiamo è una fermata: la raggiungiamo in pochi minuti per un check-in, una pulizia o un imprevisto. Se la tua casa è vicino a una di queste fermate, è sulla nostra linea.</p>
<p>Milano ha cinque linee della metropolitana. La sesta è la nostra: per questo il simbolo del sito è un quadrato magenta con scritto <strong>M6</strong>.</p>
<h2>Come leggere il sito</h2>
<ul class="incl"><li><strong>Il quadrato M6</strong> accanto ai titoli: sei sulla linea GAB.</li><li><strong>I cerchi con il bordo magenta</strong> sono fermate: le zone, i passi del nostro lavoro, i punti chiave di ogni servizio.</li><li><strong>I numeri 01, 02, 03</strong> sulle card sono l'ordine delle fermate.</li><li><strong>Le bande magenta</strong> sopra e sotto le sezioni vengono dal nostro logo, che ha la stessa forma di un cartello di stazione.</li></ul>
<h2>Un omaggio alla segnaletica di Milano</h2>
<p>La metropolitana di Milano, inaugurata nel 1964, ha una delle segnaletiche più famose al mondo: il progetto di Franco Albini e Franca Helg con la grafica di Bob Noorda, fatto di fasce di colore continue e scritte grandi, leggibili da lontano. Il sito riprende quell'idea: caratteri condensati, colori pieni, angoli netti e niente decorazioni inutili.</p>
<p>Anche i numeri seguono la linea: 6 fermate, 9 appartamenti, un solo referente. <a href="/zone/">Guarda le zone sulla mappa</a> o <a href="/chi-siamo/">scopri chi c'è dietro GAB</a>.</p>
</div></section>'''
    simple_page('/linea-m6/', [H, ('La linea M6', None)], 'Il concept', 'La linea M6: la metro di GAB', 'Milano ha cinque linee della metropolitana. La sesta è la nostra: unisce le zone dove gestiamo case, da Porta Venezia a Bicocca.', inner,
                'La linea M6: il concept del sito GAB', 'Perché il sito di GAB è disegnato come una linea della metropolitana di Milano: 6 fermate da Porta Venezia a Bicocca e un omaggio alla segnaletica di Albini, Helg e Noorda.', priority='0.3')

    # privacy
    inner = f'''<section class="section" style="padding-top:10px"><div class="wrap prose">
<h2>Titolare del trattamento</h2><p>Vito Semeraro, GAB Gestione Affitti Brevi, Milano. Email: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<h2>Quali dati raccogliamo</h2><p>Solo i dati che ci invii con il modulo di contatto, via email, telefono o WhatsApp: nome, telefono, email, zona e informazioni sull'immobile.</p>
<h2>Perché</h2><p>Per risponderti e prepararti una proposta (base giuridica: misure precontrattuali richieste da te, art. 6.1.b GDPR). Non usiamo i dati per altre finalità e non li cediamo a terzi.</p>
<h2>Per quanto tempo</h2><p>Fino a 24 mesi dall'ultimo contatto, salvo un rapporto di gestione in corso.</p>
<h2 id="cookie">Cookie</h2><p>Questo sito non usa cookie di profilazione né strumenti di tracciamento pubblicitario. Usa Google Analytics 4 (Google Ireland Ltd) solo se lo accetti dal banner: misura in forma aggregata le pagine visitate e i contatti avviati, con i cookie _ga e _ga_* che durano fino a 14 mesi. Per contare le visite in forma anonima usiamo anche Cloudflare Web Analytics, che non usa cookie né altri dati salvati sul tuo dispositivo e non ti segue su altri siti. Senza il tuo consenso lo script di Google non viene caricato. Puoi cambiare scelta in ogni momento dal link "Preferenze cookie" in fondo alla pagina; la scelta resta salvata nel tuo browser. La mappa delle zone carica la libreria Leaflet da cdnjs (Cloudflare) e le immagini da OpenStreetMap, che ricevono il tuo indirizzo IP come avviene per ogni immagine sul web. Il link a Calendly e WhatsApp ti porta su servizi esterni con le loro informative.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, rettifica, cancellazione, limitazione e portabilità dei tuoi dati scrivendo a <a href="mailto:{MAIL}">{MAIL}</a>, e puoi presentare reclamo al Garante per la protezione dei dati personali.</p>
<p class="meta">Ultimo aggiornamento: {date.today().strftime('%d/%m/%Y')}</p></div></section>'''
    simple_page('/privacy/', [H, ('Privacy', None)], 'Informativa', 'Privacy e cookie', 'Come trattiamo i tuoi dati.', inner,
                'Privacy e cookie | GAB', 'Informativa privacy e cookie di GAB Gestione Affitti Brevi: quali dati raccogliamo dal modulo contatti e come li trattiamo.', band=False, priority='0.2')

    # grazie + 404 (noindex, non in sitemap)
    for p, h1, lead in [('/grazie/', 'Grazie, ti ricontatto presto', 'Ho ricevuto la tua richiesta. Ti rispondo personalmente entro 24 ore lavorative. Se è urgente, scrivimi su WhatsApp.'),
                        ('/404.html', 'Pagina non trovata', 'La pagina che cerchi non esiste più o è stata spostata. Prova dalla home o scrivimi.')]:
        body = f'''<section class="pagehero"><div class="wrap"><h1>{h1}</h1><p class="lead">{lead}</p>
<div class="ctas" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:20px"><a class="btn btn-primary" href="/">Torna alla home</a><a class="btn btn-wa" href="{WA}">WhatsApp</a></div></div></section>'''
        write(p, page(p, h1 + ' | GAB', lead, body, robots='noindex,follow'))

GUIDES = []
GUIDE_BRIEFS = {'cedolare-secca-affitti-brevi': "Nel 2026 la cedolare secca sugli affitti brevi è al 21% per un solo immobile e al 26% dal secondo; con tre o più immobili l'attività si presume d'impresa. Si paga sul canone lordo: su 2.100 € al mese sono 441 € con il 21% e 546 € con il 26%. Al 26 ottobre 2026 la manovra 2027 non la cambia.", 'codice-cin-affitti-brevi': "Il CIN è obbligatorio per ogni immobile affittato fino a 30 giorni, anche per una notte. Si richiede gratis sul portale BDSR del Ministero del Turismo con SPID o CIE, servono rilevatori di gas e monossido ed estintori, e va indicato negli annunci e fuori dall'edificio. Senza CIN la sanzione va da 800 a 8.000 €.", 'affitto-breve-o-medio-termine': "Su un appartamento milanese da 2.100 € lordi al mese, il medio termine lascia 1.606 € netti contro 1.260 € dell'affitto breve: 346 € in più al mese, con un'occupazione del 95% nei nostri appartamenti. L'affitto breve conviene se vuoi usare la casa ogni tanto, in zone turistiche e durante fiere ed eventi.", 'prenotazioni-dirette-affitti-brevi': "Ogni prenotazione diretta evita circa il 15% di commissioni dei portali: su 2.000 € al mese sono circa 300 €, oltre 3.500 € l'anno. Funziona usare Airbnb e Booking per il primo soggiorno e un sito proprio, con scheda Google e prenotatore sincronizzato, per gli ospiti che tornano e per le aziende.", 'home-staging-affitti-brevi': "Nell'affitto breve l'home staging serve a ottenere foto che fanno cliccare e recensioni a cinque stelle. Conviene spendere prima su luce, letto e biancheria, poi sulla cucina. Il ritorno si calcola dividendo il costo del restyle per il maggiore incasso netto mensile: 6.000 € con 150 € in più al mese rientrano in 40 mesi."}

def guide(slug, title, h1, desc, lead, toc, content, faqs, updated=None, brief=''):
    brief = brief or GUIDE_BRIEFS.get(slug, '')
    path = f'/guide/{slug}/'
    H = ('Home', '/'); G = ('Guide', '/guide/')
    tochtml = '<nav class="toc" aria-label="Indice"><strong>In questa guida</strong><ol>' + ''.join(f'<li><a href="#{a}">{t}</a></li>' for a, t in toc) + '</ol></nav>'
    upd = updated or date.today().isoformat()
    inner = f'''<section class="section" style="padding-top:10px"><div class="wrap prose">
<div class="signed">{picture('vito-avatar', [160], 'Vito Semeraro', '56px', eager=True)}<div><strong>Vito Semeraro</strong><small>Aggiornata il {date.fromisoformat(upd).strftime('%d/%m/%Y')}</small></div></div>
{inbreve(brief) if brief else ''}{tochtml}{content}
<div class="note">Questa guida è informativa e non sostituisce il parere del tuo commercialista. Vuoi capire cosa conviene nel tuo caso? <a href="/contatti/">Scrivimi</a> o <a href="/calcola-rendita/">calcola la rendita</a>.</div>
</div></section>'''
    art = {"@type": "Article", "headline": h1, "description": desc, "datePublished": upd, "dateModified": upd, "inLanguage": "it-IT",
           "author": {"@type": "Person", "@id": SITE + "/chi-siamo/#vito", "name": "Vito Semeraro", "url": SITE + "/chi-siamo/"}, "publisher": {"@id": SITE + "/#gab"},
           "image": SITE + "/img/vito-hero-1200.webp", "mainEntityOfPage": SITE + path, **({"abstract": brief} if brief else {})}
    simple_page(path, [H, G, (h1 if len(h1) < 50 else title.split('|')[0].strip(), None)], 'Guida', h1, lead, inner, title, desc, faqs, [art], priority='0.7')
    GUIDES.append((path, h1, desc))

# MD: guide scritte in Markdown, senza librerie esterne
def md_inline(t):
    t = esc(t).replace('&#x27;', "'")
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)\*', r'<em>\1</em>', t)
    return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{m.group(2)}"' + (' rel="noopener"' if m.group(2).startswith('http') else '') + f'>{m.group(1)}</a>', t)

def md_slug(t):
    t = t.lower()
    for a, b in (('à', 'a'), ('è', 'e'), ('é', 'e'), ('ì', 'i'), ('ò', 'o'), ('ù', 'u')): t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:40]

def md_blocks(text):
    out, toc, lines, i = [], [], text.strip().split('\n'), 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l: i += 1; continue
        if l.startswith('## '):
            h = l[3:].strip(); a = md_slug(h); toc.append((a, h)); out.append(f'<h2 id="{a}">{md_inline(h)}</h2>'); i += 1
        elif l.startswith('### '):
            out.append(f'<h3>{md_inline(l[4:].strip())}</h3>'); i += 1
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                c = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-{2,}:?', x) for x in c): rows.append(c)
                i += 1
            head = ''.join(f'<th>{md_inline(x)}</th>' for x in rows[0])
            body = ''.join('<tr>' + ''.join(f'<td>{md_inline(x)}</td>' for x in r) + '</tr>' for r in rows[1:])
            out.append(f'<table><tr>{head}</tr>{body}</table>')
        elif re.match(r'(- |\d+\. )', l):
            tag = 'ol' if l[0].isdigit() else 'ul'; items = []
            while i < len(lines) and re.match(r'(- |\d+\. )', lines[i]):
                items.append(re.sub(r'^(- |\d+\. )', '', lines[i]).strip()); i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{md_inline(x)}</li>' for x in items) + f'</{tag}>')
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r'(#{2,3} |\||- |\d+\. )', lines[i]):
                para.append(lines[i].strip()); i += 1
            out.append(f'<p>{md_inline(" ".join(para))}</p>')
    return '\n'.join(out), toc

def md_guides():
    folder = os.path.join(HERE, 'content', 'guide')
    if not os.path.isdir(folder): return
    for fn in sorted(os.listdir(folder)):
        m = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md$', fn)
        if not m or m.group(1) > TODAY: continue
        raw = open(os.path.join(folder, fn), encoding='utf-8').read()
        head, _, text = raw.partition('\n---\n')
        meta = dict(x.split(':', 1) for x in head.strip().strip('-').strip().split('\n') if ':' in x)
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        if meta.get('bozza') == 'si': continue
        text, _, faq_md = text.partition('\n## Domande frequenti\n')
        faqs = re.findall(r'^### (.+?)\n+(.+?)(?=\n### |\Z)', faq_md.strip(), flags=re.S | re.M)
        content, toc = md_blocks(text)
        guide(m.group(2), meta['titolo_seo'], meta['titolo'], meta['descrizione'], meta['sommario'], toc, content,
              [(q.strip(), ' '.join(a.split())) for q, a in faqs], updated=meta.get('aggiornato', m.group(1)), brief=meta.get('in_breve', ''))

def build_guides():
    guide('cedolare-secca-affitti-brevi', 'Cedolare secca affitti brevi 2026: aliquote 21% e 26% | GAB',
          'Cedolare secca affitti brevi 2026: aliquote, casi ed esempi',
          'Cedolare secca affitti brevi 2026: 21% per un immobile, 26% dal secondo, impresa da tre immobili. Esempi di calcolo e medio termine.',
          'Quanto paghi di tasse su un affitto breve nel 2026, quando si applica il 26% e cosa cambia se scegli il medio termine.',
          [('cosa', 'Cos\'è la cedolare secca'), ('aliquote', 'Le aliquote 2026'), ('manovra', 'Legge di Bilancio 2027: cosa si discute'), ('esempio', 'Un esempio di calcolo'), ('impresa', 'Da tre immobili: attività d\'impresa'), ('medio', 'Il medio termine'), ('come', 'Come e quando si paga')],
          '''<h2 id="cosa">Cos'è la cedolare secca</h2><p>È una tassa fissa che sostituisce l'IRPEF e le addizionali sui redditi da affitto. Per gli affitti brevi, cioè fino a 30 giorni, si applica sul <strong>canone lordo</strong> incassato, senza dedurre spese.</p>
<h2 id="aliquote">Le aliquote 2026</h2><table><tr><th>Situazione</th><th>Aliquota</th></tr><tr><td>Un solo immobile in affitto breve (a scelta del proprietario)</td><td><strong>21%</strong></td></tr><tr><td>Dal secondo immobile in affitto breve</td><td><strong>26%</strong></td></tr><tr><td>Tre o più immobili in affitto breve</td><td>Attività d'impresa presunta: serve la partita IVA</td></tr></table>
<p>La Legge di Bilancio 2026 ha confermato il doppio binario 21% e 26% e ha abbassato la soglia oltre la quale l'affitto breve si considera attività d'impresa: da cinque a <strong>tre</strong> immobili.</p>
<h2 id="manovra">Legge di Bilancio 2027: cosa si discute</h2><p><em>Aggiornato al 26 ottobre 2026.</em> Nelle proposte sulla manovra 2027 uscite finora non ci sono modifiche alla cedolare sugli affitti brevi: restano il 21%, il 26% dal secondo immobile e la soglia dei tre immobili.</p><ul><li><strong>Canone concordato</strong>: la maggioranza propone di scendere dal 10% al 5%. Non è approvato e servono le coperture: per ora resta il 10%.</li><li><strong>Negozi</strong>: si valuta di riportare la cedolare al 21% sugli affitti commerciali dei piccoli negozi.</li></ul><p>Se il 5% passasse, il <a href="/servizi/medio-termine/">medio termine</a> con contratto concordato diventerebbe ancora più conveniente rispetto all'affitto breve dal secondo immobile. Aggiorneremo questa pagina quando il testo sarà approvato. Fonti: <a href="https://tg24.sky.it/economia/2026/10/22/bonus-casa-cedolare-secca-affitti-manovra-2027" rel="noopener">Sky TG24</a>, <a href="https://www.fiscoetasse.com/new-rassegna-stampa/4685-cedolare-secca-al-5-sugli-affitti-concordati-cosa-prevede-la-proposta-per-il-2027.html" rel="noopener">FiscoeTasse</a>, 22 ottobre 2026.</p>
<h2 id="esempio">Un esempio di calcolo</h2><p>Bilocale a Milano, 70 € a notte per 30 notti: incasso lordo 2.100 €.</p><ul><li>Se è il tuo unico affitto breve: 2.100 × 21% = <strong>441 €</strong></li><li>Se è il secondo: 2.100 × 26% = <strong>546 €</strong></li></ul><p>La differenza è di 105 € al mese: è la voce "maggiore cedolare" che usiamo nel <a href="/guide/affitto-breve-o-medio-termine/">confronto tra breve e medio termine</a>.</p>
<h2 id="impresa">Da tre immobili: attività d'impresa</h2><p>Se destini all'affitto breve tre o più unità, l'attività si presume imprenditoriale: niente cedolare, partita IVA e tassazione ordinaria. Conta il numero di immobili del singolo proprietario, non quelli gestiti dall'agenzia.</p>
<h2 id="medio">Il medio termine</h2><p>Sopra i 30 giorni non è più locazione breve: si usa di solito un contratto transitorio con cedolare al 21%, o al 10% se a canone concordato dove previsto. Per questo, dal secondo immobile, il medio termine può essere fiscalmente più conveniente.</p>
<h2 id="come">Come e quando si paga</h2><p>Se incassi tramite un portale come Airbnb, il portale trattiene una ritenuta del 21% a titolo di acconto. Il saldo si calcola nella dichiarazione dei redditi. Gestiamo noi i dati da passare al tuo commercialista.</p>''',
          [('La cedolare secca sugli affitti brevi è obbligatoria?', 'No, è facoltativa: in alternativa si applica l\'IRPEF ordinaria. Per la maggior parte dei proprietari conviene.'),
           ('Il 26% si applica alla prima casa in affitto?', 'No: puoi scegliere un immobile su cui applicare il 21%; il 26% vale dal secondo.'),
           ('La Legge di Bilancio 2027 cambia la cedolare sugli affitti brevi?', 'Al 26 ottobre 2026 no: le proposte in discussione riguardano il canone concordato (dal 10% al 5%) e i negozi, non gli affitti brevi.'),
           ('Con tre appartamenti posso ancora usare la cedolare?', 'No, dal 2026 con tre o più unità in affitto breve l\'attività si presume d\'impresa e serve la partita IVA.')])

    guide('codice-cin-affitti-brevi', 'Codice CIN affitti brevi: cos\'è, come ottenerlo, sanzioni | GAB',
          'Codice CIN per affitti brevi: cos\'è, come ottenerlo e sanzioni',
          'Codice CIN per affitti brevi: chi deve averlo, come richiederlo sulla BDSR, requisiti di sicurezza, dove esporlo e sanzioni.',
          'Il CIN è obbligatorio per tutti gli affitti brevi e turistici. Ecco come ottenerlo e cosa rischi senza.',
          [('cosa', 'Cos\'è il CIN'), ('chi', 'Chi deve averlo'), ('come', 'Come si richiede'), ('requisiti', 'Requisiti di sicurezza'), ('dove', 'Dove esporlo'), ('sanzioni', 'Sanzioni')],
          '''<h2 id="cosa">Cos'è il CIN</h2><p>Il Codice Identificativo Nazionale identifica ogni immobile usato per affitti brevi o turistici. È stato introdotto dall'articolo 13-ter del decreto legge 145/2023 ed è rilasciato dalla Banca Dati nazionale delle Strutture Ricettive (BDSR) del Ministero del Turismo.</p>
<h2 id="chi">Chi deve averlo</h2><p>Tutti i proprietari, o chi gestisce l'immobile, che affittano per periodi fino a 30 giorni, anche per una sola notte e anche tramite portali come Airbnb e Booking.</p>
<h2 id="come">Come si richiede</h2><ol><li>Accedi al portale BDSR del Ministero del Turismo con SPID o CIE.</li><li>Se l'immobile ha già un codice regionale (in Lombardia il CIR), trovi i dati precompilati e confermi.</li><li>Dichiari i requisiti di sicurezza e ottieni il CIN, di solito in tempi brevi.</li></ol><p>Se ci affidi la gestione, la richiesta la facciamo noi.</p>
<h2 id="requisiti">Requisiti di sicurezza</h2><ul><li>Rilevatori funzionanti di gas combustibili e di monossido di carbonio</li><li>Estintori portatili a norma, accessibili e visibili</li></ul>
<h2 id="dove">Dove esporlo</h2><p>Il CIN va indicato in ogni annuncio online e affisso all'esterno dell'edificio in cui si trova l'appartamento.</p>
<h2 id="sanzioni">Sanzioni</h2><table><tr><th>Violazione</th><th>Sanzione</th></tr><tr><td>Affitto senza CIN</td><td>da 800 a 8.000 €</td></tr><tr><td>CIN non esposto o non indicato negli annunci</td><td>da 500 a 5.000 €</td></tr><tr><td>Mancanza dei dispositivi di sicurezza</td><td>da 600 a 6.000 €</td></tr></table>''',
          [('Il CIN costa qualcosa?', 'No, la richiesta sulla BDSR è gratuita. Costano solo eventuali dispositivi di sicurezza da installare.'),
           ('Serve il CIN anche per il medio termine?', 'Il CIN riguarda le locazioni brevi e turistiche. Per i contratti transitori sopra i 30 giorni si applicano le regole delle locazioni ordinarie.')])

    guide('affitto-breve-o-medio-termine', 'Affitto breve o medio termine a Milano: quale rende di più | GAB',
          'Affitto breve o medio termine: quale rende di più a Milano',
          'Affitto breve o medio termine a Milano? Confronto con numeri reali: su 2.100 € lordi il medio termine lascia 346 € in più al mese.',
          'Abbiamo messo a confronto le due formule con i nostri numeri. Il risultato non è scontato.',
          [('ipotesi', 'Le ipotesi'), ('breve', 'Affitto breve'), ('medio', 'Medio termine'), ('quando', 'Quando conviene l\'uno o l\'altro')],
          '''<h2 id="ipotesi">Le ipotesi</h2><p>Appartamento a 70 € a notte, 30 notti, al netto delle utenze: incasso lordo 2.100 € al mese. Sono i numeri del nostro report sul medio termine, aggiornati con le commissioni GAB.</p>
<h2 id="breve">Affitto breve</h2><table><tr><td>Incasso lordo</td><td>2.100 €</td></tr><tr><td>Commissioni portali (15%)</td><td>−315 €</td></tr><tr><td>Commissione GAB (15%)</td><td>−315 €</td></tr><tr><td>Maggiore cedolare (26% invece di 21%)</td><td>−105 €</td></tr><tr><td>Usura e manutenzione (5%)</td><td>−105 €</td></tr><tr><th>Netto</th><th>1.260 €</th></tr></table>
<h2 id="medio">Medio termine</h2><table><tr><td>Incasso lordo</td><td>2.100 €</td></tr><tr><td>Sconto mensile all'ospite (15%)</td><td>−315 €</td></tr><tr><td>Commissione GAB (10%)</td><td>−179 €</td></tr><tr><td>Commissioni portali con booking diretto</td><td>0 €</td></tr><tr><th>Netto</th><th>1.606 €</th></tr></table>
<p>Il medio termine lascia <strong>346 € in più al mese</strong>. Nei nostri appartamenti in medio termine l'occupazione è del 95%.</p>
<h2 id="quando">Quando conviene l'uno o l'altro</h2><ul><li><strong>Affitto breve</strong> se vuoi usare la casa ogni tanto, se sei in una zona turistica come Porta Venezia o Centrale, o nei mesi di Fashion Week, Salone del Mobile e grandi fiere.</li><li><strong>Medio termine</strong> se vuoi stabilità e meno usura, se la casa è vicina a università e uffici come Bicocca e Precotto, o se è il tuo secondo immobile.</li><li><strong>Un mix</strong>: medio termine in autunno e inverno, affitto breve nei mesi di eventi. È la soluzione che proponiamo più spesso.</li></ul>''',
          [('Il medio termine rende sempre di più?', 'No. Con tariffe e occupazione alte, per esempio nelle settimane di eventi, l\'affitto breve può rendere di più. Per questo valutiamo caso per caso.')])

    guide('prenotazioni-dirette-affitti-brevi', 'Prenotazioni dirette affitti brevi: come pagare meno commissioni | GAB',
          'Prenotazioni dirette per affitti brevi: come pagare meno commissioni',
          'Prenotazioni dirette per case vacanza e affitti brevi: vantaggi, rischi, regole fiscali e i canali per portare ospiti al tuo sito senza commissioni.',
          'Airbnb e Booking restano utili, ma ogni prenotazione diretta vale circa il 15% in più. Ecco come costruire il tuo canale diretto passo per passo.',
          [('perche', 'Perché puntare sulle prenotazioni dirette'), ('vantaggi', 'I vantaggi'), ('traffico', 'Come portare ospiti al sito'), ('convertire', 'Come trasformare le visite in prenotazioni'), ('regole', 'Regole e tasse'), ('mix', 'Il mix giusto con i portali')],
          '''<h2 id="perche">Perché puntare sulle prenotazioni dirette</h2><p>Le commissioni dei portali pesano intorno al 15% dell'incasso. Su un appartamento che incassa 2.000 € al mese sono circa 300 € al mese, oltre 3.500 € l'anno. Ogni ospite che torna e prenota dal tuo sito, invece che dal portale, è un ospite su cui quella commissione non la paghi più.</p>
<h2 id="vantaggi">I vantaggi</h2><ul><li><strong>Zero commissioni</strong> sulle prenotazioni dirette</li><li><strong>Pagamenti anticipati</strong> e regole di caparra e cancellazione decise da te</li><li><strong>Controllo delle recensioni</strong> e dei contatti degli ospiti</li><li><strong>Indipendenza</strong> da cambi di algoritmo, penalizzazioni e nuove regole dei portali</li></ul>
<h2 id="traffico">Come portare ospiti al sito</h2><table><tr><th>Canale</th><th>Come funziona</th><th>Tempi</th></tr><tr><td>Portali (Airbnb, Booking)</td><td>Portano il primo soggiorno: poi l'ospite può tornare da te</td><td>Subito</td></tr><tr><td>Scheda Google</td><td>Ti trova chi cerca alloggi nella zona, con foto e recensioni</td><td>Settimane</td></tr><tr><td>Campagne su Google e social</td><td>Visite mirate con budget controllato</td><td>2-3 mesi</td></tr><tr><td>SEO</td><td>Pagine e articoli che compaiono nelle ricerche</td><td>Circa 6 mesi</td></tr><tr><td>Aziende e università</td><td>Accordi per trasferte e soggiorni lunghi</td><td>Variabile</td></tr></table>
<h2 id="convertire">Come trasformare le visite in prenotazioni</h2><ul><li>Un <strong>sito veloce</strong>, pensato prima di tutto per lo smartphone</li><li><strong>Foto curate</strong> e testi in più lingue</li><li><strong>Prenotatore</strong> con disponibilità e prezzo in tempo reale, sincronizzato con i portali</li><li><strong>Recensioni</strong> in evidenza e una chat per le domande</li><li>Un piccolo <strong>vantaggio</strong> per chi prenota diretto, per esempio il check-in flessibile</li></ul><p>Sono gli elementi che mettiamo nei siti per case vacanza che realizziamo: <a href="/servizi/booking-diretto/">scopri il sito per prenotazioni dirette</a>.</p>
<h2 id="regole">Regole e tasse</h2><p>Le prenotazioni dirette seguono le stesse regole di quelle dai portali: <a href="/guide/codice-cin-affitti-brevi/">codice CIN</a> esposto anche sul sito, comunicazione degli ospiti su Alloggiati Web, imposta di soggiorno e <a href="/guide/cedolare-secca-affitti-brevi/">cedolare secca</a>. La differenza è che nessun portale trattiene la ritenuta del 21%: la cedolare la versi tu in dichiarazione, quindi conviene tenere traccia di ogni incasso.</p>
<h2 id="mix">Il mix giusto con i portali</h2><p>Non serve lasciare Airbnb e Booking. La strategia che funziona è usare i portali per farsi conoscere e il sito per gli ospiti che tornano, le aziende e chi ti trova su Google. Con il tempo la quota di prenotazioni dirette cresce e quella che paghi in commissioni scende. Se vuoi accelerare, c'è il nostro <a href="/servizi/marketing-affitti-brevi/">marketing per affitti brevi</a>.</p>''',
          [('È legale chiedere agli ospiti di Airbnb di prenotare direttamente?', 'Durante una prenotazione Airbnb non puoi spostare l\'ospite fuori dalla piattaforma. Puoi però avere un sito pubblico e una scheda Google, dove chi ti conosce ti ritrova da solo per il soggiorno successivo.'),
           ('Quanto costa un sito per prenotazioni dirette?', 'Dipende da lingue, prenotatore e servizi inclusi. Con una call di 30 minuti ti facciamo un preventivo per la tua casa.')])

    guide('home-staging-affitti-brevi', 'Home staging per affitti brevi: cosa fare e come calcolare il ritorno | GAB',
          'Home staging per affitti brevi: cosa fare e come calcolare il ritorno',
          'Home staging per affitti brevi: gli interventi che contano per gli ospiti, come stabilire il budget e come calcolare in quanti mesi rientri della spesa.',
          'Un restyle ben fatto fa salire tariffa e occupazione. Ma quanto spendere, e dove? Ecco il metodo che usiamo con i proprietari.',
          [('cosa', 'Cos\'è l\'home staging per affitti brevi'), ('dove', 'Dove conviene spendere'), ('budget', 'Come decidere il budget'), ('calcolo', 'Come calcolare il ritorno'), ('ai', 'L\'anteprima con l\'AI')],
          '''<h2 id="cosa">Cos'è l'home staging per affitti brevi</h2><p>Nella vendita l'home staging serve a far piacere la casa a chi visita. Negli affitti brevi l'obiettivo è diverso: <strong>foto che fanno cliccare</strong> e un soggiorno che porta <strong>recensioni a cinque stelle</strong>. Tariffa, occupazione e recensioni sono le tre leve che determinano quanto rende la casa.</p>
<h2 id="dove">Dove conviene spendere</h2><ol><li><strong>Luce</strong>: lampade calde, tende chiare, specchi. Nelle foto fa la differenza più di tutto.</li><li><strong>Letto e biancheria</strong>: materasso buono, lenzuola di qualità, cuscini in più. È la voce più citata nelle recensioni.</li><li><strong>Cucina attrezzata</strong>: chi resta più notti cucina, soprattutto nel medio termine.</li><li><strong>Postazione di lavoro</strong>: scrivania e sedia comoda per chi lavora in trasferta.</li><li><strong>Un dettaglio riconoscibile</strong>: una parete colorata, un quadro, un angolo che diventa la foto di copertina.</li><li><strong>Foto professionali</strong>: senza, il resto si vede a metà.</li></ol>
<h2 id="budget">Come decidere il budget</h2><p>Si parte da quanto vuoi investire, non da un progetto ideale. Con budget piccoli si lavora su luce, tessili e dettagli; con budget medi su arredi e tinteggiatura; con budget più alti su cucina, bagno e piccoli lavori. Il punto è scegliere il livello che rientra prima.</p>
<h2 id="calcolo">Come calcolare il ritorno</h2><p>Il calcolo è semplice: <strong>mesi di rientro = costo del restyle ÷ maggiore incasso netto al mese</strong>.</p><table><tr><td>Costo del restyle (esempio)</td><td>6.000 €</td></tr><tr><td>Netto al mese prima</td><td>1.000 €</td></tr><tr><td>Netto al mese dopo (esempio con +15%)</td><td>1.150 €</td></tr><tr><th>Mesi di rientro</th><th>6.000 ÷ 150 = 40 mesi</th></tr></table><p>I numeri sono un esempio: l'aumento reale dipende dalla zona e dalla concorrenza, e lo stimiamo confrontando annunci simili prima e dopo un restyle. Per un primo ordine di grandezza usa il <a href="/calcola-rendita/">simulatore di rendita</a>: se la casa è da rinnovare, ti dice in quanti mesi di rendita rientra il budget.</p>
<h2 id="ai">L'anteprima con l'AI</h2><p>Prima di comprare qualsiasi cosa puoi vedere il risultato. Con <a href="https://home-staged.ai/">home-staged.ai</a>, la piattaforma di home staging virtuale ideata da Vito, da una foto della stanza ottieni la versione arredata, gli interventi consigliati e i costi. È il primo passo della nostra <a href="/servizi/consulenza-home-staging/">consulenza home staging con AI</a>.</p>''',
          [('Quanto costa l\'home staging di un bilocale?', 'Dipende da quanto c\'è da fare: si va da poche centinaia di euro per luci e tessili a diverse migliaia per arredi e lavori. Per questo partiamo dal tuo budget.'),
           ('Conviene fare home staging se affitto a medio termine?', 'Sì, ma con priorità diverse: cucina, postazione di lavoro e armadi contano più dei dettagli scenografici.')])

    md_guides()
    H = ('Home', '/')
    cards = ''.join(f'<a class="card" href="{p}"><h2 style="font-size:1.2rem">{t}</h2><p>{d}</p><span>Leggi →</span></a>' for p, t, d in GUIDES)
    simple_page('/guide/', [H, ('Guide', None)], 'Guide', 'Guide per proprietari di affitti brevi a Milano',
                'Tasse, burocrazia, numeri e marketing: tutto quello che serve per decidere come affittare la tua casa.',
                f'<section class="section" style="padding-top:10px"><div class="wrap grid3 cards-link">{cards}</div></section>',
                'Guide affitti brevi Milano: cedolare, CIN, prenotazioni dirette | GAB',
                'Guide pratiche per proprietari a Milano: cedolare secca 2026, codice CIN, affitto breve o medio termine, prenotazioni dirette e home staging.', priority='0.8')

HTACCESS = r'''# GAB - sito statico
Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html

RewriteEngine On
# HTTPS e dominio senza www
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} ^www\. [NC]
RewriteRule ^ https://gestione-affitti-brevi-milano.it%{REQUEST_URI} [L,R=301]

# Redirect 301 dalle vecchie pagine WordPress
RewriteRule ^services/?$ /servizi/ [R=301,L]
RewriteRule ^gestione-affitti/?$ / [R=301,L]
RewriteRule ^metti-il-tuo-immobile-a-reddito/?$ / [R=301,L]
RewriteRule ^property-management/?$ /property-manager-milano/ [R=301,L]
RewriteRule ^gestione-airbnb/?$ /gestione-airbnb-milano/ [R=301,L]
RewriteRule ^affittare-con-airbnb/?$ /gestione-airbnb-milano/ [R=301,L]
RewriteRule ^avviare-casa-vacanza/?$ /servizi/consulenza-avvio/ [R=301,L]
RewriteRule ^airbnb-cedolare-secca/?$ /guide/cedolare-secca-affitti-brevi/ [R=301,L]
RewriteRule ^sito-casa-vacanza/?$ /servizi/booking-diretto/ [R=301,L]
RewriteRule ^prenota-una-consulenza-gratuita/?$ /contatti/ [R=301,L]
RewriteRule ^contact/?$ /contatti/ [R=301,L]
RewriteRule ^blog/?$ /guide/ [R=301,L]
RewriteRule ^feed/?$ / [R=301,L]

# Pagine demo del vecchio tema e WordPress: rimosse definitivamente
RewriteRule ^(20[0-9]{2})/ - [G,L]
RewriteRule ^(cart|checkout|shop|courses|dashboard|my-account|profile|sample-page|hero|sections-about-me|instructor-registration|student-registration|become-a-teacher|author|category|tag|comments)(/.*)?$ - [G,L]
RewriteRule ^(wp-admin|wp-content|wp-includes|wp-json|wp-login\.php|xmlrpc\.php|wp-sitemap.*|sitemap_index\.xml|page-sitemap\.xml|post-sitemap\.xml)(/.*)?$ - [G,L]
RewriteCond %{QUERY_STRING} (^|&)(p|page_id|cat|s)= [NC]
RewriteRule ^$ /? [R=301,L]

# Cartelle senza slash finale
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^(.*[^/])$ /$1/ [R=301,L]

# Compressione
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml text/plain application/xml
</IfModule>
<IfModule mod_brotli.c>
AddOutputFilterByType BROTLI_COMPRESS text/html text/css application/javascript application/json image/svg+xml text/plain application/xml
</IfModule>

# Cache
<IfModule mod_expires.c>
ExpiresActive On
ExpiresDefault "access plus 1 hour"
ExpiresByType text/html "access plus 1 hour"
ExpiresByType image/webp "access plus 1 year"
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType image/svg+xml "access plus 1 month"
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"
</IfModule>
<IfModule mod_headers.c>
<FilesMatch "\.(webp|jpg|css|js|woff2)$">
Header set Cache-Control "public, max-age=31536000, immutable"
</FilesMatch>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Strict-Transport-Security "max-age=31536000"
</IfModule>

<FilesMatch "^\.">
Require all denied
</FilesMatch>

# php -- BEGIN cPanel-generated handler, do not edit
# Set the “ea-php81” package as the default “PHP” programming language.
<IfModule mime_module>
  AddHandler application/x-httpd-ea-php81___lsphp .php .php8 .phtml
</IfModule>
# php -- END cPanel-generated handler, do not edit
'''

CONTACT_PHP = r'''<?php
// Modulo contatti GAB: invia la richiesta a hello@ e rimanda alla pagina di ringraziamento.
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contatti/', true, 303); exit; }
$spam = !empty($_POST['sito']); // honeypot: non scarta, segnala nell'oggetto (il browser a volte lo compila)

function campo($k, $max = 300) { return trim(mb_substr(strip_tags($_POST[$k] ?? ''), 0, $max)); }
$nome = campo('nome', 100); $tel = campo('telefono', 40); $zona = campo('zona', 100); $msg = campo('messaggio', 1000);
if ($nome === '' || strlen(preg_replace('/\D/', '', $tel)) < 6) { header('Location: /contatti/?errore=1', true, 303); exit; }

$to = 'hello@gestione-affitti-brevi-milano.it';
$subject = '=?UTF-8?B?' . base64_encode(($spam ? '[possibile spam] ' : '') . 'Nuova richiesta dal sito: ' . $nome . ($zona ? ' - ' . $zona : '')) . '?=';
$fonte = parse_url($_SERVER['HTTP_REFERER'] ?? '', PHP_URL_PATH);
$body = "Nome: $nome\nTelefono: $tel\nZona: $zona\nMessaggio: $msg\nPagina: $fonte\nData: " . date('d/m/Y H:i') . "\n";
$headers = "From: Sito GAB <$to>\r\nContent-Type: text/plain; charset=UTF-8\r\n";
@mail($to, $subject, $body, $headers, '-f' . $to);
header('Location: /grazie/', true, 303);
'''

FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#fff"/><rect y="0" width="64" height="14" fill="#ff0088"/><rect y="50" width="64" height="14" fill="#ff0088"/><text x="32" y="43" font-family="Georgia,serif" font-size="25" font-weight="700" text-anchor="middle" fill="#ff0088">GAB</text></svg>'

def build_seo_files():
    # IndexNow: file di verifica della chiave (Bing, Yandex, Seznam)
    open(os.path.join(DIST, INDEXNOW_KEY + '.txt'), 'w').write(INDEXNOW_KEY)
    open(os.path.join(DIST, '.htaccess'), 'w').write(HTACCESS)
    open(os.path.join(DIST, 'contatti.php'), 'w').write(CONTACT_PHP)
    open(os.path.join(DIST, 'favicon.svg'), 'w').write(FAVICON)
    open(os.path.join(DIST, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /grazie/\n\nSitemap: {SITE}/sitemap.xml\n')
    zl = '\n'.join(f'- [{z[2]}]({SITE}/zone/{z[0]}/)' for z in ZONES)
    gl = '\n'.join(f'- [{t}]({SITE}{p}): {d}' for p, t, d in GUIDES)
    open(os.path.join(DIST, 'llms.txt'), 'w').write(f"""# GAB Gestione Affitti Brevi

> Boutique agency di gestione affitti brevi e a medio termine a Milano, fondata da Vito Semeraro. Gestisce pochi appartamenti selezionati lungo la M1 e viale Monza, da Porta Venezia a Bicocca.

- Commissione: 15% sugli incassi per l'affitto breve, 10% sul canone per il medio termine (30+ notti). Nessun costo fisso, disdetta con 30 giorni di preavviso.
- Servizi: gestione completa (annunci su Airbnb, Booking e Vrbo, prezzi dinamici, ospiti, check-in, pulizie, CIN, Alloggiati Web, imposta di soggiorno, report mensile), medio termine con contratti transitori, consulenza avvio, home staging, sito per prenotazioni dirette, marketing.
- Zone servite (solo Milano città): Porta Venezia e Lima, Stazione Centrale, Loreto/NoLo/Pasteur, viale Monza/Turro/Gorla, Precotto/Greco, Bicocca.
- Occupazione media nel medio termine: 95%. Voto medio degli ospiti su Airbnb: 4,9 su 5.
- Contatti: {MAIL}, telefono {TEL}, WhatsApp {WA}

## Pagine principali

- [Home]({SITE}/)
- [Servizi]({SITE}/servizi/)
- [Prezzi e cosa è incluso]({SITE}/prezzi/)
- [Calcola la rendita]({SITE}/calcola-rendita/)
- [Chi siamo]({SITE}/chi-siamo/)
- [Contatti]({SITE}/contatti/)

## Zone

{zl}

## Guide

{gl}
""")
    urls = ''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>' for p, pr in PAGES)
    open(os.path.join(DIST, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')

if __name__ == '__main__':
    build()
    print(len(PAGES), 'pagine')
