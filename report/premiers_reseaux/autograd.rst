.. _sec-autograd:

Taking derivatives with autograd
================================

Why do we need it?
------------------

The equation of a PINN contains derivatives of the unknown, for example
:math:`y'(x)`. If a neural network :math:`y(x; w, b)` represents the unknown,
we must be able to compute :math:`\partial y / \partial x`. This is the
derivative of the network **output** with respect to its **input**. We often
need the second derivative too.

There are three ways to compute a derivative on a computer:

- **by hand**: we take the derivative of the formula on paper, then we code
  the result. It is exact, but impossible in practice for a network with
  thousands of parameters;
- **with finite differences**: we approximate the derivative by a rate of
  change, for example :math:`y'(x) \approx \frac{y(x+h) - y(x-h)}{2h}`. It is
  simple, but approximate: the error depends on the step :math:`h`;
- **with automatic differentiation**: the computer itself applies the chain
  rule to the elementary operations of the calculation. The result is exact,
  up to rounding errors.

PyTorch provides the third method under the name *autograd*
:cite:p:`pytorch_autograd_mechanics`.

The idea: a computational graph
-------------------------------

A natural question comes up. When we call ``torch.autograd.grad(y, x)``, we
seem to give only values: the points ``x`` and the function values ``y``. How
can PyTorch compute an **exact** derivative without knowing the function?
Finite differences, on the other hand, must compare neighbouring points.

The answer: ``y`` is not just an array of numbers. It is a tensor that
**carries the full history of the calculation** that produced it. So PyTorch
does know the function: it knows the exact sequence of elementary operations
applied to ``x``.

Step 1: record the calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We ask PyTorch to track a tensor ``x`` (``x.requires_grad_(True)``). From then
on, every operation that starts from ``x`` is **recorded** at the moment it is
computed. For :math:`f(x) = x^2 \sin x`, PyTorch splits the calculation into
three elementary operations:

.. math::

   a = x^2, \qquad b = \sin x, \qquad y = a \cdot b .

Each result keeps, in its attribute ``grad_fn``, a reference to the operation
that produced it. Each operation keeps a reference to its inputs. This gives a
**computational graph** (as seen in class this semester), attached to the
result ``y``:

.. code-block:: text

          x  (requires_grad=True)
         / \
    a = x²   b = sin x        PowBackward0, SinBackward0
         \ /
       y = a · b              MulBackward0   <- y.grad_fn

We can look at it directly:

.. code-block:: python

   x = torch.tensor([2.0], dtype=torch.float64, requires_grad=True)
   y = x**2 * torch.sin(x)

   print(y)                         # tensor([3.6372], grad_fn=<MulBackward0>)
   print(y.grad_fn.next_functions)  # ((<PowBackward0>, 0), (<SinBackward0>, 0))

Besides the graph, PyTorch **stores the intermediate values** it will need to
take the derivative: here :math:`x`, :math:`a` and :math:`b` at the chosen
point.

Step 2: walk back through the graph (like the example in class)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each type of elementary operation, PyTorch has a **derivative rule written
once and for all**: the derivative of :math:`\sin` is :math:`\cos`, the
derivative of :math:`u \mapsto u^2` is :math:`2u`, the derivative of a product
:math:`a \cdot b` is :math:`b` with respect to :math:`a` and :math:`a` with
respect to :math:`b`, and so on.

``torch.autograd.grad(y, x)`` starts from ``y`` and follows the ``grad_fn``
back to ``x``. At each step, it applies the rule of the operation it meets,
evaluated with the stored values. The **chain rule** combines the
contributions:

.. math::
   :label: eq-chaine

   \frac{\mathrm{d}y}{\mathrm{d}x}
   = \frac{\partial y}{\partial a}\,\frac{\mathrm{d}a}{\mathrm{d}x}
   + \frac{\partial y}{\partial b}\,\frac{\mathrm{d}b}{\mathrm{d}x}
   = b \cdot 2x + a \cdot \cos x .

At the point :math:`x = 2`, with the stored values :math:`a = 4` and
:math:`b = \sin 2 \approx 0.9093`:

