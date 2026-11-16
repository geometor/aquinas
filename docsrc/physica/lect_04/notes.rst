:order: 4
:canonical_id: Phys. VI, lect. 1
:folio: Phys. VI, lect. 1
:title: Commentary & Notes — That No Continuum (Line, Time, or Motion) Can Be Composed of Indivisible Points
:tracks: English: index | Latin: la | Summary: summary | Notes: notes

.. _physica-lect_04-notes:
.. _physica-s4-notes:
.. _pars-4-s4-notes:

Commentary & Notes — That No Continuum (Line, Time, or Motion) Can Be Composed of Indivisible Points
====================================================================================================

.. rubric:: *Aristotelian Sources, Euclidean Counterparts, Hoenen's Noetics, and GEOMETOR Significance*

Aristotelian & Scholastic Foundations
-------------------------------------

Aquinas comments on the celebrated opening chapter of *Physics* VI (231a21–231b18), where :person:`Aristotle <aristotle>` launches his refutation of spatial, temporal, and kinematic atomism (directed historically against :person:`Democritus <democritus>`, Xenocrates' indivisible lines, and Zeno's paradoxes, and elaborated by :person:`Simplicius <simplicius>`, *In Phys.* 925–935, :person:`Themistius <themistius>`, and :person:`Averroes <averroes>`, *In Phys.* VI, comm. 1–6). Importing the three topological relations rigorously defined in *Physics* V.3 (226b18–227a32)—*suneches* (*continuum*, whose extremes are one), *haptomenon* (*contactum* / *contiguum*, whose extremes are together in the same immediate place), and *ephexes* (*consequenter se habens*, between which nothing of the same genus intervenes)—Aquinas constructs a tight syllogistic dilemma reinforced by the Book III.1 (200b18–20) definition of the :term:`continuum <continuum>` as infinitely divisible. Every escape route for point-atomism is sealed in nn. 7–8: two distinct points cannot touch (whole-to-whole contact collapses positional distinction), nor be *consecutive* without a gap, and any gap between two points must itself be infinitely divisible into further divisibles (*in semper divisibilia*), establishing strict isomorphism across spatial magnitude, motion, and time.

Euclidean & Classical Geometric Counterparts
--------------------------------------------

Aquinas's commentary on *Physics* VI.1 is the indispensable philosophical key to reading the opening definitions of :person:`Euclid <euclid>`\ 's *Elements* Book I without falling into point-set anachronism. Euclid defines a point as *that which has no part* (*semeion estin hou meros outhen*, Def. 1), a line as *breadthless length* (Def. 2), and—crucially—*the extremities of a line are points* (*grammes de perata semeia*, Def. 3), parallel to Book I Def. 6 (*the extremities of a surface are lines*) and Book XI Def. 2 (*the extremity of a solid is a surface*). Far from building lines out of points like beads on a string, Euclid treats the continuous line as ontologically prior to its endpoint markers and internal section points! Furthermore, Aquinas's theorem that every :term:`continuum <continuum>` is divisible *in semper divisibilia* directly underwrites *Elements* Book I Proposition 10 (bisecting any given finite straight line), Book X Proposition 1 (the exhaustion principle of endless bisection), Book X Proposition 2 (incommensurable magnitudes whose Euclidean *antenairesis* never terminates in a common atomic unit), and Book II Proposition 11 / Book VI Proposition 30 (cutting a line in extreme and mean ratio, whose golden-section anthyphairesis continues *in infinitum*).

Hoenen's De Noetica Geometriae & Judgment Theory
------------------------------------------------

In *De Noetica Geometriae* (Chapter III, §§ 1–2, pp. 88–178), Peter :person:`Hoenen <hoenen>` S.J. deploys the Aristotelian-Thomistic :term:`continuum <continuum>` doctrine of *Physics* VI.1 to diagnose the foundational crisis of nineteenth- and twentieth-century arithmetized analysis (Cantor, Dedekind, Wellstein, :person:`Russell <russell>`). Modern rigorists sought to build the geometric continuum upward from an uncountable point-set because they mistakenly began with the point as an isolated corpuscle shrunk to zero (*Grenzprozess*), rendering its mathematical existence unintelligible. Reversing that order with :person:`Aristotle <aristotle>` and Aquinas, Hoenen begins from the primary intellective datum: three-dimensional continuous extension, whose first *propria passio* is infinite divisibility. When an extended magnitude is divided without separating its parts, the boundary *between* the parts—through which transition occurs in an indivisible—emerges in act: first the surface, then the line, and finally the point, an *indivisible having position*. Because points exist in potency within the undivided continuum and arise in act only as indivisible cuts or intersections, no collection of points—finite or transfinite—can ever constitute extension by *contact* or *consecutiveness*; rather, between any two constructible points an infinitely divisible line segment necessarily intervenes.

GEOMETOR Constructive & Symbolic Significance
---------------------------------------------

Nowhere does Aquinas's philosophy of mathematics speak more directly to GEOMETOR than in *In VI Physicorum*, lect. 1. Digital graphics engines approximate geometry on discrete pixel or floating-point lattices—a computational atomism in which lines are literally *consecutive* arrays of indivisible raster points, causing false misses or rounded drift whenever two loci intersect at irrational coordinates. By contrast, ``geometor.model`` implements the exact Thomistic ontology of the :term:`continuum <continuum>`: lines and circles are represented as continuous algebraic loci (linear and quadratic polynomial equations), and points arise *solely* as exact symbolic boundaries and intersections (*termini*) where two continuous loci cut one another. Moreover, Aquinas's proof that between any two distinct points lies a continuum divisible *in semper divisibilia* is the exact mathematical condition enabling the golden ratio (*phi*) investigations of ``geometor.divine``: because the golden section is quadratic and irrational, cutting a segment in extreme and mean ratio induces a self-similar cascade of nested golden sections without ever hitting an indivisible atomic quantum.
