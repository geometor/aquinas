=========
changelog
=========

0.1.1 (2026-11-13)
------------------

- **added**: Added track-aware primary-source folio map (``resources/aquinas/folio_map.json``) resolving 76/76 folio directives to verified Latin text loci and Oxford/Leonine source files.

0.1.0 (2026-11-11)
------------------

- Initial release of ``geometor-aquinas`` (*Sancti Thomae de Aquino Opera de Scientia Mathematica et Materia Intelligibili*).
- Assembled 37 unabridged sections (613 paragraphs, 65,402 diplomatic Latin words) across Five Parts: *Super Boetium De Trinitate* (qq. 5–6), *Expositio libri Posteriorum Analyticorum* (I.1–6, 17–19, 42; II.20), *Sentencia libri De anima* (I.11; II.16; III.8, 12–13), *In Physicam* (II.3, III.5, IV.7, VI.1) & *De Caelo* (I.2, II.2), and *Sententia super Metaphysicam* (V.9, VII.10–11, IX.3 & 10) with *Summa Theologiae* I, *De Potentia* q. 7 a. 2, and *De Veritate* q. 10 a. 6.
- Produced 1-to-1 paragraph-synchronized English translations, executive summaries, and GEOMETOR / Euclidean / Aristotelian commentary tracks (`-en`, `-la`, `-summary`, `-notes`) using ``photon_platform.publish`` ``:layout: book``.
- Built complete 78-key Hoenen–Aquinas–Aristotle–Euclid–GEOMETOR concordance (`resources/aquinas/concordance.json`) together with interactive ``:cite:`` (113 entries), ``:person:`` (30 entries), and ``:term:`` (36 entries) apparatus registries.
