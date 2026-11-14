.. _sec-contact-lubrifie:

Le contact lubrifié
===================

La situation physique
---------------------

Dans un roulement, entre un piston et un cylindre, ou dans un engrenage, deux
pièces roulent ou glissent l'une sur l'autre. Dans cette étude au moins une des 
surfaces est en mouvement. Pour éviter qu'elles se touchent
et s'usent, on intercale un lubrifiant, ici de l'huile. Si le mouvement est
assez rapide, l'huile entraînée par les surfaces forme un **film** continu qui
les sépare complètement : on parle de **lubrification hydrodynamique**. 

Ce film est extrêmement mince en comparaison aux pièces autour et sera porté par 
la direction :math:`y` dans ce projet. 
Il est pourtant capable de porter des charges importantes. 
Le mécanisme est le suivant :

- au voisinage du contact, l'écart entre les deux surfaces a la forme d'un
  **convergent** (l'écart diminue), puis d'un **divergent** (l'écart augmente) ;
- les surfaces en mouvement **entraînent** l'huile vers le convergent, comme un
  tapis roulant ;
- l'huile, forcée de passer dans un espace qui se rétrécit, ne peut pas
  s'écouler assez vite : sa **pression monte**. C'est cette surpression qui
  maintient les surfaces écartées et porte la charge.

.. note:: Image simple

   C'est le même phénomène que l'aquaplaning : une voiture roulant vite sur une
   route mouillée entraîne l'eau sous le pneu. L'eau ne s'échappe pas assez vite,
   sa pression monte et soulève le pneu.

La géométrie
------------

Le cas 1D : le contact d'un rouleau
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On considère la situation la plus simple : une surface plane et une surface
courbe de rayon :math:`R_x`, par exemple un rouleau sur une piste 
(il n'y a pas de déplacement dans le sens de l'axe du rouleau). Près du
point le plus proche, l'écart entre les surfaces, appelé **épaisseur de film**,
est bien approché par une parabole :

.. math::
   :label: eq-geometrie-dimensionnelle

   h(x) = h_0 + \frac{x^2}{2 R_x},

où :math:`x` est la position le long de la direction du mouvement et
:math:`h_0` l'épaisseur minimale, atteinte en :math:`x = 0`. Pour
:math:`x < 0`, le film est convergent, pour :math:`x > 0` il est divergent.

Les surfaces se déplacent avec une vitesse moyenne :math:`u_m`, qui est la
vitesse à laquelle l'huile est entraînée dans le contact.

Le cas 2D : le contact elliptique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le cas 1D suppose que le rouleau est infiniment long : rien ne varie le long
de son axe. En réalité, les surfaces sont souvent courbées dans les **deux**
directions, comme une bille ou un rouleau bombé sur une piste. On ajoute alors
la direction :math:`z`, perpendiculaire au mouvement, avec un second rayon de
courbure :math:`R_z`. L'épaisseur de film devient un paraboloïde
:cite:p:`biboulet2020hdr` :

.. math::
   :label: eq-geometrie-dimensionnelle-2d

   h(x, z) = h_0 + \frac{x^2}{2 R_x} + \frac{z^2}{2 R_z} .

Les lignes de même épaisseur sont des **ellipses** : on parle de **contact
elliptique**. Sa forme est caractérisée par le rapport des rayons

.. math::

   D = \frac{R_x}{R_z} .

- :math:`D = 1` : les deux rayons sont égaux, le contact est circulaire (une
  bille sur un plan) ;
- :math:`D \to 0` : :math:`R_z` devient infini, la surface n'est plus courbée
  selon :math:`z`, et on retrouve le **cas 1D** (contact linéique). Le 1D est
  donc la limite d'un contact infiniment large.

La différence physique essentielle est la **fuite latérale** : en 2D, une
partie de l'huile entraînée dans le contact s'échappe sur les côtés, dans la
direction :math:`z`, au lieu de traverser le contact. La quantité d'huile n'est
plus la même à l'entrée et à la sortie, et la zone sous pression devient une
région du plan, délimitée par des frontières courbes.

Les hypothèses générales du problème complet
---------------------------------------------------

Le projet se place dans le régime le plus simple, dit **iso-visqueux rigide**
(IVR) :

- **iso-visqueux** : la viscosité :math:`\eta_0` de l'huile est constante. En
  réalité, elle augmente avec la pression, mais on néglige cet effet
- **rigide** : les surfaces ne se déforment pas sous la pression. La géométrie
  :eq:`eq-geometrie-dimensionnelle` est donc connue à l'avance et ne dépend pas
  de la solution

S'y ajoutent les hypothèses classiques de la lubrification en film mince :

- le film est **mince** devant les autres dimensions du contact
- l'huile est un **fluide newtonien** et **incompressible**, et l'écoulement est
  **laminaire** : les forces visqueuses dominent et l'inertie est négligeable 
- la pression est **constante dans l'épaisseur** du film 
- l'huile **adhère** aux parois (pas de glissement à la paroi) 
- le régime est **stationnaire** et **isotherme** 
- en 1D, le contact est **infiniment large** dans la direction perpendiculaire
  au mouvement : l'huile ne peut pas s'échapper sur les côtés.

Les deux phénomènes qui compliquent le problème
-----------------------------------------------

La cavitation
~~~~~~~~~~~~~

Dans le divergent, l'écart entre les surfaces augmente. L'équation qui décrit
le film (:ref:`sec-equations`) y prédit une **dépression**. La pression est donc 
**inférieure** à la pression ambiante, et la solution peut même être négative.
Un liquide ne supporte pas une telle dépression :
le film se **rompt**, des poches de gaz ou de vapeur apparaissent, et l'huile ne
remplit plus tout l'espace entre les surfaces. C'est la **cavitation**.

Dans une zone cavitée :

- la pression reste égale à la **pression de cavitation**, que l'on prend comme
  référence : :math:`p = 0` ;
- l'espace entre les surfaces n'est que **partiellement** rempli d'huile. On
  note :math:`\theta` la **fraction de vide** : :math:`\theta = 0` si le film est
  plein, :math:`\theta = 0{,}3` si 30 % de l'épaisseur est occupée par du gaz.

La frontière entre zone pleine et zone cavitée n'est pas connue à l'avance :
elle fait partie de la solution. C'est une **frontière libre**, et c'est la
principale difficulté numérique du problème.

L'alimentation limitée
~~~~~~~~~~~~~~~~~~~~~~

Le cas « idéal » suppose qu'il y a de l'huile en abondance devant le contact :
le contact est dit **noyé**. Souvent, ce n'est pas le cas : les surfaces
n'apportent qu'une **couche d'huile d'épaisseur finie** :math:`h_{\text{oil}}`.
Le contact est alors **sous-alimenté**.

Conséquence : le film ne devient plein qu'à partir d'une certaine position
:math:`x_a`, appelée **ménisque d'entrée**, là où l'écart entre les surfaces
devient égal à l'épaisseur d'huile disponible. En amont, l'espace est
partiellement vide. Moins il y a d'huile, plus le ménisque d'entrée se
rapproche du centre du contact, plus la zone sous pression rétrécit, et plus
la charge que le contact peut porter diminue.

Ce que l'on cherche
-------------------

Le contact présente donc, de l'amont vers l'aval, trois zones :

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Zone
     - Film
     - Pression
     - Fraction de vide
   * - avant le ménisque d'entrée :math:`x_a`
     - partiellement rempli
     - :math:`p = 0`
     - :math:`\theta > 0`
   * - entre :math:`x_a` et :math:`x_b`
     - plein
     - :math:`p > 0`
     - :math:`\theta = 0`
   * - après la frontière de cavitation :math:`x_b`
     - partiellement rempli (cavitation)
     - :math:`p = 0`
     - :math:`\theta > 0`

Résoudre le problème, c'est trouver, pour une quantité d'huile disponible
donnée la **pression** :math:`p(x)` et la **fraction de vide** :math:`\theta(x)` en
tout point.

On pourra ensuite calculer :

- les positions des deux frontières : le **ménisque d'entrée** :math:`x_a` et la
  **frontière de cavitation** :math:`x_b` ;
- la **charge** :math:`w` que le contact peut porter, égale à l'intégrale de la
  pression.
