.. _sec-autograd:

Dériver avec autograd
=====================

Pourquoi en a-t-on besoin ?
---------------------------

L'équation d'un PINN contient des dérivées de l'inconnue, par exemple
:math:`y'(x)`. Si l'inconnue est représentée par un réseau de neurones
:math:`y(x; w, b)`, il faut savoir calculer :math:`\partial y / \partial x`,
la dérivée de la **sortie** du réseau par rapport à son **entrée**, et
souvent la dérivée seconde.

Il existe trois façons de calculer une dérivée sur ordinateur :

- **à la main** : on dérive la formule sur papier, puis on code le résultat.
  C'est exact, mais impossible en pratique pour un réseau de plusieurs
  milliers de paramètres ;
- **par différences finies** : on approche la dérivée par un taux
  d'accroissement, par exemple
  :math:`y'(x) \approx \frac{y(x+h) - y(x-h)}{2h}`. C'est simple, mais
  approché : l'erreur dépend du pas :math:`h` ;
- **par différentiation automatique** : l'ordinateur applique lui-même la
  dérivation en chaîne aux opérations élémentaires du calcul. Le résultat
  est exact, aux erreurs d'arrondi près.

PyTorch fournit la troisième méthode sous le nom d'*autograd*
:cite:p:`pytorch_autograd_mechanics`.

Le principe : un graphe de calcul
---------------------------------

Une question naturelle se pose. Quand on appelle
``torch.autograd.grad(y, x)``, on ne semble donner que des valeurs : les
abscisses ``x`` et les valeurs ``y`` de la fonction. Comment PyTorch peut-il
calculer une dérivée **exacte** sans connaître la fonction, alors que les
différences finies, elles, doivent comparer des points voisins ?

La réponse est que ``y`` n'est pas qu'un tableau de nombres : c'est un tenseur
qui **transporte l'historique complet du calcul** qui l'a produit. PyTorch
connaît donc bien la fonction, sous la forme de la suite exacte des
opérations élémentaires appliquées à ``x``.

Étape 1 : enregistrer le calcul
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Quand on demande à PyTorch de suivre un tenseur ``x``
(``x.requires_grad_(True)``), chaque opération effectuée à partir de ``x`` est
**enregistrée** au moment même où elle est calculée. Pour
:math:`f(x) = x^2 \sin x`, PyTorch décompose le calcul en trois opérations
élémentaires :

.. math::

   a = x^2, \qquad b = \sin x, \qquad y = a \cdot b .

Chaque résultat garde dans son attribut ``grad_fn`` une référence vers
l'opération qui l'a produit, et chaque opération garde une référence vers ses
entrées. On obtient un **graphe de calcul**, comme vu ce semestre, accroché au résultat ``y`` :

.. code-block:: text

          x  (requires_grad=True)
         / \
    a = x²   b = sin x        PowBackward0, SinBackward0
         \ /
       y = a · b              MulBackward0   <- y.grad_fn

On peut l'observer directement :

.. code-block:: python

   x = torch.tensor([2.0], dtype=torch.float64, requires_grad=True)
   y = x**2 * torch.sin(x)

   print(y)                         # tensor([3.6372], grad_fn=<MulBackward0>)
   print(y.grad_fn.next_functions)  # ((<PowBackward0>, 0), (<SinBackward0>, 0))

En plus du graphe, PyTorch **mémorise les valeurs intermédiaires** dont il
aura besoin pour dériver : ici :math:`x`, :math:`a` et :math:`b` au point
considéré.

Étape 2 : remonter le graphe : comme l'exemple du cours
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pour chaque type d'opération élémentaire, PyTorch possède une **règle de
dérivation écrite une fois pour toutes** : la dérivée de :math:`\sin` est
:math:`\cos`, celle de :math:`u \mapsto u^2` est :math:`2u`, celle d'un
produit :math:`a \cdot b` est :math:`b` par rapport à :math:`a` et :math:`a`
par rapport à :math:`b`, etc.

``torch.autograd.grad(y, x)`` part de ``y``, suit les ``grad_fn`` jusqu'à
``x``, et applique à chaque étape la règle de l'opération rencontrée, évaluée
avec les valeurs mémorisées. Les contributions sont combinées par la **règle
de dérivation en chaîne** :

.. math::
   :label: eq-chaine

   \frac{\mathrm{d}y}{\mathrm{d}x}
   = \frac{\partial y}{\partial a}\,\frac{\mathrm{d}a}{\mathrm{d}x}
   + \frac{\partial y}{\partial b}\,\frac{\mathrm{d}b}{\mathrm{d}x}
   = b \cdot 2x + a \cdot \cos x .

Au point :math:`x = 2`, avec les valeurs mémorisées :math:`a = 4` et
:math:`b = \sin 2 \approx 0{,}9093` :

.. math::

   \frac{\mathrm{d}y}{\mathrm{d}x}(2)
   = 0{,}9093 \times 4 + 4 \times \cos 2
   \approx 3{,}6372 - 1{,}6646
   = 1{,}9726,

