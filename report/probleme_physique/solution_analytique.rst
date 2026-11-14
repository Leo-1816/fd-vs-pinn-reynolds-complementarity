.. _sec-solution-analytique:

La solution analytique 1D
=========================

En 1D, le problème de :ref:`sec-equations` possède une solution **exacte**,
donnée par :cite:t:`biboulet2020hdr` (section 2.2.1). C'est elle qui servira
de **référence** pour valider la méthode des différences finies puis le PINN.
Avant de comparer les deux méthodes entre elles, chacune doit retrouver cette
solution.


Idée : intégrer une fois l'équation de Reynolds
-----------------------------------------------

Dans la zone sous pression, :math:`X_a < X < X_b`, le film est plein
(:math:`\theta = 0`) et le débit constant :eq:`eq-debit-constant` s'écrit
:math:`H - H^3 \, \mathrm{d}P/\mathrm{d}X = H_b`. Le gradient de pression est
donc connu explicitement :

.. math::
   :label: eq-gradient-pression

   \frac{\mathrm{d}P}{\mathrm{d}X} = \frac{H - H_b}{H^3} .

Cette formule se lit facilement :

- là où :math:`H > H_b`, c'est-à-dire en amont de :math:`-X_b`, la pression
  **augmente** : l'huile entraînée dans le convergent est comprimée ;
- là où :math:`H < H_b`, entre :math:`-X_b` et :math:`X_b`, la pression
  **diminue** ;
- la pression est donc **maximale** en :math:`-X_b`, et le gradient est de
  nouveau **nul en** :math:`X_b`, où :math:`H(X_b) = H_b`. C'est la condition dite de
  Reynolds à la frontière de cavitation : la pression y arrive à zéro « en
  douceur », avec une tangente horizontale.

Comme :math:`H(X) = 1 + X^2/2`, la condition :math:`H(X_b) = H_b` donne la position
de la frontière de cavitation :

.. math::
   :label: eq-xb

   X_b = \sqrt{2\, (H_b - 1)} .

La pression
-----------

Il reste à intégrer :eq:`eq-gradient-pression`. Le calcul est plus simple avec
la variable auxiliaire :math:`Y = X / \sqrt{2}`, pour laquelle
:math:`H = 1 + Y^2`. En posant :math:`Z = Y / H`, une primitive du gradient de
pression est

.. math::
   :label: eq-primitive-pression

   P_d(Y) = \sqrt{2} \left[
   \left( \frac{1}{2} - \frac{3 H_b}{8} \right) \big( \arctan Y + Z \big)
   - \frac{Z}{4} \frac{H_b}{H}
   \right] .

La pression doit s'annuler en :math:`X_b`, c'est-à-dire en
:math:`Y_b = \sqrt{H_b - 1}`. On soustrait donc la valeur de la primitive en ce
point :

.. math::
   :label: eq-pression-analytique

   P(X) = P_d\!\left( \tfrac{X}{\sqrt{2}} \right) - P_d(Y_b),
   \qquad X_a \leq X \leq X_b .

En dehors de :math:`[X_a, X_b]`, :math:`P = 0`.

La fraction de vide
-------------------

En dehors de la zone sous pression, :math:`P = 0`, et le débit constant
:eq:`eq-debit-constant` donne directement la fraction de vide :

.. math::
   :label: eq-theta-analytique

   \theta(X) =
   \begin{cases}
     1 - \dfrac{H_b}{H(X)} & \text{si } X < X_a \text{ ou } X > X_b, \\[2mm]
     0 & \text{si } X_a \leq X \leq X_b .
   \end{cases}

Cette solution a deux propriétés caractéristiques, qu'il faudra retrouver
numériquement :

- en :math:`X_b`, :math:`H = H_b` donc :math:`\theta` vaut 0 des deux côtés :
  la fraction de vide est **continue** à la frontière de cavitation ;