.. math::

   \frac{\mathrm{d}y}{\mathrm{d}x}(2)
   = 0.9093 \times 4 + 4 \times \cos 2
   \approx 3.6372 - 1.6646
   = 1.9726 .

This is exactly the value of the formula
:math:`f'(x) = 2x \sin x + x^2 \cos x` at :math:`x = 2`. It is also what
``torch.autograd.grad`` returns.

Key points
~~~~~~~~~~

- **Autograd never looks at neighbouring points.** Each derivative is computed
  at the point :math:`x_i` itself, from the exact formulas of the elementary
  operations. This is the key difference with finite differences, which
  compare :math:`f(x+h)` and :math:`f(x-h)`.
- **The result is exact**, up to rounding errors. It is the same calculation
  as by hand, but automated. It works for functions as complicated as we like
  (a neural network is just a long sequence of elementary operations).
- **It is not symbolic computation.** PyTorch does not produce the formula
  :math:`2x \sin x + x^2 \cos x`, only its **value** at the requested points.
- **No history, no derivative.** A tensor with the same numbers, but created
  without going through ``x``, has no ``grad_fn``. Autograd cannot do anything
  with it.

  .. code-block:: python

     y_without_graph = torch.tensor([3.6372], dtype=torch.float64)
     torch.autograd.grad(y_without_graph.sum(), x)
     # RuntimeError: element 0 of tensors does not require grad
     #               and does not have a grad_fn

  This is also what ``x.detach()`` (a copy of ``x`` cut off from the graph)
  and the block ``with torch.no_grad():`` (no operation inside the block is
  recorded) do on purpose.

In the project code
~~~~~~~~~~~~~~~~~~~

Two details of the function used in this project:

.. literalinclude:: /../src/pinn/autograd_derivatives.py
   :pyobject: autograd_first_and_second_derivative

The options of ``torch.autograd.grad`` are described in its documentation
:cite:p:`pytorch_autograd_grad`.

- **The sum** ``function_values.sum()``: ``autograd.grad`` differentiates a
  scalar. We sum the values :math:`f(x_1) + \dots + f(x_n)`. The derivative of
  this sum with respect to :math:`x_i` is exactly :math:`f'(x_i)`, because each
  term only depends on its own point. So we get all the derivatives in a
  single call.
- **The option** ``create_graph=True``: by default, PyTorch deletes the graph
  after walking back through it. With this option, the calculation of the
  derivative is itself recorded. So we can take its derivative again to get
  :math:`f''`. This is essential for PINNs (see :ref:`sec-premiere-edo`).

Check on a known function
-------------------------

We compare the three methods on

.. math::
   :label: eq-fonction-test

   f(x) = x^2 \sin x,

whose derivatives, computed by hand, are

.. math::
   :label: eq-derivees-test

   f'(x) = 2x \sin x + x^2 \cos x,
   \qquad
   f''(x) = (2 - x^2) \sin x + 4x \cos x.

We compare them at many points spread over an interval, and keep the largest
gap between the methods. The script ``src/pinn/autograd_derivatives.py``
prints these gaps. The test ``tests/test_autograd_derivatives.py`` checks
automatically that the formulas :eq:`eq-derivees-test` and autograd agree to
within :math:`10^{-12}`.

What we observe:

- **Hand and autograd agree to machine rounding**, for :math:`f'` and for
  :math:`f''`. This is expected: both methods are exact, only the order of the
  operations differs.
- **Finite differences are much further off.** With a step :math:`h`, the
  centred scheme has a truncation error of order :math:`O(h^2)`. For the second
  derivative, there is also a rounding error of order
  :math:`O(\varepsilon / h^2)`, where :math:`\varepsilon` is the machine
  precision. So making :math:`h` smaller does not improve the result forever.

.. note:: Key point

   Autograd gives **exact** derivatives (up to rounding) of the function that
   is actually computed, however complex it is. This is what makes PINNs
   possible: we can take the derivative of a neural network with respect to
   its input as easily as for a formula.

In what follows, the finite differences are evaluated inside a
``with torch.no_grad():`` block, which turns off the recording of the graph.
Finite differences do not use autograd, so building a graph would be useless
(and costly). It also guarantees that this check does not depend on autograd.
