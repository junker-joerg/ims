"""Deterministic, editable SVG diagrams of the implemented AP5/AP7/AP8 core."""
from html import escape
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/handbook/images"
COLORS = {"retained": "#087c86", "extension": "#565bb4", "boundary": "#ac5710", "neutral": "#284966"}


def diagram(name: str, title: str, subtitle: str, boxes: list, edges: list, footer: str) -> None:
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 850" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}. {escape(footer)}</desc>',
               '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L8 3L0 6Z" fill="#476781"/></marker></defs>',
               '<rect width="1280" height="850" fill="#f6f9fc"/>',
               f'<text x="40" y="50" font-family="Arial,sans-serif" font-size="30" font-weight="700" fill="#102b46">{escape(title)}</text>',
               f'<text x="40" y="84" font-family="Arial,sans-serif" font-size="19" fill="#284966">{escape(subtitle)}</text>']
    for x1,y1,x2,y2,label in edges:
        content.append(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#476781" stroke-width="2" marker-end="url(#arrow)"/>')
        if label:
            content.append(f'<text x="{(x1+x2)/2+10}" y="{(y1+y2)/2-8}" font-family="Arial,sans-serif" font-size="17" fill="#284966">{escape(label)}</text>')
    for x,y,w,h,heading,lines,kind in boxes:
        color=COLORS[kind]
        content.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="white" stroke="{color}" stroke-width="2"/><rect x="{x}" y="{y}" width="6" height="{h}" rx="3" fill="{color}"/>')
        content.append(f'<text x="{x+20}" y="{y+32}" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="{color}">{escape(heading)}</text>')
        yy=y+63
        for line in lines:
            for part in wrap(line,width=int((w-40)/10)):
                content.append(f'<text x="{x+20}" y="{yy}" font-family="Arial,sans-serif" font-size="18" fill="#172e42">{escape(part)}</text>');yy+=26
        if yy>y+h+4:
            raise ValueError(f"Text exceeds box: {heading}")
    content.append(f'<text x="40" y="810" font-family="Arial,sans-serif" font-size="18" fill="#284966">{escape(footer)}</text></svg>')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/f"ap8_core_{name}.svg").write_text("\n".join(content)+"\n",encoding="utf-8")


