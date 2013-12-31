INSTALL
#######

For core functionality and tutorials you can simply install via ::

    python setup.py install

or ::

    python setup.py install --user

to install without admin rights. Please refer to the
`user-guide http://kmos.readthedocs.org` for further
instructions.


USAGE
#####

Start the main program with ::

  kmos editor

and create your model or create using IPython and the tutorials in
the documentation. Both ways will give a XML file in the end that
contains the entire definition of your kMC model. Run ::

  kmos export <xml-file>

and you will find a new folder under the same name with the compiled
model and self-contained source code. Inside that directory run ::

  kmos view

and readily watch your model and manipulate parameters at the same time.
