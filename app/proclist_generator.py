#!/usr/bin/env python
import itertools
import operator


def most_common(L):
  # thanks go to Alex Martelli for this function
  # get an iterable of (item, iterable) pairs
  SL = sorted((x, i) for i, x in enumerate(L))
  # print 'SL:', SL
  groups = itertools.groupby(SL, key=operator.itemgetter(0))
  # auxiliary function to get "quality" for an item
  def _auxfun(g):
    item, iterable = g
    count = 0
    min_index = len(L)
    for _, where in iterable:
      count += 1
      min_index = min(min_index, where)
    # print 'item %r, count %r, minind %r' % (item, count, min_index)
    return count, -min_index
  # pick the highest-count/earliest item
  return max(groups, key=_auxfun)[0]


class ProcListWriter():
    """This class just exports the proclist.f90 module
    from a kmos project tree, but since this is the most
    algorithm extensive part, this is stored in an extra
    submodule"""
    def __init__(self, data, dir):
        self.data = data
        self.dir = dir
        
    def write_lattice_module(self):
        data = self.data
        out = open('%s/lattice.f90' % self.dir 'w')
        out.write(self._gpl_message())
        out.write('\n\nmodule lattice\n')
        out.write('use kind_values\n')
        out.write('use base, only: &\n')
        out.write('    assertion_fail, &\n)
        out.write('    deallocate_system, &\n)
        out.write('    get_kmc_step, &\n)
        out.write('    get_kmc_time, &\n)
        out.write('    get_kmc_time_step, &\n)
        out.write('    get_rate, &\n)
        out.write('    base_increment_procstat => increment_procstat, &\n)
        out.write('    base_add_proc => add_proc, &\n)
        out.write('    base_allocate_system => allocate_system, &\n)
        out.write('    base_can_do => can_do, &\n)
        out.write('    base_del_proc => del_proc, &\n)
        out.write('    determine_procsite, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.write('    assertion_fail, &\n)
        out.close()

    def write_proclist(self):
        data = self.data
        out = open('%s/proclist.f90' % self.dir, 'w')
        out.write(self._gpl_message())
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

        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_proc = %s\n'\
            % (len(self.data.process_list) + 1))
        out.write('character(len=2000), dimension(%s) :: processes, rates')
        out.write('\n\ncontains\n\n')
        out.write(('subroutine init(input_system_size, system_name)\n'
            + '    integer(kind=iint), dimension(%s), intent(in) :: input_system_size\n'
            + '    character(len=400), intent(in) :: system_name\n'
            + '    print *, "This kMC Model \'%s\' was written by %s (%s)"\n'
            + '    print *, "and implemented with the help of kmos,'
            + '    which is distributed under\n"'
            + '    print *, "GNU/GPL Version 3 (C) Max J. Hoffmann mjhoffmann@gmail.com"\n'
            + '    print *, "Currently kms is in a very alphaisch stage and there is"\n'
            + '    print *, "ABSOLUTELY NO WARRANTY for correctness."\n'
            + '    print *,"Please check back with the author prior to using\n'
            + '    results in a publication."\n')\
            % (data.meta.model_dimension, data.meta.model_name, data.meta.author, data.meta.email, ))

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
                                    if species == condition.species and op == 'put' \
                                        or condition.species == data.species_list.default_species and op == 'take' :
                                        for condition2 in process.condition_list:
                                            enabled_procs.append((process, condition2))
                                    else:
                                        disabled_procs.append(process, condition)
                        for process, condition in disabled_procs:
                            out.write('    if(can_do(%(site)s, %(proc)s)then\n'
                            + '        call del_site(%(proc)s, %(site)s)\n'
                            + '    endif\n') % {'site':condition.site, 'proc':process.name}
                        self._write_optimal_iftree(list=enabled_procs, indent=4)
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

    def _write_optimal_iftree(items, indent, out):
        # this function is called recursively
        # so first we define the ANCHORS or SPECIAL CASES
        # if no items are left in this branch, return empty
        if not items:
            return

        # if all items left belong to the same process, don't nest further
        # but ask them all at once and act accordingly
        if len(set([x[0] for x in items])) == 1 :
            out.write('%sif(' % (' '*indent, ))
            out.write('get_species(%s).eq.%s' % (items[0][1].coord, items[0][1].species))
            for condition in items[1 :]:
                out.write(' &\n%s.and. get_species(%s).eq.%s' % (item[1].coord, item[1].species))
            out.write(')then')
            out.write('%scall add_site(%s,%s)\n' % (item[0].name, item[1].coord))
            out.write('%sendif' % (' '*indent, ))
            return

        # now the GENERAL CASE
        # first find site, that is most sought after
        most_common_coord = most_common([x[1].coord for x in items])

        # filter out list of uniq answers for this site
        answers = [condition.species for condition in filter(lambda x: x[1].coord == most_common_coord, item)]
        uniq_answers = list(set(answers))

        out.write('%sselect case(get_species(%s))\n' % (indent*' ', most_common_coord))
        for a, answer in enumerate(uniq_answers):
            out.write('%scase(species.eq.%s)\n' % (indent*' ', answer))

            # build list of all outcomes that need this answer
            covered_procs = [ x[0] for x in  filter(lambda x: (x[1].coord, x[1].species) == (most_common_coord, answer) , items)]
            # build list of all questions aiming towards this outcome
            new_items = filter(lambda x: x[0] in covered_procs, item)

            # all remain questions go behind 'select case' block
            items = [ x not in new_items for x in items ]
            # the RECURSION I
            self._write_optimal_iftree(new_items, indent+4, out)
        out.write('%send case\n' % (indent*' ',))

        if items:
            # if items are left
            # the RECURSION II
            self._write_optimal_iftree(item, indent, out)

        
    def _gpl_message(self):
        """Prints the GPL statement at the top of the source file"""
        out = ''
        out += "!  This file was generated by kMOS (kMC modelling on steroids)\n"
        out += "!  written by Max J. Hoffmann mjhoffmann@gmail.com (C) 2009-2010.\n"
        if self.data.meta.has_key('author') :
            out += '!  The model was written by ' + self.data.meta['author'] + '.\n"
        out += """
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
"""

