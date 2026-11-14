"""GEOMETOR • aquinas — Opera de Scientia Mathematica et Materia Intelligibili.

Critical bilingual Book Codex, philological apparatus, and Hoenen–Aquinas–Aristotle–Euclid
concordance for St. Thomas Aquinas's foundational writings on mathematical science,
intelligible matter (*materia intelligibilis*), abstraction, heuristic division in act,
and mathematical judgment terminating at the imagination.
"""

from __future__ import annotations

from geometor.aquinas.concordance import (
    CitationEntry,
    ConcordanceEntry,
    GlossaryEntry,
    PersonEntry,
    get_resources_dir,
    load_citations,
    load_concordance,
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

__version__ = "0.1.1"

__all__ = [
    "__version__",
    "CitationEntry",
    "ConcordanceEntry",
    "GlossaryEntry",
    "PersonEntry",
    "get_resources_dir",
    "load_citations",
    "load_concordance",
    "load_concordance_document",
    "load_english_section",
    "load_glossary",
    "load_latin_part",
    "load_part_apparatus",
    "load_persons",
    "load_sources_manifest",
    "slugify_apparatus_key",
    "verify_codex_integrity",
]
