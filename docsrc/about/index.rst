:navigation: header
:order: 20
:nav_title: About

.. _about:
.. _about-index:

About
=====

.. rubric:: Extracting Historical Semantic Knowledge & Repurposing It for Exact Symbolic Reasoning

About This Edition
------------------

**GEOMETOR • aquinas** recovers, translates, and annotates the foundational writings of **St. Thomas Aquinas, O.P. (1225–1274)** on mathematical science, *materia intelligibilis* (intelligible matter), abstraction, and constructive geometry. Assembled from the critical Leonine, Marietti (Pirotta, Cathala–Spiazzi), and Decker editions across **Five Parts** (37 unabridged sections, 613 synchronized paragraphs), this codex gathers Aquinas's complete architectural doctrine on the nature and certitude of mathematical demonstration:

* **Pars I** (*Super Boetium De Trinitate* qq. 5–6): The vital distinction between *abstractio formae* and *separatio*, the doctrine of *materia intelligibilis*, and why mathematical judgment terminates at the imagination (*terminari ad imaginationem*).
* **Pars II** (*In Posteriora Analytica*): Why Euclidean geometry provides the *certissimus modus demonstrationis*, dissecting axioms (*dignitates*), definitions, hypotheses (*suppositiones*), postulates (*petitiones*), and sensible dust diagrams.
* **Pars III** (*In De Anima*): The psychological necessity of *conversio ad phantasmata*—why the human intellect never understands geometric truth without beholding intelligible extension in an imagined figure.
* **Pars IV** (*In Physicorum* & *De Caelo*): Continuum non-atomism, indivisibles, and the physical realization of geometric motion.
* **Pars V** (*In Metaphysicorum* & *Summa Theologiae*): Individual intelligible matter and heuristic discovery by division in act (*divisio in actu* for Euclid I.32 and III.31).

Through the GEOMETOR Digital Scriptorium architecture, every text is extracted into a synchronized 4-track Book Codex (unabridged English translation, critical Latin diplomatic text, chapter-by-chapter modern summary, and deep philosophical notes). The edition incorporates a comprehensive 78-locus concordance linking Aquinas's Aristotelian commentaries directly to Fr. Peter Hoenen, S.J.'s *De Noetica Geometriae* (1954), Fra Luca Pacioli's *De Divina Proportione* (1509), and Euclid's *Elements*. Within the broader GEOMETOR canon, this work establishes the epistemological foundation for exact symbolic geometry, explaining how symbolic algebraic DAGs in ``geometor.model``, interactive SVG diagrams in ``geometor.explorer``, and golden-ratio invariants in ``geometor.divine`` computationalize Aquinas's classical realism.

The GEOMETOR Mission
--------------------

The GEOMETOR project, directed by **phi ARCHITECT**, is dedicated to the systematic recovery, exact formalization, and dynamic re-expression of foundational geometric and philosophical knowledge. The mission unfolds across three essential pillars:

* **Extracting Historical Semantic Knowledge**: Moving beyond passive page scans and OCR to recover the living deductive structure of 2,300+ years of geometric, axiomatic, and philosophical treatises—elevating prose, marginal citations, primary-source folios (via ``publish folio``), and calibrated Ink-to-Vector ``.euclid-graphic`` diagrams into structured, machine-addressable semantic graphs.
* **Exact Symbolic Grounding (``geometor.model``)**: Anchoring geometric constructions in 100% exact symbolic algebra (using ``SymPy``) and Rational Trigonometry invariants (quadrance, spread, cross-ratio) over exact algebraic fields rather than floating-point approximations.
* **Repurposing Knowledge Across Mediums**: Re-deploying extracted semantic and algebraic structures across synchronized multi-track **Book Codices** and EPUB 3 editions (via ``photon-platform/publish``), computable deductive canons (``geometor.elements``, ``geometor.etc``, ``geometor.pappus``, ``geometor.divine``), interactive SVG laboratories (``geometor.explorer``), QHD visual broadcasts, and neuro-symbolic program synthesis (``geometor.seer``) across ``geometor.com``.

Sources, Provenance & Methodology
---------------------------------

Archival Sources & Critical Editions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Editio Leonina (Rome, 1882–present)**: Critical Latin texts established under Pope Leo XIII and the Leonine Commission, including *Posterior Analytics* (Tom. I, 1882; Tom. I* 2, ed. R.-A. Gauthier, 1989), *Physics* (Tom. II, 1884), *De Caelo* (Tom. III, 1886), *Summa Theologiae* (Tom. IV–V, 1888–1889), *De Veritate* (Tom. XXII, 1970–1976), *De Anima* (Tom. XLV.1, 1984), and *Super Boetium De Trinitate* (Tom. L, 1992).
* **Marietti Taurini Manual Editions**: Sequential numbering traditions edited by Angelo Maria Pirotta, O.P. (*In De Anima*, 1925/1936, paragraphs ``#1–#846``) and Marie-Raymond Cathala, O.P. & Raimondo M. Spiazzi, O.P. (*In Metaphysicorum*, 1915/1950, paragraphs ``#1–#2663``).
* **Bruno Decker Critical Edition (Leiden, 1959)**: Transcription of the Vatican autograph *Codex Vaticanus Latinus 9850* for *Super Boetium De Trinitate*, restoring Aquinas's autograph distinction between *separatio* and *abstractio*.

Digital Scriptorium Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Primary Philological Fidelity**: 100% unabridged, verbatim Latin diplomatic texts paired with rigorous, paragraph-synchronized English translations.
* **Complete Hoenen–Euclid Concordance**: Direct cross-referencing between Thomistic noetics, Aristotelian texts (``geometor.aristotle``), and Euclidean theorems (``geometor.euclid``, ``geometor.elements``).
* **Epistemology of Symbolic Constructive Geometry**: Formal demonstration of how exact symbolic computation in ``geometor.model`` realizes the Thomistic synthesis of *intellectus*, *phantasma*, and *divisio in actu*.

Historical, Critical & Philosophical Essays
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* :ref:`St. Thomas Aquinas (1225–1274) & the Philosophy of Mathematics <about-thomas-aquinas>`
* :ref:`Critical Editions: Leonine, Marietti, Decker & Corpus Thomisticum <about-editions>`
* :ref:`Thomistic Noetics, Peter Hoenen & the GEOMETOR Symbolic Engine <about-thomistic-geometor>`

.. toctree::
   :maxdepth: 1
   :hidden:

   thomas-aquinas
   corpus-thomisticum-editions
   thomistic-noetics-and-geometor
