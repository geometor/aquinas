"""Compile the unbundled, granular Multi-Track Book Codex RST tree for St. Thomas Aquinas.

Generates:

* ``docsrc/index.rst`` (Author Home Page with ``.. collection:: :type: book``)
* ``docsrc/prooemium/{index,la,summary,notes}.rst`` & ``figure.svg``
* 6 Top-Level Books with ``:type: book``, ``:navigation: header``:

  * ``docsrc/super_boetium_de_trinitate/`` (6 articles: ``art_01``..``art_06``)
  * ``docsrc/analytica_posteriora/`` (11 lectiones: ``lect_01``..``lect_11``)
  * ``docsrc/de_anima/`` (5 lectiones: ``lect_01``..``lect_05``)
  * ``docsrc/physica/`` (6 lectiones: ``lect_01``..``lect_06``)
  * ``docsrc/metaphysica/`` (5 lectiones: ``lect_01``..``lect_05``)
  * ``docsrc/summa_theologiae/`` (4 articles: ``art_01``..``art_04``)

* ``docsrc/{concordance,bibliography,persons,glossary}.rst`` (Shared Apparatus at docsrc root)
"""

from __future__ import annotations

import html
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from geometor.aquinas.concordance import (
    get_repo_root,
    load_citations,
    load_concordance_document,
    load_english_section,
    load_glossary,
    load_latin_part,
    load_part_apparatus,
    load_persons,
    load_sources_manifest,
    slugify_apparatus_key,
    verify_codex_integrity,
)

# Strictly follow photon_platform.publish heading underline hierarchy:
# H1: =, H2: -, H3: ~, H4: ^
H1_CHAR = "="
H2_CHAR = "-"
H3_CHAR = "~"
H4_CHAR = "^"


def rst_heading(title: str, char: str) -> str:
    """Format an RST section heading with exact underline length (>= 4)."""
    clean = " ".join(title.splitlines()).strip()
    bar = char * max(len(clean), 4)
    return f"{clean}\n{bar}"


# Safe first-occurrence inline tagging rules per section (applied ONLY outside *...* and :role:`...`)
EN_TAG_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bindividual intelligible matter\b", re.I), "term:materia-intelligibilis-individualis"),
    (re.compile(r"\bcommon intelligible matter\b", re.I), "term:materia-intelligibilis-communis"),
    (re.compile(r"\bintelligible matter\b", re.I), "term:materia-intelligibilis"),
    (re.compile(r"\bsensible matter\b", re.I), "term:materia-sensibilis"),
    (re.compile(r"\bdesignated matter\b", re.I), "term:materia-signata"),
    (re.compile(r"\babstraction of form\b", re.I), "term:abstractio-formae"),
    (re.compile(r"\babstraction of the whole\b", re.I), "term:abstractio-totius"),
    (re.compile(r"\bintuitive formal abstraction\b", re.I), "term:abstractio-intuitiva"),
    (re.compile(r"\bturning to the phantasms\b", re.I), "term:conversio-ad-phantasmata"),
    (re.compile(r"\bterminate(?:s)? at the imagination\b", re.I), "term:terminari-ad-imaginationem"),
    (re.compile(r"\bcommon conceptions of the mind\b", re.I), "term:communes-animi-conceptiones"),
    (re.compile(r"\bagent intellect\b", re.I), "term:intellectus-agens"),
    (re.compile(r"\bsubject-genus\b", re.I), "term:genus-subiectum"),
    (re.compile(r"\bphantasms?\b", re.I), "term:phantasma"),
    (re.compile(r"\bquiddity\b", re.I), "term:quidditas"),
    (re.compile(r"\bcontinuum\b", re.I), "term:continuum"),
    (re.compile(r"\bAristotle\b"), "person:aristotle"),
    (re.compile(r"\bBoethius\b"), "person:boethius"),
    (re.compile(r"\bPlato\b"), "person:plato"),
    (re.compile(r"\bEuclid\b"), "person:euclid"),
    (re.compile(r"\bAvicenna\b"), "person:avicenna"),
    (re.compile(r"\bAverroes\b"), "person:averroes"),
    (re.compile(r"\bDemocritus\b"), "person:democritus"),
    (re.compile(r"\bPythagoras\b"), "person:pythagoras"),
    (re.compile(r"\bPtolemy\b"), "person:ptolemy"),
    (re.compile(r"\bThemistius\b"), "person:themistius"),
    (re.compile(r"\bSimplicius\b"), "person:simplicius"),
    (re.compile(r"\bAugustine\b"), "person:augustine"),
    (re.compile(r"\bHoenen\b"), "person:hoenen"),
    (re.compile(r"\bLonergan\b"), "person:lonergan"),
    (re.compile(r"\bHilbert\b"), "person:hilbert"),
    (re.compile(r"\bRussell\b"), "person:russell"),
    (re.compile(r"\bCajetan\b"), "person:cajetan"),
    (re.compile(r"\bPacioli\b"), "person:pacioli"),
]

LA_TAG_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bmateria[em]? intelligibil(?:is|em|i)\b", re.I), "term:materia-intelligibilis"),
    (re.compile(r"\bmateria[em]? sensibil(?:is|em|i)\b", re.I), "term:materia-sensibilis"),
    (re.compile(r"\bmateria[em]? signata[em]?\b", re.I), "term:materia-signata"),
    (re.compile(r"\babstractio(?:nem|ne)? formae\b", re.I), "term:abstractio-formae"),
    (re.compile(r"\babstractio(?:nem|ne)? totius\b", re.I), "term:abstractio-totius"),
    (re.compile(r"\bcommunes animi conceptiones\b", re.I), "term:communes-animi-conceptiones"),
    (re.compile(r"\bintellectus agens\b", re.I), "term:intellectus-agens"),
    (re.compile(r"\bphantasma(?:ta|tibus|tis)?\b", re.I), "term:phantasma"),
    (re.compile(r"\bquiddita(?:s|tem|tis|te)\b", re.I), "term:quidditas"),
    (re.compile(r"\bdignita(?:s|tes|tibus)\b", re.I), "term:dignitates"),
    (re.compile(r"\bsuppositio(?:nes|nibus)?\b", re.I), "term:suppositiones"),
    (re.compile(r"\bpetitio(?:nes|nibus)?\b", re.I), "term:petitiones"),
    (re.compile(r"\bAristotel(?:es|is|em|i)\b"), "person:aristotle"),
    (re.compile(r"\bBoeti(?:us|i|o|um)\b"), "person:boethius"),
    (re.compile(r"\bPlato(?:nis|nem|ni)?\b"), "person:plato"),
    (re.compile(r"\bEuclid(?:es|is)\b"), "person:euclid"),
    (re.compile(r"\bAvicenna(?:e)?\b"), "person:avicenna"),
    (re.compile(r"\bAverro(?:es|is)\b"), "person:averroes"),
    (re.compile(r"\bDemocrit(?:us|i|um)\b"), "person:democritus"),
    (re.compile(r"\bPythagor(?:as|ae|ici)\b"), "person:pythagoras"),
    (re.compile(r"\bPtolemae(?:us|i)\b"), "person:ptolemy"),
    (re.compile(r"\bThemisti(?:us|i)\b"), "person:themistius"),
    (re.compile(r"\bAugustin(?:us|i|o)\b"), "person:augustine"),
]

PROTECTED_SPAN_RE = re.compile(
    r"(?::[a-z]+:`[^`]+`|``[^`]+``|\*\*[^*]+\*\*|\*[^*\n]+\*)"
)


def normalize_inline_rst(text: str) -> str:
    """Clean whitespace and ensure balanced inline asterisks for Sphinx RST."""
    s = " ".join(text.strip().split())
    if s.count("*") % 2 != 0:
        s = s.replace("*", r"\*")
    return s


def enrich_inline_apparatus(
    text: str,
    rules: list[tuple[re.Pattern[str], str]],
    seen_in_section: set[str],
) -> str:
    """Tag first occurrences of key persons and terms per section outside protected spans."""
    parts = PROTECTED_SPAN_RE.split(text)
    matches = PROTECTED_SPAN_RE.findall(text)
    enriched_parts: list[str] = []

    for chunk in parts:
        cur = chunk
        for rx, spec in rules:
            if spec in seen_in_section:
                continue
            role, slug = spec.split(":", 1)

            def _repl(m: re.Match[str], r: str = role, sl: str = slug, sp: str = spec) -> str:
                seen_in_section.add(sp)
                word = m.group(0)
                return f":{r}:`{word} <{sl}>`"

            sub_segments = re.split(r"(:[a-z]+:`[^`]+`)", cur)
            new_segs: list[str] = []
            replaced = False
            for seg in sub_segments:
                if not replaced and not seg.startswith(":"):
                    seg2, n = rx.subn(_repl, seg, count=1)
                    if n:
                        replaced = True
                    new_segs.append(seg2)
                else:
                    new_segs.append(seg)
            cur = "".join(new_segs)
        enriched_parts.append(cur)

    out: list[str] = []
    for idx, p in enumerate(enriched_parts):
        out.append(p)
        if idx < len(matches):
            out.append(matches[idx])
    result = "".join(out)
    # Ensure `:role:` immediately followed by a letter/apostrophe gets `\ ` escaped
    result = re.sub(r"(:[a-z]+:`[^`]+`)(?=[A-Za-z0-9'])", r"\1\\ ", result)
    return result


def format_para_badge(p: dict[str, object]) -> str:
    """Format subtle critical-edition locus badge for synchronized Latin/English paragraphs."""
    title = str(p["title"])
    short_loc = title.split(",", 1)[-1].strip() if "," in title else title
    if "marietti_no" in p:
        return f"**[{short_loc} · Marietti #{p['marietti_no']}]**"
    return f"**[{short_loc}]**"


