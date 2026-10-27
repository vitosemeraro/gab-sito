# Come aggiungere una guida

Crea un file `AAAA-MM-GG-slug.md` in questa cartella. La data è quella di pubblicazione: se è nel futuro, la guida esce da sola quella mattina tra le 6 e le 7. Lo slug diventa l'indirizzo `/guide/slug/`.

```
---
titolo: Titolo H1 della guida
titolo_seo: Titolo per Google, massimo 60 caratteri | GAB
descrizione: Meta description, 140-155 caratteri.
sommario: Una o due frasi sotto il titolo.
in_breve: La risposta diretta in 40-60 parole, testo semplice: è quella che leggono i motori AI.
aggiornato: AAAA-MM-GG (facoltativo)
bozza: si (facoltativo: non la pubblica)
---
Testo introduttivo.

## Prima sezione
Paragrafi, elenchi con "- ", tabelle con "|", **grassetto**, *corsivo*, [link](/prezzi/).

## Domande frequenti

### Domanda?
Risposta.
```

Le sezioni `##` formano l'indice; quella chiamata "Domande frequenti" diventa le FAQ con lo schema FAQPage.
