.. _sec-ajustement-sinus:

Training a network: fitting sin(x)
==================================

The problem
-----------

Before we solve an equation, we learn to train a network on the simplest
possible task: approximate a known function, :math:`\sin x` on
:math:`[-\pi, \pi]`, from a few of its values. We have :math:`N` evenly spaced
training points :math:`(x_i, \sin x_i)`. We look for a network
:math:`y(x; w, b)` that passes as close as possible to these points.

This is **supervised learning**: we give the answer to the network, at the
points :math:`x_i`.

The network
-----------

We use an **MLP** (*Multi-Layer Perceptron*), the simplest kind of neural
network. The input goes through a sequence of layers. Each layer passes its
result to the next one, with no loop and no going back. The layers between the
input and the output are called **hidden layers**. Each layer of an MLP has two
steps:

- a **linear layer** computes :math:`w\,x + b`. The weights :math:`w` and the
  biases :math:`b` are the parameters to learn;
- an **activation function** (here :math:`\tanh`) is applied to each neuron.
  It has no parameter, but it is essential: without it, a stack of linear
  layers is still a linear function.

The network we use has a single hidden layer with :math:`H` neurons:

.. math::
   :label: eq-reseau-une-couche

   y(x; w, b) = \sum_{k=1}^{H} w_{2,k} \tanh\!\left(w_{1,k}\, x + b_{1,k}\right) + b_2 .

In theory, a single hidden layer is enough to approximate any continuous
function on a bounded interval, as long as there are enough neurons. This is
the universal approximation theorem (see :cite:t:`nielsen2015neural`,
chapter 4, for a visual proof).

.. literalinclude:: /../src/pinn/fit_sine_mlp.py
   :pyobject: make_network

The layers ``nn.Linear`` and ``nn.Tanh`` and the container ``nn.Sequential``
come from the ``torch.nn`` module :cite:p:`pytorch_nn`.

The loss
--------

We measure the gap between the network and the data with the **mean squared
error**:

.. math::
   :label: eq-perte-supervisee

   \mathcal{L}(w, b) = \frac{1}{N} \sum_{i=1}^{N}
   \left( y(x_i; w, b) - \sin x_i \right)^2 .

Training the network means finding the :math:`w` and :math:`b` that make
:math:`\mathcal{L}` as small as possible.

.. literalinclude:: /../src/pinn/fit_sine_mlp.py
   :pyobject: mean_squared_error_loss

Training
--------

We minimise :math:`\mathcal{L}` with a gradient descent method. At each
iteration, we compute the gradient of the loss with respect to all the
parameters, :math:`\partial \mathcal{L} / \partial w` and
:math:`\partial \mathcal{L} / \partial b`. Then we move the parameters in the
direction that makes the loss smaller. Autograd computes the gradient
(:ref:`sec-autograd`), this time with respect to the parameters and not with
respect to :math:`x`.

We use the **Adam** optimiser :cite:p:`pytorch_adam`. It is a variant of
gradient descent that adapts the step size for each parameter automatically.
One iteration (one *epoch*) always has the same four steps:

.. literalinclude:: /../src/pinn/fit_sine_mlp.py
   :pyobject: train

1. ``optimizer.zero_grad()`` sets the gradients back to zero. This is needed
   because ``backward()`` **adds** the new gradient to the one already stored.
   Without this reset, we would use the sum of all past gradients, computed
   with old parameters.
2. We compute the loss with the current parameters.
3. ``loss.backward()`` computes the gradient of the loss with respect to all
   the :math:`w` and :math:`b`.
4. ``optimizer.step()`` updates the parameters.

Results
-------

.. plot:: ../figures/fit_sine_mlp.py
   :caption: Fitting :math:`\sin x` with the one-hidden-layer network.
      Top: training data, network and exact function.
      Bottom: absolute error between the network and :math:`\sin x`, on a
      log scale.

The figure above answers two questions:

- **Has the network learned the function between the points?** The error is
  evaluated at many more points than the training points. It drops to zero
  wherever the network crosses the exact function. With **little data**, these
  dips match the training points: the network goes through the data, and the
  error sits **between** them, where the network received no information. With
  **a lot of data**, the error is about the same everywhere, and the dips are
  just crossings with no special meaning.
- **Where is the approximation worst?** The error is often larger near the
  ends of the interval. A point at the edge only has data on one side, so the
  approximation is less constrained there.

So the amount of data is an important setting in supervised learning. In a
PINN, the equivalent is the number of collocation points
(:ref:`sec-premiere-edo`).

.. note:: Key point

   Training a network means minimising a loss with respect to its weights and
   biases. Here the loss compares the network with **known values** of the
   solution. The next section replaces these values with the **equation**.
