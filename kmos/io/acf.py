"""ACF Code Generation Module.

This module handles the generation of Fortran code for autocorrelation
function (ACF) and mean squared displacement (MSD) calculations in kinetic
Monte Carlo simulations.

The module uses pure inheritance to support multiple kMC backends:
- local_smart: Standard backend with local site tracking
- otf: On-the-fly backend with coordinate offsets
- lat_int: Lattice interpolation backend (uses OTF implementation)

Usage Example
-------------

>>> from kmos.io.acf import get_acf_writer
>>> writer = get_acf_writer(project_tree, export_dir, code_generator='local_smart')
>>> writer.write_proclist_acf()

This generates proclist_acf.f90 containing:
- do_kmc_steps_acf(): Main ACF calculation loop
- get_diff_sites_acf(): Site tracking for diffusion
- get_diff_sites_displacement(): Displacement tracking for MSD

Backend Differences
-------------------

Smart Backend:
    - Direct lattice site indexing
    - No coordinate offsets
    - Simpler conditional logic

OTF Backend:
    - Coordinate offset: lsite + (/0,0,0,-1/)
    - More complex conditional branching
    - Handles executing coordinate differences

Design Pattern
--------------
Uses pure inheritance with the Template Method pattern:
- ACFWriterBase: Abstract base class with shared orchestration
- SmartACFWriter: local_smart implementation
- OTFACFWriter: otf/lat_int implementation

Migration from Old API
----------------------

Old way (still supported):
    from kmos.io import ProcListWriter
    writer = ProcListWriter(project, export_dir)
    writer.write_proclist_acf(code_generator='local_smart')

New way (recommended):
    from kmos.io.acf import get_acf_writer
    writer = get_acf_writer(project, export_dir, code_generator='local_smart')
    writer.write_proclist_acf()

The old API is maintained for backward compatibility.
"""

import os
from kmos.utils import evaluate_template


class ACFWriterBase:
    """Abstract base class for ACF code generation.

    This class provides the template method pattern for generating Fortran ACF
    code. Subclasses must implement backend-specific methods for site tracking
    and displacement calculations.

    Attributes:
        data: Project data tree containing process and species information
        dir: Output directory for generated Fortran files
    """

    def __init__(self, data, dir):
        """Initialize the ACF writer.

        Args:
            data: Project data tree
            dir: Output directory path
        """
        self.data = data
        self.dir = dir

    def write_proclist_acf(self):
        """Write the proclist_acf.f90 module.

        This is the main entry point that orchestrates the generation of the
        complete ACF module. It creates the file, writes the header, generates
        backend-specific subroutines, and finalizes the module.
        """
        out = open(f"{self.dir}/proclist_acf.f90", "w")
        self._write_header(out)
        self._write_generic_subroutines(out)
        self.write_diff_sites_acf(out)
        self.write_diff_sites_displacement(out)
        self._write_end(out)
        out.close()

    def _write_header(self, out):
        """Write the module header and imports.

        Args:
            out: File handle to write to
        """
        out.write(
            (
                "module proclist_acf\n"
                "use kind_values\n"
                "use base, only: &\n"
                "    update_accum_rate, &\n"
                "    update_integ_rate, &\n"
                "    determine_procsite, &\n"
                "    update_clocks, &\n"
                "    avail_sites, &\n"
                "    null_species, &\n"
                "    increment_procstat\n\n"
                "use base_acf, only: &\n"
                "    assign_particle_id, &\n"
                "    update_id_arr, &\n"
                "    update_displacement, &\n"
                "    update_config_bin, &\n"
                "    update_buffer_acf, &\n"
                "    update_property_and_buffer_acf, &\n"
                "    drain_process, &\n"
                "    source_process, &\n"
                "    update_kmc_step_acf, &\n"
                "    get_kmc_step_acf, &\n"
                "    update_trajectory, &\n"
                "    update_displacement, &\n"
                "    nr_of_annhilations, &\n"
                "    wrap_count, &\n"
                "    update_after_wrap_acf\n\n"
                "use lattice\n\n"
                "use proclist\n"
            )
        )
        out.write("\nimplicit none\n")
        out.write("\n\ncontains\n\n")

    def _write_generic_subroutines(self, out):
        """Write generic ACF subroutines using template.

        Args:
            out: File handle to write to
        """
        with open(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "fortran_src",
                "proclist_generic_subroutines_acf.mpy",
            )
        ) as infile:
            template = infile.read()

        # Determine code_generator from class type
        if isinstance(self, SmartACFWriter):
            code_generator = "local_smart"
        elif isinstance(self, OTFACFWriter):
            code_generator = "otf"  # Will work for both otf and lat_int
        else:
            code_generator = "local_smart"  # Fallback

        out.write(
            evaluate_template(
                template,
                self=self,
                data=self.data,
                code_generator=code_generator,
            )
        )

    def _write_end(self, out):
        """Write the module end statement.

        Args:
            out: File handle to write to
        """
        out.write("end module proclist_acf\n")

    def write_diff_sites_acf(self, out):
        """Write the get_diff_sites_acf subroutine (backend-specific).

        This method must be implemented by subclasses to generate
        backend-specific code for tracking initial and final sites
        during diffusion processes.

        Args:
            out: File handle to write to

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement write_diff_sites_acf()")

    def write_diff_sites_displacement(self, out):
        """Write the get_diff_sites_displacement subroutine (backend-specific).

        This method must be implemented by subclasses to generate
        backend-specific code for tracking displacements during
        diffusion processes.

        Args:
            out: File handle to write to

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            "Subclasses must implement write_diff_sites_displacement()"
        )


