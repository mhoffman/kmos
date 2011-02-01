#!/usr/bin/env python

class ProcListWriter():
    """This class just exports the proclist.f90 module
    from a kmos project tree, but since this is the most
    algorithm extensive part, this is stored in an extra
    submodule"""
    def __init__(self, data, dir):
        self.data = data
        self.dir = dir
        
    def write_proclist(self):
        data = self.data
        out = open('%s/proclist.f90' % self.dir, 'w')
        out.write('module proclist\n' 
            + 'use kind_values\n'
            + 'use base, only: &\n'
            + '    update_accum_rate, &\n'
            + '    determine_procsite, &\n'
            + '    update_clocks, &\n'
            + '    increment_procstat, &\n')
        out.write('use lattice, only:\n'
            + '    lattice_allocate_system => allocate_system, &\n')
        for lattice in self.data.lattice_list:
            out.write(('    nr2%(name)s, &\n'
                + '    %(name)s2nr, &\n'
                + '    %(name)s_add_proc, &\n'
                + '    %(name)s_can_do, &\n'
                + '    %(name)s_replace_species, &\n'
                + '    %(name)s_del_proc, &\n'
                + '    %(name)s_get_species, &\n') % {'name': lattice.name})
        for i, species in enumerate(self.data.species_list):
            if i+1 < len(self.data.species_list):
                out.write('    %s, &\n' % species.name)
            else:
                out.write('    %s\n\n' % species.name)
        out.write('implicit none\n\n')

        out.write('! Process constants\n')
        for i, process in enumerate(self.data.process_list):
            out.write(('integer(kind=iint), parameter, public :: %s = %s\n') % (process.name, i + 1))

        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_proc = %s\n' % (len(self.data.process_list) + 1))
        out.write('character(len=2000), dimension(%s) :: processes, rates')
        out.write('\n\ncontains\n\n')
        out.write(('subroutine init(input_system_size, system_name)\n'
            + '    integer(kind=iint), dimension(%s), intent(in) :: input_system_size\n'
            + '    character(len=400), intent(in) :: system_name\n'
            + '    print *, "This kMC Model \'%s\' was written by %s (%s)"\n'
            + '    print *, "and implemented with the help of kmos, which is distributed under\n"'
            + '    print *, "GNU/GPL Version 3 (C) Max J. Hoffmann mjhoffmann@gmail.com"\n'
            + '    print *, "Currently kms is in a very alphaisch stage and there is"\n'
            + '    print *, "ABSOLUTELY NO WARRANTY for correctness."\n'
            + '    print *,"Please check back with the author prior to using results in a publications."\n') % (data.meta.model_dimension, data.meta.model_name, data.meta.author, data.meta.email, ))

        # TODO: finish init function
        out.write('end subroutine init\n\n')
        

        # TODO: subroutine do_kmc_step

        # TODO: subroutine run_proc_nr

        # TODO: atomistic updates

        # TODO: maybe check_... function (as far as touchup functions rely on it)

        for species in data.species_list:
            for lattice in data.lattice_list:
                for site in lattice.sites:
                    for op in ['take','put']:
                        enabled_procs = []
                        disabled_procs = []
                        # op = operation
                        routine_name = '%s_%s_%s_%s' % (op, species.name, lattice.name, site.name)
                        out.write('subroutine  %s(species, site)\n' % routine_name)
                        for process in data.process_list:
                            for condition in process.condition_list:
                                if site.name == condition.coord.name:
                                    if species == condition.species and op == 'put':
                                        for condition2 in process.condition_list:
                                            enabled_procs.append((process, condition2))
                                    else:
                                        disabled_procs.append(process, condition)
                        for process, condition in disabled_procs:
                            out.write('    if(.not.can_do(%(site)s, %(proc))then' % {'site':condition.site, 'proc':process.name})
                            out.write('        call add_site(

                                        
                                        
                                    
                        out.write('end subroutine %s\n\n' % routine_name)

        # TODO: subroutine touchup functions
        for species in data.species_list:
            for lattice in data.lattice_list:
                for site in lattice.sites:
                    routine_name = 'touchup_%s_%s_%s' % (species.name, lattice.name, site.name)
                    out.write('subroutine  %s(species, site)\n' % routine_name)
                    out.write('end subroutine %s\n\n' % routine_name)

        # TODO: subroutine get_char fuctions, the crumpy part
            
        out.close()
        
    def _print_gpl_message(self):
        """Prints the GPL statement at the top of the source file"""
        self._out("!  This file was generated by kMOS (kMC modelling on steroids)")
        self._out("!  written by Max J. Hoffmann mjhoffmann@gmail.com (C) 2009-2010.")
        if self.meta.has_key('author') :
            self._out('!  The model was written by ' + self.meta['author'] + '.')
        self._out("""
!  This file is part of kmos.
!
!  kmos is free software; you can redistribute it and/or modify
!  it under the terms of the GNU General Public License as published by
!  the Free Software Foundation; either version 2 of the License, or
!  (at your option) any later version.
!
!  kmos is distributed in the hope that it will be useful,
!  but WITHOUT ANY WARRANTY; without even the implied warranty of
!  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
!  GNU General Public License for more details.
!
!  You should have received a copy of the GNU General Public License
!  along with kmos; if not, write to the Free Software
!  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
!  USA
""")

