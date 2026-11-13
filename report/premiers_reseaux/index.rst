Premiers réseaux de neurones
============================

Un PINN est un réseau de neurones entraîné à vérifier une équation
différentielle. Pour en construire un, trois briques sont nécessaires :

1. **dériver la sortie d'un réseau par rapport à son entrée** : c'est le rôle
   de la différentiation automatique (autograd) de PyTorch ;
2. **entraîner un réseau**, c'est-à-dire ajuster ses poids :math:`w` et ses
   biais :math:`b` pour minimiser une perte ;
3. **écrire une perte qui contient l'équation** au lieu de la solution.

Ce chapitre traite ces trois briques dans l'ordre, chacune sur un cas simple
dont la solution exacte est connue, ce qui permet de vérifier chaque résultat.

Tous les calculs sont faits en double précision (``float64``). Ces problèmes
sont minuscules, donc le coût supplémentaire est négligeable, et l'erreur
d'arrondi (de l'ordre de :math:`10^{-16}` en relatif, contre
:math:`10^{-7}` en simple précision) ne se mélange pas aux erreurs que l'on
cherche à mesurer. Les tirages aléatoires (initialisation des poids) partent
d'une ``Seed`` fixée, chaque résultat est donc reproductible.

.. toctree::
   :maxdepth: 2

   autograd
   ajustement_sinus
   premiere_edo
