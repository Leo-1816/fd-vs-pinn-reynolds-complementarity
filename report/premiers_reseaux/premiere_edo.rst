.. _sec-premiere-edo:

First PINN: solving y' = -y
===========================

The problem
-----------

We look for the function :math:`y` defined on :math:`[0, X]` such that

.. math::
   :label: eq-edo-test

   y'(x) = -y(x), \qquad y(0) = 1 .

Its exact solution, :math:`y(x) = e^{-x}`, is **only** used to check the
result. It is never used in training.

The idea of a PINN
------------------

In the previous section, the loss compared the network with known values of
the solution. Here, the solution is unknown, so we cannot write
:math:`y(x_i; w, b) - y_{\text{exact}}(x_i)`. But we do know what the solution
must satisfy: the equation :eq:`eq-edo-test`.

The idea of a PINN (*Physics-Informed Neural Network*) is to replace the
unknown with a network :math:`y(x; w, b)` and to **put the equation into the
loss**. We define the **residual** of the equation

.. math::
   :label: eq-residu

   r(x; w, b) = y'(x; w, b) + y(x; w, b) .

It is zero everywhere if and only if the network satisfies the equation. We
choose points :math:`x_1, \dots, x_N` in the domain, called **collocation
points** (they play a role close to the nodes of a finite difference grid).
Then we minimise

.. math::
   :label: eq-perte-pinn

   \mathcal{L}(w, b) =
   \underbrace{\frac{1}{N} \sum_{i=1}^{N} r(x_i; w, b)^2}_{\text{the equation holds}}
   \; + \;
   \underbrace{\left( y(0; w, b) - 1 \right)^2}_{\text{the initial condition holds}} .

If :math:`\mathcal{L} = 0`, the network satisfies the equation at all
collocation points **and** the initial condition: it is the solution. The
second term is essential. Without it, any function :math:`C e^{-x}` would make
the residual zero, and the problem would not have a unique solution.

.. list-table:: Supervised fitting and PINN
   :header-rows: 1
   :widths: 30 35 35

   * -
     - Fitting :math:`\sin x`
     - PINN for :math:`y' = -y`
   * - What we give the network
     - values of the solution
     - the equation and the initial condition
   * - What the loss measures
     - the gap to the data
     - the residual of the equation
   * - Derivative with respect to :math:`x`
     - not needed
     - essential (:math:`y'` in the residual)
   * - Points :math:`x_i`
     - data points
     - collocation points

Computing the residual
----------------------

The residual contains :math:`y'(x; w, b)`, the derivative of the network
output with respect to its input. We compute it with autograd
(:ref:`sec-autograd`). For this, the collocation points are created with
``requires_grad``, so that PyTorch records the computational graph from
:math:`x`:

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: make_sample_points

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: ode_residual

The option ``create_graph=True`` is **mandatory** here. The PINN takes
derivatives twice, with respect to two different variables:

1. first :math:`y` with respect to :math:`x`, to build the residual;
2. then the loss, which contains :math:`y'`, with respect to the parameters
   :math:`w` and :math:`b`, for training (``loss.backward()``).

The second derivative must go through the calculation of :math:`y'`. Without
``create_graph=True``, this calculation would not be recorded, and the
parameters would get no gradient from the residual.

The loss follows :eq:`eq-perte-pinn` directly:

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: pinn_loss

The network and training
------------------------

The network has two hidden layers with a :math:`\tanh` activation:

.. literalinclude:: /../src/pinn/first_pinn_ode.py
   :pyobject: make_network

Choosing :math:`\tanh` instead of the ReLU function, which is widely used
elsewhere, matters. ReLU is piecewise linear: its second derivative is zero
almost everywhere. So a ReLU network could not represent an equation that
contains :math:`y''`. :math:`\tanh` can be differentiated as many times as we
want, which suits all the equations of this project.

Training is **identical** to the previous section (Adam, same four steps per
iteration). Only the loss function changes. This is an important point: a PINN
is not a new learning algorithm. It is an ordinary network trained with a
different loss.

Results
-------

.. plot:: ../figures/first_pinn_ode.py
   :caption: First PINN for :math:`y' = -y`, :math:`y(0) = 1`.
      Top: network solution, exact solution :math:`e^{-x}` and collocation
      points. Bottom: absolute error, on a log scale.

The figure above shows that:

- **the network found the solution without ever seeing it**: only the
  equation and the initial condition are in the loss;
- **the error between the collocation points is about the same as at the
  points themselves**: the network gives a continuous solution that we can
  evaluate and differentiate anywhere in the domain. Finite differences, on the
  other hand, only give values at the nodes.

Observed limits
---------------

- **The initial condition only holds approximately.** It is just one term of
  the loss, competing with the residual: the error at :math:`x = 0` is not
  zero.
- **The solution is only valid on the training domain.** The equation is only
  imposed on :math:`[0, X]`. Beyond that, nothing constrains the network, and
  it has no reason to follow :math:`e^{-x}`: a PINN does not extrapolate.
- **The two terms of the loss have the same weight here.** This arbitrary
  choice changes the balance between the residual and the initial condition.
  Its effect will be studied in dedicated experiments.

.. note:: Key point

   A PINN is an ordinary network whose loss contains the residual of the
   equation and the boundary or initial conditions. Autograd gives the
   derivatives of the network with respect to its input. ``create_graph=True``
   then makes it possible to backpropagate through these derivatives down to
   the weights and biases.
