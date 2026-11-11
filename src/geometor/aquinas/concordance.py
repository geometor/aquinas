"""Structured query, validation, and concordance API for ``geometor.aquinas``.

Loads and validates the verbatim diplomatic Latin texts, synchronized English
translations, scholarly commentary apparatus, and the 78-locus Hoenen–Aquinas–
Aristotle–Euclid–GEOMETOR concordance stored under ``resources/``.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def slugify_apparatus_key(target: str) -> str:
    """Normalize an apparatus key to match ``photon_platform.publish`` anchor slugs."""
    return re.sub(r"[^a-z0-9]+", "-", target.lower()).strip("-")


def get_repo_root() -> Path:
    """Return the root directory of the ``geometor-aquinas`` repository."""
    return Path(__file__).resolve().parents[3]


def get_resources_dir() -> Path:
    """Return the ``resources/`` directory containing primary texts and apparatus."""
    return get_repo_root() / "resources"


@dataclass(frozen=True)
class ConcordanceEntry:
    """Single locus entry in the Hoenen–Aquinas–Aristotle–Euclid–GEOMETOR concordance."""

    key: str
    slug: str
    author: str
    work_title: str
    locus: str
    critical_edition_ref: str
    codex_status: str
    codex_part: str
    codex_ref: str
    aristotle_source: str
    euclid_elements_link: str
    hoenen_occurrences: list[dict[str, Any]]
    hoenen_sample_context_en: str
    hoenen_sample_context_la: str
    hoenen_thesis: str
    geometor_relevance: str


@dataclass(frozen=True)
class PersonEntry:
    """Prosopographical entry in the Index Nominum (``resources/persons.json``)."""

    slug: str
    name: str
    dates: str
    role: str
    bio: str
    works: list[str]


@dataclass(frozen=True)
class GlossaryEntry:
    """Technical term entry in the Glossarium Technicum (``resources/glossary.json``)."""

    slug: str
    headword: str
    language: str
    translation: str
    definition: str


@dataclass(frozen=True)
class CitationEntry:
    """Bibliographic citation entry in ``resources/citations.json``."""

    key: str
    author: str
    work: str
    locus: str


def load_sources_manifest(resources_dir: Path | None = None) -> dict[str, Any]:
    """Load ``resources/aquinas/sources_manifest.json``."""
    base = resources_dir or get_resources_dir()
    path = base / "aquinas" / "sources_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_latin_part(part_num: int, resources_dir: Path | None = None) -> dict[str, Any]:
    """Load verbatim Latin source JSON for ``part_num`` (1..5)."""
    if part_num not in {1, 2, 3, 4, 5}:
        raise ValueError(f"part_num must be in 1..5, got {part_num}")
    base = resources_dir or get_resources_dir()
    path = base / "aquinas" / "sources" / f"pars_{part_num}_latin.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_english_section(
    part_num: int, sec_id: str, resources_dir: Path | None = None
) -> dict[str, Any]:
    """Load synchronized English translation JSON for ``(part_num, sec_id)``."""
    if part_num not in {1, 2, 3, 4, 5}:
        raise ValueError(f"part_num must be in 1..5, got {part_num}")
    base = resources_dir or get_resources_dir()
    path = base / "aquinas" / "translations" / f"pars_{part_num}" / f"{sec_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_part_apparatus(part_num: int, resources_dir: Path | None = None) -> dict[str, Any]:
    """Load scholarly summary and GEOMETOR commentary JSON for ``part_num`` (1..5)."""
    if part_num not in {1, 2, 3, 4, 5}:
        raise ValueError(f"part_num must be in 1..5, got {part_num}")
    base = resources_dir or get_resources_dir()
    path = base / "aquinas" / "commentary" / f"pars_{part_num}_apparatus.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_concordance_document(resources_dir: Path | None = None) -> dict[str, Any]:
    """Load the full ``resources/aquinas/concordance.json`` document."""
    base = resources_dir or get_resources_dir()
    path = base / "aquinas" / "concordance.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_concordance(resources_dir: Path | None = None) -> list[ConcordanceEntry]:
    """Load typed ``ConcordanceEntry`` records for all 78 Hoenen Thomistic keys."""
    doc = load_concordance_document(resources_dir)
    return [ConcordanceEntry(**entry) for entry in doc["entries"]]


def load_persons(resources_dir: Path | None = None) -> dict[str, PersonEntry]:
    """Load typed ``PersonEntry`` records from ``resources/persons.json``."""
    base = resources_dir or get_resources_dir()
    raw = json.loads((base / "persons.json").read_text(encoding="utf-8"))
    return {
        k: PersonEntry(
            slug=v["slug"],
            name=v["name"],
            dates=v["dates"],
            role=v["role"],
            bio=v["bio"],
            works=list(v.get("works", [])),
        )
        for k, v in raw.items()
    }


def load_glossary(resources_dir: Path | None = None) -> dict[str, GlossaryEntry]:
    """Load typed ``GlossaryEntry`` records from ``resources/glossary.json``."""
    base = resources_dir or get_resources_dir()
    raw = json.loads((base / "glossary.json").read_text(encoding="utf-8"))
    return {
        k: GlossaryEntry(
            slug=v["slug"],
            headword=v["headword"],
            language=v["language"],
            translation=v["translation"],
            definition=v["definition"],
        )
        for k, v in raw.items()
    }


def load_citations(resources_dir: Path | None = None) -> dict[str, CitationEntry]:
    """Load typed ``CitationEntry`` records from ``resources/citations.json``."""
    base = resources_dir or get_resources_dir()
    raw = json.loads((base / "citations.json").read_text(encoding="utf-8"))
    return {
        k: CitationEntry(
            key=v["key"],
            author=v["author"],
            work=v["work"],
            locus=v.get("locus", ""),
        )
        for k, v in raw.items()
    }


def verify_codex_integrity(resources_dir: Path | None = None) -> dict[str, Any]:
    """Verify cryptographic provenance, 1-to-1 Latin/English parity, and apparatus links.

    Raises ``ValueError`` if any SHA-256 digest mismatches, any ``ct_id`` paragraph lacks
    a synchronized English translation, or any concordance citation key is missing.
    """
    base = resources_dir or get_resources_dir()
    manifest = load_sources_manifest(base)
    aq_dir = base / "aquinas"

    total_paras = 0
    total_en_words = 0
    total_la_words = 0

    for idx, p_meta in enumerate(manifest["parts"], start=1):
        json_path = aq_dir / p_meta["json_source"]
        txt_path = aq_dir / p_meta["diplomatic_text"]
        if hashlib.sha256(json_path.read_bytes()).hexdigest() != p_meta["sha256_json"]:
            raise ValueError(f"SHA-256 mismatch on {json_path}")
        if hashlib.sha256(txt_path.read_bytes()).hexdigest() != p_meta["sha256_txt"]:
            raise ValueError(f"SHA-256 mismatch on {txt_path}")

        la_part = load_latin_part(idx, base)
        apparatus = load_part_apparatus(idx, base)
        sec_ids = [s["sec_id"] for s in la_part["sections"]]
        if [s["sec_id"] for s in apparatus["section_summaries"]] != sec_ids:
            raise ValueError(f"Section summary mismatch in pars-{idx}")
        if [s["sec_id"] for s in apparatus["section_notes"]] != sec_ids:
            raise ValueError(f"Section notes mismatch in pars-{idx}")

        for sec in la_part["sections"]:
            en_sec = load_english_section(idx, sec["sec_id"], base)
            la_ids = [p["ct_id"] for p in sec["paragraphs"]]
            en_ids = [p["ct_id"] for p in en_sec["paragraphs"]]
            if la_ids != en_ids:
                raise ValueError(
                    f"Latin/English ct_id mismatch in pars-{idx} {sec['sec_id']}: "
                    f"{len(la_ids)} vs {len(en_ids)}"
                )
            for la_p, en_p in zip(sec["paragraphs"], en_sec["paragraphs"], strict=True):
                en_txt = en_p["english"].strip()
                la_txt = la_p["latin"].strip()
                if not en_txt or not la_txt:
                    raise ValueError(f"Empty text in pars-{idx} {sec['sec_id']} ct_id={la_p['ct_id']}")
                total_paras += 1
                total_la_words += len(la_txt.split())
                total_en_words += len(en_txt.split())

    concordance = load_concordance(base)
    citations = load_citations(base)
    persons = load_persons(base)
    glossary = load_glossary(base)

    for entry in concordance:
        if entry.key not in citations:
            raise ValueError(f"Concordance key {entry.key} missing from citations.json")

    return {
        "parts": len(manifest["parts"]),
        "sections": manifest["totals"]["section_count"],
        "paragraphs": total_paras,
        "latin_words": total_la_words,
        "english_words": total_en_words,
        "concordance_keys": len(concordance),
        "persons": len(persons),
        "glossary_terms": len(glossary),
        "citations": len(citations),
    }
