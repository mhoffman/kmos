The otf Backend
===============

  NOTICE: The otf backend is still on an EXPERIMENTAL state and not
  ready for production.


As described in ":ref:`o1-backend`" the
default kmos backends (local_smart and
lat_int) produce code which executes in time O(1) with the system size
(total number of sites in the lattice). This is achieved through some
book-keeping overhead, in particular storing every rate constant
beforehand in an array. For some particular class of problems,
*i.e.* those in which extended lateral interactions are taken into
account. This implies that some elementary processes need to be
included multiple times in the model definition (to account for the
effect of the surrounding lattice configuration on the rate constants).
Depending on the amount of sites taken in account and the number of
different species that participate, the number of repetitions can
easily reach several thousands or more. This leads to two undesired
effects: First the amount of memory required by the book-keeping
structures (which is proportional to the number of processes) could
quickly be larger than your system has available. Second, the kmos
algorithm is O(1) in system size, but O(N) in number of processes,
which eventually leads to a slow down for more complex systems.

The otf backend was developed with these setbacks in mind. otf stands
for On The Fly, because rate constants of processes affected by
lateral interactions are calculated at runtime, according to user
specifications.

  NOTE: Up to now only a limited type of lateral interactions are
  supported at the moment, but the developement of additional ones
  should be easy within the framework of the otf backend.

In this new backend, kmos is not able to generate O(1) code in the
system size, but now each process corresponds to a full group of
processes from the traditional backends. For this reason, the otf
bakend is been built to deal with simulations in which
multisite/multispecies lateral interactions are included and in which
the system size is not too large.

  TODO: Put numbers to when_to_use_otf(volume, nr_of_procs)

Reference
^^^^^^^^^

Here we will detail how to set up a kmc model for the otf kmos
backend. It will be assumed that the reader is familiar with
Tutorial ":ref:`api-tutorial`" and focus will be in the differences between the
traditional backends (local_smart and lat_int) and otf.  Most of the model
elements (Project, ConditionAction, Species, Parameter) work exactly
the same in the new backend.

The Process object, is the one whose usage is most distinct, as
it can take two otf-backend exclusive attributes:
  - otf_rate: Reperesent the expression to be used to calculate the
    rate of the process at runtime. It is parsed similarly to the
    'rate_constant' attribute and likewise can contain all the user
    defined parameters, as well as all constant and chemical
    potentials know to kmos. Additionally, special keywords (namely
    base_rate and nr_<species>_<flag>) also have an special
    meaning. This is described below.
  - bystander_list: A list objects from the Bystander class (described
    below) to represent the sites which do not participate in the
    reaction but which affect the rate constant.

Additionally, the meaning of the 'rate_constant' attribute is
modified. This expression now represents the rate constant in the
'default' configuration around the process. What this default
configuration means is up to the user, but it will normaly be the rate
at the zero coverage limit (ZCL).

Additionally a new model description element, the Bystander, has been
introduced. It has the attributies
 - coord: Represents a coordinate relative to the coordinates in the
   process.
 - allowed_species: This is a list of species, which can affect
   the rate constant of the process when they sit in 'coord'
 - flag: This is a short string that works a descriptor of the
   bystander. It is useful when defining the otf_rate of the process
   to which the bystander is associated.

The rate constant to be calculated at runtime for each Process is
given by the expression in 'otf_rate'. Appart from all standard
parameters, kmos also parses the strings
 - 'base_rate': Which is evaluated to the value of the 'rate_constant'
   attribute
     NOTE: For now, the 'base_rate' expression is **required**.
 - Any number of expressions of the form 'nr_<species>_<flag>'. Where
   <species> is to be replaced by any of the species defined in the
   model and <flag> is to be replaced by one of the flags given to the
   bystanders of this process.

During export, kmos will write routines that look at the occupation of
each of the bystanders at runtime and count the total number of each
species within 'allowed_species' for each bystander type (flag).

Example
^^^^^^^
For this we will write down an alternative to the
render_pairwise_interaction.py example file. Most of the script can be
left as is. From the import statements, we can delete the line that
imports itertools, as we won't be needing it. From then on, up to the point where we have
defined all process not affected by lateral interactions, we do not
need any changes.
We also need to collect a set of all interacting coordinates which
will affect CO desorption rate::
  # fetch a lot of coordinates
  coords = pt.lattice.generate_coord_set(size=[2, 2, 2],
                                         layer_name='simplecubic_2d')
  # fetch all nearest neighbor coordinates
  nn_coords = [nn_coord for i, nn_coord in enumerate(coords)
               if 0 < (np.linalg.norm(nn_coord.pos - center.pos)) <= A]

