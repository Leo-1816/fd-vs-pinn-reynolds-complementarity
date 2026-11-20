.. _sec-pinn-cas-noye:

PINN: complementarity between pressure and residual
===================================================

Why we need a complementarity
-----------------------------

The network must find by itself where the film is full and where it is
cavitated. We cannot just add a penalty on :math:`P < 0` and keep the Reynolds
equation everywhere. In the cavitated zone, :math:`P = 0` gives the residual

.. math::

   r = \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   - \frac{\mathrm{d}H}{\mathrm{d}X} = -\frac{\mathrm{d}H}{\mathrm{d}X} \neq 0 .

The network would have to choose between meeting the equation and meeting
:math:`P \geq 0`. It would find a wrong compromise.

We need a rule that says: "meet the Reynolds equation, **except** where the
pressure is held at zero". And only where the oil *wants* a negative pressure.
The sign of :math:`r` tells us which way the pressure pulls:

- :math:`r < 0`: without the constraint, the pressure would go below zero. We
  hold it at zero. This is physical: the oil cavitates.
- :math:`r > 0`: the pressure would like to go up. Setting it to zero would
  not be physical: the oil pushes, it does not cavitate.

This gives three conditions. They are the Swift-Stieber condition written as
an obstacle problem :cite:p:`cheng2023hlnets` (eq. 5):

.. math::

   P \geq 0, \qquad -r \geq 0, \qquad P \, r = 0 .

At each point, at least one of the two quantities is zero. Either
:math:`P > 0` and the Reynolds equation holds exactly (:math:`r = 0`), or
:math:`P = 0` and we accept :math:`r < 0`. The boundary :math:`X_b` is not
imposed.

.. note:: A picture: the obstacle problem

   Think of a stretched sheet above a flat floor. Where the sheet would like to
   go below the floor, it rests on it (:math:`P = 0`, and the floor holds it
   up: :math:`r < 0`). Elsewhere, it hangs freely and follows its own equation
   (:math:`r = 0`). Nobody tells the sheet where it touches the floor: the
   contact point :math:`X_b` appears by itself.

The loss
--------

The Fischer-Burmeister function brings the three conditions together (as in
:eq:`eq-fischer-burmeister`, with :math:`-r` instead of :math:`\theta`). So a
single loss term :math:`\varphi^2` replaces the three conditions. Two details
are needed on this wide domain:

- the residual is divided by :math:`H^3 > 0`. This does not change its sign,
  but it stops the residual from crushing the other terms upstream, where
  :math:`H^3` is very large;
- the network input is scaled to :math:`[-1, 1]`, otherwise :math:`\tanh`
  saturates at the far end of the domain.

.. literalinclude:: /../src/pinn/reynolds_1d_flooded.py
   :pyobject: complementarity_residual

The loss adds the mean of :math:`\varphi^2` and the conditions :math:`P = 0`
at both ends. :cite:t:`cheng2023hlnets` (section 2.3.2) suggest another way:
find the cavitated zone during training and remove the term
:math:`\mathrm{d}H/\mathrm{d}X` from the residual there.

The size of the network
-----------------------

The network has 3 hidden layers of 30 neurons, more than for the first case.
The domain is much wider, and the pressure has a long slow part upstream, a
narrow peak near the contact and a kink in its curvature at :math:`X_b`.

- **Width** (neurons per layer): with one layer, the network is a sum of
  smoothed steps, one per neuron. More neurons give finer shapes, but a narrow
  feature needs many of them.
- **Depth** (number of layers): each layer bends the functions of the previous
  one. A deep and narrow network can represent complex shapes with fewer
  parameters.
- **Cost**: the number of parameters grows like (layers) × (width)², and a
  deeper network is harder to train. In a PINN, the limit is often the
  training, not the size of the network.

Validation
----------

We compare the result with the same analytical solution as for finite
differences (:ref:`sec-fd-cas-noye`).
