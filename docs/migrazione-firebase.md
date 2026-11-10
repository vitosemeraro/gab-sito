# Migrazione da Netsons a Firebase Hosting

Stato: codice pronto, Netsons ancora online. Ogni passo qui sotto si può fare senza fermare il sito,
tranne il cambio DNS (passo 5) e la disdetta (passo 7), che vanno fatti solo con l'ok di Vito.

## Cosa è già nel repo
- `firebase.json`: pubblica `src/dist`, URL con slash finale, redirect 301 delle vecchie pagine WordPress
  (stessi del `.htaccess`), header di sicurezza e cache. Verificato con l'emulatore: 38 pagine della sitemap a 200,
  file Search Console `google0b3463b7ea847862.html` e chiave IndexNow serviti, 404 personalizzata.
- Differenze rispetto al `.htaccess`: Firebase non ha il 410, quindi `wp-*`, `shop`, `cart` e le date dei vecchi
  articoli danno 404 (per Google è equivalente). Il redirect `?p=` / `?page_id=` sparisce (Firebase ignora la query).
  `www` → dominio senza www si imposta nella console quando si aggiunge il dominio.
- Modulo contatti: `WEB3FORMS_KEY` in `src/build.py`. Vuota = si usa ancora `contatti.php` (Netsons).
  Con la chiave il form manda a Web3Forms (gratis, 250 invii al mese) e poi a `/grazie/`; controllo di nome e
  telefono (almeno 6 cifre) nel browser, anti-spam con la casella nascosta `botcheck`.
- Workflow `pubblica.yml`: pubblica sul progetto Firebase `gab-sito` se c'è il secret `FIREBASE_SERVICE_ACCOUNT`, e continua a pubblicare su Netsons finché ci sono i secrets FTP.

## Passi
1. **Chiave Web3Forms** (fatto il 10/11/2026): su web3forms.com inserire vsemeraro@gmail.com (direttamente Gmail, così il form non
   dipende dalla mail del dominio), copiare la chiave in `WEB3FORMS_KEY`. Il form funziona subito anche su Netsons.
2. **Progetto Firebase** (fatto il 10/11/2026): progetto `gab-sito` (piano Spark, senza Analytics e Gemini), Hosting attivo,
   account di servizio `github-deploy@gab-sito.iam.gserviceaccount.com` con ruoli Firebase Hosting Admin e Service Usage Consumer.
3. **Secret GitHub** del repo: `FIREBASE_SERVICE_ACCOUNT` = chiave JSON di github-deploy (la crea Vito da Cloud Console > Service account > Chiavi).
   Al primo push il sito va online su https://gab-sito.web.app: controllarlo lì.
4. **Prima del DNS, la mail**: oggi `hello@gestione-affitti-brevi-milano.it` è un inoltro di cPanel verso Gmail.
   Spenta Netsons, l'inoltro sparisce. Sostituto gratuito: Cloudflare Email Routing (serve spostare i nameserver
   su Cloudflare, dove c'è già l'account di Web Analytics) oppure ImprovMX (bastano due record MX dove sta il DNS).
   Prima di toccare i nameserver copiare tutti i record della zona da cPanel (Zone Editor): MX, TXT (SPF,
   verifiche Google), eventuali sottodomini.
5. **Cambio DNS** (con ok di Vito): in Firebase "Aggiungi dominio personalizzato" per il dominio e per `www`
   (redirect al dominio), inserire i record A/TXT che indica Firebase. Il certificato arriva in qualche ora.
6. **Dopo il cambio**: Search Console resta verificata (file HTML), controllare form, redirect e IndexNow.
   Togliere i secrets FTP dal repo.
7. **Disdetta hosting Netsons** (con ok di Vito): solo l'hosting, NON il dominio se è registrato lì.
   Prima scaricare un backup di `public_html` (c'è anche `homestaged-AI/`, da spostare se serve ancora)
   e della vecchia copia WordPress `wp-old-2026-10-25/`.
