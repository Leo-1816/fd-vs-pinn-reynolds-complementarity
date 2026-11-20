1D Reynolds without cavitation
==============================

This is the first case solved with both methods: the equation
:eq:`eq-reynolds`, with a full film everywhere and :math:`P = 0` at both ends.

.. important:: A problem simplified on purpose

   The equations solved here contain neither the void fraction :math:`\theta`,
   nor the amount of oil :math:`H_b`, nor complementarity. Nothing in them
   describes cavitation or a lack of oil. So they do not yet capture how
   complex the starved case is.

   We borrow the domain :math:`[X_a, X_b]` from the analytical solution
   (:math:`H_b = 1.1`) for one reason only. On this interval, the film is full
   and the pressure is zero at both ends. So the analytical pressure is an
   exact solution of this simplified problem. It is only used as a reference to
   validate both methods.

.. toctree::
   :maxdepth: 2

   differences_finies
   pinn
   comparaison