def main() -> None:
    diagram("architecture", "IMS-Rechenkern · vom Experiment zum Nachweis", "Stand 06.10.2026 · AP8 alpha.11 · gemeinsame Marktquelle und unveränderte Rechenkanäle", [
        (40,125,365,175,"Endogene Entscheidungen",["Familien und Zuordnungen", "VU-Parameter, Maßnahmen und Antworten", "VN-Regel mit eigener Schwelle"],"retained"),
        (445,125,365,175,"Exogene Annahmen",["Risikozeilen, Schadenindikator", "Eintritt, Nachfrage, Ausfall, hypothetische Regulierung", "Ereigniszeit und Wirkungskanal"],"extension"),
        (850,125,390,175,"Quellen und Anfangsbestände",["Modellwährung, Seed, Horizont", "VU-/Spartenbücher und Kunden", "BaFin-Referenz: keine deutsche Direktmarkt-Kalibrierung"],"boundary"),
        (40,355,1200,105,"1 · Vollständigen Vertrag validieren",["AP5 contract.py / AP6 reference.py / AP7 shock_contract.py · bekannte Bezüge, Zeitfenster, Bilanz und Quellenbindung"],"neutral"),
        (40,515,365,200,"2 · Zwei Vergleichsseiten",["runner.py + shock_runner.py", "Identischer tatsächlicher Anfang P1–P5", "Kein partielles Ergebnis bei Vertragsfehlern"],"retained"),
        (445,515,365,200,"3 · Ausgeführte Modellkanäle",["Angebot → Antrag → Vertrag", "ICT-Arbeit und Kostenledger", "Getrennte Spartenbücher → Aggregate", "Bestehende Leben-/Krankenkerne"],"extension"),
        (850,515,390,200,"4 · Lesen und erklären",["explorer.py / transport.py", "6 Ansichten, Portfolio, Wiedergabe", "Filter ändern keine Rechnung", "Frische JSON-/Einzel-VU-Exporte mit Digestbindung"],"neutral"),
    ],[(220,300,220,355,""),(620,300,620,355,""),(1040,300,1040,355,""),(220,460,220,515,""),(405,610,445,610,""),(810,610,850,610,"")],"Teal: übernommene Vertragslogik · Violett: moderne Ergänzung · Orange: fachliche Grenze · Details im Handbuch.")
    diagram("period", "Eine AP7-Periode · der kausale Wirkungspfad", "24 Prozessstunden = 1 Modellperiode · Prozessplan wird vor der finanziellen Seitenauswertung erstellt",[
        (40,125,570,170,"1 · Vorperiodische Fertigstellungen",["Abgeschlossene Anträge aus P−1 werden in P wirksam.", "Altverträge bleiben bei wartendem Wechsel erhalten.", "Neue Lebenspolicen behalten ihre eigene Garantie."],"extension"),
        (670,125,570,170,"2 · Angebote und neue Anträge",["Familie + wirksame Parameter / Antwort → Angebot", "VN-Auswahl; Lebenspool deterministisch verteilt", "Noch kein neuer Vertrag allein durch einen Antrag"],"retained"),
        (40,350,570,190,"4 · FIFO-Arbeit auf Ressourcen",["shock_process.py: Anträge, Claims, Service", "Geteilte Kapazität, Teilfortschritt und Warteschlange", "Fertige Anträge werden erst in P+1 wirksam.", "Kosten nach deklarierten Trägergewichten, Summe 1"],"extension"),
        (670,350,570,190,"3 · Ereignisse und Antworten",["Zeitüberschneidung → transitive Abhängigkeiten", "Konkreten Ersatzpfad prüfen → verfügbare Stunden", "Gemeinsame Ressource einmal zählen", "Ereignis-/Antwortkosten genau einmal buchen"],"extension"),
        (40,600,570,155,"5 · Verträge, Risiko und Spartenbücher",["Beiträge nur beim wirksamen Vertrag", "Nichtleben: A = L + E; Aufwand ≠ Auszahlung", "Leben/Kranken: bestehende isolierte Kernverträge"],"retained"),
        (670,600,570,155,"6 · Aggregate und Nachweise",["VU-/Spartenzeilen summieren; Nenner offenlegen", "Snapshot P ist für VU in P+1 verfügbar.", "Claims/Service verändern keine Leistungszahlung."],"boundary"),
    ],[(610,210,670,210,""),(950,295,950,350,""),(670,450,610,450,""),(330,540,330,600,""),(610,675,670,675,"")],"Prozessplan → Buchungsadapter, keine zweite Ereignissimulation. Original-ESS-Aktionsmischung wird hier nicht nachgebildet.")
    diagram("deviations", "Original IMS und heutiger Markt · erhalten, geändert, offen", "Keine Behauptung einer vollständigen numerischen Identität mit dem historischen IMS/ESS",[
        (40,125,370,590,"Historische Referenz",["ESS.C: Aktionen nach Periode und logischer Zeit; optionale Subjektmischung", "IMS.E: aktive Anbieter; Vrvu01 / Vrvn06", "VN: Einzelakteure, historische Zufalls-Schadenerzeugung", "IMSDATA.C: VU-/VN-/BAV-Zustände und Aggregattabellen", "Historische Finanz- und Garantiestrukturen als Herkunft der bestehenden Portierungen"],"neutral"),
        (455,125,370,590,"Bewusst moderne Abbildung",["Explizite Verträge und getrennte Baseline/Variante", "Gebundene VU-Zufallszüge; keine myrndf-Identität", "Kohorten in stabiler ID-Reihenfolge; ganze Kohorte bei Kapazitätszulassung", "Deklarierte Schäden statt neuer historischer Schadenzüge im Markt", "AP7: ICT-Graph, FIFO, wirksame Anträge und deterministisches LV-Neugeschäft", "BaFin: empirische Beiträge + getrennte Workshop-Annahmen"],"extension"),
        (870,125,370,590,"Nicht nachgewiesen / offen",["Vollständiger C/Python-Markt-Gleichlauf", "Deutscher Top-40-Direktmarkt und echter Spartenmix", "Regulatorische Solvenz / SCR / MCR", "Dynamische Insolvenz, Konzerneliminierung, spartenübergreifende Finanzierung", "Claims-Queue → verzögerte Auszahlung", "Gespeicherte Kernpause und Fortsetzung", "Korrelation als kausal kalibrierter Kanal"],"boundary"),
    ],[(410,410,455,410,""),(825,410,870,410,"")],"Quellenstellen und Prüfgrenzen im Handbuch rechenkern.md; die UI-Mockups erweitern keinen Modellvertrag.")


if __name__ == "__main__":
    main()