# Canonical 6 Top-Level Books Configuration
BOOKS_CONFIG = [
    {
        "slug": "super_boetium_de_trinitate",
        "order": 1,
        "nav_title": "On the Trinity",
        "breadcrumb_title": "On the Trinity",
        "title": "Commentary on Boethius's On the Trinity (Questions V–VI)",
        "subtitle": "Expositio super librum Boethii De Trinitate — De Divisione Scientiae Speculativae et Materia Intelligibili (c. 1257–1259)",
        "work_title": "Super Boetium De Trinitate",
        "date_composed": "c. 1257–1259",
        "editions": [
            "Sancti Thomae de Aquino, Expositio super librum Boethii De Trinitate, recensuit Bruno Decker (Leiden: E. J. Brill, 1959); Editio Leonina, Tom. L (Roma–Paris, 1992).",
            "Corpus Thomisticum (recognovit Enrique Alarcón, Pompaelone, Universitatis Studiorum Navarrensis): https://www.corpusthomisticum.org/cbt.html",
        ],
        "part_source": 1,
        "unit_prefix": "art",
        "sec_indices": list(range(6)),
        "legacy_part_id": "pars-1",
        "excerpt": "Aquinas's foundational treatise on the division of speculative science, distinguishing mathematical abstraction of form (abstractio formae) and intelligible matter from metaphysical separation (separatio), and establishing why mathematical judgment terminates at the imagination.",
    },
    {
        "slug": "analytica_posteriora",
        "order": 2,
        "nav_title": "Posterior Analytics",
        "breadcrumb_title": "Posterior Analytics",
        "title": "Commentary on Aristotle's Posterior Analytics",
        "subtitle": "Expositio libri Posteriorum Analyticorum (c. 1270–1272)",
        "work_title": "Expositio libri Posteriorum Analyticorum",
        "date_composed": "c. 1270–1272",
        "editions": [
            "Sancti Thomae Aquinatis Opera Omnia iussu impensaque Leonis XIII P. M. edita, Tom. I (Romae, 1882); Editio altera retractata, Tom. I* 2 (Roma–Paris, 1989).",
            "Corpus Thomisticum (recognovit Enrique Alarcón): https://www.corpusthomisticum.org/cpa1.html & https://www.corpusthomisticum.org/cpa2.html",
        ],
        "part_source": 2,
        "unit_prefix": "lect",
        "sec_indices": list(range(11)),
        "legacy_part_id": "pars-2",
        "excerpt": "Aquinas's exposition of Aristotle's theory of demonstration: supreme certitude in mathematics, subject-genus vs proper attributes, common conceptions vs postulates, why geometers do not demonstrate of dust diagrams, and the genesis of first principles from experience.",
    },
    {
        "slug": "de_anima",
        "order": 3,
        "nav_title": "On the Soul",
        "breadcrumb_title": "On the Soul",
        "title": "Commentary on Aristotle's On the Soul",
        "subtitle": "Sentencia libri De anima (c. 1267–1268)",
        "work_title": "Sentencia libri De anima",
        "date_composed": "c. 1267–1268",
        "editions": [
            "Sancti Thomae Aquinatis In Aristotelis Librum De Anima Commentarium, cura et studio P. F. Angeli M. Pirotta, O.P. (Taurini: Marietti, 1936; 1959); Editio Leonina, Tom. XLV.1 (Roma–Paris, 1984).",
            "Corpus Thomisticum (recognovit Enrique Alarcón): https://www.corpusthomisticum.org/can1.html, can2.html, can3.html",
        ],
        "part_source": 3,
        "unit_prefix": "lect",
        "sec_indices": list(range(5)),
        "legacy_part_id": "pars-3",
        "excerpt": "Aquinas's psychological foundations for mathematics: why the human soul never understands without turning to phantasms (conversio ad phantasmata), the distinction between physical flesh/bone and spatial continuum, and the hand as organ of organs.",
    },
    {
        "slug": "physica",
        "order": 4,
        "nav_title": "Physics & Heavens",
        "breadcrumb_title": "Physics & Heavens",
        "title": "Commentaries on Physics and On the Heavens",
        "subtitle": "In octo libros Physicorum et In libros De caelo et mundo expositio (c. 1268–1273)",
        "work_title": "In octo libros Physicorum & In libros De caelo et mundo expositio",
        "date_composed": "c. 1268–1273",
        "editions": [
            "Sancti Thomae Aquinatis Opera Omnia, Editio Leonina, Tom. II: Commentaria in octo libros Physicorum Aristotelis (Romae, 1884; ed. Maggiòlo, Taurini: Marietti, 1954).",
            "Sancti Thomae Aquinatis Opera Omnia, Editio Leonina, Tom. III: In libros Aristotelis De caelo et mundo expositio (Romae, 1886).",
            "Corpus Thomisticum (recognovit Enrique Alarcón): https://www.corpusthomisticum.org/cpy012.html, cpy03.html, cpy05.html, ccm1.html, ccm2.html",
        ],
        "part_source": 4,
        "unit_prefix": "lect",
        "sec_indices": list(range(6)),
        "legacy_part_id": "pars-4",
        "excerpt": "Aquinas's physical doctrine on mathematical entities: abstrahentium non est mendacium (no falsehood in abstraction), immobile place grounding rigid translation, the impossibility of composing a continuum from indivisible points, and three-dimensional magnitude.",
    },
    {
        "slug": "metaphysica",
        "order": 5,
        "nav_title": "Metaphysics",
        "breadcrumb_title": "Metaphysics",
        "title": "Commentary on Aristotle's Metaphysics",
        "subtitle": "Sententia super Metaphysicam (c. 1270–1272)",
        "work_title": "Sententia super Metaphysicam",
        "date_composed": "c. 1270–1272",
        "editions": [
            "Sancti Thomae Aquinatis In duodecim libros Metaphysicorum Aristotelis expositio, ed. M.-R. Cathala et R. M. Spiazzi (Taurini: Marietti, 1950).",
            "Corpus Thomisticum (recognovit Enrique Alarcón): https://www.corpusthomisticum.org/cmp05.html, cmp07.html, cmp09.html",
        ],
        "part_source": 5,
        "unit_prefix": "lect",
        "sec_indices": list(range(5)),
        "legacy_part_id": "pars-5",
        "excerpt": "Aquinas's metaphysical pinnacle of geometric epistemology: individual vs common intelligible matter, the derivation of actuality from motion, and the famous revelation of heuristic discovery: geometers discover truth by dividing figures in act (Euclid I.32 and III.31).",
    },
    {
        "slug": "summa_theologiae",
        "order": 6,
        "nav_title": "Summa Theologiae",
        "breadcrumb_title": "Summa Theologiae",
        "title": "Summa Theologiae and Disputed Questions",
        "subtitle": "Summa Theologiae et Quaestiones Disputatae de Potentia et de Veritate (c. 1256–1273)",
        "work_title": "Summa Theologiae, Quaestiones Disputatae de Potentia et de Veritate",
        "date_composed": "c. 1256–1273",
        "editions": [
            "Sancti Thomae Aquinatis Summa Theologiae, Prima Pars, Editio Leonina, Tom. IV–V (Romae, 1888–1889).",
            "Sancti Thomae Aquinatis Quaestiones disputatae de potentia Dei, ed. P. Bazzi et al. (Taurini: Marietti, 1953); Quaestiones disputatae de veritate, Editio Leonina, Tom. XXII (Romae, 1970–1976).",
            "Corpus Thomisticum (recognovit Enrique Alarcón): https://www.corpusthomisticum.org/sth1003.html, sth1084.html, qdp7.html, qdv10.html",
        ],
        "part_source": 5,
        "unit_prefix": "art",
        "sec_indices": [5, 6, 7, 8],
        "legacy_part_id": None,
        "excerpt": "Aquinas's mature theological syntheses: Ipsum Esse as the actuality of all acts, the geometer's infinite line, turning to phantasms in the Summa Theologiae, and the origin of indemonstrable principles in De Potentia and De Veritate.",
    },
]


def build_svg_prooemium() -> str:
    """Generate master SVG vector diagram for Prooemium."""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <defs>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#d4af37"/>
    </linearGradient>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00d2ff"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
  </defs>
  <!-- Background Grid & Axes -->
  <line x1="60" y1="180" x2="540" y2="180" stroke="#1e293b" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="300" y1="40" x2="300" y2="320" stroke="#1e293b" stroke-width="1" stroke-dasharray="4,4"/>
  <!-- Primary Circle in Materia Intelligibilis -->
  <circle cx="300" cy="180" r="110" fill="none" stroke="url(#cyanGrad)" stroke-width="2"/>
  <!-- Inscribed Equilateral Triangle -->
  <polygon points="300,70 395.26,235 204.74,235" fill="none" stroke="url(#goldGrad)" stroke-width="2"/>
  <!-- Inscribed Pentagram / Golden Ratio Division -->
  <line points="300,70 358.78,250.9" stroke="#64748b" stroke-width="1" stroke-dasharray="3,3"/>
  <circle cx="300" cy="180" r="4" fill="#f59e0b"/>
  <!-- Golden Section Division Line -->
  <line x1="190" y1="235" x2="410" y2="235" stroke="#f59e0b" stroke-width="1.5"/>
  <circle cx="300" cy="70" r="4.5" fill="#00d2ff"/>
  <circle cx="395.26" cy="235" r="4.5" fill="#00d2ff"/>
  <circle cx="204.74" cy="235" r="4.5" fill="#00d2ff"/>
  <!-- Labels -->
  <text x="300" y="55" fill="#f8fafc" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">A (Vertex Intellectualis)</text>
  <text x="415" y="242" fill="#cbd5e1" font-size="12" font-family="system-ui, sans-serif">B</text>
  <text x="185" y="242" fill="#cbd5e1" font-size="12" font-family="system-ui, sans-serif">C</text>
  <text x="300" y="172" fill="#d4af37" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">Centrum Cognitionis</text>
  <text x="300" y="325" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">PROOEMIUM · Scientia Mathematica et Materia Intelligibilis</text>
