First neural networks
=====================

A PINN is a neural network trained to satisfy a differential equation. To
build one, we need three building blocks:

1. **take the derivative of the network output with respect to its input**:
   this is the job of PyTorch's automatic differentiation (autograd);
2. **train a network**, that is, adjust its weights :math:`w` and its biases
   :math:`b` to make a loss as small as possible;
3. **write a loss that contains the equation** instead of the solution.

This chapter covers these three blocks in order. Each one is tested on a
simple case whose exact solution is known, so we can check every result.

All calculations use double precision (``float64``). These problems are tiny,
so the extra cost is negligible. The rounding error (about :math:`10^{-16}` in
relative terms, against :math:`10^{-7}` in single precision) then does not mix
with the errors we want to measure. The random draws (initial weights) start
from a fixed ``Seed``, so every result can be reproduced.

.. toctree::
   :maxdepth: 2

   autograd
   ajustement_sinus
   premiere_edo
