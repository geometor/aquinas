:order: 2
:canonical_id: Lib. I, lect. 2
:folio: Lib. I, lect. 2
:title: Commentary & Notes — On the Twofold Foreknowledge (That It Is and What It Is) of Subject and Attribute: Unit and Triangle
:tracks: English: index | Latin: la | Summary: summary | Notes: notes

.. _analytica_posteriora-lect_02-notes:
.. _analytica_posteriora-s2-notes:
.. _pars-2-s2-notes:

Commentary & Notes — On the Twofold Foreknowledge (That It Is and What It Is) of Subject and Attribute: Unit and Triangle
=========================================================================================================================

.. rubric:: *Aristotelian Sources, Euclidean Counterparts, Hoenen's Noetics, and GEOMETOR Significance*

Aristotelian & Scholastic Foundations
-------------------------------------

Expositing *Posterior Analytics* I.1 (71a11–29), Aquinas resolves a classic exegetical puzzle already debated by :person:`Themistius <themistius>`, Philoponus, and Grosseteste: why :person:`Aristotle <aristotle>` cites *unit* (*monas*) as requiring foreknowledge of both *what it is* and *that it is*, while citing *triangle* (*trigonon*) as requiring foreknowledge only of *what the name signifies* (*quid est quod dicitur*). Drawing upon *Metaphysics* IV.4 and VII.4–17, Aquinas explains that in accidental sciences of quantity—unlike metaphysics or physics, whose substantial subjects can never be attributes—an accidental form can stand as a *proper attribute* (*passio*) of a prior quantitative subject while serving in turn as the *subject* of subsequent attributes, terminating without infinite regress in primary quantitative subjects (*unitas*, *linea*, *superficies*). He likewise clarifies Aristotle's distinction at 71a17–24 between temporal foreknowledge of the major premise and simultaneous recognition (*hama epagomenos*) of a singular under its species.

Euclidean & Classical Geometric Counterparts
--------------------------------------------

This lecture contains Aquinas's explicit philosophical explanation of the architecture of Book I of :person:`Euclid <euclid>`\ 's *Elements*. Quoting *Elements* I.1 verbatim (*super rectam lineam datam triangulum aequilaterum constituere*) and referencing *Elements* I.46 (construction of the square), Aquinas characterizes Euclidean constructive problems as *quasi-operative demonstrations* (*demonstrationes quasi operativae*). Euclid presupposes the existence and nominal definitions of points, straight lines, surfaces, and circles (Postulates 1–3), uses them in I.1 to *demonstrate the mathematical existence* of the equilateral triangle from its nominal definition (Def. 20), and thereafter treats the constructed triangle as a subject to prove *proper attributes* such as the equality of its angles (*Elements* I.5 Cor.) and the two-right-angle sum (*Elements* I.32), instantiated immediately in a triangle inscribed in a semicircle (*Elements* III.31).

Hoenen's De Noetica Geometriae & Judgment Theory
------------------------------------------------

Lecture 2, no. 5 is one of :person:`Hoenen <hoenen>`\ 's pivotal proof-texts across *De Noetica Geometriae* (cited extensively in Chapter IV on :person:`Euclid <euclid>` I.1 and Chapter VII on geometric existence). Engaging Bertrand :person:`Russell <russell>`\ 's critique that Euclid illicitly assumes without continuity axioms that the two circles in *Elements* I.1 intersect at point *C*, Hoenen agrees with Russell that I.1 is an *existence proof*—just as Aquinas's doctrine of *demonstratio quasi operativa* establishes—while refuting Russell's blind formalism: mathematical existence (*esse mathematicum*, non-repugnance in continuous extension) cannot be conjured from empty symbolic postulates, because the intersection of the two circles is intellectually *intuited as necessary* in the phantasmatic :term:`continuum <continuum>` from the presupposed nature of *linea* and *superficies*.

GEOMETOR Constructive & Symbolic Significance
---------------------------------------------

Aquinas's account of *quasi-operative demonstrations*, in which constructed figures transition from demonstrated *attributes* of prior lines and circles into *subjects* of downstream properties, directly mirrors the Directed Acyclic Graph (DAG) construction engine of *geometor.model* and *geometor.elements*. Starting from two foundational seed points (the presupposed primary subjects of position and unit distance), every subsequent straight line, circle, intersection point, equilateral triangle, or square is constructively *generated* as a derived algebraic node whose existence (real symbolic intersection roots in SymPy) is proved from ancestor elements before *geometor.divine* analyzes the resulting figure as a subject bearing emergent golden-ratio attributes.