</svg>"""


def build_unit_svg(unit_key: str, title: str, canonical_id: str) -> str:
    """Generate a clean, mathematically thematic SVG diagram for an atomic leaf page."""
    if "art_01" in unit_key and "trinitate" in unit_key:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <circle cx="230" cy="200" r="85" fill="#0284c7" fill-opacity="0.12" stroke="#00d2ff" stroke-width="2"/>
  <circle cx="370" cy="200" r="85" fill="#d97706" fill-opacity="0.12" stroke="#f59e0b" stroke-width="2"/>
  <circle cx="300" cy="115" r="85" fill="#7c3aed" fill-opacity="0.12" stroke="#a855f7" stroke-width="2"/>
  <text x="300" y="80" fill="#c084fc" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Metaphysica / Theologia</text>
  <text x="300" y="98" fill="#94a3b8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">(Sine materia et motu)</text>
  <text x="180" y="215" fill="#38bdf8" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Physica</text>
  <text x="180" y="233" fill="#94a3b8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">(Cum materia sensibili et motu)</text>
  <text x="420" y="215" fill="#fbbf24" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Mathematica</text>
  <text x="420" y="233" fill="#94a3b8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">(In materia intelligibili sine motu)</text>
  <circle cx="300" cy="175" r="5" fill="#f8fafc"/>
  <text x="300" y="325" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">{canonical_id} · Triplex Divisio Scientiae Speculativae</text>
</svg>"""

    if "art_03" in unit_key and "trinitate" in unit_key:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <defs>
    <pattern id="brassPattern" width="12" height="12" patternUnits="userSpaceOnUse">
      <path d="M0 12 L12 0 M6 18 L18 6 M-6 6 L6 -6" stroke="#78350f" stroke-width="1"/>
    </pattern>
  </defs>
  <circle cx="180" cy="170" r="75" fill="url(#brassPattern)" stroke="#b45309" stroke-width="2.5"/>
  <text x="180" y="275" fill="#f59e0b" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Circulus Aeneus</text>
  <text x="180" y="295" fill="#94a3b8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">(Materia Sensibilis &amp; Mutabilitas)</text>
  <path d="M280 170 L340 170" stroke="#64748b" stroke-width="2" stroke-dasharray="4,4"/>
  <polygon points="345,170 335,165 335,175" fill="#64748b"/>
  <text x="310" y="155" fill="#38bdf8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">Abstractio Formae</text>
  <circle cx="440" cy="170" r="75" fill="none" stroke="#00d2ff" stroke-width="2.5"/>
  <circle cx="440" cy="170" r="3.5" fill="#00d2ff"/>
  <line x1="440" y1="170" x2="515" y2="170" stroke="#00d2ff" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="477" y="162" fill="#38bdf8" font-size="12" font-family="system-ui, sans-serif">radius r</text>
  <text x="440" y="275" fill="#38bdf8" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Circulus Mathematicus</text>
  <text x="440" y="295" fill="#94a3b8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">(In Materia Intelligibili)</text>
  <text x="300" y="335" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">{canonical_id} · Abstractio Formae a Materia Sensibili</text>
</svg>"""

    if "art_06" in unit_key and "trinitate" in unit_key:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <ellipse cx="440" cy="170" rx="110" ry="85" fill="#0f172a" stroke="#0284c7" stroke-width="1.5" stroke-dasharray="6,4"/>
  <text x="440" y="110" fill="#38bdf8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">IMAGINATIO</text>
  <polygon points="440,135 505,215 375,215" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <circle cx="440" cy="135" r="3" fill="#f59e0b"/>
  <circle cx="505" cy="215" r="3" fill="#f59e0b"/>
  <circle cx="375" cy="215" r="3" fill="#f59e0b"/>
  <circle cx="130" cy="170" r="45" fill="#1e1b4b" stroke="#818cf8" stroke-width="2"/>
  <text x="130" y="165" fill="#c7d2fe" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">INTELLECTUS</text>
  <text x="130" y="185" fill="#a5b4fc" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">Iudicium</text>
  <path d="M185 170 L320 170" stroke="#f8fafc" stroke-width="2"/>
  <polygon points="328,170 318,165 318,175" fill="#f8fafc"/>
  <text x="255" y="155" fill="#f8fafc" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">terminari ad</text>
  <text x="300" y="325" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">{canonical_id} · Iudicium Mathematicum Terminatur ad Imaginationem</text>
</svg>"""

    if "lect_03" in unit_key and "posteriora" in unit_key:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <path d="M140 240 A160 160 0 0 1 460 240 Z" fill="#0284c7" fill-opacity="0.08" stroke="#00d2ff" stroke-width="2"/>
  <line x1="140" y1="240" x2="460" y2="240" stroke="#f59e0b" stroke-width="2"/>
  <line x1="140" y1="240" x2="260" y2="92" stroke="#f8fafc" stroke-width="2"/>
  <line x1="460" y1="240" x2="260" y2="92" stroke="#f8fafc" stroke-width="2"/>
  <path d="M248 107 L263 119 L275 104" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
  <circle cx="300" cy="240" r="3.5" fill="#00d2ff"/>
  <line x1="300" y1="240" x2="260" y2="92" stroke="#64748b" stroke-width="1" stroke-dasharray="3,3"/>
  <circle cx="140" cy="240" r="4.5" fill="#f59e0b"/>
  <circle cx="460" cy="240" r="4.5" fill="#f59e0b"/>
  <circle cx="260" cy="92" r="4.5" fill="#f8fafc"/>
  <text x="120" y="248" fill="#f59e0b" font-size="14" font-family="system-ui, sans-serif" font-weight="600">A</text>
  <text x="475" y="248" fill="#f59e0b" font-size="14" font-family="system-ui, sans-serif" font-weight="600">B</text>
  <text x="260" y="75" fill="#f8fafc" font-size="14" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">C (Angulus Rectus = 90°)</text>
  <text x="300" y="260" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">O (Centrum)</text>
  <text x="300" y="325" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">{canonical_id} · Triangulus in Semicirculo Inscriptus (Euclides III.31)</text>
</svg>"""

    if "lect_09" in unit_key and "posteriora" in unit_key:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <path d="M120 120 Q200 130 300 115 T480 125" fill="none" stroke="#78350f" stroke-width="4" stroke-dasharray="6,4"/>
  <text x="300" y="85" fill="#d97706" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Linea in Pulvere Descripta</text>
  <text x="300" y="105" fill="#94a3b8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">(Sensibilis, imperfecta, curva)</text>
  <line x1="120" y1="220" x2="480" y2="220" stroke="#00d2ff" stroke-width="2.5"/>
  <circle cx="120" cy="220" r="4.5" fill="#00d2ff"/>
  <circle cx="480" cy="220" r="4.5" fill="#00d2ff"/>
  <circle cx="300" cy="220" r="4" fill="#f8fafc"/>
  <text x="300" y="255" fill="#38bdf8" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Linea Intelligibilis Signata</text>
  <text x="300" y="275" fill="#94a3b8" font-size="11" font-family="system-ui, sans-serif" text-anchor="middle">(Longitudo sine latitudine pura)</text>
  <text x="120" y="205" fill="#00d2ff" font-size="13" font-family="system-ui, sans-serif">P₁</text>
  <text x="480" y="205" fill="#00d2ff" font-size="13" font-family="system-ui, sans-serif">P₂</text>
  <text x="300" y="325" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">{canonical_id} · Non Demonstrat per Lineam in Pulvere Descriptam</text>
</svg>"""

    if "lect_05" in unit_key and "metaphysica" in unit_key:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <polygon points="180,240 380,240 300,100" fill="#0284c7" fill-opacity="0.1" stroke="#00d2ff" stroke-width="2"/>
  <line x1="380" y1="240" x2="510" y2="240" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="380" y1="240" x2="500" y2="100" stroke="#f8fafc" stroke-width="2"/>
  <path d="M360 240 A20 20 0 0 1 370 225" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
  <path d="M380 220 A20 20 0 0 1 400 215" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="160" y="248" fill="#cbd5e1" font-size="14" font-family="system-ui, sans-serif">A</text>
  <text x="375" y="260" fill="#cbd5e1" font-size="14" font-family="system-ui, sans-serif">B / C</text>
  <text x="295" y="85" fill="#cbd5e1" font-size="14" font-family="system-ui, sans-serif">C'</text>
  <text x="520" y="245" fill="#f59e0b" font-size="14" font-family="system-ui, sans-serif">D</text>
  <text x="510" y="95" fill="#f8fafc" font-size="14" font-family="system-ui, sans-serif">E (Parallela)</text>
  <text x="300" y="300" fill="#d4af37" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">Divisio in Actu: Statim Manifestum Est Videnti (Euclides I.32)</text>
  <text x="300" y="325" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">{canonical_id} · Inventio Veritatis Geometricae Dividendo</text>
</svg>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" height="auto">
  <rect width="600" height="360" rx="8" fill="#0c1017" stroke="#1e293b" stroke-width="1.5"/>
  <defs>
    <linearGradient id="geomGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00d2ff"/>
      <stop offset="50%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#d4af37"/>
    </linearGradient>
  </defs>
  <line x1="80" y1="180" x2="520" y2="180" stroke="#1e293b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <line x1="300" y1="50" x2="300" y2="310" stroke="#1e293b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <circle cx="300" cy="180" r="105" fill="none" stroke="#334155" stroke-width="1.2"/>
  <circle cx="300" cy="180" r="70" fill="#0284c7" fill-opacity="0.08" stroke="url(#geomGrad)" stroke-width="2"/>
  <line x1="160" y1="110" x2="440" y2="250" stroke="#f59e0b" stroke-width="1.8"/>
  <line x1="160" y1="250" x2="440" y2="110" stroke="#00d2ff" stroke-width="1.8"/>
  <circle cx="300" cy="180" r="4.5" fill="#f8fafc"/>
  <circle cx="230" cy="145" r="4" fill="#00d2ff"/>
  <circle cx="370" cy="215" r="4" fill="#00d2ff"/>
  <circle cx="230" cy="215" r="4" fill="#f59e0b"/>
  <circle cx="370" cy="145" r="4" fill="#f59e0b"/>
  <text x="300" y="75" fill="#f8fafc" font-size="13" font-family="system-ui, sans-serif" text-anchor="middle" font-weight="600">{html.escape(title[:45])}</text>
  <text x="300" y="325" fill="#94a3b8" font-size="12" font-family="system-ui, sans-serif" text-anchor="middle">{canonical_id} · Scientia Mathematica et Materia Intelligibilis</text>
