INSTALL
#######

For core functionality and tutorials you can simply install via ::

    python setup.py install

or ::

    python setup.py install --user

to install without admin rights. Please refer to the
`user-guide http://kmos.readthedocs.org` for further
instructions.


DEPENDENCIES
############

In general this script has been developed and tested on Ubuntu 9.04-12.04 in
conjunction with both gfortran and ifort. So things will most likely work
best under a similar setup. Other than standard libraries you need to fetch:

*  python-numpy : contains f2py
*  python-lxml

Optional:

*  python-gtk2: GUI toolkit
*  python-kiwi, gazpacho: frameworks for python-gtk


TEST INPUT
##########

Running a minimal test case to check whether the installation
was successful includes::

    * Change to the examples directory

        cd examples

    * Execute the ZGB Model render script

        ./render ZGB_model.py

    * Export the Fortran90 source code and compile in one step
      from the generated XML file

        kmos export ZGB_model.xml

    * Change to the export directory

        cd ZGB_model_local_smart

    * Run benchmark

        kmos benchmark


If everything is working you should see
the single-core CPU time to run 1 mio.
steps printed on STDOUT.

BASIC USAGE
###########

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
