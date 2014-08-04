INSTALL
#######

For core functionality and tutorials you can simply install via ::

    python setup.py install

or ::

    python setup.py install --user

in order to install without admin rights. Please refer to the
`Manual <http://kmos.readthedocs.org>`_ for further
instructions.


DEPENDENCIES
############

In general this framework has been developed and tested on Ubuntu 9.04-12.04 in
conjunction with both gfortran and ifort. So things will most likely work
best under a similar setup. Other than standard libraries you most likely need to fetch:

*  python-numpy : contains f2py
*  python-lxml
*  python-ase : download https://wiki.fysik.dtu.dk/ase/python-ase-3.9.0.3502.tar.gz, unzip and run ::

    python setup.py install [--user]

*  python-dev

Optional (GUI Editor):

All kMC models can be built, compiled, and executed without
using the GUI editor. However the GUI editor can be
quite useful for spotting logical error in process
definitions as models grow more complex.

    *  python-gtk2: GUI toolkit
    *  python-pygoocanvas
    *  python-kiwi, gazpacho: frameworks for python-gtk
       kiwi is currently available from many repositories
       Unfortunately the development of gazpacho has been
       discontinued. If you are using an apt based distribution
       system you can download the last available package from

       http://packages.debian.org/squezze/all/gazpacho/download

       and install it with ::

         sudo dpkg -i gazpacho_*.deb


TEST INPUT
##########

Running a minimal test case to check whether the installation
was successful includes

    * Change to the examples directory ::

        cd examples

    * Execute the ZGB Model render script ::

        ./render ZGB_model.py

    * Export the Fortran90 source code and compile in one step
      from the generated XML file ::

        kmos export ZGB_model.xml

    * Change to the export directory ::

        cd ZGB_model_local_smart

    * Run benchmark ::

        kmos benchmark


If everything is working you should see
the single-core CPU time to run 1 mio.
steps printed on STDOUT.

GETTING STARTED
###############

Before creating any models of your own you might take look around
the *examples* folder and try playing with the models already
specified there. Instead of `kmos benchmark`, try ::

    kmos view

on an exported model and observe how it behaves for different
conditions.

Create a model XML file as explained in the `Tutorials <http://kmos.readthedocs.org/en/latest/tutorials/index.html>`_ or alternatively  (and optionally) inspect and change it with ::

  kmos edit [<xml-file>]

Both ways will give a XML file that contains the entire
definition of your kMC model. Run ::

  kmos export <xml-file>

and you will find a new folder under the same name with the compiled
model and self-contained source code. Inside that directory run ::

  kmos view

and readily watch your model and manipulate parameters at the same time.

For other ways of running models interactively or scripted please
refer to the `tutorial <http://kmos.readthedocs.org/en/latest/tutorials/index.html#running-the-model-the-api-way>`_
