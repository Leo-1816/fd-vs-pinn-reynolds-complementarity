.. _sec-ajustement-sinus:

Entraîner un réseau : ajustement de sin(x)
==========================================

Le problème
-----------

Avant de résoudre une équation, on apprend à entraîner un réseau sur la
tâche la plus simple possible : approcher une fonction connue,
:math:`\sin x` sur :math:`[-\pi, \pi]`, à partir de quelques-unes de ses
valeurs. On dispose de :math:`N` points d'entraînement
:math:`(x_i, \sin x_i)` régulièrement espacés, et on cherche un réseau
:math:`y(x; w, b)` qui passe au plus près de ces points.

C'est de l'**apprentissage supervisé** : on donne la réponse au réseau, aux
points :math:`x_i`.

Le réseau
---------

On utilise un **MLP** (*Multi-Layer Perceptron*, ou perceptron multicouche),
la forme la plus simple de réseau de neurones : l'entrée traverse une suite
de couches, chacune transmettant son résultat à la suivante, sans boucle ni
retour en arrière. Les couches entre l'entrée et la sortie sont appelées
**couches cachées**. Chaque couche d'un MLP est formée de deux étapes :

- une **couche linéaire** calcule :math:`w\,x + b`, où les poids :math:`w` et
  les biais :math:`b` sont les paramètres à apprendre ;
- une **fonction d'activation** (ici :math:`\tanh`) est appliquée à chaque
  neurone. Elle n'a pas de paramètre, mais elle est indispensable : sans elle,
  un empilement de couches linéaires reste une fonction linéaire.

Le réseau utilisé a une seule couche cachée de :math:`H` neurones :

.. math::
   :label: eq-reseau-une-couche

   y(x; w, b) = \sum_{k=1}^{H} w_{2,k} \tanh\!\left(w_{1,k}\, x + b_{1,k}\right) + b_2 .

Une seule couche cachée suffit en théorie à approcher toute fonction continue
sur un intervalle borné, à condition d'avoir assez de neurones : c'est le
théorème d'approximation universelle
(voir :cite:t:`nielsen2015neural`, chapitre 4, pour une démonstration
visuelle).

.. literalinclude:: /../src/pinn/fit_sine_mlp.py
   :pyobject: make_network

Les couches ``nn.Linear``, ``nn.Tanh`` et le conteneur ``nn.Sequential`` sont
ceux du module ``torch.nn`` :cite:p:`pytorch_nn`.

La perte
--------

On mesure l'écart entre le réseau et les données par l'**erreur quadratique
moyenne** :

.. math::
   :label: eq-perte-supervisee

   \mathcal{L}(w, b) = \frac{1}{N} \sum_{i=1}^{N}
   \left( y(x_i; w, b) - \sin x_i \right)^2 .

Entraîner le réseau, c'est chercher les :math:`w` et :math:`b` qui rendent
:math:`\mathcal{L}` aussi petite que possible.

.. literalinclude:: /../src/pinn/fit_sine_mlp.py
   :pyobject: mean_squared_error_loss

L'entraînement
--------------

On minimise :math:`\mathcal{L}` par une méthode de descente de gradient : à
chaque itération, on calcule le gradient de la perte par rapport à tous les
paramètres, :math:`\partial \mathcal{L} / \partial w` et
:math:`\partial \mathcal{L} / \partial b`, puis on déplace les paramètres dans
la direction qui fait diminuer la perte. Le gradient est calculé par autograd
(:ref:`sec-autograd`), cette fois par rapport aux paramètres et non par
rapport à :math:`x`.

On utilise l'optimiseur **Adam** :cite:p:`pytorch_adam`, une variante de la descente de gradient qui
adapte automatiquement la taille du pas pour chaque paramètre. Une itération
(une *époque*) comporte toujours les mêmes quatre étapes :

.. literalinclude:: /../src/pinn/fit_sine_mlp.py
   :pyobject: train

1. ``optimizer.zero_grad()`` remet les gradients à zéro. C'est nécessaire car
   ``backward()`` **ajoute** le nouveau gradient à celui déjà stocké. Sans
   remise à zéro, on utiliserait la somme de tous les gradients passés,
   calculés avec d'anciens paramètres.
2. On calcule la perte avec les paramètres actuels.
3. ``loss.backward()`` calcule le gradient de la perte par rapport à tous les
   :math:`w` et :math:`b`.
4. ``optimizer.step()`` met à jour les paramètres.

Résultats
---------

.. plot:: ../figures/fit_sine_mlp.py
   :caption: Ajustement de :math:`\sin x` par le réseau à une couche cachée.
      En haut : données d'entraînement, réseau et fonction exacte.
      En bas : erreur absolue entre le réseau et :math:`\sin x`, en échelle
      logarithmique.

La figure ci-dessus permet de répondre à deux questions :

- **Le réseau a-t-il appris la fonction entre les points ?** L'erreur est
  évaluée sur des points bien plus nombreux que les points d'entraînement.
  Elle s'annule ponctuellement là où le réseau croise la fonction exacte.
  Avec **peu de données**, ces creux coïncident avec les points
  d'entraînement : le réseau passe par les données, et l'erreur est
  concentrée **entre** elles, là où il n'a reçu aucune information. Avec
  **beaucoup de données**, l'erreur devient du même ordre partout, et les
  creux ne sont plus que des croisements sans signification particulière.
- **Où l'approximation est-elle la moins bonne ?** L'erreur est souvent plus
  grande près des bords de l'intervalle : un point du bord n'a des données
  que d'un seul côté, l'approximation y est moins contrainte.

Le nombre de données est donc un réglage important de l'apprentissage
supervisé. Dans un PINN, son équivalent est le nombre de points de
collocation (:ref:`sec-premiere-edo`).

.. note:: À retenir

   Entraîner un réseau, c'est minimiser une perte par rapport à ses poids et
   biais. Ici la perte compare le réseau à des **valeurs connues** de la
   solution. La section suivante remplace ces valeurs par l'**équation**.
