.. _about-editions:

Critical Editions: Leonine, Marietti, Decker & Corpus Thomisticum
=================================================================

.. rubric:: *Philological Provenance & Paragraph Synchronization in geometor-aquinas*

To ensure complete philological reliability and 1-to-1 cross-referencing with twentieth-century Thomistic scholarship (especially **Fr. Peter Hoenen, S.J.**'s *De Noetica Geometriae*, 1954), ``geometor-aquinas`` preserves the exact diplomatic Latin text and canonical numbering of three landmark editorial traditions:

1. **The Leonine Edition (*Editio Leonina*, Rome, 1882–present)**
   Commissioned by Pope Leo XIII in 1879, the Leonine Commission established the critical Latin text of the *Posterior Analytics* (Tom. I, 1882; Tom. I* 2, ed. R.-A. Gauthier, 1989), *Physics* (Tom. II, 1884), *De Caelo* (Tom. III, 1886), *Summa Theologiae* Prima Pars (Tom. IV–V, 1888–1889), *De Veritate* (Tom. XXII, 1970–1976), *De Anima* (Tom. XLV.1, 1984), and *Super Boetium De Trinitate* (Tom. L, 1992).

2. **The Marietti Taurini Manual Editions (Pirotta, Cathala–Spiazzi, Maggiòlo, Bazzi)**
   Throughout the twentieth century, scholars citing Aquinas's Aristotelian commentaries referenced the sequential paragraph numbers introduced by the Dominican editors of Casa Editrice Marietti (Turin):
   - **Angelo Maria Pirotta, O.P.** (*In Aristotelis Librum De Anima Commentarium*, 1925 / 1936): sequential paragraphs ``#1–#846`` (e.g., Hoenen's citations of Pirotta ``#170``, ``#770–777``, and ``#791`` in Pars III).
   - **Marie-Raymond Cathala, O.P. & Raimondo M. Spiazzi, O.P.** (*In duodecim libros Metaphysicorum Aristotelis expositio*, 1915 / 1950): sequential paragraphs ``#1–#2663`` (e.g., Hoenen's citations of Cathala ``#890``, ``#1496``, ``#1805–1806``, and ``#1894`` in Pars V).

3. **Bruno Decker's Edition of Vatican Autograph *Vat. lat. 9850* (1959)**
   Because Aquinas's personal autograph manuscript of *Super Boetium De Trinitate* survives in the Vatican Library (*Codex Vaticanus Latinus* 9850), Bruno Decker's 1959 Leiden critical edition (together with the 1992 Leonine edition) restored Aquinas's exact autograph wording in Question 5, Article 3—crucially distinguishing *separatio* from *abstractio*.

4. **Index Thomisticus & Corpus Thomisticum**
   Initiated by **Fr. Roberto Busa, S.J.** in 1949 and curated online by **Prof. Enrique Alarcón** at the University of Navarra (*Corpus Thomisticum*), the public-domain diplomatic Latin corpus preserves the exact paragraph boundaries of the Leonine and Marietti editions. Every paragraph in ``resources/aquinas/sources/pars_1..5_latin.json`` records its ``ct_id``, scholastic title, Marietti number (where applicable), and SHA-256 cryptographic digest in ``resources/aquinas/sources_manifest.json``.
