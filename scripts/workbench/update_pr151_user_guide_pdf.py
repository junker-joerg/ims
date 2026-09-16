"""Replace only the outdated output pages in the existing ten-page guide."""

from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "output/pdf/IMS-Bedienungsanleitung.pdf"
SCREENSHOT = (
    ROOT / "docs/handbook/images/"
    "windows_hundred_period_results_pr151_wide_2026-09-16.png"
)
GREEN = colors.HexColor("#17624b")
INK = colors.HexColor("#26323a")
MUTED = colors.HexColor("#52616b")
BODY = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=9.6, leading=14,
    textColor=INK, spaceAfter=0,
)
CAPTION = ParagraphStyle(
    "caption", parent=BODY, fontName="Helvetica-Oblique", fontSize=7.9,
    leading=10.5, textColor=MUTED,
)


def _paragraph(pdf: canvas.Canvas, text: str, y: float, *, style=BODY,
               after: float = 8) -> float:
    paragraph = Paragraph(text, style)
    width = 475
    _, height = paragraph.wrap(width, 1000)
    y -= height
    if y < 65:
        raise ValueError("PR151 guide content exceeds the page")
    paragraph.drawOn(pdf, 63, y)
    return y - after


def _section(pdf: canvas.Canvas, title: str, y: float) -> float:
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(GREEN)
    pdf.drawString(63, y - 12, title)
    return y - 24


def _screenshot(pdf: canvas.Canvas, y: float, *, width: float) -> float:
    image = ImageReader(SCREENSHOT)
    image_width, image_height = image.getSize()
    height = width * image_height / image_width
    y -= height
    if y < 65:
        raise ValueError("PR151 screenshot exceeds the page")
    pdf.drawImage(image, 63 + (475 - width) / 2, y, width, height,
                  preserveAspectRatio=True)
    return y - 8


def _page(number: int, title: str, draw_content) -> bytes:
    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=(595.2756, 841.8898), pageCompression=1)
    pdf.setFillColor(GREEN)
    pdf.rect(0, 824, 595.2756, 18, fill=1, stroke=0)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(INK)
    pdf.drawString(63, 784, title)
    pdf.setFont("Helvetica", 7.8)
    pdf.setFillColor(MUTED)
    pdf.drawString(63, 29, "IMS 1995-2026 | Bedienungsanleitung | Stand 2026-09-16")
    pdf.drawRightString(535, 29, f"{number} / 10")
    draw_content(pdf, 763)
    pdf.showPage()
    pdf.save()
    return stream.getvalue()


def _output_page(pdf: canvas.Canvas, y: float) -> None:
    y = _paragraph(
        pdf,
        "Fuer <b>vorbereitete 100-Perioden-Ketten</b> finden Sie den Output "
        "unter <b>Strategien &gt; Ergebnisse</b>. Waehlen Sie Kette und "
        "Fuenf-Perioden-Nachweis, tragen Sie Freigabe und Grund ein und "
        "bestaetigen Sie den fluechtigen Lauf.",
        y,
    )
    y = _screenshot(pdf, y, width=430)
    y = _paragraph(
        pdf,
        "Abbildung 4: Vorbereiteter 100-Perioden-Teststand. Diagramm und "
        "Tabelle zeigen denselben vorhandenen Versichererwert; der zweite "
        "Lauf hat denselben gespeicherten Prefix.",
        y, style=CAPTION, after=12,
    )
    y = _section(pdf, "So lesen und sichern Sie das Ergebnis", y)
    y = _paragraph(
        pdf,
        "1. Akteur, Kennzahl und gegebenenfalls Vektorposition waehlen. "
        "Die Tabelle zeigt alle 100 Perioden ohne neue Modellrechnung.<br/>"
        "2. Einen zweiten, gleich praefixierten Lauf danebenstellen. "
        "Das ist ein Vergleich, noch keine Kausalaussage.<br/>"
        "3. <b>ZIP herunterladen</b> liefert JSON, CSV und XLSX nur dann, "
        "wenn ein erneut gerechneter Lauf denselben Wirkungsdigest hat.",
        y, after=9,
    )
    _paragraph(
        pdf,
        "Der Browser speichert das 100er-Ergebnis nicht dauerhaft. "
        "Nach Neuladen ist es weg; sichern Sie das ZIP. Ein eigener neuer "
        "100er-Fall muss noch ausserhalb dieses Bedienwegs vorbereitet werden. "
        "Historische Vollgleichheit wird nicht behauptet.",
        y,
    )


def _benefit_page(pdf: canvas.Canvas, y: float) -> None:
    y = _paragraph(
        pdf,
        "Die deutsche Wiedervereinigung war das historische Anwendungsbeispiel, "
        "nicht die Grenze des Modells. Damals umfasste jeder Lauf 100 Perioden. "
        "In Periode 50 wurden VN[151] bis VN[200] aktiviert; eine "
        "staerkere Werbereaktion von VU[14] wurde als Allianz-Effekt "
        "untersucht.",
        y,
    )
    y = _paragraph(
        pdf,
        "Die Dissertation verglich Marktanteile, Praemien und Reserven vor "
        "und nach diesem Schock. Das sind Aussagen eines damaligen "
        "kuenstlichen Experiments, keine Rekonstruktion realer Marktzahlen "
        "und kein Vergleichsnachweis fuer die heutige Workbench.",
        y, after=12,
    )
    y = _screenshot(pdf, y, width=355)
    y = _paragraph(
        pdf,
        "Abbildung 8: Heutige 100-Perioden-Ergebnisansicht eines kleinen "
        "Teststands. Die historische Wiedervereinigungswirkung ist hier "
        "nicht nachgestellt.",
        y, style=CAPTION, after=12,
    )
    y = _section(pdf, "Was Sie heute damit tun koennen", y)
    y = _paragraph(
        pdf,
        "1. Eine vorbereitete Kette kontrolliert freigeben und ueber "
        "100 Perioden laufen lassen.<br/>"
        "2. Vorhandene VU-/VN-Zustandsfelder als Zeitreihe und Tabelle "
        "lesen, zwei passende Laeufe vergleichen.<br/>"
        "3. Das Ergebnis mit Herkunft und Digest als JSON/CSV/XLSX-ZIP "
        "fuer eigene Auswertungen sichern.",
        y, after=10,
    )
    _paragraph(
        pdf,
        "Noch nicht moeglich: einen neuen fachlichen Schock frei konfigurieren, "
        "die 100 Kandidaten gefuehrt erzeugen oder den 100er-Lauf dauerhaft "
        "ablegen. Auch Bilanz-, Solvency-II- und DORA-Aussagen sind keine "
        "heutigen Produktfunktionen. Installation: INSTALLATION.pdf.",
        y,
    )


def main() -> None:
    reader = PdfReader(GUIDE)
    if len(reader.pages) != 10:
        raise ValueError("Expected the existing ten-page user guide")
    replacements = {
        4: PdfReader(BytesIO(_page(5, "Seite 5 - Wo ist der Output?", _output_page))).pages[0],
        9: PdfReader(BytesIO(_page(10, "Seite 10 - Beispiel und heutiger Nutzen", _benefit_page))).pages[0],
    }
    writer = PdfWriter()
    for index, old in enumerate(reader.pages):
        writer.add_page(replacements.get(index, old))
    target = GUIDE.with_name("IMS-Bedienungsanleitung.pr151.tmp.pdf")
    with target.open("wb") as stream:
        writer.write(stream)
    if len(PdfReader(target).pages) != 10:
        raise ValueError("Updated guide must still have ten pages")
    os.replace(target, GUIDE)


if __name__ == "__main__":
    main()