</svg>"""


def build_author_index(docsrc_dir: Path, books: list[dict[str, Any]]) -> None:
    """Write docsrc/index.rst (Author Home Page)."""
    lines = [
        ":site_title: St. Thomas Aquinas",
        "",
        ".. _aquinas-index:",
        ".. _scientia-mathematica-index:",
        "",
        ".. container:: author-overline",
        "",
        "   the works of",
        "",
        rst_heading("St. Thomas Aquinas", H1_CHAR),
        "",
        "The mission of this project is to capture a semantic digital library of the works of :person:`St. Thomas Aquinas <aquinas>` (1225–1274), the Dominican theologian and philosopher whose commentaries on Aristotle and Boethius established the classical doctrine of mathematical abstraction (*abstractio formae*), intelligible matter (*materia intelligibilis*), and the epistemic certitude of geometry.",
        "",
        ".. collection::",
        "   :type: book",
        "   :sort: order",
        "",
        ".. toctree::",
        "   :hidden:",
        "   :maxdepth: 2",
        "",
    ]
    for b in books:
        lines.append(f"   {b['slug']}/index")
    lines.extend([
        "   prooemium/index",
        "   concordance",
        "   bibliography",
        "   persons",
        "   glossary",
        "   usage/index",
        "   about/index",
        "   log/index",
        "   modules/index",
        "",
    ])
    (docsrc_dir / "index.rst").write_text("\n".join(lines), encoding="utf-8")


def build_prooemium(docsrc_dir: Path) -> None:
    """Write docsrc/prooemium/{index,la,summary,notes}.rst and figure.svg."""
    pdir = docsrc_dir / "prooemium"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "figure.svg").write_text(build_svg_prooemium(), encoding="utf-8")

    tracks_frontmatter = ":tracks: English: index | Latin: la | Summary: summary | Notes: notes"

    en_lines = [
        ":title: Introduction — Aquinas's Philosophy of Mathematical Science",
        ":layout: book",
        ":canonical_id: Prooemium",
        ":folio: Prooemium",
        tracks_frontmatter,
        "",
        ".. _prooemium:",
        ".. _prooemium-en:",
        "",
        rst_heading("Introduction — Aquinas's Philosophy of Mathematical Science", H1_CHAR),
        "",
        ".. rubric:: *Intelligible Matter, Constructive Imagination, and the Architecture of Geometric Truth*",
        "",
        ".. folio:: Prooemium",
        "",
        ".. figure:: figure.svg",
        "   :alt: Aquinas Philosophy of Geometry",
        "   :align: center",
        "",
        rst_heading("1. Why St. Thomas Aquinas Matters to Constructive Geometry", H2_CHAR),
        "",
        "Across the history of Western mathematics and philosophy, few problems have proved deeper than the paradox of geometric exactitude and necessity. A circle traced by a brass compass upon parchment or rendered as pixels upon a screen is sensibly imperfect, mutable, and contingent; yet :person:`Euclid <euclid>`\\ 's theorems concerning the circle, the equilateral triangle, the angle in a semicircle, and the division of a segment in extreme and mean ratio possess rigorous, timeless necessity. If one follows :person:`Plato <plato>`, mathematical figures must subsist as separate eternal entities outside the physical world; if one follows radical empiricism, geometric axioms degrade into approximate generalizations from rough measurements; if one follows modern pure formalism (:person:`David Hilbert <hilbert>`) or logicism (:person:`Bertrand Russell <russell>`), geometry is severed from spatial intuition altogether and reduced to uninterpreted postulational syntax.",
        "",
        "In the thirteenth century, :person:`St. Thomas Aquinas <aquinas>` (1225–1274), building upon :person:`Aristotle <aristotle>`, :person:`Boethius <boethius>`, and :person:`Euclid <euclid>`, forged a luminous middle path that resolves this trilemma without sacrificing either deductive rigor or objective spatial reality. As recovered in the twentieth century by the Dutch Jesuit physicist and philosopher :person:`Peter Hoenen <hoenen>` (:cite:`*De Noetica Geometriae*, 1954 <hoenen:1954>`; :cite:`*La théorie du jugement*, 1946 <hoenen:1946>`) and extended by :person:`Bernard Lonergan <lonergan>` (:cite:`*Verbum*, 1946–1949 <lonergan:1946:verbum>`; :cite:`*Insight*, 1957 <lonergan:1957:insight>`), Aquinas's philosophy of mathematics rests upon five interconnected pillars assembled in full in the five Parts of this Codex.",
        "",
        rst_heading("2. The Five Pillars of the Codex", H2_CHAR),
        "",
        "1. **Abstraction of Form and Intelligible Matter (Super Boetium De Trinitate, qq. 5–6)**: In Question 5, Article 3 (:ref:`Pars I, s3 <pars-1-s3-en>`), Aquinas distinguishes the intellect's two fundamental operations—:term:`simple apprehension <simplex-apprehensio>` of essence and :term:`composition and division <compositio-et-divisio>` looking to :term:`act of being <ipsum-esse>`—to contrast metaphysical :term:`separation <separatio>` with natural :term:`abstraction of the whole <abstractio-totius>` and mathematical :term:`abstraction of form <abstractio-formae>`. Because continuous quantity inheres in corporeal substance ontologically prior to sensible qualities (heat, color, weight), the geometer abstracts dimensional figure from all :term:`sensible matter <materia-sensibilis>` while retaining :term:`intelligible matter <materia-intelligibilis>`—continuous spatial extension. And in Question 6, Article 2 (:ref:`Pars I, s6 <pars-1-s6-en>`), Aquinas establishes his decisive methodological law: whereas natural judgment terminates at external sense and metaphysical judgment at pure intellect, mathematical judgment must :term:`terminate at the imagination <terminari-ad-imaginationem>`.",
        "",
        "2. **Supreme Demonstrative Certitude and Euclidean Principles (Posterior Analytics)**: In his mature commentary on :person:`Aristotle <aristotle>`\\ 's *Posterior Analytics* (:ref:`Pars II <pars-2-en>`), Aquinas explains why mathematics alone among human sciences achieves the *certissimus modus demonstrationis* (Lib. I, lect. 1), maps out the tripartite structure of :term:`subject-genus <genus-subiectum>`, :term:`proper attributes <passiones>`, and :term:`common conceptions of the mind <communes-animi-conceptiones>` vs. :term:`hypotheses <suppositiones>` and :term:`postulates <petitiones>` (Lib. I, lect. 5 & 18–19), proves why the geometer demonstrates not of rough lines drawn in dust (*non demonstrat per lineam in pulvere descriptam*) but of the intelligible lines signified by them (Lib. I, lect. 19), distinguishes the arithmetical unit without position from the geometric :term:`point having position <unitas-et-punctus>` (Lib. I, lect. 42), and traces the genesis of :term:`first principles <intellectus-principiorum>` from sense, memory, and :term:`experience <experimentum>` (Lib. II, lect. 20).",
        "",
        "3. **Turning to the Phantasm in Abstract Geometry (Sentencia libri De anima)**: Expounding *De Anima* (:ref:`Pars III <pars-3-en>`), Aquinas shows why *nequaquam sine phantasmate intelligit anima*—the human soul never understands even abstract mathematical truths without :term:`turning to the phantasms <conversio-ad-phantasmata>` (Lib. III, lect. 12, Pirotta nos. 770–777). Just as :term:`the snub <simum-et-curvum>` (*simum*) includes sensible flesh in its ratio, *rectum* (the straight) includes the spatial :term:`continuum <continuum>` (Lib. III, lect. 8). When proving a theorem about an indeterminate triangle, the geometer places a determinate finite triangle before the eyes of the imagination while abstracting from its accidental scale.",
        "",
        "4. **Realism of Abstraction, Continuum, and Geometric Motion (Physics & De Caelo)**: In *Physics* II, lect. 3 (:ref:`Pars IV, s1 <pars-4-s1-en>`), Aquinas defends :term:`abstrahentium non est mendacium <abstrahentium-non-est-mendacium>`—there is no falsehood in those who abstract geometric boundaries from physical bodies. In *Physics* IV, lect. 7 (:ref:`Pars IV, s3 <pars-4-s3-en>`), he shows how :term:`immobile place <locus-immobilis>` and congruence emerge from local translation; in *Physics* VI, lect. 1 (:ref:`Pars IV, s4 <pars-4-s4-en>`), he rigorously proves that no continuum can be composed of indivisible points; and in *De Caelo* I, lect. 2 (:ref:`Pars IV, s5 <pars-4-s5-en>`), he clarifies how geometers speak imaginatively of a moving point describing a line.",
        "",
        "5. **Individual Intelligible Matter, Heuristic Division in Act, and Ipsum Esse (Metaphysics & Systematic Works)**: Culminating in *Metaphysics* VII, lect. 10–11 (:ref:`Pars V, s2–s3 <pars-5-s2-en>`), Aquinas distinguishes :term:`individual intelligible matter <materia-intelligibilis-individualis>` (whereby many mathematical circles of equal or unequal radius coexist and intersect) from :term:`common intelligible matter <materia-intelligibilis-communis>`. In *Metaphysics* IX, lect. 10 (:ref:`Pars V, s5 <pars-5-s5-en>`, Cathala #1894), he unveils the secret of geometric discovery (:term:`divisio figurarum in actu <divisio-in-actu>`): geometers discover truth by dividing figures in act—drawing the parallel line for :cite:`Euclid I.32 <euclid:elements:I.32>` or the radius for :cite:`Euclid III.31 <euclid:elements:III.31>`—making what was latent in potency immediately luminous to intellectual vision (*statim manifestum est videnti*). Finally, *Summa Theologiae* I (:ref:`Pars V, s6–s7 <pars-5-s6-en>`), *De Potentia* q. 7 a. 2 (:ref:`Pars V, s8 <pars-5-s8-en>`), and *De Veritate* q. 10 a. 6 (:ref:`Pars V, s9 <pars-5-s9-en>`) anchor the entire edifice in the light of the :term:`agent intellect <intellectus-agens>` and :term:`ipsum esse <ipsum-esse>`, the actuality of all acts.",
        "",
        rst_heading("3. Editorial Principles & Relation to the GEOMETOR Canon", H2_CHAR),
        "",
        "Every Latin text in this codex (37 unabridged sections, 613 paragraphs, 65,402 Latin words) is reproduced diplomatically from public-domain critical editions (Leonine, Marietti Pirotta/Cathala–Spiazzi, and Decker via the :cite:`Corpus Thomisticum <corpus-thomisticum>`) with cryptographic SHA-256 verification in ``resources/aquinas/sources_manifest.json``. Facing English tracks provide complete, 1-to-1 paragraph-synchronized scholarly translations alongside analytical summaries, GEOMETOR commentary, and a 100% concordance of all 78 Thomistic citation keys in :person:`Peter Hoenen <hoenen>`\\ 's :cite:`*De Noetica Geometriae* <hoenen:1954>` and :person:`Luca Pacioli <pacioli>`\\ 's :cite:`*De Divina Proportione* <pacioli:1509>`.",
        "",
        ".. toctree::",
        "   :hidden:",
        "",
        "   la",
        "   summary",
        "   notes",
        "",
    ]
    (pdir / "index.rst").write_text("\n".join(en_lines), encoding="utf-8")

    la_lines = [
        ":title: Prooemium Editoris — De Scientia Mathematica apud S. Thomam",
        ":layout: book",
        ":canonical_id: Prooemium",
        ":folio: Prooemium",
        tracks_frontmatter,
        "",
        ".. _prooemium-la:",
        "",
        rst_heading("Prooemium Editoris — De Scientia Mathematica et Materia Intelligibili", H1_CHAR),
        "",
        ".. rubric:: *Praefatio Critica et Sententiae Capitales Sancti Thomae de Aquino*",
        "",
        ".. folio:: Prooemium",
        "",
        rst_heading("1. Ratio Huius Codicis", H2_CHAR),
        "",
        "Hic codex colligit atque integre exhibet triginta septem lectiones et articulos capitales quibus :person:`Sanctus Thomas de Aquino <aquinas>` (1225–1274) naturam, obiectum, methodum et certitudinem scientiae mathematicae fundavit. Omnes textus Latini (613 paragraphi) de verbo ad verbum ex editionibus criticis Leonina, Marietti (:person:`Pirotta <pirotta>`, :person:`Cathala <cathala>`) et :person:`Decker <decker>` (secundum recensionem :cite:`Corporis Thomistici <corpus-thomisticum>`) sine ulla immutatione deprompti sunt, addita plena concordantia omnium septuaginta octo locorum Thomisticorum quos :person:`Petrus Hoenen, S.I. <hoenen>` in opere suo :cite:`*De Noetica Geometriae* (1954) <hoenen:1954>` allegavit.",
        "",
        rst_heading("2. Sententiae Capitales S. Thomae in Hoc Codice Contenta", H2_CHAR),
        "",
        "* **De Materia Intelligibili et Duplici Operatione Intellectus** (:ref:`Super Boetium De Trinitate, q. 5, a. 3 <pars-1-s3-la>`): *« Substantia autem, quae est materia intelligibilis quantitatis, potest esse sine quantitate; unde considerare substantiam sine quantitate magis pertinet ad genus separationis quam abstractionis. Sic ergo in operatione intellectus triplex distinctio invenitur... Secunda secundum operationem qua format quidditates rerum, quae est abstractio formae a materia sensibili. »*",
        "",
        "* **Quod Iudicium Mathematicum Terminatur ad Imaginationem** (:ref:`Super Boetium De Trinitate, q. 6, a. 2 <pars-1-s6-la>`): *« In mathematicis oportet cognitionem secundum iudicium terminari ad imaginationem, non ad sensum, quia iudicium mathematicum superat apprehensionem sensus. »*",
        "",
        "* **De Certissimo Modo Demonstrationis et Lineis in Pulvere Descriptis** (:ref:`In I Anal. Post., lect. 1 & lect. 19 <pars-2-s9-la>`): *« Geometra enim non concludit aliquid ex hoc quod haec linea est talis quam ipse descripsit in pulvere, sed ex his quae per huiusmodi descriptionem manifestantur. »*",
        "",
        "* **De Necessitate Conversionis ad Phantasmata in Mathematicis** (:ref:`In III De Anima, lect. 12, Pirotta n. 777 <pars-3-s4-la>`): *« Nequaquam sine phantasmate intelligit anima... Quamvis enim triangulus sit indeterminatae quantitatis de quo demonstrat geometra, tamen semper ponit ante oculos suos triangulum determinatae quantitatis. »*",
        "",
        "* **Quod Abstrahentium Non Est Mendacium et Nullum Continuum Ex Punctis Componitur** (:ref:`In II Phys., lect. 3 & In VI Phys., lect. 1 <pars-4-s1-la>`): *« Abstrahentium non est mendacium... Impossibile est aliquod continuum ex indivisibilibus componi, ut puta lineam ex punctis. »*",
        "",
        "* **De Inventione Veritatis Geometricae Dividendo in Actu** (:ref:`In IX Metaph., lect. 10, Cathala n. 1894 <pars-5-s5-la>`): *« Geometrae inveniunt veritatem quae quaeritur dividendo... Si enim iam esset divisum in actu, statim esset manifestum videnti. »*",
        "",
    ]
    (pdir / "la.rst").write_text("\n".join(la_lines), encoding="utf-8")

    sum_lines = [
        ":title: Introduction Summary — Architecture of the Codex",
        ":layout: book",
        ":canonical_id: Prooemium",
        ":folio: Prooemium",
        tracks_frontmatter,
        "",
        ".. _prooemium-summary:",
        "",
        rst_heading("Introduction — Executive Summary", H1_CHAR),
        "",
        ".. rubric:: *Overview of the Thomistic Corpus on Mathematical Science*",
        "",
        "This Codex unites the foundational primary texts in which :person:`St. Thomas Aquinas <aquinas>` establishes the ontology, psychology, logic, and heuristic discovery of geometry across six canonical treatises.",
        "",
        rst_heading("Overview of the Treatises", H2_CHAR),
        "",
        ".. list-table:: Architecture of the Thomistic Mathematical Corpus",
        "   :header-rows: 1",
        "   :widths: 14 28 28 30",
        "",
        "   * - Treatise",
        "     - Primary Work",
        "     - Core Doctrinal Focus",
        "     - Key Geometric Paradigm",
        "   * - :ref:`De Trinitate <super_boetium_de_trinitate>`",
        "     - *Super Boetium De Trinitate* (qq. 5–6)",
        "     - Twofold intellectual act; *separatio* vs. *abstractio formae*; *materia intelligibilis*; judgment terminating at imagination",
        "     - Continuous extension abstracted from sensible qualities; imaginative verification of figures",
        "   * - :ref:`Posterior Analytics <analytica_posteriora>`",
        "     - *In Posteriora Analytica* (I.1–6, 17–19, 42; II.20)",
        "     - Supreme certitude; *dignitates*, *suppositiones*, *petitiones*; dust diagrams; unit vs. point; inductive *intellectus*",
        "     - Euclid's Common Notions & Postulates; triangle in semicircle (I.3); point with *positio*",
        "   * - :ref:`De Anima <de_anima>`",
        "     - *Sentencia libri De anima* (I.11; II.16; III.8, 12–13)",
        "     - Moving point in imagination; *carnes et ossa* vs. *continuum*; *conversio ad phantasmata*; hand as *organum organorum*",
        "     - Determinate drawn triangle manifesting universal angle properties",
        "   * - :ref:`Physics & Heavens <physica>`",
        "     - *In Physicam* (II.3, III.5, IV.7, VI.1) & *De Caelo* (I.2, II.2)",
        "     - *Abstrahentium non est mendacium*; ten categories; immobile place; continuum non-atomism; three dimensions",
        "     - Infinite divisibility of line; rigid translation & congruence; oriented figures",
        "   * - :ref:`Metaphysics <metaphysica>`",
        "     - *In Metaphysicam* (V.9, VII.10–11, IX.3 & 10)",
        "     - Individual vs. common *materia intelligibilis*; discovery by division in act; agent intellect",
        "     - Bronze vs. mathematical circles; Euclid I.32 & III.31 auxiliary constructions; diagonal incommensurability",
        "   * - :ref:`Summa Theologiae <summa_theologiae>`",
        "     - *Summa Theologiae* I, *De Potentia* 7.2, *De Veritate* 10.6",
        "     - Ipsum esse; geometer's infinite line; agent intellect; indemonstrable principles",
        "     - The geometer's infinite magnitude; cognitive degrees of abstraction",
        "",
    ]
    (pdir / "summary.rst").write_text("\n".join(sum_lines), encoding="utf-8")

    notes_lines = [
        ":title: Introduction Notes — GEOMETOR & the Thomistic-Hoenen Tradition",
        ":layout: book",
        ":canonical_id: Prooemium",
        ":folio: Prooemium",
        tracks_frontmatter,
        "",
        ".. _prooemium-notes:",
        "",
        rst_heading("Introduction — Editorial & GEOMETOR Notes", H1_CHAR),
        "",
        ".. rubric:: *From Medieval Scholasticism to Symbolic Constructive Geometry*",
        "",
        rst_heading("1. The Historical Arc: Aristotle -> Euclid -> Aquinas -> Pacioli -> Hoenen -> GEOMETOR", H2_CHAR),
        "",
        "Within the ``geometor`` workspace, ``geometor-aquinas`` bridges the classical mathematical canon (``euclid``, ``elements``, ``pappus``, ``pacioli``) and the modern epistemological synthesis of :person:`Peter Hoenen <hoenen>` (``hoenen``). When :person:`Fra Luca Pacioli <pacioli>` argued in :cite:`*De Divina Proportione* (1509) <pacioli:1509>` that the mathematical sciences occupy the *primo grado di certezza* ('first degree of certainty'), he stood directly inside the tradition of :person:`Aquinas <aquinas>`\\ 's *Super Boetium De Trinitate* q. 6 a. 1 and *In I Anal. Post.* lect. 1. Four and a half centuries later, confronting :person:`Hilbert <hilbert>`\\ 's formalist axiomatics and non-Euclidean geometry, :person:`Hoenen <hoenen>` returned to these exact Thomistic texts—citing 78 distinct Thomistic loci—to prove that formal rigor and spatial intuition are allies rather than rivals.",
        "",
        rst_heading("2. Computational Mapping to the GEOMETOR Engine", H2_CHAR),
        "",
        "* **Exact Symbolic Algebra as Materia Intelligibilis**: Unlike floating-point dynamic geometry tools whose coordinates drift by numeric epsilon (like lines drawn in sensible dust), ``geometor.model`` represents every point, line, and circle over exact algebraic number fields in SymPy—preserving $\\sqrt{2}$, $\\sqrt{3}$, and the golden ratio $\\phi = \\frac{1+\\sqrt{5}}{2}$ in pure :term:`intelligible matter <materia-intelligibilis>`.",
        "* **The Interactive Canvas as Phantasma**: In exact fidelity to :term:`conversio ad phantasmata <conversio-ad-phantasmata>` (*De Anima* III, lect. 12) and :term:`terminari ad imaginationem <terminari-ad-imaginationem>` (*De Trinitate* q. 6 a. 2), ``geometor.explorer`` projects those exact symbolic structures onto an interactive SVG canvas where human geometric intuition inspects determinate diagrams.",
        "* **Constructive Discovery by Division in Act**: Just as *Metaphysics* IX, lect. 10 (Cathala #1894) celebrates geometers discovering latent truths *dividendo in actu*, ``geometor.divine`` systematically scans newly constructed intersections across the DAG to bring latent golden sections and harmonic ranges into luminous act.",
        "",
    ]
    (pdir / "notes.rst").write_text("\n".join(notes_lines), encoding="utf-8")


def build_concordance_page(docsrc_dir: Path) -> None:
    """Write docsrc/concordance.rst."""
    doc = load_concordance_document()
    counts = doc["summary_counts"]
    entries = doc["entries"]

    lines = [
        ":title: Hoenen–Aquinas–Aristotle–Euclid–GEOMETOR Concordance",
        ":layout: book",
        "",
        ".. _concordance:",
        ".. _hoenen-aquinas-concordance:",
        "",
        rst_heading("Hoenen–Aquinas–Aristotle–Euclid–GEOMETOR Concordance", H1_CHAR),
        "",
        ".. rubric:: *Complete 78-Locus Cross-Reference Matrix Grounding Thomistic Geometric Noetics*",
        "",
        normalize_inline_rst(str(doc["description"])),
        "",
        f"* **Total Hoenen Thomistic Citation Keys**: **{counts['total_hoenen_thomistic_keys']}** ({counts['authentic_aquinas_keys']} authentic :person:`Thomas Aquinas <aquinas>` keys + {counts['pseudo_thomas_keys']} Pseudo-Thomas scholastic keys)",
        f"* **Unabridged Full-Text Coverage in Pars I–V**: **{counts['full_text_in_codex_keys']}** core geometric-noetic keys",
        f"* **Complementary Metaphysical & Logical Loci**: **{counts['complementary_loci_keys']}** keys fully analyzed below",
        "",
        rst_heading("Sister Repository Bridges Across GEOMETOR", H2_CHAR),
        "",
    ]

    for bridge in doc["sister_codex_bridges"]:
        lines.extend([
            rst_heading(f"{bridge['repository']} — {bridge['work']}", H3_CHAR),
            "",
            normalize_inline_rst(str(bridge["bridge_summary"])),
            "",
        ])

    lines.extend([
        rst_heading("Master Summary Matrix (All 78 Citation Keys)", H2_CHAR),
        "",
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 22 24 22 18 14",
        "",
        "   * - Hoenen Key",
        "     - Thomistic Work & Locus",
        "     - Aristotelian Source",
        "     - Hoenen Occurrence(s)",
        "     - Codex Link",
    ])

    for e in entries:
        occs = "; ".join(
            f"{o.get('book', '')} p.{o.get('page', '')}".strip()
            for o in e["hoenen_occurrences"][:3]
        )
        if len(e["hoenen_occurrences"]) > 3:
            occs += f" (+{len(e['hoenen_occurrences']) - 3})"
        status_link = (
            f":ref:`Full Text ({e['codex_part']}) <{e['codex_ref']}>`"
            if e["codex_status"] == "full_text"
            else f":ref:`Locus Note <conc-{e['slug']}>`"
        )
        lines.extend([
            f"   * - :ref:`{e['key']} <conc-{e['slug']}>`",
            f"     - *{e['work_title']}* ({e['locus']})",
            f"     - {normalize_inline_rst(str(e['aristotle_source']))}",
            f"     - {occs or 'passim'}",
            f"     - {status_link}",
        ])
    lines.append("")

    lines.extend([
        rst_heading("Detailed Locus-by-Locus Analytical Concordance", H2_CHAR),
        "",
    ])

    by_work: dict[str, list[dict[str, object]]] = defaultdict(list)
    for e in entries:
        by_work[str(e["work_title"])].append(e)

    for work_title, w_entries in by_work.items():
        lines.extend([
            rst_heading(work_title, H3_CHAR),
            "",
        ])
        for e in w_entries:
            slug = str(e["slug"])
            lines.extend([
                f".. _conc-{slug}:",
                "",
                rst_heading(f"{e['key']} — {e['locus']}", H4_CHAR),
                "",
                f"* **Critical Edition**: {normalize_inline_rst(str(e['critical_edition_ref']))}",
                f"* **Aristotelian Foundation**: {normalize_inline_rst(str(e['aristotle_source']))}",
                f"* **Euclidean Counterpart**: {normalize_inline_rst(str(e['euclid_elements_link']))}",
            ])
            if e["codex_status"] == "full_text":
                la_ref = str(e["codex_ref"]).replace("-en", "-la")
                lines.append(
                    f"* **Codex Edition**: Unabridged in :ref:`English ({e['codex_part']}) <{e['codex_ref']}>` · :ref:`Diplomatic Latin <{la_ref}>`"
                )
            else:
                lines.append("* **Codex Status**: Complementary Metaphysical / Logical Locus")
            occs_detail = "; ".join(
                f"{o.get('book', '')} p. {o.get('page', '')} (``{o.get('display', '')}``)"
                for o in e["hoenen_occurrences"]
            )
            if occs_detail:
                lines.append(f"* **Cited in Hoenen (1954)**: {occs_detail}")
            lines.extend([
                f"* **Hoenen's Doctrinal Argument**: {normalize_inline_rst(str(e['hoenen_thesis']))}",
                f"* **GEOMETOR Architectural Significance**: {normalize_inline_rst(str(e['geometor_relevance']))}",
                "",
            ])

    (docsrc_dir / "concordance.rst").write_text("\n".join(lines), encoding="utf-8")


def build_bibliography_page(docsrc_dir: Path) -> None:
    """Write docsrc/bibliography.rst with cite-<slug> anchors."""
    citations = load_citations()

    lines = [
        ":navigation: header",
        ":order: 8",
        ":nav_title: Bibliography",
        ":title: Bibliography",
        ":layout: book",
        "",
        ".. _bibliography:",
        ".. _bibliographia-et-fontes:",
        "",
        rst_heading("Bibliography", H1_CHAR),
        "",
        ".. rubric:: Critical Editions, Classical Sources, and Modern Studies in Geometric Noetics",
        "",
        f"This registry catalogues all **{len(citations)} bibliographic editions and cited loci** across ``geometor-aquinas``. Every inline ``:cite:`` reference resolves directly to its ``#cite-<slug>`` anchor below and displays hover metadata automatically.",
        "",
        "----",
        "",
    ]

    primary_ed_keys = [k for k in citations if k.endswith("-ed") or k in {"aquinas:de-trin", "corpus-thomisticum"}]
    classical_modern_keys = [
        k
        for k in citations
        if k not in primary_ed_keys and not k.startswith("aquinas:") and not k.startswith("pseudo-thomas:")
    ]
    locus_keys = sorted(
        k for k in citations if (k.startswith("aquinas:") or k.startswith("pseudo-thomas:")) and k not in primary_ed_keys
    )

    sections = [
        ("Primary Critical Editions of St. Thomas Aquinas", primary_ed_keys),
        ("Classical, Renaissance & Modern Philosophical-Mathematical Works", sorted(classical_modern_keys)),
        ("Cited Thomistic & Scholastic Loci (Hoenen Concordance Keys)", locus_keys),
    ]

    for sec_title, keys in sections:
        lines.extend([
            rst_heading(sec_title, H2_CHAR),
            "",
        ])
        for k in keys:
            c = citations[k]
            slug = slugify_apparatus_key(c.key)
            lines.extend([
                f".. _cite-{slug}:",
                "",
                rst_heading(f"{c.work} ({c.key})", H3_CHAR),
                "",
                f"* **Author / Editor**: {c.author}",
                f"* **Edition / Locus**: {c.locus}",
                "",
            ])

    (docsrc_dir / "bibliography.rst").write_text("\n".join(lines), encoding="utf-8")


def build_persons_page(docsrc_dir: Path) -> None:
    """Write docsrc/persons.rst with person-<slug> anchors."""
    persons = load_persons()
    sorted_items = sorted(persons.values(), key=lambda p: p.name.lower())

    lines = [
        ":navigation: header",
        ":order: 7",
        ":nav_title: People",
        ":title: People",
        ":layout: book",
        "",
        ".. _persons:",
        ".. _index-nominum:",
        "",
        rst_heading("People", H1_CHAR),
        "",
        ".. rubric:: Biographical Register of Philosophers, Geometers, Commentators, and Critical Editors",
        "",
        f"This prosopographical register documents **{len(persons)} key figures** shaping Thomistic geometric noetics—from :person:`Pythagoras <pythagoras>`, :person:`Plato <plato>`, :person:`Aristotle <aristotle>`, and :person:`Euclid <euclid>` through :person:`Boethius <boethius>`, :person:`Avicenna <avicenna>`, :person:`Averroes <averroes>`, :person:`Albert the Great <albertus>`, :person:`Thomas Aquinas <aquinas>`, :person:`Cajetan <cajetan>`, and :person:`Luca Pacioli <pacioli>` to :person:`David Hilbert <hilbert>`, :person:`Peter Hoenen <hoenen>`, :person:`Étienne Gilson <gilson>`, and :person:`Bernard Lonergan <lonergan>`.",
        "",
        rst_heading("Authors, Translators & Editors", H2_CHAR),
        "",
    ]

    author_slugs = ["aquinas", "william-of-moerbeke", "pirotta", "cathala", "decker", "busa"]
    for slug in author_slugs:
        if slug in persons:
            p = persons[slug]
            p_slug = slugify_apparatus_key(p.slug)
            lines.extend([
                f".. _person-{p_slug}:",
                "",
                rst_heading(f"{p.name} ({p.dates})", H3_CHAR),
                "",
                f"**Role**: *{p.role}*",
                "",
            ])
            if slug == "aquinas":
                lines.extend([
                    "Born at Roccasecca near Aquino around 1225, **Thomas Aquinas, O.P.** studied the liberal arts and the *quadrivium* (arithmetic, geometry, music, and astronomy) at the University of Naples before entering the Order of Preachers and studying under **St. Albert the Great** at Paris and Cologne. Across a remarkably concentrated career spanning Paris, Orvieto, Rome, Viterbo, and Naples (1252–1274), Aquinas produced both monumental theological syntheses and twelve penetrating commentaries on Aristotle—working closely with the literal Greek-to-Latin translations and revisions of his Dominican confrere **William of Moerbeke**.",
                    "",
                    "Although Aquinas did not compose a separate mathematical treatise like Euclid's *Elements*, geometry and arithmetic form the indispensable structural middle of his entire epistemology and metaphysics:",
                    "",
                    "1. **Between Physics and Metaphysics (*Super Boetium De Trinitate* qq. 5–6, 1257–1259)**: In his autograph exposition of Boethius's *De Trinitate*, Master Thomas broke decisively with Platonic reification and Avicennian emanationism alike. Distinguishing the intellect's simple apprehension of essence from its existential judgment (*separatio*), he showed why mathematical science abstracts dimensional form (*abstractio formae*) from sensible qualities while preserving continuous spatial extension (*materia intelligibilis*)—and why mathematical judgment terminates neither at mutable external sense nor at pure imageless intellect, but at the constructive imagination (*terminari ad imaginationem*).",
                    "2. **Paradigm of Demonstrative Science (*In Posteriora Analytica*, 1270–1272)**: Throughout his mature *Posterior Analytics* commentary, Euclidean geometry provides Aquinas's primary laboratory for analyzing axioms (*dignitates / communes animi conceptiones*), definitions, hypotheses (*suppositiones*), and postulates (*petitiones*), explaining why mathematics enjoys the *certissimus modus demonstrationis* without mistaking diagrams drawn in dust for the intelligible continuum signified through them.",
                    "3. **Psychological Unity of Intellect and Phantasm (*In De Anima*, 1267–1268 & *ST* I q. 84–85)**: Aquinas insists that even in pure geometry, the human intellect never understands without turning to a concrete *phantasma* (*conversio ad phantasmata*), beholding universal necessary ratios inside a determinate imagined figure.",
                    "4. **Heuristic Discovery by Division in Act (*In IX Metaphysicorum* lect. 10, c. 1270–1272)**: Commenting on Aristotle's *Metaphysics* IX.9 (1051a21–33), Aquinas analyzes Euclid I.32 and III.31 to reveal how geometers discover hidden truths: what lies latent in potency in an undivided figure leaps into immediate intellectual clarity (*statim manifestum est videnti*) the instant auxiliary constructions divide the continuum in act.",
                    "",
                ])
            else:
                lines.extend([
                    normalize_inline_rst(p.bio),
                    "",
                ])
            if p.works:
                lines.append("**Principal Works**:")
                lines.append("")
                for w in p.works:
                    lines.append(f"* *{w}*")
                lines.append("")

    lines.extend([
        rst_heading("Cited Geometers, Philosophers & Scholars", H2_CHAR),
        "",
    ])

    for p in sorted_items:
        if p.slug in author_slugs:
            continue
        slug = slugify_apparatus_key(p.slug)
        lines.extend([
            f".. _person-{slug}:",
            "",
            rst_heading(f"{p.name} ({p.dates})", H3_CHAR),
            "",
            f"**Role**: *{p.role}*",
            "",
            normalize_inline_rst(p.bio),
            "",
        ])
        if p.works:
            lines.append("**Principal Works**:")
            lines.append("")
            for w in p.works:
                lines.append(f"* *{w}*")
            lines.append("")

    if not (docsrc_dir / "people" / "index.rst").is_file():
        (docsrc_dir / "persons.rst").write_text("\n".join(lines), encoding="utf-8")


def build_glossary_page(docsrc_dir: Path) -> None:
    """Write docsrc/glossary.rst with term-<slug> anchors."""
    glossary = load_glossary()
    sorted_terms = sorted(glossary.values(), key=lambda g: g.headword.lower())

    lines = [
        ":title: Technical Glossary — Scholastic & Geometric Lexicon",
        ":layout: book",
        "",
        ".. _glossary:",
        ".. _glossarium-technicum:",
        "",
        rst_heading("Technical Glossary", H1_CHAR),
        "",
        ".. rubric:: *Glossarium Technicum* — Lexicon of Thomistic Epistemology, Metaphysics, and Constructive Geometry",
        "",
        f"This lexicon defines **{len(glossary)} foundational Latin and Greek technical terms** governing Aquinas's philosophy of mathematics and its modern reception in :person:`Peter Hoenen <hoenen>` and GEOMETOR. Every inline ``:term:`` tag links directly to its ``#term-<slug>`` anchor below.",
        "",
        rst_heading("Alphabetical Index of Terms", H2_CHAR),
        "",
    ]

    for g in sorted_terms:
        slug = slugify_apparatus_key(g.slug)
        lines.append(f"* :ref:`{g.headword} <term-{slug}>` — *{g.translation}* ({g.language})")
    lines.extend(["", "----", "", rst_heading("Lexicon Definitions", H2_CHAR), ""])

    for g in sorted_terms:
        slug = slugify_apparatus_key(g.slug)
        lines.extend([
            f".. _term-{slug}:",
            "",
            rst_heading(f"{g.headword} — {g.translation}", H3_CHAR),
            "",
            f"* **Tradition**: {g.language}",
            f"* **English Rendering**: *{g.translation}*",
            "",
            normalize_inline_rst(g.definition),
            "",
        ])

    (docsrc_dir / "glossary.rst").write_text("\n".join(lines), encoding="utf-8")


def compile_all(repo_root: Path | None = None) -> dict[str, object]:
    """Compile the entire unbundled multi-book RST codex from resources/."""
    root = repo_root or get_repo_root()
    res_dir = root / "resources"
    stats = verify_codex_integrity(res_dir)

    docsrc_dir = root / "docsrc"
    docsrc_dir.mkdir(parents=True, exist_ok=True)

    # 1. Remove old bundled scientia_mathematica directory if present
    old_bundled_dir = docsrc_dir / "scientia_mathematica"
    if old_bundled_dir.is_dir():
        shutil.rmtree(old_bundled_dir)

    # 2. Write author home page, prooemium, apparatus
    build_author_index(docsrc_dir, BOOKS_CONFIG)
    build_prooemium(docsrc_dir)
    build_concordance_page(docsrc_dir)
    build_bibliography_page(docsrc_dir)
    build_persons_page(docsrc_dir)
    build_glossary_page(docsrc_dir)

    tracks_frontmatter = ":tracks: English: index | Latin: la | Summary: summary | Notes: notes"

    # 3. Write each of the 6 canonical books
    for b_idx, b_cfg in enumerate(BOOKS_CONFIG, start=1):
        b_slug = b_cfg["slug"]
        b_dir = docsrc_dir / b_slug
        b_dir.mkdir(parents=True, exist_ok=True)

        part_num = b_cfg["part_source"]
        la_part = load_latin_part(part_num, res_dir)
        apparatus = load_part_apparatus(part_num, res_dir)

        sec_indices = b_cfg["sec_indices"]
        b_la_sections = [la_part["sections"][i] for i in sec_indices]
        b_sum_sections = [apparatus["section_summaries"][i] for i in sec_indices]
        b_note_sections = [apparatus["section_notes"][i] for i in sec_indices]

        unit_dirs = [f"{b_cfg['unit_prefix']}_{i+1:02d}" for i in range(len(b_la_sections))]

        # Book Title Page (<book>/index.rst)
        index_lines = [
            f":title: {b_cfg['title']}",
            ":layout: book",
            ":type: book",
            f":order: {b_cfg['order']}",
            ":navigation: header",
            f":nav_title: {b_cfg['nav_title']}",
            f":breadcrumb_title: {b_cfg['breadcrumb_title']}",
            f":book_title: {b_cfg['title']}",
            f":book_subtitle: {b_cfg['subtitle']}",
            ":author: St. Thomas Aquinas, O.P. (1225–1274)",
            ":series: GEOMETOR Classical Canon · Critical Multi-Track Codex",
            ":publisher: GEOMETOR Scriptorium (ex Editionibus Leonina, Marietti et Decker)",
            ":location: Pompaelone / Romae / Taurini",
            f":year: {b_cfg['date_composed']}",
            ":tracks: English: index | Latin: title-la",
            f":excerpt: {b_cfg['excerpt']}",
            "",
            f".. _{b_slug}:",
            f".. _{b_slug}-index:",
        ]
        if b_cfg["legacy_part_id"]:
            leg_id = b_cfg["legacy_part_id"]
            index_lines.extend([
                f".. _{leg_id}:",
                f".. _{leg_id}-en:",
                f".. _{leg_id}-la:",
                f".. _{leg_id}-summary:",
                f".. _{leg_id}-notes:",
            ])

        index_lines.extend([
            "",
            rst_heading(b_cfg["title"], H1_CHAR),
            "",
            f".. rubric:: *{b_cfg['subtitle']}*",
            "",
            ".. container:: title-page",
            "",
            "   | :person:`St. Thomas Aquinas, O.P. <aquinas>` (1225–1274 · *Doctor Communis*)",
            "   |",
            f"   | **{b_cfg['work_title']}** ({b_cfg['date_composed']})",
            f"   | {len(b_la_sections)} Unabridged Lectiones & Articles · Critical Multi-Track Edition",
            "   | Diplomatic Latin Texts from the Leonine, Marietti, and Decker Editions",
            "   | With Facing English Translation, Analytical Summaries & GEOMETOR Notes",
            "",
            "----",
            "",
            rst_heading("Executive Thesis", H2_CHAR),
            "",
        ])

        seen_sum: set[str] = set()
        for para in str(apparatus["executive_thesis"]).split("\n\n"):
            clean_p = normalize_inline_rst(para)
            if clean_p:
                index_lines.append(enrich_inline_apparatus(clean_p, EN_TAG_RULES, seen_sum))
                index_lines.append("")

        index_lines.extend([
            rst_heading("Key Scholastic & Mathematical Concepts", H2_CHAR),
            "",
            ".. list-table::",
            "   :header-rows: 1",
            "   :widths: 22 22 16 40",
            "",
            "   * - Latin Term",
            "     - English Rendering",
            "     - Primary Locus",
            "     - Doctrinal & Geometric Significance",
        ])
        for row in apparatus["conceptual_table"]:
            clean_lat = normalize_inline_rst(str(row["latin_term"]).replace("*", ""))
            index_lines.extend([
                f"   * - *{clean_lat}*",
                f"     - {normalize_inline_rst(str(row['english_term']))}",
                f"     - ``{normalize_inline_rst(str(row['locus']))}``",
                f"     - {normalize_inline_rst(str(row['significance']))}",
            ])
        index_lines.extend([
            "",
            "----",
            "",
            rst_heading("Table of Contents", H2_CHAR),
            "",
            ".. collection::",
            "   :sort: order",
            "",
            ".. toctree::",
            "   :hidden:",
            "   :maxdepth: 2",
            "",
        ])
        for u_dir in unit_dirs:
            index_lines.append(f"   {u_dir}/index")
        index_lines.extend([
            "",
            ".. toctree::",
            "   :maxdepth: 1",
            "   :hidden:",
            "   :caption: Title Pages",
            "",
            "   title-la",
            "",
        ])

        (b_dir / "index.rst").write_text("\n".join(index_lines), encoding="utf-8")

        # Atomic unit pages
        for u_idx, (sec_la, sec_sum, sec_note, u_dir) in enumerate(
            zip(b_la_sections, b_sum_sections, b_note_sections, unit_dirs, strict=True),
            start=1,
        ):
            sec_id = str(sec_la["sec_id"])
            folio = str(sec_la["folio"])
            en_sec = load_english_section(part_num, sec_id, res_dir)
            u_path = b_dir / u_dir
            u_path.mkdir(parents=True, exist_ok=True)

            unit_key = f"{b_slug}_{u_dir}"
            svg_content = build_unit_svg(unit_key, str(sec_la["heading_en"]), folio)
            (u_path / "figure.svg").write_text(svg_content, encoding="utf-8")

            raw_heading_en = str(sec_la["heading_en"])
            if "—" in raw_heading_en:
                principle_title = raw_heading_en.split("—", 1)[-1].strip()
            elif " - " in raw_heading_en:
                principle_title = raw_heading_en.split(" - ", 1)[-1].strip()
            else:
                principle_title = raw_heading_en

            raw_heading_la = str(sec_la["heading_la"])
            if "—" in raw_heading_la:
                principle_title_la = raw_heading_la.split("—", 1)[-1].strip()
            elif " - " in raw_heading_la:
                principle_title_la = raw_heading_la.split(" - ", 1)[-1].strip()
            else:
                principle_title_la = raw_heading_la

            # Track 1: English (index.rst)
            en_u_lines = [
                f":order: {u_idx}",
                f":canonical_id: {folio}",
                f":folio: {folio}",
                f":title: {principle_title}",
                f":tags: aquinas, {b_cfg['slug']}",
                tracks_frontmatter,
                "",
                f".. _{b_slug}-{u_dir}:",
                f".. _{b_slug}-{u_dir}-en:",
                f".. _{b_slug}-{sec_id}-en:",
                f".. _pars-{part_num}-{sec_id}-en:",
                f".. _pars-{part_num}-{sec_id}:",
                "",
                rst_heading(raw_heading_en, H1_CHAR),
                "",
                f".. rubric:: *{raw_heading_la}*",
                "",
                f".. folio:: {folio}",
                "",
                ".. figure:: figure.svg",
                f"   :alt: {principle_title}",
                "   :align: center",
                "",
            ]
            seen_en: set[str] = set()
            for la_p, en_p in zip(sec_la["paragraphs"], en_sec["paragraphs"], strict=True):
                badge = format_para_badge(la_p)
                raw_en = normalize_inline_rst(str(en_p["english"]))
                tagged_en = enrich_inline_apparatus(raw_en, EN_TAG_RULES, seen_en)
                en_u_lines.append(f"{badge} {tagged_en}")
                en_u_lines.append("")

            en_u_lines.extend([
                ".. toctree::",
                "   :hidden:",
                "",
                "   la",
                "   summary",
                "   notes",
                "",
            ])
            (u_path / "index.rst").write_text("\n".join(en_u_lines), encoding="utf-8")

            # Track 2: Latin (la.rst)
            la_u_lines = [
                f":order: {u_idx}",
                f":canonical_id: {folio}",
                f":folio: {folio}",
                f":title: {principle_title_la}",
                tracks_frontmatter,
                "",
                f".. _{b_slug}-{u_dir}-la:",
                f".. _{b_slug}-{sec_id}-la:",
                f".. _pars-{part_num}-{sec_id}-la:",
                "",
                rst_heading(raw_heading_la, H1_CHAR),
                "",
                ".. rubric:: *Editio Critica Diplomatica (via Corpus Thomisticum)*",
                "",
                f".. folio:: {folio}",
                "",
            ]
            seen_la: set[str] = set()
            for la_p in sec_la["paragraphs"]:
                badge = format_para_badge(la_p)
                raw_la = normalize_inline_rst(str(la_p["latin"]))
                tagged_la = enrich_inline_apparatus(raw_la, LA_TAG_RULES, seen_la)
                la_u_lines.append(f"{badge} {tagged_la}")
                la_u_lines.append("")
            (u_path / "la.rst").write_text("\n".join(la_u_lines), encoding="utf-8")

            # Track 3: Summary (summary.rst)
            sum_u_lines = [
                f":order: {u_idx}",
                f":canonical_id: {folio}",
                f":folio: {folio}",
                f":title: Summary — {principle_title}",
                tracks_frontmatter,
                "",
                f".. _{b_slug}-{u_dir}-summary:",
                f".. _{b_slug}-{sec_id}-summary:",
                f".. _pars-{part_num}-{sec_id}-summary:",
                "",
                rst_heading(f"Summary — {principle_title}", H1_CHAR),
                "",
                f".. rubric:: *Analytical Synopsis & Core Theses of {folio}*",
                "",
                rst_heading("Argument Summary", H2_CHAR),
                "",
            ]
            seen_sec_sum: set[str] = set()
            for para in str(sec_sum["argument_summary"]).split("\n\n"):
                clean_p = normalize_inline_rst(para)
                if clean_p:
                    sum_u_lines.append(enrich_inline_apparatus(clean_p, EN_TAG_RULES, seen_sec_sum))
                    sum_u_lines.append("")
            if sec_sum.get("key_theses"):
                sum_u_lines.append(rst_heading("Key Theses", H2_CHAR))
                sum_u_lines.append("")
                for th in sec_sum["key_theses"]:
                    sum_u_lines.append(f"* {normalize_inline_rst(str(th))}")
                sum_u_lines.append("")
            (u_path / "summary.rst").write_text("\n".join(sum_u_lines), encoding="utf-8")

            # Track 4: Notes (notes.rst)
            note_u_lines = [
                f":order: {u_idx}",
                f":canonical_id: {folio}",
                f":folio: {folio}",
                f":title: Commentary & Notes — {principle_title}",
                tracks_frontmatter,
                "",
                f".. _{b_slug}-{u_dir}-notes:",
                f".. _{b_slug}-{sec_id}-notes:",
                f".. _pars-{part_num}-{sec_id}-notes:",
                "",
                rst_heading(f"Commentary & Notes — {principle_title}", H1_CHAR),
                "",
                f".. rubric:: *Aristotelian Sources, Euclidean Counterparts, Hoenen's Noetics, and GEOMETOR Significance*",
                "",
                rst_heading("Aristotelian & Scholastic Foundations", H2_CHAR),
                "",
                enrich_inline_apparatus(normalize_inline_rst(str(sec_note["aristotelian_foundations"])), EN_TAG_RULES, set()),
                "",
                rst_heading("Euclidean & Classical Geometric Counterparts", H2_CHAR),
                "",
                enrich_inline_apparatus(normalize_inline_rst(str(sec_note["euclidean_counterparts"])), EN_TAG_RULES, set()),
                "",
                rst_heading("Hoenen's De Noetica Geometriae & Judgment Theory", H2_CHAR),
                "",
                enrich_inline_apparatus(normalize_inline_rst(str(sec_note["hoenen_noetics"])), EN_TAG_RULES, set()),
                "",
                rst_heading("GEOMETOR Constructive & Symbolic Significance", H2_CHAR),
                "",
                enrich_inline_apparatus(normalize_inline_rst(str(sec_note["geometor_significance"])), EN_TAG_RULES, set()),
                "",
            ]
            (u_path / "notes.rst").write_text("\n".join(note_u_lines), encoding="utf-8")

    return stats


def main() -> None:
    """CLI entry point for geometor-aquinas-compile."""
    stats = compile_all(get_repo_root())
    print(f"Compiled geometor-aquinas Book Codex successfully: {stats}")


if __name__ == "__main__":
    main()
