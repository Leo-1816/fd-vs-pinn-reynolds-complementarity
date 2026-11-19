Reynolds 1D, cas noyé avec cavitation
=====================================

Le ménisque d'entrée est rejeté à l'infini (:math:`X_a = -\infty`) et le film
se rompt en :math:`X_b`, suivi d'une zone cavitée où :math:`P = 0`. Seule la
condition de Reynolds en sortie est prise en compte : la fraction de vide
:math:`\theta` n'intervient pas encore.

La figure ci-dessous résume les deux zones. Dans le film plein, l'équation
de Reynolds est vérifiée (résidu :math:`r = 0`) et :math:`P > 0`. Dans la
zone cavitée, :math:`P = 0` et le résidu vaut :math:`-\mathrm{d}H/\mathrm{d}X < 0` :
la pression voudrait y devenir négative, elle est bloquée à zéro. En chaque
point, l'une des deux grandeurs :math:`P` ou :math:`r` est donc nulle : c'est
la complémentarité utilisée par le PINN (:ref:`sec-pinn-cas-noye`).

.. plot:: ../figures/flooded_zones.py

.. toctree::
   :maxdepth: 2

   differences_finies
   pinn
