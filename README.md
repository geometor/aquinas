# GEOMETOR • aquinas

**Sancti Thomae de Aquino Opera de Scientia Mathematica et Materia Intelligibili** — *Foundational Texts on Mathematical Science, Intelligible Matter, Abstraction, Heuristic Construction, and Judgment*.

`geometor-aquinas` is a critical multi-track bilingual **Book Codex** (`:layout: book`), philological source archive, and 78-locus concordance assembling the foundational writings of **St. Thomas Aquinas, O.P. (1225–1274)** on the ontology, psychology, demonstrative logic, and heuristic discovery of geometry.

Within the **GEOMETOR** Classical Canon, this repository supplies the primary thirteenth-century Thomistic foundation underlying **Fr. Peter Hoenen, S.J.**'s *De Noetica Geometriae* (`geometor-hoenen`), **Fra Luca Pacioli**'s *De Divina Proportione* (`geometor-pacioli`), and Euclid's *Elements* (`geometor-euclid` & `geometor-elements`), while illuminating the computational architecture of `geometor.model`, `geometor.explorer`, and `geometor.divine`.

---

## Architecture of the Five-Part Book Codex

Published with [`photon-platform/publish`](https://github.com/photon-platform/publish), every Part of `docsrc/scientia_mathematica/` provides four synchronized, track-preserving companion views (**English**, **Latin**, **Summary**, and **Notes**):

1. **Pars I — *Super Boetium De Trinitate* (Questions V–VI)**:
   - Unabridged Questions 5 (Articles 1–4) and 6 (Articles 1–2): the twofold operation of the intellect, metaphysical *separatio* vs. natural *abstractio totius* vs. mathematical *abstractio formae*, continuous extension as *materia intelligibilis* (q. 5, a. 3), proceeding *disciplinaliter* (q. 6, a. 1), and why mathematical judgment must terminate at the imagination (*terminari ad imaginationem*, q. 6, a. 2).
2. **Pars II — *Expositio libri Posteriorum Analyticorum* (Book I, Lect. 1–6, 17–19, 42; Book II, Lect. 20)**:
   - Why mathematics attains the *certissimus modus demonstrationis* (I.1); twofold foreknowledge of unit and triangle (I.2); recognizing universal theorems in singular figures inscribed in a semicircle (I.3); *dignitates / communes animi conceptiones* vs. *suppositiones* and *petitiones* (I.5, I.18–19); why the geometer does not demonstrate of rough lines drawn in dust (I.19); unit without position vs. point having position (I.42); and the origin of *intellectus* from sense, memory, and *experimentum* (II.20).
3. **Pars III — *Sentencia libri De anima* (Book I, Lect. 11; Book II, Lect. 16; Book III, Lect. 8, 12–13)**:
   - Geometers imagining a moving point describing a line (I.11, Pirotta #170); fluent being of sound vs. permanent extension (II.16); *carnes et ossa : simum :: continuum : rectum* (III.8); why *nequaquam sine phantasmate intelligit anima* even in abstract geometry (III.12, Pirotta #770–777); and the hand as *organum organorum* / intellect as *species specierum* (III.13, #791).
4. **Pars IV — *In Physicam* (II.3, III.5, IV.7, VI.1) & *In De Caelo* (I.2, II.2)**:
   - *Abstrahentium non est mendacium* (Phys. II.3); the ten categories proportional to modes of being (Phys. III.5); immobile place and local translation (Phys. IV.7); proof that no continuum is composed of indivisible points (Phys. VI.1); completeness of three spatial dimensions and kinematic speech in geometry (De Caelo I.2); and positional orientation in mathematical figures (De Caelo II.2).
5. **Pars V — *Sententia super Metaphysicam* (V.9, VII.10–11, IX.3 & 10) & Systematic Works (*ST* I, *De Potentia* q. 7 a. 2, *De Veritate* q. 10 a. 6)**:
   - Propositional truth and the incommensurable diagonal (Metaph. V.9, Cathala #890–895); bronze vs. mathematical circles in individual and common *materia intelligibilis* (Metaph. VII.10–11, #1496); discovering geometric truth by dividing figures in act—Euclid I.32 & III.31 (Metaph. IX.10, #1894); agent intellect, phantasms, and infinite extendibility (*ST* I q. 7 a. 1 & 3, q. 12 a. 4, q. 84 a. 6–7, q. 85 a. 1); *ipsum esse* as actuality of all acts (*De Potentia* q. 7 a. 2); and first indemonstrable principles (*De Veritate* q. 10 a. 6).

---

## Primary Corpus & Apparatus Metrics

- **5 Parts · 37 Unabridged Sections · 613 Synchronized Paragraphs** (~65,400 verbatim diplomatic Latin words with SHA-256 provenance in `resources/aquinas/sources_manifest.json`).
- **100% Hoenen Thomistic Concordance**: `resources/aquinas/concordance.json` maps all **78** Thomistic & scholastic citation keys from `geometor-hoenen` to critical editions, Aristotle, Euclid's *Elements*, and GEOMETOR.
- **Interactive Hover Apparatus**: `resources/citations.json` (113 entries), `resources/persons.json` (30 biographies), and `resources/glossary.json` (36 technical terms).

---

## Development & Documentation Build

```bash
# Run integrity verification & test suite
pytest

# Lint source and tests
ruff check src tests

# Recompile the Multi-Track Book Codex RST tree from JSON sources
uv run --no-sync python3 -m geometor.aquinas.compile_codex

# Build HTML documentation into docs/
publish build
```

## License

Code, original scholarly translations, commentary, and structured concordance data are released under the [MIT License](LICENSE). All primary Latin texts derive from public-domain critical editions (Leonine, Marietti, Decker / Corpus Thomisticum).
