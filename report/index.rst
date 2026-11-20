FD vs PINN: the Reynolds equation with complementarity
======================================================

:Author: Leonard von Fabeck
:Framework: PRI project
:Tutor: Nans Biboulet

This report compares two ways to solve the Reynolds equation with a
complementarity condition (cavitation, limited oil supply):

- a **finite difference** method (FD), which is the reference;
- a **physics-informed neural network** (PINN).

Before we tackle this problem, the first part builds the tools step by step.
Each tool is tested on a case where we know the exact solution.

.. _sec-demarche:

How the project works
=====================

The goal is to compare two ways to solve the problem of :ref:`sec-equations`.
The first one is a classical method, **finite differences**. It is the
reference. The second one is a **PINN**. We want to find out what it is worth.

The two methods
---------------

**Finite differences (FD).** We cut the domain into evenly spaced points. We
replace each derivative by a difference between neighbouring points. The two
equations :eq:`eq-reynolds-theta` and :eq:`eq-fischer-burmeister` then become
a system of non-linear equations. We solve it with Newton's method. Following
:cite:t:`biboulet2020hdr` (section 3.3.3), we use a single combined unknown
:math:`u = P - \theta`. This works because :math:`P` and :math:`\theta` are
never positive at the same time: :math:`P` is the positive part of :math:`u`,
and :math:`\theta` is its negative part. We get the solution at the grid
points. It gets more accurate when we use more points.

**PINN.** A neural network represents :math:`P` and :math:`\theta`. We put the
equations into the loss, as for the first PINN (:ref:`sec-premiere-edo`): the
residual of :eq:`eq-reynolds-theta`, the residual of
:eq:`eq-fischer-burmeister` and the boundary conditions. We get a continuous
solution, which we can evaluate at any point.

The steps
---------

.. list-table::
   :header-rows: 1
   :widths: 10 45 45

   * - Step
     - Problem
     - Reference for validation
   * - 1
     - Learn to code a PINN on a simple ODE
     -
   * - 2
     - Understand the physical problem
     -
   * - 3
     - 1D Reynolds without cavitation :eq:`eq-reynolds`, imposed boundaries
     - analytical pressure :eq:`eq-pression-analytique`
   * - 4
     - 1D Reynolds, flooded case with cavitation (without :math:`\theta`), FD and PINN
     - analytical solution with the meniscus at the domain inlet
   * - 5
     - 1D Reynolds with complementarity, with finite differences
     - analytical :math:`P`, :math:`\theta`, :math:`X_a`, :math:`X_b`, :math:`W`
   * - 6
     - 1D Reynolds with complementarity, with a PINN
     - same analytical quantities, and the FD solution
   * - 7 (if time allows)
     - 2D Reynolds with complementarity, FD and PINN
     - quasi-analytical 2D solution, and the FD solution

.. toctree::
   :maxdepth: 2
   :numbered:

   premiers_reseaux/index
   probleme_physique/index
   reynolds_sans_cavitation/index
   cas_noye/index
   starved_case/index
   bibliographie
