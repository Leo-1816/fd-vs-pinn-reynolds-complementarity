Le problème physique
====================

.. important:: Origine du contenu

   Le contenu scientifique de ce chapitre (modèle physique, équations,
   adimensionnement, formulation avec complémentarité, solution analytique 1D)
   provient intégralement de l'habilitation à diriger des recherches de Nans
   Biboulet :cite:p:`biboulet2020hdr`. Ce chapitre n'apporte rien de nouveau : il
   reformule ce travail dans le but d'en faciliter la compréhension. 

Ce chapitre décrit le problème que le projet cherche à résoudre, sans
supposer de connaissance préalable en lubrification. Il répond à quatre
questions :

1. **De quoi parle-t-on ?** Un contact lubrifié, dans lequel un film d'huile
   très mince sépare deux surfaces en mouvement, et ce qui s'y passe quand
   l'huile vient à manquer (:ref:`sec-contact-lubrifie`).
2. **Quelles équations faut-il résoudre ?** L'équation de Reynolds, complétée
   par une condition de complémentarité qui décrit la cavitation
   (:ref:`sec-equations`).
3. **Existe-t-il une solution exacte pour vérifier les calculs ?** Oui, en 1D :
   elle servira de référence pour valider les deux méthodes
   (:ref:`sec-solution-analytique`).
4. **Que va faire le projet ?** Résoudre ce problème par différences finies et
   par PINN, puis comparer les deux méthodes (:ref:`sec-demarche`).

Toutes les équations de ce chapitre sont tirées de :cite:t:`biboulet2020hdr`
(section 2.2.1 pour la solution analytique 1D, section 3.3.3 pour la
formulation avec complémentarité, annexe A pour les grandeurs
dimensionnelles).

.. toctree::
   :maxdepth: 2

   contact_lubrifie
   equations
   solution_analytique
   demarche
