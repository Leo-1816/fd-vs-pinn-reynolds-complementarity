1D Reynolds, flooded case with cavitation
=========================================

In this case, there is plenty of oil in front of the contact. The inlet
meniscus is pushed infinitely far upstream (:math:`X_a = -\infty`). The film
breaks up at :math:`X_b`, and a cavitated zone with :math:`P = 0` follows. We
only take into account the Reynolds condition at the outlet: the void fraction
:math:`\theta` is not used yet.

Why :math:`P = 0` far upstream? The pressure :math:`P` is a **relative**
pressure: we measure it from the ambient pressure, which is therefore
:math:`P = 0`. Far upstream, the gap is huge and the oil is just a bath at
rest, at ambient pressure. Numerically, we put the inlet at a finite
:math:`X_{in}` far upstream and impose :math:`P(X_{in}) = 0`.

The figure below sums up the two zones. In the full film, the Reynolds
equation holds (residual :math:`r = 0`) and :math:`P > 0`. In the cavitated
zone, :math:`P = 0` and the residual is :math:`-\mathrm{d}H/\mathrm{d}X < 0`:
the pressure would like to become negative there, but it is held at zero. So
at every point, one of the two quantities :math:`P` or :math:`r` is zero. This
is the complementarity used by the PINN (:ref:`sec-pinn-cas-noye`).

.. plot:: ../figures/flooded_zones.py

.. note:: What this model cannot do

   Without :math:`\theta`, nothing controls the amount of oil. The model can
   describe the film breaking up at the outlet, but not a starved inlet with a
   meniscus inside the domain. Upstream of such a meniscus, the film is partly
   empty and :math:`P = 0`, but the residual would be positive there, which
   the model forbids. The starved case needs :math:`\theta`.

.. toctree::
   :maxdepth: 2

   differences_finies
   pinn
