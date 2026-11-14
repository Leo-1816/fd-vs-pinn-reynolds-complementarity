.. _sec-equations:

Les équations à résoudre
========================

D'où vient l'équation de Reynolds
---------------------------------

L'équation de Reynolds traduit une idée simple : **l'huile ne disparaît pas**.
En régime stationnaire et en 1D, le débit d'huile qui traverse chaque section
du film est le même partout. C'est la conservation de débit 
:math:`\mathrm{d}q / \mathrm{d}x = 0` classique en mécanique des fluides.

Dans l'épaisseur du film, la vitesse de l'huile est la somme de deux
écoulements :

- un écoulement de **Couette**, dû à l'entraînement par les surfaces. Il
  transporte l'huile à la vitesse moyenne :math:`u_m` ;
- un écoulement de **Poiseuille**, dû au gradient de pression. L'huile est
  poussée des zones de haute pression vers les zones de basse pression.

En intégrant le profil de vitesse sur l'épaisseur :math:`h` direction :math:`y`,
 le débit par unité de largeur vaut

.. math::
   :label: eq-debit-dimensionnel

   q = \underbrace{u_m\, h}_{\text{Couette}}
     \; \underbrace{- \, \frac{h^3}{12\,\eta_0} \frac{\mathrm{d}p}{\mathrm{d}x}}_{\text{Poiseuille}} .

Écrire que ce débit est constant, :math:`\mathrm{d}q / \mathrm{d}x = 0`, donne
l'**équation de Reynolds** pour un film plein, en régime iso-visqueux rigide :

.. math::
   :label: eq-reynolds-dimensionnelle

   \frac{\mathrm{d}}{\mathrm{d}x} \left( h^3 \frac{\mathrm{d}p}{\mathrm{d}x} \right)
   = 12\, \eta_0\, u_m \frac{\mathrm{d}h}{\mathrm{d}x} .

Le second membre montre que c'est la **variation de l'épaisseur**,
:math:`\mathrm{d}h / \mathrm{d}x`, combinée à l'entraînement :math:`u_m`, qui crée
la pression. Si les surfaces étaient parallèles, il n'y aurait aucune
surpression.

Adimensionnement
----------------

Les grandeurs physiques ont des ordres de grandeur très différents : des
micromètres pour :math:`h`, des millimètres pour :math:`x`, des mégapascals pour
:math:`p`. On les remplace par des grandeurs **sans dimension**, d'ordre 1, ce
qui simplifie les équations et convient mieux au calcul numérique :

.. math::
   :label: eq-adimensionnement

   X = \frac{x}{\sqrt{R_x h_0}}, \qquad
   H = \frac{h}{h_0}, \qquad
   P = \frac{p\, h_0^{3/2}}{12\, \eta_0\, u_m\, R_x^{1/2}}, \qquad
   W = \frac{w\, h_0}{12\, \eta_0\, u_m\, R_x} .

Avec ces variables, la géométrie :eq:`eq-geometrie-dimensionnelle` et l'équation
de Reynolds :eq:`eq-reynolds-dimensionnelle` deviennent

.. math::
   :label: eq-geometrie

   H(X) = 1 + \frac{X^2}{2},

.. math::
   :label: eq-reynolds

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   = \frac{\mathrm{d}H}{\mathrm{d}X} .

.. note:: Un problème sans paramètre

   Ces variables ont un avantage remarquable : le rayon :math:`R_x`, la viscosité
   :math:`\eta_0`, la vitesse :math:`u_m` et l'épaisseur :math:`h_0` ont tous
   disparu. Pour un contact parabolique, il n'existe qu'**une seule** équation
   à résoudre, quel que soit le contact réel. Le seul paramètre qui reste est
   la quantité d'huile disponible (voir plus bas). Les unités physiques ne
   servent qu'à l'affichage final.

Dans la suite, **toutes les grandeurs sont adimensionnées**.

Prendre en compte la cavitation : la complémentarité
----------------------------------------------------

L'équation de Reynolds conservatrice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

L'équation :eq:`eq-reynolds` n'est valable que là où le film est plein. Pour
décrire **tout** le contact, y compris les zones cavitées, on reprend le bilan
de débit en tenant compte de la fraction de vide :math:`\theta`. Seule la partie
remplie d'huile, :math:`(1 - \theta) H`, est entraînée par les surfaces. Le débit
adimensionné vaut

