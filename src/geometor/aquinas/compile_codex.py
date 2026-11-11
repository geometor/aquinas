"""Compile the ``scientia_mathematica`` Multi-Track Book Codex RST tree from ``resources/``.

Generates:
- ``docsrc/scientia_mathematica/index.rst`` (``:layout: book`` Conspectus Operis)
- ``docsrc/scientia_mathematica/prooemium/prooemium-{en,la,summary,notes}.rst``
- ``docsrc/scientia_mathematica/pars-{1..5}/pars-{1..5}-{en,la,summary,notes}.rst``
- ``docsrc/scientia_mathematica/{concordance,bibliography,persons,glossary}.rst``
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

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
    # Fix accidental '* word*' or '*word *' spaces inside emphasis if any
    if s.count("*") % 2 != 0:
        # Escape stray unmatched asterisk so docutils never raises a warning
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

            # Only replace in plain segments that don't already contain backticks
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
    result = re.sub(r"(`)(?=[A-Za-z0-9'])", r"`\\ ", result)
    return result


def format_para_badge(p: dict[str, object]) -> str:
    """Format subtle critical-edition locus badge for synchronized Latin/English paragraphs."""
    title = str(p["title"])
    # Extract compact locus suffix (e.g. 'q. 5 a. 3 co.', 'lib. 1 l. 19 n. 4')
    short_loc = title.split(",", 1)[-1].strip() if "," in title else title
    if "marietti_no" in p:
        return f"**[{short_loc} · Marietti #{p['marietti_no']}]**"
    return f"**[{short_loc}]**"


def build_book_index(codex_dir: Path, manifest: dict[str, object]) -> None:
    """Write ``docsrc/scientia_mathematica/index.rst``."""
    parts = manifest["parts"]
    assert isinstance(parts, list)
    totals = manifest["totals"]
    assert isinstance(totals, dict)

    lines = [
        ":navigation: header",
        ":order: 1",
        ":layout: book",
        ":title: De Scientia Mathematica",
        ":book_title: De Scientia Mathematica",
        ":book_subtitle: Opera de Scientia Mathematica et Materia Intelligibili",
        ":author: Sanctus Thomas de Aquino, O.P. (1225–1274)",
        ":series: GEOMETOR Classical Canon · Critical Multi-Track Codex",
        ":publisher: GEOMETOR Scriptorium (ex Editionibus Leonina, Marietti et Decker)",
        ":location: Pompaelone / Romae / Taurini",
        ":year: 1256–1273",
        "",
        ".. _aquinas-index:",
        ".. _scientia-mathematica-index:",
        "",
        rst_heading("OPERA DE SCIENTIA MATHEMATICA ET MATERIA INTELLIGIBILI", H1_CHAR),
        "",
        ".. rubric:: *Foundational Texts on Mathematical Science, Intelligible Matter, Abstraction, Heuristic Construction, and Judgment*",
        "",
        ".. container:: title-page",
        "",
        "   | :person:`SANCTI THOMAE DE AQUINO, O.P. <aquinas>`",
        "   | *(1225 – 1274 · Doctor Communis)*",
        "   |",
        "   | **OPERA SELECTA DE NOETICA ET PHILOSOPHIA MATHEMATICAE**",
        f"   | {totals['part_count']} Parts · {totals['section_count']} Unabridged Lectiones & Articles · {totals['paragraph_count']} Synchronized Paragraphs",
        "   | Diplomatic Latin Texts from the Leonine, Marietti (:person:`Pirotta <pirotta>`, :person:`Cathala <cathala>`), and :person:`Decker <decker>` Editions",
        "   | With Facing English Translation, GEOMETOR Commentary & 100% :person:`Hoenen <hoenen>` Concordance",
        "",
        "----",
        "",
        rst_heading("Conspectus Totius Operis", H2_CHAR),
        "",
        "*(Analytical Table of Contents)*",
        "",
        rst_heading("Prooemium — Introduction to Aquinas's Philosophy of Geometry", H3_CHAR),
        "",
        ":ref:`English <prooemium-en>` · :ref:`Latin <prooemium-la>` · :ref:`Summary <prooemium-summary>` · :ref:`Notes <prooemium-notes>`",
        "",
    ]

    for idx, p in enumerate(parts, start=1):
        assert isinstance(p, dict)
        lines.extend([
            rst_heading(str(p["title_en"]), H3_CHAR),
            "",
            f"*({p['title_la']} — {p['work_title']}, {p['date_composed']} · {p['section_count']} sections, {p['paragraph_count']} paragraphs)*",
            "",
            f":ref:`English <pars-{idx}-en>` · :ref:`Latin <pars-{idx}-la>` · :ref:`Summary <pars-{idx}-summary>` · :ref:`Notes <pars-{idx}-notes>`",
            "",
        ])

    lines.extend([
        rst_heading("Apparatus Criticus et Concordantia", H3_CHAR),
        "",
        "* :ref:`Hoenen–Aquinas–Aristotle–Euclid–GEOMETOR Master Concordance (78 Thomistic Loci) <concordance>`",
        "* :ref:`Bibliographia et Fontes — Critical Editions & Cited Works (113 Entries) <bibliography>`",
        "* :ref:`Index Nominum — Biographical Register of Philosophers & Geometers (30 Persons) <persons>`",
        "* :ref:`Glossarium Technicum — Scholastic & Mathematical Lexicon (36 Terms) <glossary>`",
        "",
        ".. toctree::",
        "   :maxdepth: 2",
        "   :hidden:",
        "   :caption: English Edition",
        "",
        "   prooemium/prooemium-en",
        "   pars-1/pars-1-en",
        "   pars-2/pars-2-en",
        "   pars-3/pars-3-en",
        "   pars-4/pars-4-en",
        "   pars-5/pars-5-en",
        "",
        ".. toctree::",
        "   :maxdepth: 2",
        "   :hidden:",
        "   :caption: Editio Latina",
        "",
        "   prooemium/prooemium-la",
        "   pars-1/pars-1-la",
        "   pars-2/pars-2-la",
        "   pars-3/pars-3-la",
        "   pars-4/pars-4-la",
        "   pars-5/pars-5-la",
        "",
        ".. toctree::",
        "   :maxdepth: 1",
        "   :hidden:",
        "   :caption: Summaries & GEOMETOR Commentary",
        "",
        "   prooemium/prooemium-summary",
        "   prooemium/prooemium-notes",
        "   pars-1/pars-1-summary",
        "   pars-1/pars-1-notes",
        "   pars-2/pars-2-summary",
        "   pars-2/pars-2-notes",
        "   pars-3/pars-3-summary",
        "   pars-3/pars-3-notes",
        "   pars-4/pars-4-summary",
        "   pars-4/pars-4-notes",
        "   pars-5/pars-5-summary",
        "   pars-5/pars-5-notes",
        "",
        ".. toctree::",
        "   :maxdepth: 1",
        "   :hidden:",
        "   :caption: Apparatus & Concordance",
        "",
        "   concordance",
        "   bibliography",
        "   persons",
        "   glossary",
        "",
    ])

    (codex_dir / "index.rst").write_text("\n".join(lines), encoding="utf-8")


def build_prooemium(codex_dir: Path) -> None:
    """Write the 4 synchronized tracks of ``docsrc/scientia_mathematica/prooemium/``."""
    pdir = codex_dir / "prooemium"
    pdir.mkdir(parents=True, exist_ok=True)

    en_lines = [
        ":title: Prooemium — Aquinas's Philosophy of Mathematical Science",
        ":layout: book",
        "",
        ".. _prooemium-en:",
        "",
        rst_heading("Prooemium — Aquinas's Philosophy of Mathematical Science", H1_CHAR),
        "",
        ".. rubric:: *Intelligible Matter, Constructive Imagination, and the Architecture of Geometric Truth*",
        "",
        ".. folio:: Prooemium",
        "",
        rst_heading("1. Why St. Thomas Aquinas Matters to Constructive Geometry", H2_CHAR),
        "",
        "Across the history of Western mathematics and philosophy, few problems have proved deeper than the paradox of geometric exactitude and necessity. A circle traced by a brass compass upon parchment or rendered as pixels upon a screen is sensibly imperfect, mutable, and contingent; yet :person:`Euclid <euclid>`\\ 's theorems concerning the circle, the equilateral triangle, the angle in a semicircle, and the division of a segment in extreme and mean ratio possess rigorous, timeless necessity. If one follows :person:`Plato <plato>`, mathematical figures must subsist as separate eternal entities outside the physical world; if one follows radical empiricism, geometric axioms degrade into approximate generalizations from rough measurements; if one follows modern pure formalism (:person:`David Hilbert <hilbert>`) or logicism (:person:`Bertrand Russell <russell>`), geometry is severed from spatial intuition altogether and reduced to uninterpreted postulational syntax.",
        "",
        "In the thirteenth century, :person:`St. Thomas Aquinas <aquinas>` (1225–1274), building upon :person:`Aristotle <aristotle>`, :person:`Boethius <boethius>`, and :person:`Euclid <euclid>`, forged a luminous middle path that resolves this trilemma without sacrificing either deductive rigor or objective spatial reality. As recovered in the twentieth century by the Dutch Jesuit physicist and philosopher :person:`Peter Hoenen <hoenen>` (:cite:`*De Noetica Geometriae*, 1954 <hoenen:1954>`; :cite:`*La théorie du jugement*, 1946 <hoenen:1946>`) and extended by :person:`Bernard Lonergan <lonergan>` (:cite:`*Verbum*, 1946–1949 <lonergan:1946:verbum>`; :cite:`*Insight*, 1957 <lonergan:1957:insight>`), Aquinas's philosophy of mathematics rests upon five interconnected pillars assembled in full in the five Parts of this Codex.",
        "",
        rst_heading("2. The Five Pillars of the Codex", H2_CHAR),
        "",
        "1. **Abstraction of Form and Intelligible Matter (Pars I — Super Boetium De Trinitate, qq. 5–6)**: In Question 5, Article 3 (:ref:`Pars I, s3 <pars-1-s3-en>`), Aquinas distinguishes the intellect's two fundamental operations—:term:`simple apprehension <simplex-apprehensio>` of essence and :term:`composition and division <compositio-et-divisio>` looking to :term:`act of being <ipsum-esse>`—to contrast metaphysical :term:`separation <separatio>` with natural :term:`abstraction of the whole <abstractio-totius>` and mathematical :term:`abstraction of form <abstractio-formae>`. Because continuous quantity inheres in corporeal substance ontologically prior to sensible qualities (heat, color, weight), the geometer abstracts dimensional figure from all :term:`sensible matter <materia-sensibilis>` while retaining :term:`intelligible matter <materia-intelligibilis>`—continuous spatial extension. And in Question 6, Article 2 (:ref:`Pars I, s6 <pars-1-s6-en>`), Aquinas establishes his decisive methodological law: whereas natural judgment terminates at external sense and metaphysical judgment at pure intellect, mathematical judgment must :term:`terminate at the imagination <terminari-ad-imaginationem>`.",
        "",
        "2. **Supreme Demonstrative Certitude and Euclidean Principles (Pars II — Posterior Analytics)**: In his mature commentary on :person:`Aristotle <aristotle>`\\ 's *Posterior Analytics* (:ref:`Pars II <pars-2-en>`), Aquinas explains why mathematics alone among human sciences achieves the *certissimus modus demonstrationis* (Lib. I, lect. 1), maps out the tripartite structure of :term:`subject-genus <genus-subiectum>`, :term:`proper attributes <passiones>`, and :term:`common conceptions of the mind <communes-animi-conceptiones>` vs. :term:`hypotheses <suppositiones>` and :term:`postulates <petitiones>` (Lib. I, lect. 5 & 18–19), proves why the geometer demonstrates not of rough lines drawn in dust (*non demonstrat per lineam in pulvere descriptam*) but of the intelligible lines signified by them (Lib. I, lect. 19), distinguishes the arithmetical unit without position from the geometric :term:`point having position <unitas-et-punctus>` (Lib. I, lect. 42), and traces the genesis of :term:`first principles <intellectus-principiorum>` from sense, memory, and :term:`experience <experimentum>` (Lib. II, lect. 20).",
        "",
        "3. **Turning to the Phantasm in Abstract Geometry (Pars III — Sentencia libri De anima)**: Expounding *De Anima* (:ref:`Pars III <pars-3-en>`), Aquinas shows why *nequaquam sine phantasmate intelligit anima*—the human soul never understands even abstract mathematical truths without :term:`turning to the phantasms <conversio-ad-phantasmata>` (Lib. III, lect. 12, Pirotta nos. 770–777). Just as :term:`the snub <simum-et-curvum>` (*simum*) includes sensible flesh in its ratio, *rectum* (the straight) includes the spatial :term:`continuum <continuum>` (Lib. III, lect. 8). When proving a theorem about an indeterminate triangle, the geometer places a determinate finite triangle before the eyes of the imagination while abstracting from its accidental scale.",
        "",
        "4. **Realism of Abstraction, Continuum, and Geometric Motion (Pars IV — Physics & De Caelo)**: In *Physics* II, lect. 3 (:ref:`Pars IV, s1 <pars-4-s1-en>`), Aquinas defends :term:`abstrahentium non est mendacium <abstrahentium-non-est-mendacium>`—there is no falsehood in those who abstract geometric boundaries from physical bodies. In *Physics* IV, lect. 7 (:ref:`Pars IV, s3 <pars-4-s3-en>`), he shows how :term:`immobile place <locus-immobilis>` and congruence emerge from local translation; in *Physics* VI, lect. 1 (:ref:`Pars IV, s4 <pars-4-s4-en>`), he rigorously proves that no continuum can be composed of indivisible points; and in *De Caelo* I, lect. 2 (:ref:`Pars IV, s5 <pars-4-s5-en>`), he clarifies how geometers speak imaginatively of a moving point describing a line.",
        "",
        "5. **Individual Intelligible Matter, Heuristic Division in Act, and Ipsum Esse (Pars V — Metaphysics & Systematic Works)**: Culminating in *Metaphysics* VII, lect. 10–11 (:ref:`Pars V, s2–s3 <pars-5-s2-en>`), Aquinas distinguishes :term:`individual intelligible matter <materia-intelligibilis-individualis>` (whereby many mathematical circles of equal or unequal radius coexist and intersect) from :term:`common intelligible matter <materia-intelligibilis-communis>`. In *Metaphysics* IX, lect. 10 (:ref:`Pars V, s5 <pars-5-s5-en>`, Cathala #1894), he unveils the secret of geometric discovery (:term:`divisio figurarum in actu <divisio-in-actu>`): geometers discover truth by dividing figures in act—drawing the parallel line for :cite:`Euclid I.32 <euclid:elements:I.32>` or the radius for :cite:`Euclid III.31 <euclid:elements:III.31>`—making what was latent in potency immediately luminous to intellectual vision (*statim manifestum est videnti*). Finally, *Summa Theologiae* I (:ref:`Pars V, s6–s7 <pars-5-s6-en>`), *De Potentia* q. 7 a. 2 (:ref:`Pars V, s8 <pars-5-s8-en>`), and *De Veritate* q. 10 a. 6 (:ref:`Pars V, s9 <pars-5-s9-en>`) anchor the entire edifice in the light of the :term:`agent intellect <intellectus-agens>` and :term:`ipsum esse <ipsum-esse>`, the actuality of all acts.",
        "",
        rst_heading("3. Editorial Principles & Relation to the GEOMETOR Canon", H2_CHAR),
        "",
        "Every Latin text in ``Pars I–V`` (37 unabridged sections, 613 paragraphs, 65,402 Latin words) is reproduced diplomatically from public-domain critical editions (Leonine, Marietti Pirotta/Cathala–Spiazzi, and Decker via the :cite:`Corpus Thomisticum <corpus-thomisticum>`) with cryptographic SHA-256 verification in ``resources/aquinas/sources_manifest.json``. Facing English tracks provide complete, 1-to-1 paragraph-synchronized scholarly translations alongside analytical summaries, GEOMETOR commentary, and a 100% concordance of all 78 Thomistic citation keys in :person:`Peter Hoenen <hoenen>`\\ 's :cite:`*De Noetica Geometriae* <hoenen:1954>` and :person:`Luca Pacioli <pacioli>`\\ 's :cite:`*De Divina Proportione* <pacioli:1509>`.",
        "",
    ]

    la_lines = [
        ":title: Prooemium Editoris — De Scientia Mathematica apud S. Thomam",
        ":layout: book",
        "",
        ".. _prooemium-la:",
        "",
        rst_heading("Prooemium Editoris — De Scientia Mathematica et Materia Intelligibili", H1_CHAR),
        "",
        ".. rubric:: * Praefatio Critica et Sententiae Capitales Sancti Thomae de Aquino *",
        "",
        ".. folio:: Prooemium",
        "",
        rst_heading("1. Ratio Huius Codicis", H2_CHAR),
        "",
        "Hic codex colligit atque integre exhibet triginta septem lectiones et articulos capitales quibus :person:`Sanctus Thomas de Aquino <aquinas>` (1225–1274) naturam, obiectum, methodum et certitudinem scientiae mathematicae fundavit. Omnes textus Latini in :ref:`Partibus I–V <pars-1-la>` (613 paragraphi) de verbo ad verbum ex editionibus criticis Leonina, Marietti (:person:`Pirotta <pirotta>`, :person:`Cathala <cathala>`) et :person:`Decker <decker>` (secundum recensionem :cite:`Corporis Thomistici <corpus-thomisticum>`) sine ulla immutatione deprompti sunt, addita plena concordantia omnium septuaginta octo locorum Thomisticorum quos :person:`Petrus Hoenen, S.I. <hoenen>` in opere suo :cite:`*De Noetica Geometriae* (1954) <hoenen:1954>` allegavit.",
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

    summary_lines = [
        ":title: Prooemium Summary — Architecture of the Codex",
        ":layout: book",
        "",
        ".. _prooemium-summary:",
        "",
        rst_heading("Prooemium — Executive Summary", H1_CHAR),
        "",
        ".. rubric:: *Overview of the Five-Part Thomistic Codex on Mathematical Science*",
        "",
        "This Codex unites the foundational primary texts in which :person:`St. Thomas Aquinas <aquinas>` establishes the ontology, psychology, logic, and heuristic discovery of geometry.",
        "",
        rst_heading("Five-Part Structural Overview", H2_CHAR),
        "",
        ".. list-table:: Architecture of *Opera de Scientia Mathematica et Materia Intelligibili*",
        "   :header-rows: 1",
        "   :widths: 14 28 28 30",
        "",
        "   * - Part",
        "     - Primary Thomistic Work(s)",
        "     - Core Doctrinal Focus",
        "     - Key Geometric Paradigm",
        "   * - :ref:`Pars I <pars-1-en>`",
        "     - *Super Boetium De Trinitate* (qq. 5–6)",
        "     - Twofold intellectual act; *separatio* vs. *abstractio formae*; *materia intelligibilis*; judgment terminating at imagination",
        "     - Continuous extension abstracted from sensible qualities; imaginative verification of figures",
        "   * - :ref:`Pars II <pars-2-en>`",
        "     - *In Posteriora Analytica* (I.1–6, 17–19, 42; II.20)",
        "     - Supreme certitude; *dignitates*, *suppositiones*, *petitiones*; dust diagrams; unit vs. point; inductive *intellectus*",
        "     - Euclid's Common Notions & Postulates; triangle in semicircle (I.3); point with *positio*",
        "   * - :ref:`Pars III <pars-3-en>`",
        "     - *Sentencia libri De anima* (I.11; II.16; III.8, 12–13)",
        "     - Moving point in imagination; *carnes et ossa* vs. *continuum*; *conversio ad phantasmata*; hand as *organum organorum*",
        "     - Determinate drawn triangle manifesting universal angle properties",
        "   * - :ref:`Pars IV <pars-4-en>`",
        "     - *In Physicam* (II.3, III.5, IV.7, VI.1) & *De Caelo* (I.2, II.2)",
        "     - *Abstrahentium non est mendacium*; ten categories; immobile place; continuum non-atomism; three dimensions",
        "     - Infinite divisibility of line; rigid translation & congruence; oriented figures",
        "   * - :ref:`Pars V <pars-5-en>`",
        "     - *In Metaphysicam* (V.9, VII.10–11, IX.3 & 10), *ST* I, *De Potentia* 7.2, *De Veritate* 10.6",
        "     - Individual vs. common *materia intelligibilis*; discovery by division in act; agent intellect; *ipsum esse*",
        "     - Bronze vs. mathematical circles; Euclid I.32 & III.31 auxiliary constructions; diagonal incommensurability",
        "",
    ]

    notes_lines = [
        ":title: Prooemium Notes — GEOMETOR & the Thomistic-Hoenen Tradition",
        ":layout: book",
        "",
        ".. _prooemium-notes:",
        "",
        rst_heading("Prooemium — Editorial & GEOMETOR Notes", H1_CHAR),
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

    (pdir / "prooemium-en.rst").write_text("\n".join(en_lines), encoding="utf-8")
    (pdir / "prooemium-la.rst").write_text("\n".join(la_lines), encoding="utf-8")
    (pdir / "prooemium-summary.rst").write_text("\n".join(summary_lines), encoding="utf-8")
    (pdir / "prooemium-notes.rst").write_text("\n".join(notes_lines), encoding="utf-8")


def build_part_tracks(part_num: int, codex_dir: Path) -> None:
    """Compile ``pars-{N}-{en,la,summary,notes}.rst`` for ``part_num`` (1..5)."""
    la_part = load_latin_part(part_num)
    apparatus = load_part_apparatus(part_num)
    part_id = str(la_part["part_id"])
    pdir = codex_dir / part_id
    pdir.mkdir(parents=True, exist_ok=True)

    # 1. English Track (`pars-N-en.rst`) & 2. Latin Track (`pars-N-la.rst`)
    en_lines = [
        f":title: {la_part['title_en']}",
        ":layout: book",
        "",
        f".. _{part_id}-en:",
        "",
        rst_heading(str(la_part["title_en"]), H1_CHAR),
        "",
        f".. rubric:: *{la_part['subtitle_en']}*",
        "",
        f"**Source Work**: *{la_part['work_title']}* ({la_part['date_composed']}) · :ref:`Switch to Diplomatic Latin <{part_id}-la>` · :ref:`Summary <{part_id}-summary>` · :ref:`GEOMETOR Notes <{part_id}-notes>`",
        "",
        "----",
        "",
    ]

    la_lines = [
        f":title: {la_part['title_la']}",
        ":layout: book",
        "",
        f".. _{part_id}-la:",
        "",
        rst_heading(str(la_part["title_la"]), H1_CHAR),
        "",
        f".. rubric:: *{la_part['subtitle_la']}*",
        "",
        f"**Opus**: *{la_part['work_title']}* ({la_part['date_composed']}) · :ref:`English Translation <{part_id}-en>` · :ref:`Summary <{part_id}-summary>` · :ref:`GEOMETOR Notes <{part_id}-notes>`",
        "",
    ]
    for ed in la_part["editions"]:
        la_lines.append(f"* {normalize_inline_rst(str(ed))}")
    la_lines.extend(["", "----", ""])

    for sec in la_part["sections"]:
        sec_id = str(sec["sec_id"])
        folio = str(sec["folio"])
        en_sec = load_english_section(part_num, sec_id)

        en_lines.extend([
            f".. _{part_id}-{sec_id}-en:",
            "",
            f".. folio:: {folio}",
            "",
            rst_heading(str(sec["heading_en"]), H2_CHAR),
            "",
            f"*Latin Locus*: :ref:`{folio} <{part_id}-{sec_id}-la>` · *Commentary*: :ref:`Notes on {folio} <{part_id}-{sec_id}-notes>`",
            "",
        ])

        la_lines.extend([
            f".. _{part_id}-{sec_id}-la:",
            "",
            f".. folio:: {folio}",
            "",
            rst_heading(str(sec["heading_la"]), H2_CHAR),
            "",
            f"*Versio Anglica*: :ref:`{folio} <{part_id}-{sec_id}-en>` · *Commentarius*: :ref:`Notae ad {folio} <{part_id}-{sec_id}-notes>`",
            "",
        ])

        seen_en: set[str] = set()
        seen_la: set[str] = set()

        for la_p, en_p in zip(sec["paragraphs"], en_sec["paragraphs"], strict=True):
            badge = format_para_badge(la_p)
            raw_en = normalize_inline_rst(str(en_p["english"]))
            raw_la = normalize_inline_rst(str(la_p["latin"]))

            tagged_en = enrich_inline_apparatus(raw_en, EN_TAG_RULES, seen_en)
            tagged_la = enrich_inline_apparatus(raw_la, LA_TAG_RULES, seen_la)

            en_lines.append(f"{badge} {tagged_en}")
            en_lines.append("")

            la_lines.append(f"{badge} {tagged_la}")
            la_lines.append("")

    # 3. Summary Track (`pars-N-summary.rst`)
    sum_lines = [
        f":title: Summary — {la_part['title_en']}",
        ":layout: book",
        "",
        f".. _{part_id}-summary:",
        "",
        rst_heading(f"Summary — {la_part['title_en']}", H1_CHAR),
        "",
        f".. rubric:: *Analytical Synopsis of {la_part['work_title']} ({la_part['date_composed']})*",
        "",
        rst_heading("Executive Thesis", H2_CHAR),
        "",
    ]
    seen_sum: set[str] = set()
    for para in str(apparatus["executive_thesis"]).split("\n\n"):
        clean_p = normalize_inline_rst(para)
        if clean_p:
            sum_lines.append(enrich_inline_apparatus(clean_p, EN_TAG_RULES, seen_sum))
            sum_lines.append("")

    sum_lines.extend([
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
        sum_lines.extend([
            f"   * - *{clean_lat}*",
            f"     - {normalize_inline_rst(str(row['english_term']))}",
            f"     - ``{normalize_inline_rst(str(row['locus']))}``",
            f"     - {normalize_inline_rst(str(row['significance']))}",
        ])
    sum_lines.append("")

    sum_lines.extend([
        rst_heading("Section-by-Section Analytical Breakdown", H2_CHAR),
        "",
    ])
    for s_sum in apparatus["section_summaries"]:
        sec_id = str(s_sum["sec_id"])
        folio = str(s_sum["folio"])
        sum_lines.extend([
            f".. _{part_id}-{sec_id}-summary:",
            "",
            rst_heading(str(s_sum["heading"]), H3_CHAR),
            "",
            f"*Read Primary Text*: :ref:`English ({folio}) <{part_id}-{sec_id}-en>` · :ref:`Latin ({folio}) <{part_id}-{sec_id}-la>` · :ref:`Commentary <{part_id}-{sec_id}-notes>`",
            "",
        ])
        seen_sec_sum: set[str] = set()
        for para in str(s_sum["argument_summary"]).split("\n\n"):
            clean_p = normalize_inline_rst(para)
            if clean_p:
                sum_lines.append(enrich_inline_apparatus(clean_p, EN_TAG_RULES, seen_sec_sum))
                sum_lines.append("")
        if s_sum.get("key_theses"):
            sum_lines.append("**Key Theses**:")
            sum_lines.append("")
            for th in s_sum["key_theses"]:
                sum_lines.append(f"* {normalize_inline_rst(str(th))}")
            sum_lines.append("")

    # 4. Notes / GEOMETOR Commentary Track (`pars-N-notes.rst`)
    notes_lines = [
        f":title: Commentary & Notes — {la_part['title_en']}",
        ":layout: book",
        "",
        f".. _{part_id}-notes:",
        "",
        rst_heading(f"Commentary & GEOMETOR Notes — {la_part['title_en']}", H1_CHAR),
        "",
        ".. rubric:: *Aristotelian Sources, Euclidean Counterparts, Hoenen's Noetics, and Symbolic Constructive Geometry*",
        "",
    ]
    for s_note in apparatus["section_notes"]:
        sec_id = str(s_note["sec_id"])
        folio = str(s_note["folio"])
        seen_note: set[str] = set()
        notes_lines.extend([
            f".. _{part_id}-{sec_id}-notes:",
            "",
            rst_heading(str(s_note["heading"]), H2_CHAR),
            "",
            f"*Primary Text*: :ref:`English ({folio}) <{part_id}-{sec_id}-en>` · :ref:`Latin ({folio}) <{part_id}-{sec_id}-la>` · :ref:`Summary <{part_id}-{sec_id}-summary>`",
            "",
            rst_heading("Aristotelian & Scholastic Foundations", H3_CHAR),
            "",
            enrich_inline_apparatus(normalize_inline_rst(str(s_note["aristotelian_foundations"])), EN_TAG_RULES, seen_note),
            "",
            rst_heading("Euclidean & Classical Geometric Counterparts", H3_CHAR),
            "",
            enrich_inline_apparatus(normalize_inline_rst(str(s_note["euclidean_counterparts"])), EN_TAG_RULES, seen_note),
            "",
            rst_heading("Hoenen's De Noetica Geometriae & Judgment Theory", H3_CHAR),
            "",
            enrich_inline_apparatus(normalize_inline_rst(str(s_note["hoenen_noetics"])), EN_TAG_RULES, seen_note),
            "",
            rst_heading("GEOMETOR Constructive & Symbolic Significance", H3_CHAR),
            "",
            enrich_inline_apparatus(normalize_inline_rst(str(s_note["geometor_significance"])), EN_TAG_RULES, seen_note),
            "",
        ])

    (pdir / f"{part_id}-en.rst").write_text("\n".join(en_lines), encoding="utf-8")
    (pdir / f"{part_id}-la.rst").write_text("\n".join(la_lines), encoding="utf-8")
    (pdir / f"{part_id}-summary.rst").write_text("\n".join(sum_lines), encoding="utf-8")
    (pdir / f"{part_id}-notes.rst").write_text("\n".join(notes_lines), encoding="utf-8")


def build_concordance_page(codex_dir: Path) -> None:
    """Write ``docsrc/scientia_mathematica/concordance.rst``."""
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

    (codex_dir / "concordance.rst").write_text("\n".join(lines), encoding="utf-8")


def build_bibliography_page(codex_dir: Path) -> None:
    """Write ``docsrc/scientia_mathematica/bibliography.rst`` with ``cite-<slug>`` anchors."""
    citations = load_citations()

    lines = [
        ":title: Bibliographia et Fontes — Systematic Bibliography",
        ":layout: book",
        "",
        ".. _bibliography:",
        ".. _bibliographia-et-fontes:",
        "",
        rst_heading("Bibliographia et Fontes (Systematic Bibliography)", H1_CHAR),
        "",
        ".. rubric:: *Critical Editions, Classical Sources, and Modern Studies in Geometric Noetics*",
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

    (codex_dir / "bibliography.rst").write_text("\n".join(lines), encoding="utf-8")


def build_persons_page(codex_dir: Path) -> None:
    """Write ``docsrc/scientia_mathematica/persons.rst`` with ``person-<slug>`` anchors."""
    persons = load_persons()
    sorted_items = sorted(persons.values(), key=lambda p: p.name.lower())

    lines = [
        ":title: Index Nominum — Biographical Register of Persons",
        ":layout: book",
        "",
        ".. _persons:",
        ".. _index-nominum:",
        "",
        rst_heading("Index Nominum (Biographical Register)", H1_CHAR),
        "",
        ".. rubric:: *Philosophers, Geometers, Commentators, and Critical Editors*",
        "",
        f"This prosopographical register documents **{len(persons)} key figures** shaping Thomistic geometric noetics—from :person:`Pythagoras <pythagoras>`, :person:`Plato <plato>`, :person:`Aristotle <aristotle>`, and :person:`Euclid <euclid>` through :person:`Boethius <boethius>`, :person:`Avicenna <avicenna>`, :person:`Averroes <averroes>`, :person:`Albert the Great <albertus>`, :person:`Thomas Aquinas <aquinas>`, :person:`Cajetan <cajetan>`, and :person:`Luca Pacioli <pacioli>` to :person:`David Hilbert <hilbert>`, :person:`Peter Hoenen <hoenen>`, :person:`Étienne Gilson <gilson>`, and :person:`Bernard Lonergan <lonergan>`.",
        "",
        rst_heading("Alphabetical Directory", H2_CHAR),
        "",
    ]

    for p in sorted_items:
        slug = slugify_apparatus_key(p.slug)
        lines.append(f"* :ref:`{p.name} ({p.dates}) <person-{slug}>` — *{p.role}*")
    lines.extend(["", "----", "", rst_heading("Biographical Entries", H2_CHAR), ""])

    for p in sorted_items:
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

    (codex_dir / "persons.rst").write_text("\n".join(lines), encoding="utf-8")


def build_glossary_page(codex_dir: Path) -> None:
    """Write ``docsrc/scientia_mathematica/glossary.rst`` with ``term-<slug>`` anchors."""
    glossary = load_glossary()
    sorted_terms = sorted(glossary.values(), key=lambda g: g.headword.lower())

    lines = [
        ":title: Glossarium Technicum — Scholastic & Geometric Glossary",
        ":layout: book",
        "",
        ".. _glossary:",
        ".. _glossarium-technicum:",
        "",
        rst_heading("Glossarium Technicum (Technical Glossary)", H1_CHAR),
        "",
        ".. rubric:: *Lexicon of Thomistic Epistemology, Metaphysics, and Constructive Geometry*",
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

    (codex_dir / "glossary.rst").write_text("\n".join(lines), encoding="utf-8")


def compile_all(repo_root: Path | None = None) -> dict[str, object]:
    """Validate all JSON resources and compile the entire ``scientia_mathematica`` RST codex."""
    root = repo_root or get_repo_root()
    res_dir = root / "resources"
    stats = verify_codex_integrity(res_dir)
    manifest = load_sources_manifest(res_dir)

    codex_dir = root / "docsrc" / "scientia_mathematica"
    codex_dir.mkdir(parents=True, exist_ok=True)

    build_book_index(codex_dir, manifest)
    build_prooemium(codex_dir)
    for part_num in range(1, 6):
        build_part_tracks(part_num, codex_dir)
    build_concordance_page(codex_dir)
    build_bibliography_page(codex_dir)
    build_persons_page(codex_dir)
    build_glossary_page(codex_dir)

    return stats


def main() -> None:
    """CLI entry point for ``geometor-aquinas-compile``."""
    stats = compile_all(get_repo_root())
    print(f"Compiled geometor-aquinas Book Codex successfully: {stats}")


if __name__ == "__main__":
    main()
