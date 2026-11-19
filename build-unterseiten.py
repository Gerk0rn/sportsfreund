#!/usr/bin/env python3
"""Erzeugt aus index.html die Unterseiten /kundenstimmen/, /ueber-mich/ usw.

Die Startseite bleibt die lange Seite mit allen Abschnitten. Jede Unterseite
enthält Kopf, Fußbereich und genau einen Abschnitt, mit eigenem Titel, eigener
Beschreibung und eigener kanonischer Adresse. So kann Google die Bereiche als
Sitelinks unter dem Suchergebnis anzeigen.

Nach jeder Änderung an index.html neu ausführen: python3 build-unterseiten.py
(Der Deploy-Workflow macht das vor dem Hochladen automatisch.)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://www.der-sports-freund.de/"

# Abschnitt-ID -> (Ordner, Menüname, Seitentitel, Beschreibung)
SEITEN = {
    "kundenstimmen": ("kundenstimmen", "Kundenstimmen",
        "Kundenstimmen – Der Sportsfreund, Personal Training in Bersenbrück",
        "Was Kundinnen und Kunden über das Personal Training mit Pascal Stempfle sagen: echte Erfahrungen aus Bersenbrück und Umgebung."),
    "ueber-mich": ("ueber-mich", "Über mich",
        "Über mich – Pascal Stempfle, Personal Trainer | Der Sportsfreund",
        "Pascal Stempfle ist seit 2015 Personal Trainer in Bersenbrück. Ausbildung, Motivation und wie er mit dir trainiert."),
    "personal-training": ("personal-training", "Personal Training",
        "Personal Training & Functional Training in Bersenbrück | Der Sportsfreund",
        "Personal Training im Studio, draußen oder bei dir zu Hause: individuelles Functional Training mit Pascal Stempfle in Bersenbrück."),
    "firmenfitness": ("betriebssport-firmenfitness", "Betriebssport & Firmenfitness",
        "Betriebssport & Firmenfitness in Bersenbrück | Der Sportsfreund",
        "Betriebssport für Unternehmen: gesündere, motiviertere Mitarbeiter und ein starkes Team. Firmenfitness mit Pascal Stempfle."),
    "kontakt": ("kontakt", "Kontakt & kostenlose Probestunde",
        "Kontakt & kostenlose Probestunde | Der Sportsfreund Bersenbrück",
        "Vereinbare deine kostenlose Probestunde mit Pascal Stempfle: Formular, Telefon 0176 63600587 oder E-Mail."),
}


def sektion(html, sid):
    m = re.search(r'\n<!-- =+ [^\n]*=+ -->\n<section[^>]*id="%s".*?</section>\n' % re.escape(sid), html, re.S) \
        or re.search(r'\n<section[^>]*id="%s".*?</section>\n' % re.escape(sid), html, re.S)
    if not m:
        raise SystemExit(f"Abschnitt #{sid} nicht gefunden")
    return m.group(0)


def anker_zu_seiten(html):
    """#abschnitt-Links auf die Unterseiten umbiegen, #start auf die Startseite."""
    for sid, (ordner, *_rest) in SEITEN.items():
        html = html.replace(f'href="#{sid}"', f'href="/{ordner}/"')
    return html.replace('href="#start"', 'href="/"')


def setze_meta(html, titel, beschreibung, url):
    html = re.sub(r"<title>.*?</title>", f"<title>{titel.replace('&', '&amp;')}</title>", html, count=1, flags=re.S)
    html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{beschreibung}">', html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', html, count=1)
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', html, count=1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{titel.replace("&", "&amp;")}">', html, count=1)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{beschreibung}">', html, count=1)
    return html


def main():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    start = index.index("<main>") + len("<main>")
    ende = index.index("</main>")
    for sid, (ordner, name, titel, beschreibung) in SEITEN.items():
        url = f"{BASE}{ordner}/"
        seite = index[:start] + "\n" + sektion(index, sid) + index[ende:]
        seite = anker_zu_seiten(setze_meta(seite, titel, beschreibung, url))
        # Brotkrumen für Google statt der Abschnittsliste der Startseite
        krumen = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Der Sportsfreund", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": name, "item": url}]}
        seite = re.sub(r'<script type="application/ld\+json">\n\{"@context": "https://schema.org", "@graph".*?</script>',
                       '<script type="application/ld+json">\n' + json.dumps(krumen, ensure_ascii=False) + "\n</script>",
                       seite, count=1, flags=re.S)
        ziel = ROOT / ordner / "index.html"
        ziel.parent.mkdir(exist_ok=True)
        ziel.write_text(seite, encoding="utf-8")
        print("geschrieben:", ziel.relative_to(ROOT))


if __name__ == "__main__":
    main()
