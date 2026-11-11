:title: Prooemium Notes — GEOMETOR & the Thomistic-Hoenen Tradition
:layout: book

.. _prooemium-notes:

Prooemium — Editorial & GEOMETOR Notes
======================================

.. rubric:: *From Medieval Scholasticism to Symbolic Constructive Geometry*

1. The Historical Arc: Aristotle -> Euclid -> Aquinas -> Pacioli -> Hoenen -> GEOMETOR
--------------------------------------------------------------------------------------

Within the ``geometor`` workspace, ``geometor-aquinas`` bridges the classical mathematical canon (``euclid``, ``elements``, ``pappus``, ``pacioli``) and the modern epistemological synthesis of :person:`Peter Hoenen <hoenen>` (``hoenen``). When :person:`Fra Luca Pacioli <pacioli>` argued in :cite:`*De Divina Proportione* (1509) <pacioli:1509>` that the mathematical sciences occupy the *primo grado di certezza* ('first degree of certainty'), he stood directly inside the tradition of :person:`Aquinas <aquinas>`\ 's *Super Boetium De Trinitate* q. 6 a. 1 and *In I Anal. Post.* lect. 1. Four and a half centuries later, confronting :person:`Hilbert <hilbert>`\ 's formalist axiomatics and non-Euclidean geometry, :person:`Hoenen <hoenen>` returned to these exact Thomistic texts—citing 78 distinct Thomistic loci—to prove that formal rigor and spatial intuition are allies rather than rivals.

2. Computational Mapping to the GEOMETOR Engine
-----------------------------------------------

* **Exact Symbolic Algebra as Materia Intelligibilis**: Unlike floating-point dynamic geometry tools whose coordinates drift by numeric epsilon (like lines drawn in sensible dust), ``geometor.model`` represents every point, line, and circle over exact algebraic number fields in SymPy—preserving $\sqrt{2}$, $\sqrt{3}$, and the golden ratio $\phi = \frac{1+\sqrt{5}}{2}$ in pure :term:`intelligible matter <materia-intelligibilis>`.
* **The Interactive Canvas as Phantasma**: In exact fidelity to :term:`conversio ad phantasmata <conversio-ad-phantasmata>` (*De Anima* III, lect. 12) and :term:`terminari ad imaginationem <terminari-ad-imaginationem>` (*De Trinitate* q. 6 a. 2), ``geometor.explorer`` projects those exact symbolic structures onto an interactive SVG canvas where human geometric intuition inspects determinate diagrams.
* **Constructive Discovery by Division in Act**: Just as *Metaphysics* IX, lect. 10 (Cathala #1894) celebrates geometers discovering latent truths *dividendo in actu*, ``geometor.divine`` systematically scans newly constructed intersections across the DAG to bring latent golden sections and harmonic ranges into luminous act.
