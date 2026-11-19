.. _sec-comparaison-sans-cavitation:

Comparaison
===========

Les deux solutions sont évaluées sur la même grille. On compare la pression,
puis deux grandeurs globales qui caractérisent le contact : la charge et le
frottement.

La charge
---------

La charge par unité de largeur est l'intégrale de la pression
(adimensionnement :eq:`eq-adimensionnement`) :

.. math::

   W = \int P \,\mathrm{d}X .

Le frottement
-------------

Le profil de vitesse de Reynolds, intégré dans l'épaisseur du film, donne la
contrainte de cisaillement sur chaque surface. En adimensionné (vitesses
:math:`U_1`, :math:`U_2` des surfaces du bas et du haut, rapportées à
:math:`u_m`) :

.. math::

   \tau = \frac{U_2 - U_1}{H} \mp 6 H \frac{\mathrm{d}P}{\mathrm{d}X},
   \qquad F = \int \tau \,\mathrm{d}X ,

avec le signe :math:`-` sur la surface du bas et :math:`+` sur celle du haut.
Le premier terme vient du glissement (Couette), le second de la pression
(Poiseuille). Le gradient :math:`\mathrm{d}P/\mathrm{d}X` est obtenu par
différences finies pour la FD, par autograd pour le PINN.

.. literalinclude:: /../src/pri/friction.py
   :pyobject: shear_stress_1D

Résultat
--------

.. plot:: ../figures/reynolds_1d_pinn_vs_fd.py
