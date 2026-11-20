The physical problem
====================

.. important:: Where the content comes from

   The scientific content of this chapter (physical model, equations,
   dimensionless form, formulation with complementarity, 1D analytical
   solution) comes entirely from the habilitation thesis of Nans Biboulet
   :cite:p:`biboulet2020hdr`. This chapter adds nothing new: it rewrites this
   work to make it easier to understand.

This chapter describes the problem the project wants to solve. It assumes no
prior knowledge of lubrication. It answers four questions:

1. **What are we talking about?** A lubricated contact, where a very thin oil
   film separates two moving surfaces, and what happens when oil runs short
   (:ref:`sec-contact-lubrifie`).
2. **Which equations must we solve?** The Reynolds equation, plus a
   complementarity condition that describes cavitation (:ref:`sec-equations`).
3. **Is there an exact solution to check the calculations?** Yes, in 1D. It
   will be the reference to validate both methods
   (:ref:`sec-solution-analytique`).
4. **What will the project do?** Solve this problem with finite differences
   and with a PINN, then compare the two methods (:ref:`sec-demarche`).

All the equations of this chapter come from :cite:t:`biboulet2020hdr`
(section 2.2.1 for the 1D analytical solution, section 3.3.3 for the
formulation with complementarity, appendix A for the dimensional quantities).

.. toctree::
   :maxdepth: 2

   contact_lubrifie
   equations
   solution_analytique
