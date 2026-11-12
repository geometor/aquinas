"""Comprehensive test suite for ``geometor.aquinas`` resources, concordance, and RST compiler."""

from __future__ import annotations

from pathlib import Path

from geometor.aquinas import (
    __version__,
    get_resources_dir,
    load_citations,
    load_concordance,
    load_concordance_document,
    load_glossary,
    load_latin_part,
    load_persons,
    load_sources_manifest,
    slugify_apparatus_key,
    verify_codex_integrity,
)
from geometor.aquinas.compile_codex import compile_all


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_sources_manifest_and_latin_corpus() -> None:
    manifest = load_sources_manifest()
    assert manifest["totals"]["part_count"] == 5
    assert manifest["totals"]["section_count"] == 37
    assert manifest["totals"]["paragraph_count"] == 613
    assert manifest["totals"]["latin_word_count"] > 60_000

    res = get_resources_dir() / "aquinas"
    for idx, part_meta in enumerate(manifest["parts"], start=1):
        assert (res / part_meta["json_source"]).is_file()
        assert (res / part_meta["diplomatic_text"]).is_file()
        la_part = load_latin_part(idx)
        assert len(la_part["sections"]) == part_meta["section_count"]


def test_marietti_paragraph_numbers_exact() -> None:
    # Verify exact Pirotta & Cathala Marietti numbers cited by Hoenen
    pars_3 = load_latin_part(3)
    da_i_11_nos = [p["marietti_no"] for p in pars_3["sections"][0]["paragraphs"]]
    assert 170 in da_i_11_nos

    da_iii_12_nos = [p["marietti_no"] for p in pars_3["sections"][3]["paragraphs"]]
    for n in range(770, 778):
        assert n in da_iii_12_nos

    da_iii_13_nos = [p["marietti_no"] for p in pars_3["sections"][4]["paragraphs"]]
    assert 791 in da_iii_13_nos

    pars_5 = load_latin_part(5)
    met_v_9_nos = [p["marietti_no"] for p in pars_5["sections"][0]["paragraphs"]]
    assert 890 in met_v_9_nos

    met_vii_10_nos = [p["marietti_no"] for p in pars_5["sections"][1]["paragraphs"]]
    assert 1496 in met_vii_10_nos

    met_ix_3_nos = [p["marietti_no"] for p in pars_5["sections"][3]["paragraphs"]]
    assert 1805 in met_ix_3_nos
    assert 1806 in met_ix_3_nos

    met_ix_10_nos = [p["marietti_no"] for p in pars_5["sections"][4]["paragraphs"]]
    assert 1894 in met_ix_10_nos


def test_concordance_and_apparatus_registries() -> None:
    doc = load_concordance_document()
    entries = load_concordance()
    assert len(entries) == 78
    assert doc["summary_counts"]["authentic_aquinas_keys"] == 76
    assert doc["summary_counts"]["pseudo_thomas_keys"] == 2

    persons = load_persons()
    required_persons = {
        "aristotle",
        "boethius",
        "avicenna",
        "averroes",
        "albertus",
        "aquinas",
        "cajetan",
        "pirotta",
        "hoenen",
        "gilson",
        "lonergan",
        "euclid",
        "pacioli",
    }
    assert required_persons.issubset(persons.keys())

    glossary = load_glossary()
    required_terms = {
        "materia-intelligibilis",
        "materia-sensibilis",
        "abstractio-formae",
        "abstractio-totius",
        "separatio",
        "phantasma",
        "conversio-ad-phantasmata",
        "terminari-ad-imaginationem",
        "quidditas",
        "ipsum-esse",
        "communes-animi-conceptiones",
        "divisio-in-actu",
    }
    assert required_terms.issubset(glossary.keys())

    citations = load_citations()
    for entry in entries:
        assert entry.key in citations


def test_full_codex_integrity_and_rst_compilation() -> None:
    stats = verify_codex_integrity()
    assert stats["parts"] == 5
    assert stats["sections"] == 37
    assert stats["paragraphs"] == 613
    assert stats["english_words"] > 60_000
    assert stats["concordance_keys"] == 78

    repo_root = get_resources_dir().parent
    compiled_stats = compile_all(repo_root)
    assert compiled_stats == stats

    codex_dir: Path = repo_root / "docsrc" / "scientia_mathematica"
    assert (codex_dir / "index.rst").is_file()
    for track in ("en", "la", "summary", "notes"):
        assert (codex_dir / "prooemium" / f"prooemium-{track}.rst").is_file()
        for idx in range(1, 6):
            assert (codex_dir / f"pars-{idx}" / f"pars-{idx}-{track}.rst").is_file()

    for app_file in ("concordance.rst", "bibliography.rst", "persons.rst", "glossary.rst"):
        assert (codex_dir / app_file).is_file()

    # Verify anchor presence in apparatus RST files
    bib_rst = (codex_dir / "bibliography.rst").read_text(encoding="utf-8")
    for k in load_citations():
        assert f".. _cite-{slugify_apparatus_key(k)}:" in bib_rst

    persons_rst = (codex_dir / "persons.rst").read_text(encoding="utf-8")
    for k in load_persons():
        assert f".. _person-{slugify_apparatus_key(k)}:" in persons_rst

    glossary_rst = (codex_dir / "glossary.rst").read_text(encoding="utf-8")
    for k in load_glossary():
        assert f".. _term-{slugify_apparatus_key(k)}:" in glossary_rst
