The Concept of Kinetic Monte Carlo
==================================

Why use Kinetic Monte Carlo?
----------------------------

There is a class of systems in nature for which
the spatiotemporal evolution can be described
using a master type of equation. While chemical
reactions at surfaces is one of them, it is not
limited to those.

The master equation imposes that
given a probability distribution :math:`\rho_{i}(t)`
over states, the probability distribution at one
infinitesimal time :math:`\Delta t` later can be
obtained from

.. math::
  \rho_{i}(t+\Delta t) = \rho_{i}(t) + \sum_{j} -k_{ji}\rho_{i}(t)\mathrm{d}t + k_{ij}\rho_j(t)\mathrm{d}t

where the important bit is that each :math:`\rho(t)`
only depends on the state just before the current state.
The matrix :math:`k_{ij}` consists of constant real entries,
which describe the rate at which the system can propagate
from state :math:`j` to state :math:`i`.
In other words the system is without memory which is
usually known as the Markov approximation.

Kinetic Monte Carlo (kMC) integrates this equation
by generating a state-to-state trajectory using a
preset catalog of transitions or elementary steps
and a rate constant for each elementary step. The reason
to generate state-to-state trajectories rather than just
propagating the entire probability distribution at once
is that the transition matrix :math:`k_{ij}` easily becomes
too large for many systems at hand that even storing it
would be too large for any storage device in foreseeable
future.

As a quick estimate consider a system with 100
sites and 3 possible states for each site, thus having
:math:`3^{100}` different configurations. The matrix
to store all transition elements would have
:math:`(3^{100})^2 \approx 2.66\ 10^{95}` entries, which
exceeds the number of atoms on our planet by roughly 45 orders of
magnitude. [1]_ And even though most of these elements
would be zero since the number of accessible states is
usually a lot smaller, there seems to be no simple
way to transform to and solve this irreducible matrix
in the general case.


Thus it is a lot more feasible to take one particular
configuration and figure out the next process as
well as the time it takes to get there and obtain
ensemble averages from time averages taken over
a sufficiently long trajectory. The basic steps can
be described as follows

Basic Kinetic Carlo Algorithm
-----------------------------

  - Fix rate constants :math:`k_{ij}`
     initial state :math:`x_{i}`, and
     initial time :math:`t`

  - while :math:`t < t_{\mathrm{max}}` do

      #. draw random numbers :math:`R_{1}, R_{2} \in ]0,1]`

      #. find :math:`l` such that
         :math:`\sum_{j=1}^{l}k_{i,\mathrm{tot}}R_{1}\le\sum_{j_1}^{l+1}k_{ij}`

      #. increment time :math:`t\rightarrow t - \frac{\ln(R_{2})}{k_{i, \mathrm{tot}}}`

    end


Justification of the Algorithm
------------------------------

Let's understand why this simulates a physical process.
The Markov approximation mentioned above implies several things:
not only does it mean one can determine the next process from
the current state. It also implies that all processes happen
independently of one another because any memory of the system
is erased after each step. Another great simplification is
that rate constants simply add to a total rate, which is
sometimes referred to as
`Matthiessen's rule
<http://en.wikipedia.org/wiki/Matthiessen%27s_rule#Matthiessen.27s_rule>`_,
*viz* the rate with which *any* process occurs is simply
:math:`\sum_{i}k_{i}`.

First, one can show that the probability that :math:`n` such processes
occur in a time interval :math:`t` is given by a Poisson distribution [2]_

.. math::

  P(n, t) = \frac{\mathrm{e}^{-k_{\mathrm{tot}}t}(k_{\mathrm{tot}} t)^{n}}
                 {n!} .


The waiting time or escape time :math:`t_{w}` between two such processes
is characterized by the probability that *zero* such processes have occured

.. math::
  :label: poisson_0

  P(0, t_{w}) = \mathrm{e}^{-k_{\mathrm{tot}} t_{w}},

which, as expected, leads to an average waiting time of

.. math::

  \langle t_{w} \rangle = \frac{\int_{0}^{\infty}\mathrm{d}t_w\ t_w \mathrm{e}^{-k_{\mathrm{tot}} t_w}}
                               {\int_{0}^{\infty}\mathrm{d}t_w\ \mathrm{e}^{-k_{\mathrm{tot}} t_w}}
                        = \frac{1}{k_{\mathrm{tot}}}.

Therefore at  every step, we need to advance the time by a random number that
is distributed according to :eq:`poisson_0`. One can obtain such a random
number from a uniformly distributed random number :math:`R_2\in ]0,1]`
via :math:`-\ln(R_{2})/k_{\mathrm{tot}}`. [3]_

Second, we need to select the next process. The next process occurs randomly
but if we did this a very large number of times for the same initial state
the number  of times each process is chosen should be proportional to its
rate constant. Experimentally one could achieve this by randomly sprinkling
sand over an arrangement of buckets, where the size of the bucket is
proportional to the rate constant and count each hit by a grain of sand in a
bucket as one executed process. Computationally the same is achieved by
steps 2 and 3.



Further Reading
---------------

For a very practical introduction I recommend Arthur Voter's tutorial [4]_
and Fichthorn [5]_ for a derivation, why :math:`\Delta t` is chosen they
way it is. The example given there is also an excellent exercise for
any beginning kMC modeler.  For recent review on implementation techniques
I recommend the review by Reese et al. [6]_ and for a review over status
and outlook I recommend the one by Reuter [7]_ .


.. [1] Wolfram Alpha's
       `estimate <http://www.wolframalpha.com/input/?i=estimated+number+of+atoms+in+the+Earth>`_ for number of atoms on earth.

.. [2] C. Gardiner, 2004.
       *Handbook of Stochastic Methods: for Physics, Chemistry,
       and the Natural Sciences*. Springer, 3rd edition, ISBN:3540208828.

.. [3] P. W. H, T. S. A, V. W. T, and F. B. P, 2007
       *Numerical Recipes 3rd Edition: The Art of Scientific Computing*.
       Cambridge University Pres, 3rd edition, ISBN:0521768589, p. 287.
       `link <http://apps.nrbook.com/c/index.html>`_

.. [4] Voter, Arthur F. “Introduction to the Kinetic Monte Carlo Method.” In Radiation Effects in Solids, 1–23, 2007. http://dx.doi.org/10.1007/978-1-4020-5295-8_1.
       `link <http://www.ipam.ucla.edu/publications/matut/matut_5898_preprint.pdf>`_

.. [5] Fichthorn, Kristen A., and W. H. Weinberg. “Theoretical Foundations of Dynamical Monte Carlo Simulations.” The Journal of Chemical Physics 95, no. 2 (July 15, 1991): 1090–1096.
       `link <http://jcp.aip.org/resource/1/jcpsa6/v95/i2/p1090_s1>`_

.. [6] Reese, J. S., S. Raimondeau, and D. G. Vlachos. “Monte Carlo Algorithms for Complex Surface Reaction Mechanisms: Efficiency and Accuracy.” Journal of Computational Physics 173, no. 1 (October 10, 2001): 302–321.
       `link <http://dx.doi.org/10.1006/jcph.2001.6877>`_

.. [7] Reuter, Karsten. “First-principles Kinetic Monte Carlo Simulations for Heterogeneous Catalysis: Concepts, Status and Frontiers”. Wiley-VCH, 2009.
       `link <http://www.fhi-berlin.mpg.de/th/publications/wiley_reuter.pdf>`_
