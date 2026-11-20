.. _sec-comparaison-sans-cavitation:

Comparison
==========

We evaluate both solutions on the same grid. We compare the pressure, then two
global quantities that describe the contact: the load and the friction.

The load
--------

The load per unit width is the integral of the pressure (dimensionless form
:eq:`eq-adimensionnement`):

.. math::

   W = \int P \,\mathrm{d}X .

It is the force that pushes the two surfaces apart.

The friction
------------

Friction comes from the oil resisting the motion. Across the film thickness,
the oil velocity is the sum of the two flows of :ref:`sec-equations`: the
Couette flow (the surfaces drag the oil) and the Poiseuille flow (the pressure
pushes the oil). The shear stress :math:`\tau` is the viscosity times the slope
of this velocity profile at the wall. In dimensionless form (velocities
:math:`U_1`, :math:`U_2` of the bottom and top surfaces, divided by
:math:`u_m`):

.. math::

   \tau = \frac{U_2 - U_1}{H} \mp 6 H \frac{\mathrm{d}P}{\mathrm{d}X},
   \qquad F = \int \tau \,\mathrm{d}X ,

with the sign :math:`-` on the bottom surface and :math:`+` on the top one.

- The first term comes from sliding (Couette). It disappears in pure rolling,
  when both surfaces move at the same speed (:math:`U_1 = U_2`).
- The second term comes from the pressure (Poiseuille). It has opposite signs
  on the two surfaces: the oil pushed by the pressure drags the two surfaces in
  opposite directions.

So we only need :math:`\mathrm{d}P/\mathrm{d}X`. We get it with finite
differences for the FD solution, and with autograd for the PINN.

.. literalinclude:: /../src/pri/friction.py
   :pyobject: shear_stress_1D

Result
------

.. plot:: ../figures/reynolds_1d_pinn_vs_fd.py
