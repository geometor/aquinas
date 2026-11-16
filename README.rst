GEOMETOR • aquinas
==================

**Visit the Online Archive:** https://geometor.github.io/aquinas/

**St. Thomas Aquinas • Super Boetium De Trinitate & Aristotelian Commentaries • semantic digital archive**

Mission
-------

``geometor/aquinas`` is part of the interconnected `GEOMETOR <https://geometor.com>`_ semantic digital archive. It provides a critical multi-track bilingual Book Codex and concordance assembling the foundational writings of St. Thomas Aquinas on mathematical science, intelligible matter, abstraction, and the epistemic certitude of geometry. The archive liberates these thirteenth-century texts from isolated print bounds into addressable semantic units, synchronized Latin-English tracks, primary-source citation provenance, and exact symbolic connections across the GEOMETOR corpus.

Books in This Archive
---------------------

- **`Super Boetium De Trinitate (Quaestiones V–VI) <https://geometor.github.io/aquinas/super_boetium_de_trinitate/>`_** — Expositio super librum Boethii De Trinitate, treating the division of speculative science, mathematical abstraction (*abstractio formae*), and intelligible matter.
- **`Expositio libri Posteriorum Analyticorum <https://geometor.github.io/aquinas/analytica_posteriora/>`_** — Commentary on Aristotle's *Posterior Analytics*, establishing the demonstrative certitude of mathematics and Euclidean principles.
- **`Sentencia libri De anima <https://geometor.github.io/aquinas/de_anima/>`_** — Commentary on Aristotle's *De Anima*, analyzing the phantasm in geometry, continuous extension, and the intellect.
- **`Commentaria in libros Physicorum et De Caelo <https://geometor.github.io/aquinas/physica/>`_** — Commentaries on Aristotle's *Physics* and *On the Heavens*, demonstrating the non-atomism of the continuum and spatial dimensions.
- **`Sententia super Metaphysicam <https://geometor.github.io/aquinas/metaphysica/>`_** — Commentary on Aristotle's *Metaphysics*, investigating intelligible matter, actuality, and geometric truth discovered by division in act.
- **`Summa Theologiae et Quaestiones Disputatae <https://geometor.github.io/aquinas/summa_theologiae/>`_** — Systematic syntheses on *ipsum esse*, the geometer's infinite line, and indemonstrable first principles.

Repository Contents
-------------------

- ``docsrc/`` — Multi-track Book Codex, apparatus, and Sphinx documentation compiled by `PHOTON publish <https://github.com/photon-platform/publish>`_.
- ``resources/`` — Diplomatic Latin sources, Hoenen Thomistic concordance, and apparatus registries (citations, persons, glossary).
- ``src/geometor/aquinas/`` — Python codex compilation and integrity verification tools.

Local Build & Verification
--------------------------

.. code-block:: bash

   publish build
   uv run --no-sync pytest

Part of the GEOMETOR Knowledge Archive
--------------------------------------

Explore all **74 Book Codices** and **11 Mathematical Catalogs** at https://geometor.com/books/.
