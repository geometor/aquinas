:navigation: header
:order: 20
:nav_title: Usage

Using This Edition
==================

.. rubric:: Interactive Reader's Guide to St. Thomas Aquinas's *Writings on Mathematical Science*

This digital critical edition of St. Thomas Aquinas's *Writings on Mathematical Science* (*Opera de Scientia Mathematica et Materia Intelligibili*) provides a modern, interactive reading environment engineered for scholastic textual criticism, philosophical inquiry, and multi-track analysis.

Interactive Features
--------------------

1. Synchronized Reading Tracks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every section across all five parts and the introductory *Prooemium* provides four synchronized reading tracks accessible via the top track toggle bar:

* **English Track**: Unabridged English translations providing direct facing alignment with the Latin source.
* **Latin Track**: Diplomatic Latin text from verified critical editions (Leonine, Marietti Pirotta/Cathala–Spiazzi, and Bruno Decker) with SHA-256 integrity verification.
* **Summary Track**: Analytical summaries isolating Aquinas's epistemological arguments, syllogistic structures, and philosophical conclusions.
* **Notes Track**: Comprehensive GEOMETOR scholarly commentary connecting Thomistic doctrine to Peter Hoenen's *De Noetica Geometriae*, Euclid's *Elements*, and modern geometric foundations.

2. Primary-Source Folio Milestones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Marginal milestones (e.g., ``[q. 5, a. 1]``, ``[lect. 1]``) and header folio badges link every article and lectio directly to canonical citation points in the *Corpus Thomisticum*, the Leonine Commission editions, and Marietti publications.

3. Interactive Diagrams & Deductive Links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interactive diagrammatic assertions and deductive cross-references allow readers to explore geometric examples cited by Aquinas:

* Hovering over technical concepts and geometric demonstrations (such as Aristotle's dust diagrams in *Posterior Analytics* I or the division of figures in act for Euclid I.32 and III.31 in *Metaphysics* IX) highlights deductive relationships.
* Cross-references seamlessly link Aquinas's text to the :person:`Euclid <euclid>`, :person:`Aristotle <aristotle>`, and :person:`Peter Hoenen <hoenen>` codices.

4. Full-Text Search with In-Page Highlighting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The full-text search engine indexes both the Latin text and English translations, as well as commentary and apparatus. Navigating to any search hit automatically highlights terms within paragraphs via ``?highlight=`` URL parameters.

5. Categories, Tags, Document Types & Collection Views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every part, quaestio, articulus, and lectio is indexed with structured metadata:

* **Taxonomy Facets**: Filter texts by topic (e.g. *abstractio formae*, *materia intelligibilis*, *divisio in actu*, *conversio ad phantasmata*), author, or source work.
* **Collection View Toggles**: Switch between **Cards**, **Banners**, and **List** views on collection overview pages to review the treatise hierarchy at your preferred density.

6. People, Bibliography & Glossary Tooltips
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* **People**: Entity links such as :person:`St. Thomas Aquinas <aquinas>`, :person:`Aristotle <aristotle>`, :person:`Euclid <euclid>`, and :person:`Peter Hoenen <hoenen>` display biographical popovers with dates, philosophical roles, and locus occurrences.
* **Bibliography**: Interactive citations (e.g. :cite:`hoenen:1954`, :cite:`decker:1959`, :cite:`corpus-thomisticum`) open comprehensive bibliographic profiles.
* **Glossary**: Scholastic and geometric technical terms (e.g. :term:`materia intelligibilis`, :term:`abstractio`, :term:`divisio in actu`) reveal precise definitions via hover cards.
* **Theme Switching**: Toggle between Light and Dark display modes in the header navigation bar for optimal reading comfort.

Command-Line & Python Pipeline
------------------------------

``geometor.aquinas`` provides automated pipeline utilities for source verification, concordance tracking, and codex compilation:

.. code-block:: bash

   # Recompile the complete multi-track RST codex from verified source JSON
   uv run geometor-aquinas-compile

   # Execute pytest suite verifying JSON schema, concordances, and hashes
   uv run --no-sync pytest

Python API Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

   from geometor.aquinas.compile_codex import compile_all
   from geometor.aquinas.concordance import load_sources_manifest

   # Verify and compile all tracks and apparatus
   stats = compile_all()
   print(f"Compiled parts: {stats['part_count']}, paragraphs: {stats['paragraph_count']}")