- en :math:`X_a`, :math:`\theta` passe brusquement de
  :math:`1 - H_b / H(X_a)` à 0 : la fraction de vide est **discontinue** au
  ménisque d'entrée, où l'huile remplit d'un coup l'espace entre les surfaces.
  La pression, elle, y est continue mais son gradient ne s'annule pas.



Le ménisque d'entrée et la quantité d'huile
-------------------------------------------

La pression :eq:`eq-pression-analytique` dépend du paramètre :math:`H_b`, égal à
la quantité d'huile disponible :math:`H_{\text{oil}}`. Le ménisque d'entrée
:math:`X_a` est la position **en amont** (:math:`X_a < 0`) où la pression
s'annule :

.. math::
   :label: eq-xa

   P(X_a) = 0 .

Cette équation n'a pas de solution explicite. On la résout par la méthode de
Newton, en utilisant :eq:`eq-gradient-pression` comme dérivée : une dizaine
d'itérations suffisent à atteindre la précision machine
:cite:p:`biboulet2020hdr`.

On peut aussi procéder dans l'autre sens : imposer :math:`X_a` et chercher le
:math:`H_b` correspondant, toujours par Newton sur :math:`P(X_a) = 0`.

La charge
---------

La charge s'obtient en intégrant la pression. :cite:t:`biboulet2020hdr` en
donne une primitive :

.. math::
   :label: eq-charge-analytique

   \frac{W_d(Y)}{2} =
   Y \left( \frac{1}{2} - \frac{3 H_b}{8} \right) \big( \arctan Y - \arctan Y_b \big)
   + \frac{H_b}{8 H}
   + Y_b\, Y \left( \frac{3}{8} - \frac{1}{4 H_b} \right),
   \qquad
   W = W_d(Y_b) - W_d(Y_a),

avec :math:`Y_a = X_a / \sqrt{2}`.

Le cas noyé et les valeurs de référence
---------------------------------------

Quand la quantité d'huile augmente, le ménisque d'entrée recule vers l'amont.
Dans la limite :math:`X_a \to -\infty`, le contact est **noyé** : la condition
:math:`P(-\infty) = 0` fixe la valeur maximale de :math:`H_b`. Les valeurs de
référence données par :cite:t:`biboulet2020hdr` sont :

.. list-table:: Valeurs de référence (cas noyé)
   :header-rows: 1
   :widths: 50 50

   * - Grandeur
     - Valeur
   * - Épaisseur en sortie :math:`H_{b,ff}`
     - :math:`\approx 1{,}226`
   * - Charge :math:`W_{ff}`
     - :math:`\approx 0{,}408`

Pour le cas sous-alimenté, la HDR donne la correspondance suivante entre la
position du ménisque d'entrée et l'épaisseur en sortie :

.. list-table:: Correspondance :math:`X_a \leftrightarrow H_b` (HDR, figure 2.3)
   :header-rows: 1

   * - :math:`X_a`
     - :math:`-\infty`
     - :math:`-3`
     - :math:`-2`
     - :math:`-1{,}5`
     - :math:`-1`
     - :math:`-0{,}75`
     - :math:`-0{,}5`
   * - :math:`H_b`
     - 1,226
     - 1,201
     - 1,169
     - 1,136
     - 1,085
     - 1,053
     - 1,028



Ces valeurs donnent un premier test simple pour tout code : retrouver
:math:`H_{b,ff}` et :math:`W_{ff}`, puis le tableau de correspondance.

Comment la solution servira à valider les méthodes
--------------------------------------------------

Pour une quantité d'huile donnée, la solution analytique fournit :
:math:`P(X)`, :math:`\theta(X)`, :math:`X_a`, :math:`X_b` et :math:`W`. Pour
chaque méthode numérique, on mesurera :

- l'**erreur sur la pression** et sur la **fraction de vide**, en tout point ;
- l'**erreur sur la position des frontières** :math:`X_a` et :math:`X_b` ;
- l'**erreur sur la charge** :math:`W`.


