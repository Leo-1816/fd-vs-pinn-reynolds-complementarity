.. _sec-pinn-cas-noye:

PINN : complémentarité entre pression et résidu
===============================================

Pourquoi une complémentarité
----------------------------

Le réseau doit trouver seul où le film est plein et où il est cavité. On ne
peut pas simplement ajouter une pénalité sur :math:`P < 0` en gardant
l'équation de Reynolds partout : dans la zone cavitée, :math:`P = 0` donne un
résidu

.. math::

   r = \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   - \frac{\mathrm{d}H}{\mathrm{d}X} = -\frac{\mathrm{d}H}{\mathrm{d}X} \neq 0,

et le réseau devrait choisir entre respecter l'équation et respecter
:math:`P \geq 0`. La condition de Swift-Stieber s'écrit au contraire comme
une inégalité variationnelle (problème d'obstacle)
:cite:p:`cheng2023hlnets` (éq. 5) :

.. math::

   P \geq 0, \qquad -r \geq 0, \qquad P \, r = 0 .

Là où :math:`P > 0`, l'équation de Reynolds est vérifiée ; là où :math:`P = 0`,
il suffit que :math:`r \leq 0`. La frontière :math:`X_b` n'est pas imposée.

La perte
--------

Les trois conditions sont réunies par la fonction de Fischer-Burmeister
(comme :eq:`eq-fischer-burmeister`, avec :math:`-r` à la place de
:math:`\theta`). Le résidu est divisé par :math:`H^3 > 0`, ce qui ne change pas
son signe mais évite qu'il écrase les autres termes en amont, où :math:`H^3`
est très grand. L'entrée du réseau est ramenée dans :math:`[-1, 1]`.

.. literalinclude:: /../src/pinn/reynolds_1d_flooded.py
   :pyobject: complementarity_residual

La perte additionne la moyenne de :math:`\varphi^2` et les conditions
:math:`P = 0` aux bords. :cite:t:`cheng2023hlnets` (section 2.3.2) proposent
une autre voie : repérer la zone cavitée pendant l'entraînement et y retirer
le terme :math:`\mathrm{d}H/\mathrm{d}X` du résidu.

La validation
-------------

Le résultat est comparé à la même solution analytique que pour les
différences finies (:ref:`sec-fd-cas-noye`).