class SmartACFWriter(ACFWriterBase):
    """ACF writer for local_smart backend.

    This implementation uses direct lattice site indexing without coordinate
    offsets, providing simpler conditional logic for site tracking.
    """

    def write_diff_sites_acf(self, out):
        """Write get_diff_sites_acf subroutine for smart backend.

        Args:
            out: File handle to write to
        """
        data = self.data

        # Write function header and documentation
        out.write(
            "subroutine get_diff_sites_acf(proc,nr_site,init_site,fin_site)\n\n"
            "!****f* proclist_acf/get_diff_sites_acf\n"
            "! FUNCTION\n"
            "!    get_diff_sites_acf gives the site ``init_site``, which is occupied by the particle before the diffusion process \n"
            "!    and also the site ``fin_site`` after the diffusion process.\n"
            "!\n"
            "! ARGUMENTS\n"
            "!\n"
            "!    * ``proc`` integer representing the process number\n"
            "!    * ``nr_site``  integer representing the site\n"
            "!    * ``init_site`` integer representing the site, which is occupied by the particle before the diffusion process takes place\n"
            "!    * ``fin_site`` integer representing the site, which is occupied by the particle after the diffusion process\n"
            "!******\n"
            "    integer(kind=iint), intent(in) :: proc\n"
            "    integer(kind=iint), intent(in) :: nr_site\n"
            "    integer(kind=iint), intent(out) :: init_site, fin_site\n\n"
            "    integer(kind=iint), dimension(4) :: lsite\n"
            "    integer(kind=iint), dimension(4) :: lsite_new\n"
            "    integer(kind=iint), dimension(4) :: lsite_old\n"
            "    integer(kind=iint) :: exit_site, entry_site\n\n"
            "    lsite = nr2lattice(nr_site, :)\n\n"
            "    select case(proc)\n"
        )

        # Iterate over all processes
        for process in data.process_list:
            out.write("    case(%s)\n" % process.name)
            source_species = 0
            if data.meta.debug > 0:
                out.write(
                    (
                        'print *,"PROCLIST/RUN_PROC_NR/NAME","%s"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/LSITE","lsite"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/SITE","site"\n'
                    )
                    % process.name
                )

            # First pass: determine source species
            for action in process.action_list:
                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None
                if action.species == previous_species:
                    source_species = action.species

            # Second pass: generate action code
            for action in process.action_list:
                if action.coord == process.executing_coord():
                    relative_coord = "lsite"
                else:
                    relative_coord = (
                        "lsite%s" % (action.coord - process.executing_coord()).radd_ff()
                    )

                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None

                if action.species[0] == "^":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","create %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call create_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif action.species[0] == "$":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","annihilate %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call annihilate_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and source_species == 0
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )
                    out.write("        lsite_old = (%s)\n" % (relative_coord))
                    out.write(
                        "        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and not source_species == 0
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )

                    out.write("        lsite_old = (%s)\n" % (relative_coord))

                    out.write(
                        "        exit_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                    out.write(
                        "        call drain_process(exit_site,init_site,fin_site)\n"
                    )

                else:
                    if not previous_species == action.species:
                        if not previous_species == data.species_list.default_species:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        previous_species,
                                    )
                                )
                            out.write(
                                "        call take_%s_%s_%s(%s)\n"
                                % (
                                    previous_species,
                                    action.coord.layer,
                                    action.coord.name,
                                    relative_coord,
                                )
                            )
                        if source_species == 0:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = (%s)\n" % (relative_coord))
                            out.write(
                                "        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                        if not source_species == 0:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = (%s)\n" % (relative_coord))
                            out.write(
                                "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                            out.write(
                                "        call source_process(entry_site,init_site,fin_site)\n"
                            )

            out.write("\n")

        out.write("    end select\n\n")
        out.write("end subroutine get_diff_sites_acf\n\n")

    def write_diff_sites_displacement(self, out):
        """Write get_diff_sites_displacement subroutine for smart backend.

        Args:
            out: File handle to write to
        """
        data = self.data

        # Write function header and documentation
        out.write(
            "subroutine get_diff_sites_displacement(proc,nr_site,init_site,fin_site,displace_coord)\n\n"
            "!****f* proclist_acf/get_diff_sites_displacement\n"
            "! FUNCTION\n"
            "!    get_diff_sites_displacement gives the site ``init_site``, which is occupied by the particle before the diffusion process \n"
            "!    and also the site ``fin_site`` after the diffusion process.\n"
            "!    Additionally, the displacement of the jumping particle will be saved.\n"
            "!\n"
            "! ARGUMENTS\n"
            "!\n"
            "!    * ``proc`` integer representing the process number\n"
            "!    * ``nr_site``  integer representing the site\n"
            "!    * ``init_site`` integer representing the site, which is occupied by the particle before the diffusion process takes place\n"
            "!    * ``fin_site`` integer representing the site, which is occupied by the particle after the diffusion process\n"
            "!    * ``displace_coord`` writeable 3 dimensional array, in which the displacement of the jumping particle will be stored.\n"
            "!******\n"
            "    integer(kind=iint), intent(in) :: proc\n"
            "    integer(kind=iint), intent(in) :: nr_site\n"
            "    integer(kind=iint), intent(out) :: init_site, fin_site\n\n"
            "    integer(kind=iint), dimension(4) :: lsite\n"
            "    integer(kind=iint), dimension(4) :: lsite_new\n"
            "    integer(kind=iint), dimension(4) :: lsite_old\n"
            "    integer(kind=iint) :: exit_site, entry_site\n"
            "    real(kind=rdouble), dimension(3), intent(out) :: displace_coord\n\n"
            "    lsite = nr2lattice(nr_site, :)\n\n"
            "    select case(proc)\n"
        )

        # Iterate over all processes
        for process in data.process_list:
            out.write("    case(%s)\n" % process.name)
            source_species = 0
            if data.meta.debug > 0:
                out.write(
                    (
                        'print *,"PROCLIST/RUN_PROC_NR/NAME","%s"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/LSITE","lsite"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/SITE","site"\n'
                    )
                    % process.name
                )

            # First pass: determine source species
            for action in process.action_list:
                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None
                if action.species == previous_species:
                    source_species = action.species

            # Second pass: generate action code
            for action in process.action_list:
                if action.coord == process.executing_coord():
                    relative_coord = "lsite"
                else:
                    relative_coord = (
                        "lsite%s" % (action.coord - process.executing_coord()).radd_ff()
                    )

                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None

                if action.species[0] == "^":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","create %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call create_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif action.species[0] == "$":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","annihilate %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call annihilate_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and source_species == 0
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )
                    out.write("        lsite_old = (%s)\n" % (relative_coord))
                    out.write(
                        "        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and not source_species == 0
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )

                    out.write("        lsite_old = (%s)\n" % (relative_coord))

                    out.write(
                        "        exit_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                    out.write(
                        "        call drain_process(exit_site,init_site,fin_site)\n"
                    )

                else:
                    if not previous_species == action.species:
                        if not previous_species == data.species_list.default_species:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        previous_species,
                                    )
                                )
                            out.write(
                                "        call take_%s_%s_%s(%s)\n"
                                % (
                                    previous_species,
                                    action.coord.layer,
                                    action.coord.name,
                                    relative_coord,
                                )
                            )
                        if source_species == 0:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = (%s)\n" % (relative_coord))
                            out.write(
                                "        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )

                        if not source_species == 0:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = (%s)\n" % (relative_coord))
                            out.write(
                                "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                            out.write(
                                "        call source_process(entry_site,init_site,fin_site)\n"
                            )

            # Add displacement calculation (this is the key difference from write_diff_sites_acf)
            out.write(
                "        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))\n"
            )

            out.write("\n")

        out.write("    end select\n\n")
        out.write("end subroutine get_diff_sites_displacement\n\n")


class OTFACFWriter(ACFWriterBase):
    """ACF writer for otf and lat_int backends.

    This implementation uses coordinate offsets (lsite + (/0,0,0,-1/)) and
    more complex conditional logic for handling executing coordinate differences.
    """

    def write_diff_sites_acf(self, out):
        """Write get_diff_sites_acf subroutine for OTF backend.

        Args:
            out: File handle to write to
        """
        data = self.data

        # Write function header and documentation
        out.write(
            "subroutine get_diff_sites_acf(proc,nr_site,init_site,fin_site)\n\n"
            "!****f* proclist_acf/get_diff_sites_acf\n"
            "! FUNCTION\n"
            "!    get_diff_sites_acf gives the site ``init_site``, which is occupied by the particle before the diffusion process \n"
            "!    and also the site ``fin_site`` after the diffusion process.\n"
            "!\n"
            "! ARGUMENTS\n"
            "!\n"
            "!    * ``proc`` integer representing the process number\n"
            "!    * ``nr_site``  integer representing the site\n"
            "!    * ``init_site`` integer representing the site, which is occupied by the particle before the diffusion process takes place\n"
            "!    * ``fin_site`` integer representing the site, which is occupied by the particle after the diffusion process\n"
            "!******\n"
            "    integer(kind=iint), intent(in) :: proc\n"
            "    integer(kind=iint), intent(in) :: nr_site\n"
            "    integer(kind=iint), intent(out) :: init_site, fin_site\n\n"
            "    integer(kind=iint), dimension(4) :: lsite\n"
            "    integer(kind=iint), dimension(4) :: lsite_new\n"
            "    integer(kind=iint), dimension(4) :: lsite_old\n"
            "    integer(kind=iint) :: exit_site, entry_site\n\n"
            "    lsite = nr2lattice(nr_site, :) + (/0,0,0,-1/)\n\n"
            "    select case(proc)\n"
        )

        # Iterate over all processes
        for process in data.process_list:
            out.write("    case(%s)\n" % process.name)
            source_species = 0
            if data.meta.debug > 0:
                out.write(
                    (
                        'print *,"PROCLIST/RUN_PROC_NR/NAME","%s"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/LSITE","lsite"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/SITE","site"\n'
                    )
                    % process.name
                )

            # First pass: determine source species
            for action in process.action_list:
                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None
                if action.species == previous_species:
                    source_species = action.species

            # Second pass: generate action code (with enumeration for OTF)
            for i_action, action in enumerate(process.action_list):
                if action.coord == process.executing_coord():
                    relative_coord = "lsite"
                else:
                    relative_coord = (
                        "lsite%s" % (action.coord - process.executing_coord()).radd_ff()
                    )

                action_coord = process.action_list[i_action].coord.radd_ff()
                process_exec = process.action_list[1 - i_action].coord.radd_ff()

                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None

                if action.species[0] == "^":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","create %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call create_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif action.species[0] == "$":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","annihilate %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call annihilate_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and source_species == 0
                    and action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )
                    out.write("        lsite_new = lsite%s\n" % (process_exec))
                    out.write(
                        "        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and source_species == 0
                    and not action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )
                    out.write("        lsite_old = lsite%s\n" % (action_coord))
                    out.write(
                        "        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and not source_species == 0
                    and action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )

                    out.write("        lsite_new = lsite%s\n" % (process_exec))

                    out.write(
                        "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                    )
                    out.write(
                        "        call source_process(entry_site,init_site,fin_site)\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and not source_species == 0
                    and not action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )

                    out.write("        lsite_old = lsite%s\n" % (action_coord))

                    out.write(
                        "        exit_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                    out.write(
                        "        call drain_process(exit_site,init_site,fin_site)\n"
                    )

                else:
                    if not previous_species == action.species:
                        if not previous_species == data.species_list.default_species:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        previous_species,
                                    )
                                )
                            out.write(
                                "        call take_%s_%s_%s(%s)\n"
                                % (
                                    previous_species,
                                    action.coord.layer,
                                    action.coord.name,
                                    relative_coord,
                                )
                            )
                        if (
                            source_species == 0
                            and action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = lsite%s\n" % (action_coord))
                            out.write(
                                "        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                        if (
                            source_species == 0
                            and not action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_old = lsite%s\n" % (process_exec))
                            out.write(
                                "        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                            )
                        if (
                            not source_species == 0
                            and action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = lsite%s\n" % (action_coord))
                            out.write(
                                "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                            out.write(
                                "        call source_process(entry_site,init_site,fin_site)\n"
                            )
                        if (
                            not source_species == 0
                            and not action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = lsite%s\n" % (action_coord))
                            out.write(
                                "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                            out.write(
                                "        call source_process(entry_site,init_site,fin_site)\n"
                            )

            out.write("\n")

        out.write("    end select\n\n")
        out.write("end subroutine get_diff_sites_acf\n\n")

    def write_diff_sites_displacement(self, out):
        """Write get_diff_sites_displacement subroutine for OTF backend.

        Args:
            out: File handle to write to
        """
        data = self.data

        # Write function header and documentation
        out.write(
            "subroutine get_diff_sites_displacement(proc,nr_site,init_site,fin_site,displace_coord)\n\n"
            "!****f* proclist_acf/get_diff_sites_displacement\n"
            "! FUNCTION\n"
            "!    get_diff_sites_displacement gives the site ``init_site``, which is occupied by the particle before the diffusion process \n"
            "!    and also the site ``fin_site`` after the diffusion process.\n"
            "!    Additionally, the displacement of the jumping particle will be saved.\n"
            "!\n"
            "! ARGUMENTS\n"
            "!\n"
            "!    * ``proc`` integer representing the process number\n"
            "!    * ``nr_site``  integer representing the site\n"
            "!    * ``init_site`` integer representing the site, which is occupied by the particle before the diffusion process takes place\n"
            "!    * ``fin_site`` integer representing the site, which is occupied by the particle after the diffusion process\n"
            "!    * ``displace_coord`` writeable 3 dimensional array, in which the displacement of the jumping particle will be stored.\n"
            "!******\n"
            "    integer(kind=iint), intent(in) :: proc\n"
            "    integer(kind=iint), intent(in) :: nr_site\n"
            "    integer(kind=iint), intent(out) :: init_site, fin_site\n\n"
            "    integer(kind=iint), dimension(4) :: lsite\n"
            "    integer(kind=iint), dimension(4) :: lsite_new\n"
            "    integer(kind=iint), dimension(4) :: lsite_old\n"
            "    integer(kind=iint) :: exit_site, entry_site\n"
            "    real(kind=rdouble), dimension(3), intent(out) :: displace_coord\n\n"
            "    lsite = nr2lattice(nr_site, :) + (/0,0,0,-1/)\n\n"
            "    select case(proc)\n"
        )

        # Iterate over all processes
        for process in data.process_list:
            out.write("    case(%s)\n" % process.name)
            source_species = 0
            if data.meta.debug > 0:
                out.write(
                    (
                        'print *,"PROCLIST/RUN_PROC_NR/NAME","%s"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/LSITE","lsite"\n'
                        'print *,"PROCLIST/RUN_PROC_NR/SITE","site"\n'
                    )
                    % process.name
                )

            # First pass: determine source species
            for action in process.action_list:
                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None
                if action.species == previous_species:
                    source_species = action.species

            # Second pass: generate action code (with enumeration for OTF)
            for i_action, action in enumerate(process.action_list):
                if action.coord == process.executing_coord():
                    relative_coord = "lsite"
                else:
                    relative_coord = (
                        "lsite%s" % (action.coord - process.executing_coord()).radd_ff()
                    )

                action_coord = process.action_list[i_action].coord.radd_ff()
                process_exec = process.action_list[1 - i_action].coord.radd_ff()

                try:
                    previous_species = list(
                        filter(
                            lambda x: x.coord.ff() == action.coord.ff(),
                            process.condition_list,
                        )
                    )[0].species
                except IndexError:
                    import warnings

                    warnings.warn(
                        """Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site."""
                        % process.name,
                        UserWarning,
                    )
                    previous_species = None

                if action.species[0] == "^":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","create %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call create_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif action.species[0] == "$":
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","annihilate %s_%s"\n'
                            % (action.coord.layer, action.coord.name)
                        )
                    out.write(
                        "        call annihilate_%s_%s(%s, %s)\n"
                        % (
                            action.coord.layer,
                            action.coord.name,
                            relative_coord,
                            action.species[1:],
                        )
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and source_species == 0
                    and action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )
                    out.write("        lsite_new = lsite%s\n" % (process_exec))
                    out.write(
                        "        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and source_species == 0
                    and not action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )
                    out.write("        lsite_old = lsite%s\n" % (action_coord))
                    out.write(
                        "        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and not source_species == 0
                    and action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )

                    out.write("        lsite_new = lsite%s\n" % (process_exec))

                    out.write(
                        "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                    )
                    out.write(
                        "        call source_process(entry_site,init_site,fin_site)\n"
                    )
                elif (
                    action.species == data.species_list.default_species
                    and not action.species == previous_species
                    and not source_species == 0
                    and not action.coord == process.executing_coord()
                ):
                    if data.meta.debug > 0:
                        out.write(
                            'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                            % (action.coord.layer, action.coord.name, previous_species)
                        )

                    out.write("        lsite_old = lsite%s\n" % (action_coord))

                    out.write(
                        "        exit_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                    )
                    out.write(
                        "        call drain_process(exit_site,init_site,fin_site)\n"
                    )

                else:
                    if not previous_species == action.species:
                        if not previous_species == data.species_list.default_species:
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        previous_species,
                                    )
                                )
                            out.write(
                                "        call take_%s_%s_%s(%s)\n"
                                % (
                                    previous_species,
                                    action.coord.layer,
                                    action.coord.name,
                                    relative_coord,
                                )
                            )
                        if (
                            source_species == 0
                            and action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = lsite%s\n" % (action_coord))
                            out.write(
                                "        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                        if (
                            source_species == 0
                            and not action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_old = lsite%s\n" % (process_exec))
                            out.write(
                                "        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))\n"
                            )
                        if (
                            not source_species == 0
                            and action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = lsite%s\n" % (action_coord))
                            out.write(
                                "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                            out.write(
                                "        call source_process(entry_site,init_site,fin_site)\n"
                            )
                        if (
                            not source_species == 0
                            and not action.coord == process.executing_coord()
                        ):
                            if data.meta.debug > 0:
                                out.write(
                                    'print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                    % (
                                        action.coord.layer,
                                        action.coord.name,
                                        action.species,
                                    )
                                )
                            out.write("        lsite_new = lsite%s\n" % (action_coord))
                            out.write(
                                "        entry_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))\n"
                            )
                            out.write(
                                "        call source_process(entry_site,init_site,fin_site)\n"
                            )

            # Add displacement calculation (key difference from write_diff_sites_acf)
            out.write(
                "        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))\n"
            )

            out.write("\n")

        out.write("    end select\n\n")
        out.write("end subroutine get_diff_sites_displacement\n\n")


def get_acf_writer(data, dir, code_generator="local_smart"):
    """Factory function to create appropriate ACF writer.

    Args:
        data: Project data tree
        dir: Output directory path
        code_generator: Backend type ('local_smart', 'otf', or 'lat_int')

    Returns:
        ACFWriter instance (SmartACFWriter or OTFACFWriter)

    Raises:
        ValueError: If code_generator is not recognized

    Examples:
        >>> writer = get_acf_writer(data, "/tmp/export", "local_smart")
        >>> writer.write_proclist_acf()
    """
    if code_generator == "local_smart":
        return SmartACFWriter(data, dir)
    elif code_generator in ("otf", "lat_int"):
        return OTFACFWriter(data, dir)
    else:
        raise ValueError(f"Unknown code_generator: {code_generator}")
