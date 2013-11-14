Modelling Workflows
===================

At the core of modelling lies the art to capture
the most important features of a system and leave
all others out. kmos is designed around the fact
that modelling is a creative and iterative process.

A typical type of approach for modelling could be:

#. start with educated guess
#. calculate outcome
#. compare various observables and qualitative
   behavior with reference system
#. adapt model, goto 2. or publish model

So while this procedure is quite generic it may help
to illustrate that the chances to find and capture
the relevant features of a system are enhanced
if the trial/learn loop is as short as possible.


kMC Modeling
^^^^^^^^^^^^^

A good way to define a model is to use a paper and pencil to draw
your lattice, choose the species that you will need, draw
each process and write down an expression for each rate constant, and
finally fix all energy barriers and external parameters that you will need.
Putting a model prepared like this into a computer is a simple exercise.
You enter a new model by filling in

    * meta information
    * lattice
    * species
    * parameters
    * processes

in roughly this order or open an existing one by opening a kMC XML file.

If you want to see the model run
`kmos export <xml-file>` and you will get a subfolder with a self-contained
Fortran90 code, which solves the model. If all necessary dependencies are
installed you can simply run `kmos view` in the export folder.



kmos workflows
^^^^^^^^^^^^^^

Since `kmos` has several entry points, there are several ways of using it.
This section will outline different ways of using kmos:

- *the render script*

  Just write complete scripts as outlined in
  :doc:`../tutorials/first_model_api`. Export
  source from there or inspect XML file with one
  of the next methods below.

- *the GUI editor*

  Open an existing project \*.xml file with ::

    kmos edit <project_name>.xml

  and inspect or edit it through on screen

- *the CLI editor*

  Open an existing project \*.xml file with ::

    kmos import <project_name>.xml

  and edit the project interactively on the ipython console.

- *edit the XML file*

  Just open the XML file of your kmos project with a text
  editor of your choice and inspect or your model right
  there. This might only be a last resort to figure out
  what is going on. XML is often not considered very
  readable and note that changing variable names in
  one place might often break inconsistencies in other.