.. math::
   :label: eq-debit

   Q = (1 - \theta)\, H - H^3 \frac{\mathrm{d}P}{\mathrm{d}X},

et sa conservation, :math:`\mathrm{d}Q / \mathrm{d}X = 0`, donne l'équation de
Reynolds **conservatrice** (elle conserve la masse d'huile, y compris dans les
zones cavitées) :cite:p:`biboulet2020hdr` :

.. math::
   :label: eq-reynolds-theta

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   - \frac{\mathrm{d}}{\mathrm{d}X} \Big( (1 - \theta)\, H \Big) = 0 .

On vérifie qu'elle redonne bien les deux comportements attendus :

- **film plein** (:math:`\theta = 0`) : on retrouve exactement :eq:`eq-reynolds` ;
- **zone cavitée** (:math:`P = 0`) : il reste
  :math:`\mathrm{d}\big((1-\theta) H\big)/\mathrm{d}X = 0`. La quantité d'huile
  :math:`(1 - \theta) H` est simplement transportée, sans pression.

La condition de complémentarité
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Il manque une équation : on a deux inconnues, :math:`P` et :math:`\theta`, mais
une seule équation. La seconde exprime qu'en chaque point, **une seule des deux
situations** est possible :

- soit le film est plein : :math:`\theta = 0` et :math:`P \geq 0` ;
- soit il est partiel : :math:`P = 0` et :math:`\theta \geq 0`.

La pression ne peut pas être négative (le film se romprait), la fraction de
vide non plus, et les deux ne peuvent pas être positives en même temps. Ces
trois conditions forment une **condition de complémentarité** :

.. math::
   :label: eq-complementarite

   P \geq 0, \qquad \theta \geq 0, \qquad P\, \theta = 0 .

Cette condition est commode physiquement, mais difficile à utiliser
numériquement : ce sont deux inégalités et une égalité. On la remplace par
**une seule équation** grâce à la fonction de **Fischer-Burmeister**
:cite:p:`biboulet2020hdr` :

.. math::
   :label: eq-fischer-burmeister

   \phi(P, \theta) = P + \theta - \sqrt{P^2 + \theta^2} = 0 .

.. note:: Pourquoi :math:`\phi = 0` équivaut à la complémentarité

   Si :math:`\phi = 0`, alors :math:`P + \theta = \sqrt{P^2 + \theta^2} \geq 0`.
   En élevant au carré : :math:`P^2 + 2 P \theta + \theta^2 = P^2 + \theta^2`,
   donc :math:`P \theta = 0`. L'une des deux grandeurs est nulle, et l'autre
   vaut alors sa propre valeur absolue : elle est positive ou nulle.
   Réciproquement, si :eq:`eq-complementarite` est vérifiée, on vérifie
   directement que :math:`\phi = 0`.

Le système à résoudre est donc formé de **deux équations pour deux inconnues**,
:eq:`eq-reynolds-theta` et :eq:`eq-fischer-burmeister`. L'avantage est majeur :
les frontières :math:`X_a` et :math:`X_b` n'ont pas à être cherchées
séparément. Elles apparaissent d'elles-mêmes dans la solution, là où l'on passe
de :math:`\theta > 0` à :math:`P > 0`.


L'alimentation limitée
----------------------

On note :math:`H_{\text{oil}} = h_{\text{oil}} / h_0` l'épaisseur adimensionnée
de la couche d'huile apportée par les surfaces. En amont du contact, cette
huile est simplement transportée, donc le débit vaut
:math:`Q = H_{\text{oil}}`.

En 1D, l'huile ne peut pas s'échapper sur les côtés : le débit est **le même
dans tout le contact**,

.. math::
   :label: eq-debit-constant

   Q = (1 - \theta)\, H - H^3 \frac{\mathrm{d}P}{\mathrm{d}X} = H_{\text{oil}}
   \quad \text{partout.}

Deux conséquences :

- en sortie, au-delà de la frontière de cavitation, :math:`P = 0` donc
  :math:`(1 - \theta) H = H_{\text{oil}}` : **toute l'huile entrée ressort**. En
  particulier, au point :math:`X_b`, où le film est encore plein et le gradient.
  de pression nul, l'épaisseur de film vaut :math:`H_b = H(X_b) = H_{\text{oil}}` 
- la quantité d'huile disponible est **le seul paramètre** du problème. On peut
  la donner de façon équivalente par :math:`H_{\text{oil}}`, par :math:`H_b`, ou par
  la position du ménisque d'entrée :math:`X_a`.

