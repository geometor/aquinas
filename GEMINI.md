# GEMINI.md — `geometor-aquinas`

## Purpose & Role in the GEOMETOR Ecosystem

`geometor-aquinas` (`/home/phi/PROJECTS/geometor/aquinas`) is the critical bilingual **Multi-Track Book Codex** (`:layout: book`) and structured concordance of **St. Thomas Aquinas's Foundational Texts on Mathematical Science, *Materia Intelligibilis*, Abstraction, and Judgment** (*Opera de Scientia Mathematica et Materia Intelligibili*).

Within Pillar III (**Classical Canon & Historical Reconstructions**) of GEOMETOR, `aquinas` anchors the philosophical bridge connecting:
- **Classical Geometry**: `euclid`, `elements`, `pappus`, and `pacioli` (*De Divina Proportione*, 1509).
- **Modern Geometric Noetics**: `hoenen` (Peter Hoenen S.J., *De Noetica Geometriae*, 1954—100% of whose 78 Thomistic citation keys are mapped in `resources/aquinas/concordance.json`).
- **Symbolic & Visual Engines**: `model` (exact SymPy algebraic geometry in *materia intelligibilis*), `explorer` (the interactive SVG *phantasma* where mathematical judgment terminates), and `divine` (automated discovery of golden sections via *divisio in actu*).

---

## Repository Layout

- `resources/`
  - `citations.json`: 113 bibliographic editions and cited loci powering `:cite:` hover tooltips.
  - `persons.json`: 30 prosopographical entries powering `:person:` hover tooltips.
  - `glossary.json`: 36 scholastic and geometric terms powering `:term:` hover tooltips.
  - `aquinas/sources_manifest.json`: SHA-256 provenance manifest for all 5 Parts (37 sections, 613 paragraphs, 65,402 verbatim Latin words).
  - `aquinas/sources/`: Verbatim public-domain Latin JSON (`pars_1_latin.json`..`pars_5_latin.json`) and diplomatic plain-text editions (`*.la.txt`) with exact Leonine and Marietti (Pirotta / Cathala–Spiazzi) paragraph numbering.
  - `aquinas/translations/pars_{1..5}/`: Synchronized 1-to-1 English translations keyed by `ct_id`.
  - `aquinas/commentary/pars_{1..5}_apparatus.json`: Structured analytical summaries and Aristotelian / Euclidean / Hoenen / GEOMETOR commentary.
  - `aquinas/concordance.json`: Complete 78-key Hoenen–Aquinas–Aristotle–Euclid–GEOMETOR concordance.
- `src/geometor/aquinas/`
  - `__init__.py`: Package metadata (`__version__ = "0.1.0"`) and public exports.
  - `concordance.py`: Typed dataclasses, JSON loaders, and `verify_codex_integrity()`.
  - `compile_codex.py`: Deterministic compiler generating `docsrc/scientia_mathematica/` across all four tracks (`-en`, `-la`, `-summary`, `-notes`) and apparatus pages.
- `docsrc/`
  - `conf.py`, `index.rst`, `about/`, `mission/`, `log/`, `modules/`, `connect.rst`, `changelog.rst`.
  - `scientia_mathematica/`: `:layout: book` Multi-Track Codex (`prooemium/`, `pars-1/`..`pars-5/`, `concordance.rst`, `bibliography.rst`, `persons.rst`, `glossary.rst`).
- `tests/test_aquinas.py`: Automated verification of SHA-256 digests, Marietti numbers, 1-to-1 Latin/English parity, and RST compilation.

---

## Key Workflows

- **Validate & Test**: `pytest`
- **Lint**: `ruff check src tests`
- **Build Sphinx Book Codex**: `publish build`