ce qui est exactement la valeur de la formule
:math:`f'(x) = 2x \sin x + x^2 \cos x` en :math:`x = 2`, et ce que renvoie
``torch.autograd.grad``.

Ce qu'il faut retenir
~~~~~~~~~~~~~~~~~~~~~

- **Autograd ne regarde jamais les points voisins.** Chaque dérivée est
  calculée au point :math:`x_i` lui-même, à partir des formules exactes des
  opérations élémentaires. C'est la différence fondamentale avec les
  différences finies, qui comparent :math:`f(x+h)` et :math:`f(x-h)`.
- **Le résultat est exact**, aux erreurs d'arrondi près : c'est le même calcul
  qu'à la main, mais automatisé et appliqué à des fonctions aussi compliquées
  que l'on veut (un réseau de neurones n'est qu'une longue suite d'opérations
  élémentaires).
- **Ce n'est pas du calcul symbolique** : PyTorch ne produit pas la formule
  :math:`2x \sin x + x^2 \cos x`, seulement sa **valeur** aux points demandés.
- **Sans historique, pas de dérivée.** Un tenseur contenant les mêmes nombres,
  mais créé sans passer par ``x``, n'a pas de ``grad_fn`` : autograd ne peut
  rien en faire.

  .. code-block:: python

     y_sans_graphe = torch.tensor([3.6372], dtype=torch.float64)
     torch.autograd.grad(y_sans_graphe.sum(), x)
     # RuntimeError: element 0 of tensors does not require grad
     #               and does not have a grad_fn

  C'est aussi ce que font volontairement ``x.detach()`` (une copie de ``x``
  coupée du graphe) et le bloc ``with torch.no_grad():`` (aucune opération du
  bloc n'est enregistrée).

Dans le code du projet
~~~~~~~~~~~~~~~~~~~~~~

Deux détails de la fonction utilisée dans ce projet :

.. literalinclude:: /../src/pinn/autograd_derivatives.py
   :pyobject: autograd_first_and_second_derivative

Les options de ``torch.autograd.grad`` sont décrites dans sa documentation
:cite:p:`pytorch_autograd_grad`.

- **La somme** ``function_values.sum()`` : ``autograd.grad`` dérive un
  scalaire. En sommant les valeurs :math:`f(x_1) + \dots + f(x_n)`, la dérivée
  par rapport à :math:`x_i` est exactement :math:`f'(x_i)`, car chaque terme ne
  dépend que de son propre point. On obtient donc toutes les dérivées en un
  seul appel.
- **L'option** ``create_graph=True`` : par défaut, PyTorch efface le graphe
  après l'avoir remonté. Avec cette option, le calcul de la dérivée est
  lui-même enregistré, ce qui permet de la dériver à nouveau pour obtenir
  :math:`f''`. Ce point est essentiel pour les PINN
  (voir :ref:`sec-premiere-edo`).

Vérification sur une fonction connue
------------------------------------

On compare les trois méthodes sur

.. math::
   :label: eq-fonction-test

   f(x) = x^2 \sin x,

dont les dérivées calculées à la main sont

.. math::
   :label: eq-derivees-test

   f'(x) = 2x \sin x + x^2 \cos x,
   \qquad
   f''(x) = (2 - x^2) \sin x + 4x \cos x.

La comparaison est faite en de nombreux points répartis sur un intervalle,
en prenant l'écart maximal entre les méthodes. Le script
``src/pinn/autograd_derivatives.py`` affiche ces écarts, et le test
``tests/test_autograd_derivatives.py`` vérifie automatiquement que les
formules :eq:`eq-derivees-test` et autograd coïncident à :math:`10^{-12}` près.

Ce que l'on observe :

- **Main et autograd coïncident au niveau de l'arrondi machine**, pour
  :math:`f'` comme pour :math:`f''`. C'est attendu : les deux méthodes sont
  exactes, seul l'ordre des opérations diffère.
- **Les différences finies s'en écartent nettement plus.** Avec un pas
  :math:`h`, le schéma centré a une erreur de troncature en
  :math:`O(h^2)`. Pour la dérivée seconde s'ajoute une erreur d'arrondi en
  :math:`O(\varepsilon / h^2)`, où :math:`\varepsilon` est la précision
  machine : diminuer :math:`h` n'améliore donc pas indéfiniment le résultat.

.. note:: À retenir

   Autograd donne des dérivées **exactes** (à l'arrondi près) de la fonction
   réellement calculée, quelle que soit sa complexité. C'est ce qui rend les
   PINN possibles : on peut dériver un réseau de neurones par rapport à son
   entrée aussi facilement qu'une formule.

Dans la suite, l'évaluation des différences finies est faite à l'intérieur
d'un bloc ``with torch.no_grad():``, qui désactive l'enregistrement du graphe :
les différences finies n'utilisent pas autograd, il est donc inutile (et
coûteux) de construire un graphe, et cela garantit que cette vérification est
indépendante d'autograd.
