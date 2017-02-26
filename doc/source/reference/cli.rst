Entry point module for the command-line
   interface. The kmos executable should be
   on the program path, import this modules
   main function and run it.

   To call kmos command as you would from the shell,
   use ::

       kmos.cli.main('...')

   Every command can be shortened as long as it is non-ambiguous, e.g. ::


    kmos ex <xml-file>

   instead of ::

    kmos export <xml-file>


   etc.

List of commands
^^^^^^^^^^^^^^^^



``kmos benchmark``
    Run 1 mio. kMC steps on model in current directory
    and report runtime.


``kmos build``
    Build kmc_model.so from \*f90 files in the
    current directory.

    Additional Parameters ::
        -d/--debug
            Turn on assertion statements in F90 code

        -n/--no-compiler-optimization
            Do not send optimizing flags to compiler.


``kmos edit <xml-file>``
    Open the kmos xml-file in a GUI to edit
    the model.


``kmos export <xml-file> [<export-path>]``
    Take a kmos xml-file and export all generated
    source code to the export-path. There try to
    build the kmc_model.so.

    Additional Parameters ::

        -s/--source-only
            Export source only and don't build binary

        -b/--backend (local_smart|lat_int)
            Choose backend. Default is "local_smart".
            lat_int is EXPERIMENTAL and not made
            for production, yet.

        -d/--debug
            Turn on assertion statements in F90 code.
            (Only active in compile step)

           --acf
            Build the modules base_acf.f90 and proclist_acf.f90. Default is false.
            This both modules contain functions to calculate ACF (autocorrelation function) and MSD (mean squared displacement).

        -n/--no-compiler-optimization
            Do not send optimizing flags to compiler.


``kmos help <command>``
    Print usage information for the given command.


``kmos help all``
    Display documentation for all commands.


``kmos import <xml-file>``
    Take a kmos xml-file and open an ipython shell
    with the project_tree imported as pt.


``kmos rebuild``
    Export code and rebuild binary module from XML
    information included in kmc_settings.py in
    current directory.

    Additional Parameters ::
        -d/--debug
            Turn on assertion statements in F90 code


``kmos run``
    Open an interactive shell and create a KMC_Model in it
               run == shell


``kmos settings-export <xml-file> [<export-path>]``
    Take a kmos xml-file and export kmc_settings.py
    to the export-path.


``kmos shell``
    Open an interactive shell and create a KMC_Model in it
               run == shell


``kmos version``
    Print version number and exit.


``kmos view``
    Take a kmc_model.so and kmc_settings.py in the
    same directory and start to simulate the
    model visually.

    Additional Parameters ::
        -v/--steps-per-frame <number>
            Number of steps per frame



``kmos xml``
    Print xml representation of model to stdout
