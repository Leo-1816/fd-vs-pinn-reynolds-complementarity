.. _sec-premiere-edo:

Premier PINN : résoudre y' = -y
===============================

Le problème
-----------

On cherche la fonction :math:`y` définie sur :math:`[0, X]` telle que

.. math::
   :label: eq-edo-test

   y'(x) = -y(x), \qquad y(0) = 1 .

Sa solution exacte, :math:`y(x) = e^{-x}`, sert **uniquement** à vérifier le
résultat : elle n'intervient jamais dans l'entraînement.

Le principe d'un PINN
---------------------

Dans la section précédente, la perte comparait le réseau à des valeurs
connues de la solution. Ici, la solution est inconnue : on ne peut donc pas
écrire :math:`y(x_i; w, b) - y_{\text{exact}}(x_i)`. En revanche, on sait ce que
la solution doit vérifier : l'équation :eq:`eq-edo-test`.

L'idée d'un PINN (*Physics-Informed Neural Network*) est de remplacer
l'inconnue par un réseau :math:`y(x; w, b)` et de **mettre l'équation dans la
perte**. On définit le **résidu** de l'équation

.. math::
   :label: eq-residu

   r(x; w, b) = y'(x; w, b) + y(x; w, b),

qui vaut zéro partout si et seulement si le réseau vérifie l'équation. On
choisit des points :math:`x_1, \dots, x_N` dans le domaine, appelés **points
de collocation** (ils jouent un rôle proche des nœuds d'un maillage de
différences finies), et on minimise

.. math::
   :label: eq-perte-pinn

   \mathcal{L}(w, b) =
   \underbrace{\frac{1}{N} \sum_{i=1}^{N} r(x_i; w, b)^2}_{\text{l'équation est vérifiée}}
   \; + \;
   \underbrace{\left( y(0; w, b) - 1 \right)^2}_{\text{la condition initiale est vérifiée}} .

Si :math:`\mathcal{L} = 0`, le réseau vérifie l'équation en tous les points de
collocation **et** la condition initiale : c'est la solution. Le second terme
est indispensable : sans lui, toute fonction :math:`C e^{-x}` annulerait le
résidu, et le problème n'aurait pas de solution unique.

.. list-table:: Ajustement supervisé et PINN
   :header-rows: 1
   :widths: 30 35 35

   * -
     - Ajustement de :math:`\sin x`
     - PINN pour :math:`y' = -y`
   * - Ce que l'on donne au réseau
     - des valeurs de la solution
     - l'équation et la condition initiale
   * - Ce que mesure la perte
     - l'écart aux données
     - le résidu de l'équation
   * - Dérivée par rapport à :math:`x`
     - inutile
     - indispensable (:math:`y'` dans le résidu)
   * - Points :math:`x_i`
     - points de données
     - points de collocation

Calculer le résidu
------------------

Le résidu contient :math:`y'(x; w, b)`, la dérivée de la sortie du réseau par
rapport à son entrée. On la calcule par autograd (:ref:`sec-autograd`). Pour
cela, les points de collocation sont créés avec ``requires_grad``, afin que
PyTorch enregistre le graphe de calcul depuis :math:`x` :

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: make_sample_points

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: ode_residual

L'option ``create_graph=True`` est ici **obligatoire**. Le PINN dérive en
effet deux fois, par rapport à deux variables différentes :

1. d'abord :math:`y` par rapport à :math:`x`, pour former le résidu ;
2. puis la perte, qui contient :math:`y'`, par rapport aux paramètres
   :math:`w` et :math:`b`, pour l'entraînement (``loss.backward()``).

La seconde dérivation doit traverser le calcul de :math:`y'`. Sans
``create_graph=True``, ce calcul ne serait pas enregistré, et les paramètres
ne recevraient aucun gradient venant du résidu.

La perte suit directement :eq:`eq-perte-pinn` :

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: pinn_loss

Le réseau et l'entraînement
---------------------------

Le réseau a deux couches cachées avec une activation :math:`\tanh` :

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: make_network

Le choix de :math:`\tanh` plutôt que la fonction ReLU, très utilisée
ailleurs, n'est pas anodin. ReLU est linéaire par morceaux : sa dérivée
seconde est nulle presque partout. Un réseau ReLU ne pourrait donc pas
représenter une équation qui contient :math:`y''`. :math:`\tanh` est
infiniment dérivable, ce qui convient à toutes les équations de ce projet.

L'entraînement est **identique** à celui de la section précédente (Adam, mêmes
quatre étapes par itération) : seule la fonction de perte change. C'est un
point important : un PINN n'est pas un nouvel algorithme d'apprentissage,
c'est un réseau ordinaire entraîné avec une perte différente.

Résultats
---------

.. plot:: ../figures/first_pinn_ode.py
   :caption: Premier PINN pour :math:`y' = -y`, :math:`y(0) = 1`.
      En haut : solution du réseau, solution exacte :math:`e^{-x}` et points
      de collocation. En bas : erreur absolue, en échelle logarithmique.

La figure ci-dessus montre que :

- **le réseau a trouvé la solution sans jamais la voir** : seules l'équation et
  la condition initiale figurent dans la perte ;
- **l'erreur entre les points de collocation est du même ordre qu'aux points
  eux-mêmes** : le réseau fournit une solution continue, que l'on peut évaluer
  et dériver en tout point du domaine, contrairement aux différences finies
  qui ne donnent des valeurs qu'aux nœuds.

Limites observées
-----------------

- **La condition initiale n'est vérifiée qu'approximativement.** Elle n'est
  qu'un terme de la perte, en concurrence avec le résidu : l'erreur en
  :math:`x = 0` n'est pas nulle. 
- **La solution n'est valable que sur le domaine d'entraînement.** L'équation
  n'est imposée que sur :math:`[0, X]`. Au-delà, rien ne contraint le réseau,
  et il n'a aucune raison de suivre :math:`e^{-x}` : un PINN n'extrapole pas.
- **Les deux termes de la perte ont ici le même poids.** Ce choix arbitraire
  influence l'équilibre entre résidu et condition initiale. Son effet fera
  l'objet d'expériences dédiées.

.. note:: À retenir

   Un PINN est un réseau ordinaire dont la perte contient le résidu de
   l'équation et les conditions aux limites ou initiales. Autograd fournit les
   dérivées du réseau par rapport à son entrée, et ``create_graph=True``
   permet de rétropropager ensuite à travers ces dérivées jusqu'aux poids et
   biais.
