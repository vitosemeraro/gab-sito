# Sito GAB Gestione Affitti Brevi

Sorgente di https://gestione-affitti-brevi-milano.it: sito statico generato da `src/build.py`.

- `src/build.py`: pagine, schema JSON-LD, sitemap, robots, llms.txt, .htaccess
- `src/content/guide/`: guide in Markdown con data di pubblicazione (vedi LEGGIMI.md)
- `foto2/`, `static/media/`, `src/fonts/`: immagini, video e font
- `tools/check_links.py`: controllo dei link interni
- `.github/workflows/pubblica.yml`: build, controllo link, caricamento FTPS e IndexNow

In locale: `pip install pillow && python src/build.py && cp -r static/. src/dist/`.

Il caricamento usa i secrets `FTP_HOST`, `FTP_USER`, `FTP_PASSWORD` e `FTP_DIR` (di solito `public_html`).