as with traditional backends. With the otf backend however, we do not need
to account for all possible combinations (and thus we do not need
the itertools module). In this case, desorption only has one condition
and one action::
  conditions = [Condition(species='CO',coord=center)]
  actions = [Action(species='empty',cood=center)]

And we use the coordinates we picked to generate some bystanders::

  bystander_list = [Bystander(coord=coord,
                            allowed_species=['CO',],
                            flag='1nn') for coord in nn_coords]

As we are only considering the CO-CO interaction, we only include it in
the allowed_species, but we could easily have included more species. Now,
we need to describe the expresions to calculate the rate constant at runtime.
In the original script, the rate is given by::
  rate_constant = 'p_COgas*A*bar/sqrt(2*m_CO*umass/beta)'/
                  '*exp(beta*(E_CO+%s*E_CO_nn-mu_COgas)*eV)' % N_CO

where the N_CO is calculated beforehand (in the model building step) for
each of the individual lattice configurations. For the otf backend, we
define the 'base' rate constant as the rate at ZCL (N_CO = 0), that is::
  rate_constant = 'p_COgas*A*bar/sqrt(2*m_CO*umass/beta)'/
                  '*exp(beta*(E_CO-mu_COgas)*eV)'

Finally, we must provide the expression given to calculate the rate
given the amount of CO around in our bystanders. For this we simply
define::
  otf_rate = 'base_rate*exp(beta*nr_CO_1nn*E_CO_nn*eV)'

All of this comes together in the process definition::

  proc = Process(name='CO_desorption',
                 conditions=conditions,
		 actions=actions,
		 bystander_list = bystander_list,
		 rate_constant=rate_constant,
		 otf_rate=otf_rate)
  pt.add_process(proc)

Advanced OTF rate expressions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In the example above, the otf_rate variable for the processes included only a single
expression that defined the rate taking into account the values of the ``nr_<species>_<flag>``
variables. For more complex lateral interaction models, this can become cumbersome.
Alternatively, users can define otf_rate expressions that span several expressions/lines.
Lets assume we are dealing with a model similar to the one above, but now include an additional
species, O, and the corresponding lateral interaction energy ``E_CO_O`` between these two.
Similarly to the previous example, the rate would be given by::
  rate_constant = 'p_COgas*A*bar/sqrt(2*m_CO*umass/beta)'/
                  '*exp(beta*(E_CO+%s*E_CO_nn+%s*E_CO_O-mu_COgas)*eV)' % (N_CO,N_O)

where ``N_O`` is the number of nearest-neighbour O. This rate expresion is still fairly simple and the
previously described methdod would work by doing::
  otf_rate = 'base_rate*exp(beta*(nr_CO_1nn*E_CO_nn+nr_O_1nn*E_CO_O)*eV)'

However, equivalently (and maybe more easy to read) we could define::

  otf_rate = 'Vint = nr_CO_1nn*E_CO_nn+nr_O_1nn*E_CO_O\\n'
  otf_rate += 'otf_rate = base_rate*exp(beta*Vint*eV)'

in which we have defined an auxiliary variable ``Vint``. Behind the scenes, these lines are included
in the source code automatically generated by kmos. Notice the inclusion of explicit ``\\n`` characters.
This is necessary because we want the line breaks to be explicitely stored as ``\n`` in the .xml file for export
(spaces are ignored by the xml export engine). Since these expression are ultimately compiled
as Fortran90 code, variable names are not case sensitive (i.e. ``A = ...`` and ``a = ...`` declare
the same variable).

Additionaly, when we want to include more than one line of code in otf_rate, we additionally need to include a line that states ``otf_rate = ...`` in order for kmos
to know how to calculate the returned rate.

Running otf-kmos models
^^^^^^^^^^^^^^^^^^^

Once the otf model has been defined, the model can be run in a fashion very similar to the default kmos backends most of the differences arise from the

.. todo:: The rest of this sentence seems to have gotten lost somehow.


Known Issues
^^^^^^^^^^^^
#. Non-optimal updates to rates_matrix.
       The current implementation of the backend is still non-optimal and
       can lead to considerable decrease in speed for larger systems sizes
       (scaling ``O(N_sites)``). This will be improved (``O(log(N_sites))``) once
       more tests are conducted.

#. Process name length limit
       f2py will crash during compilation if a process has a name lager
       than approx. 20 characters.
