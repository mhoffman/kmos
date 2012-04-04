

``kmos help all``
    Display documentation for all commands.


``kmos run``
    Open an interactive shell and create a KMC_Model in it


``kmos help <command>``
    Print usage information for the given command.


``kmos edit <xml-file>``
    Open the kmos xml-file in a GUI to edit
    the model.


``kmos rebuild``
    Export code and rebuild binary module from XML
    information included in kmc_settings.py in
    current directory.


``kmos benchmark``
    Run 1 mio. kMC steps on model in current directory
    and report runtime.


``kmos export-view <xml-file>``
    Export an XML file, compile and run the simulation.


``kmos export <xml-file> [<export-path>]``
    Take a kmos xml-file and export all generated
    source code to the export-path. There try to
    build the kmc_model.so.


``kmos build``
    Build kmc_model.so from \*f90 files in the
    current directory.


``kmos import <xml-file>``
    Take a kmos xml-file and open an ipython shell
    with the project_tree imported as pt.


``kmos export-settings <xml-file> [<export-path>]``
    Take a kmos xml-file and export kmc_settings.py
    to the export-path.


``kmos view``
    Take a kmc_model.so and kmc_settings.py in the
    same directory and start to simulate the
    model visually.
