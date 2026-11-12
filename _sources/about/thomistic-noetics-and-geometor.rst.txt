.. _about-thomistic-geometor:

Thomistic Noetics, Peter Hoenen & the GEOMETOR Symbolic Engine
==============================================================

.. rubric:: *Why Thirteenth-Century Scholastic Epistemology Illuminates Symbolic Computation*

Modern dynamic geometry systems typically split into two disconnected worlds: numerical canvas tools (such as GeoGebra) that approximate coordinates in IEEE-754 floating-point arithmetic, and purely syntactic proof assistants that manipulate symbolic tokens with no native spatial intuition.

**GEOMETOR** unites both worlds through an architecture remarkably isomorphic to the Aristotelian-Thomistic noetics recovered by **Fr. Peter Hoenen, S.J.** in ``geometor-hoenen``:

.. list-table:: Structural Correspondence Between Thomistic Noetics & GEOMETOR
   :header-rows: 1
   :widths: 28 36 36

   * - Thomistic Concept
     - Classical Locus in ``geometor-aquinas``
     - Computational Realization in GEOMETOR
   * - *Materia intelligibilis* (continuous spatial extension free of sensible noise)
     - *Super Boetium De Trinitate* q. 5, a. 3; *In VII Metaph.* lect. 10–11
     - ``geometor.model``: exact algebraic points, lines, and circles over SymPy polynomial/radical fields ($\sqrt{2}, \sqrt{3}, \phi$)
   * - *Conversio ad phantasmata* & *terminari ad imaginationem*
     - *In III De Anima* lect. 12 (#777); *Super Boetium De Trinitate* q. 6, a. 2
     - ``geometor.explorer``: determinate SVG rendering & interactive visual inspection of exact constructions
   * - *Non demonstrat per lineam in pulvere descriptam*
     - *In I Anal. Post.* lect. 19
     - Separation between finite screen pixels and the exact symbolic identity verified in ``geometor.model``
   * - *Dignitates*, *suppositiones*, & *petitiones*
     - *In I Anal. Post.* lect. 5 & lect. 18–19
     - ``geometor.elements``: constructive Directed Acyclic Graphs (DAGs) built from Euclid's Postulates 1–3 and Common Notions
   * - *Divisio figurarum in actu* (heuristic discovery by dividing continua)
     - *In IX Metaph.* lect. 10 (Cathala #1894)
     - ``geometor.divine``: automated scanning of newly constructed intersections to reveal latent golden sections and harmonic ranges in act