Un contact ne peut faire passer qu'une quantité d'huile limitée. Au-delà d'un
seuil, noté :math:`H_{b,ff}` (*fully flooded*, voir
:ref:`sec-solution-analytique`), le contact est **noyé** : le ménisque d'entrée
part à l'infini en amont, et un supplément d'huile ne change plus la solution.

Le problème complet
-------------------

.. admonition:: Problème à résoudre (1D)

   **Données** : la géométrie :math:`H(X) = 1 + X^2/2`, un domaine
   :math:`[X_{\text{in}}, X_{\text{out}}]`, et la quantité d'huile disponible
   :math:`H_{\text{oil}}`.

   **Inconnues** : la pression :math:`P(X)` et la fraction de vide
   :math:`\theta(X)`.

   **Équations**, en tout point du domaine :

   .. math::

      \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
      - \frac{\mathrm{d}}{\mathrm{d}X} \Big( (1 - \theta)\, H \Big) = 0,
      \qquad
      P + \theta - \sqrt{P^2 + \theta^2} = 0 .

   **Conditions aux limites** :

   .. math::

      P(X_{\text{in}}) = 0, \qquad P(X_{\text{out}}) = 0, \qquad
      \theta(X_{\text{in}}) = 1 - \frac{H_{\text{oil}}}{H(X_{\text{in}})} .

   La dernière condition exprime qu'à l'entrée du domaine, l'espace
   :math:`H(X_{\text{in}})` ne contient que la couche d'huile
   :math:`H_{\text{oil}}`.

   **Grandeurs à obtenir** : :math:`P(X)`, :math:`\theta(X)`, le ménisque
   d'entrée :math:`X_a`, la frontière de cavitation :math:`X_b`, et la charge

   .. math::

      W = \int_{X_a}^{X_b} P(X)\, \mathrm{d}X .

Le domaine doit être assez grand pour contenir toute la zone sous pression :
:math:`X_{\text{in}} < X_a` et :math:`X_{\text{out}} > X_b`.

L'extension 2D
--------------

Pour le contact elliptique :eq:`eq-geometrie-dimensionnelle-2d`, la direction
transverse est adimensionnée par son propre rayon,
:math:`Z = z / \sqrt{R_z h_0}`, et la pression comme en 1D. La géométrie devient
:cite:p:`biboulet2020hdr`

.. math::
   :label: eq-geometrie-2d

   H(X, Z) = 1 + \frac{X^2}{2} + \frac{Z^2}{2},

et l'équation de Reynolds pour un film plein prend la forme (éq. 2.30 de la
HDR)

.. math::
   :label: eq-reynolds-2d

   \frac{\partial}{\partial X} \left( H^3 \frac{\partial P}{\partial X} \right)
   + D\, \frac{\partial}{\partial Z} \left( H^3 \frac{\partial P}{\partial Z} \right)
   = \frac{\partial H}{\partial X} .

Le nouveau terme décrit le débit de Poiseuille dans la direction :math:`Z`,
c'est-à-dire la **fuite latérale**. Le rapport des rayons :math:`D` est le seul
paramètre géométrique qui reste : pour :math:`D = 0`, on retrouve l'équation 1D
:eq:`eq-reynolds`. Il n'y a pas de terme de Couette selon :math:`Z`, car les
surfaces ne se déplacent que selon :math:`X`.

La cavitation se traite comme en 1D : seule la partie remplie
:math:`(1 - \theta) H` est entraînée, ce qui donne l'équation conservatrice

.. math::
   :label: eq-reynolds-theta-2d

   \frac{\partial}{\partial X} \left( H^3 \frac{\partial P}{\partial X} \right)
   + D\, \frac{\partial}{\partial Z} \left( H^3 \frac{\partial P}{\partial Z} \right)
   - \frac{\partial}{\partial X} \Big( (1 - \theta)\, H \Big) = 0,

avec la même condition de Fischer-Burmeister. La HDR écrit cette équation
(éq. 3.51) pour des surfaces texturées, avec les deux directions adimensionnées
de la même façon, ce qui revient à :math:`D = 1`. La frontière de cavitation
devient une courbe du plan. Le débit n'est plus constant (une partie de
l'huile part sur les côtés), et il n'existe plus de solution analytique
exacte, seulement une solution quasi analytique pour les contacts
elliptiques larges (section 2.2.2 de :cite:t:`biboulet2020hdr`).


