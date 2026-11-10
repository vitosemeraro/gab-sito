# Sito GAB Gestione Affitti Brevi

Sorgente di https://gestione-affitti-brevi-milano.it: sito statico generato da `src/build.py`.

- `src/build.py`: pagine, schema JSON-LD, sitemap, robots, llms.txt, .htaccess
- `src/content/guide/`: guide in Markdown con data di pubblicazione (vedi LEGGIMI.md)
- `foto2/`, `static/media/`, `src/fonts/`: immagini, video e font
- `tools/check_links.py`: controllo dei link interni
- `.github/workflows/pubblica.yml`: build, controllo link, pubblicazione su Firebase Hosting (e FTPS su Netsons finché ci sono i secrets) e IndexNow
- `firebase.json`: redirect, header e cache di Firebase Hosting (vedi `docs/migrazione-firebase.md`)

In locale: `pip install pillow && python src/build.py && cp -r static/. src/dist/`.

Firebase usa i secrets `FIREBASE_SERVICE_ACCOUNT` e `FIREBASE_PROJECT_ID`; Netsons i secrets `FTP_HOST`, `FTP_USER`, `FTP_PASSWORD` (da togliere dopo il passaggio).
