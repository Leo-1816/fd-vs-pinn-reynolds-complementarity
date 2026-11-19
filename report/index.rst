FD vs PINN : équation de Reynolds avec complémentarité
======================================================

Ce rapport compare une méthode de différences finies (FD), qui sert de
référence, et un réseau de neurones informé par la physique (PINN) pour
résoudre l'équation de Reynolds avec une condition de complémentarité
(cavitation, alimentation limitée).

Avant d'attaquer ce problème, la première partie construit les outils pas à
pas, sur des cas dont on connaît la solution exacte.

.. _sec-demarche:

La démarche du projet
=====================

L'objectif est de comparer deux façons de résoudre le problème de
:ref:`sec-equations` : une méthode classique, les **différences finies**, qui
sert de référence, et un **PINN**, dont on veut évaluer l'intérêt.

Les deux méthodes
-----------------

**Différences finies (FD).** On découpe le domaine en points régulièrement
espacés, et on remplace les dérivées par des différences entre points voisins.
Les deux équations :eq:`eq-reynolds-theta` et :eq:`eq-fischer-burmeister`
deviennent un système d'équations non linéaires, résolu par la méthode de
Newton. Suivant :cite:t:`biboulet2020hdr` (section 3.3.3), on utilisera une
seule inconnue combinée :math:`u = P - \theta` : comme :math:`P` et
:math:`\theta` ne sont jamais positifs en même temps, :math:`P` est la partie
positive de :math:`u` et :math:`\theta` sa partie négative. On obtient une
solution aux points du maillage, dont la précision s'améliore quand on raffine.

**PINN.** On représente :math:`P` et :math:`\theta` par un réseau de neurones,
et on met les équations dans la perte, comme pour le premier PINN
(:ref:`sec-premiere-edo`) : résidu de :eq:`eq-reynolds-theta`, résidu de
:eq:`eq-fischer-burmeister` et conditions aux limites. On obtient une solution
continue, que l'on peut évaluer en tout point.

Les étapes
----------



.. list-table::
   :header-rows: 1
   :widths: 10 45 45

   * - Étape
     - Problème
     - Référence de validation
   * - 1
     - Apprendre à coder un PINN sur une EDO simple
     -
   * - 2
     - Comprendre le problème physique
     -
   * - 3
     - Reynolds 1D sans cavitation :eq:`eq-reynolds`, frontières imposées
     - pression analytique :eq:`eq-pression-analytique`
   * - 4
     - Reynolds 1D avec complémentarité, par différences finies
     - :math:`P`, :math:`\theta`, :math:`X_a`, :math:`X_b`, :math:`W` analytiques
   * - 5
     - Reynolds 1D avec complémentarité, par PINN
     - mêmes grandeurs analytiques, et la solution FD
   * - 6 (si le temps le permet)
     - Reynolds 2D avec complémentarité, FD et PINN
     - solution quasi analytique 2D, et la solution FD

.. toctree::
   :maxdepth: 2
   :numbered:

   premiers_reseaux/index
   probleme_physique/index
   reynolds_sans_cavitation/index
   bibliographie
