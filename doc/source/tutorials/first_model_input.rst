A first kMC Model--with input files
===================================

One way to define kMC models is using an input file. The general format is identical to the quite common ini-files, however as we will
see below one can seamlessly embed python code here as well to use
more high-level constructs. But first things first.


Construct the model
^^^^^^^^^^^^^^^^^^^


The example sketched out here leads you to a kMC model for CO adsorption
and desorption on Pd(100) including a simple lateral interaction. Granted
this hardly excites surface scientists but we need to start somewhere, right?


The following source code should be written into a text file using the editor of your choice. Use `.ini` as the suffix such as `myfirst_kmc.ini`. Start by filling out the meta information ::

    [Meta]
    author = 'Your name'
    email = 'your.name@server.com'
    model_name = 'MyFirstModel'
    model_dimension = 2

The important bit to notice here is that one uses the correct section names (e.g. `[Meta]`) and capitalization counts. Next we will add some species. Each species has its own section of the form `[Species <species_name>]` where `<species_name>` is just a place holder. Not the space between `Species` and the name and the name shouldn't contain any spaces and follow the same rules as variables names. That is consisting only of letter and numbers or underscore (_) ::

    [Species empty]

    [Species CO]
    representation = Atoms('CO',[[0,0,0],[0,0,1.2]])

where the string passed as `representation` is a string representing
a CO molecule which can be evaluated in `ASE namespace <https://wiki.fysik.dtu.dk/ase/ase/atoms.html>`_.

Once you have all species declared is a good time to think about the geometry.
To keep it simple we will stick with a simple-cubic lattice in 2D which
could for example represent the (100) surface of a fcc crystal with only
one adsorption site per unit cell. You start by giving your layer a name ::

    [Layer simple_cubic]
    site hollow = (0.5, 0.5, 0.5)

Here we readily added a site named `'hollow` at the center of each unit cell.


Simple, huh? Now you wonder where all the rest of the geometry went?
For a simple reason: the geometric location of a site is
meaningless from a kMC point of view. In order to solve the master
equation none of the numerical coordinates
of any lattice sites matter since the master equation is only
defined in terms of states and transition between these. However
to allow a graphical representation of the simulation one can add geometry
as you have already done for the site. You set the size of the unit cell
via ::

  [Lattice]
  cell_size = 3.5 3.5 10

which are prototypical dimensions for a single-crystal surface in
Angstrom.

Ok, let us see what we managed so far: you have a *lattice* with a
*site* that can be either *empty* or occupied with *CO*.


Populate process list and parameter list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The remaining work is to populate the `process list` and the
`parameter list`. The parameter list defines the parameters
that can be used in the expressions of the rate constants.
In principle one could do without the parameter
list and simply hard code all parameters in the process list,
however one looses some nifty functionality like easily
changing parameters on-the-fly or even interactively.

A second benefit is that you achieve a clear separation
of the kinetic model from the barrier input,
which usually has a different origin.

In practice filling the parameter list and the process
list is often an iterative process, however since
we have a fairly short list, we can try to set all parameters
at once.

First of all you want to define the external parameters to
which our model is coupled. Here we use the temperature
and the CO partial pressure ::

    [Parameter T]
    value = 600
    adjustable = True
    min = 400
    max = 600


and ::

    [Parameter p_CO]
    value = 1
    adjustable = True
    min = 1e-10
    max = 1e2

You can also set a default value and a minimum and maximum value
set defines how the scrollbars a behave later in the runtime GUI.

To describe the adsorption rate constant you will need the area
of the unit cell::

  [Parameter A]
  value = (3.5*angstrom)**2


Last but not least you need a binding energy of the particle on
the surface. Since without further ado we have no value for the
gas phase chemical potential, we'll just call it deltaG and keep
it adjustable ::

  [Parameter deltaG]
  value = -0.5
  adjustable = True
  min = -1.3
  max = 0.3


Then you need to have at least two processes. A process or elementary step in kMC means that a certain local configuration must be given so that something can happen at a certain rate constant. In the framework here this is phrased in terms of 'conditions' and 'actions'. [#proc_minilanguage]_
So for example an adsorption requires at least one site to be empty
(condition). Then this site can be occupied by CO (action) with a
rate constant. Written down in code this looks as follows ::

    [Process CO_adsorption]
    rate_constant = p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)
    conditions = empty@hollow
    actions = CO@hollow

Now you might wonder, how come we can simply use m_CO and beta and such.
Well, that is because the evaluator will to some trickery to resolve such
terms. So beta will be first be translated into 1/(kboltzmann*T) and as
long as you have set a parameter `T` before, this will go through. Same
is true for m_CO, here the atomic masses are looked up and added. Note
that we need conversion factors of bar and umass.

Then the desorption process is almost the same, except the reverse::

    [Process CO_desorption]
    rate_constant = p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)*exp(beta*deltaG*eV)
    conditions = CO@hollow
    actions = empty@hollow


Finally save the file and run from the same directory ::

    kmos export myfrist_kmc.ini


If you now `cd` to that folder `myfirst_kmc` and run::

  kmos view

... and dada! Your first running kMC model right there!


If you wonder why the CO molecules are basically just dangling
there in mid-air that is because you have no background setup, yet.
Choose a transition metal of your choice and add it to the
lattice setup for extra credit :-).

Wondering where to go from here? If the work-flow makes
complete sense, you have a specific model in mind,
and just need some more idioms to implement it
I suggest you take a look at the `examples folder <https://github.com/mhoffman/kmos/tree/master/examples>`_.
for some hints. To learn more about the kmos approach
and methods you should into :ref:`topic guides <topic-guides>`.

Embedding python code [EXPERIMENTAL]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you start writing bigger model with sophisticated interaction writing down all processes in this .ini-format might be less than ideal. Therefore can understand embedded python code if you follow the following 2 rules: start every line containing python code with a `#%` (with a space after the `%`) and every variable in the .ini-parts that should be replaced by its python value in the current scope has to be placed in curly brackets {}. The latter is needed so that it gets interpolated by the str.format() function. To give you a simple example, let's add adsorption process for a lot of different species ::

    #@ for species in ['A', 'B', 'C', 'D']:
        [Process Adsorption_{species}]
        rate_constant = 100
        conditions = empty@hollow
        actions {species}@hollow

Of cource withespace matters here. To keep it simple avoid whitespace before the `#@` and indent the .ini-parts as if they were python code (counting whitespace from the `#` for the `#@` marker.


Taking it home
^^^^^^^^^^^^^^^

Despite its simplicity you have now seen all elements needed
to implement a kMC model and hopefully gotten a first feeling for
the workflow.



.. [#proc_minilanguage]  You will have to describe all processes
                         in terms of  `conditions` and
                         `actions` and you find a more complete
                         description in the
                         :ref:`topic guide <proc_mini_language>`
                         to the process description syntax.

.. [#coord_minilanguage] The description of coordinates follows
                         the simple syntax of the coordinate
                         syntax and the
                         :ref:`topic guide <coord_mini_language>`
                         explains how that works.
