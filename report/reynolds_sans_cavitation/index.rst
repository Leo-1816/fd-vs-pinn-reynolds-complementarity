Reynolds 1D sans cavitation
===========================

Premier cas résolu par les deux méthodes : l'équation :eq:`eq-reynolds`, avec
un film plein partout et :math:`P = 0` aux deux bords.

.. important:: Un problème volontairement simplifié

   Les équations résolues ici ne contiennent ni la fraction de vide
   :math:`\theta`, ni la quantité d'huile :math:`H_b`, ni la complémentarité :
   rien n'y décrit la cavitation ni le manque d'huile. Elles ne représentent
   donc pas encore la complexité du cas sous-alimenté.

   Le domaine :math:`[X_a, X_b]` est emprunté à la solution analytique
   (:math:`H_b = 1{,}1`) pour une seule raison : sur cette portion, le film
   est plein et la pression s'annule aux deux bords, donc la pression
   analytique est une solution exacte de ce problème simplifié. Elle sert
   uniquement de référence pour valider les deux méthodes.

.. toctree::
   :maxdepth: 2

   differences_finies
   pinn
   comparaison
