import pdb
#!/usr/bin/env python
import itertools
import operator
from app.models import ConditionAction

def flatten(L):
    return [item for sublist in L for item in sublist]

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
        
    def write_lattice(self):
        data = self.data
        out = open('%s/lattice.f90' % self.dir, 'w')
        out.write(self._gpl_message())
        out.write('\n\nmodule lattice\n')
        out.write('use kind_values\n')
        out.write('use base, only: &\n')
        out.write('    assertion_fail, &\n')
        out.write('    deallocate_system, &\n')
        out.write('    get_kmc_step, &\n')
        out.write('    get_kmc_time, &\n')
        out.write('    get_kmc_time_step, &\n')
        out.write('    get_rate, &\n')
        out.write('    base_increment_procstat => increment_procstat, &\n')
        out.write('    base_add_proc => add_proc, &\n')
        out.write('    base_allocate_system => allocate_system, &\n')
        out.write('    base_can_do => can_do, &\n')
        out.write('    base_del_proc => del_proc, &\n')
        out.write('    determine_procsite, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    assertion_fail, &\n')

        out.write('\n ! Site constants\n\n')
        site_params = []
        for layer in data.layer_list:
            for site in layer.sites:
                site_params.append((site.name, layer.name))
        for i,(site,layer) in enumerate(site_params):
            out.write(('integer(kind=iint), parameter, public :: %s_%s = %s\n') % (layer,site,i +1))
        out.close()

    def write_proclist(self):
        data = self.data
        out = open('%s/proclist.f90' % self.dir, 'w')
        out.write(self._gpl_message())
        out.write('\n\nmodule proclist\n' 
            + 'use kind_values\n'
            + 'use base, only: &\n'
            + '    update_accum_rate, &\n'
            + '    determine_procsite, &\n'
            + '    update_clocks, &\n'
            + '    increment_procstat, &\n')
        out.write('use lattice, only:\n'
            + '    lattice_allocate_system => allocate_system, &\n')
        out.write(('    nr2%(name)s, &\n'
            + '    %(name)s2nr, &\n'
            + '    %(name)s_add_proc, &\n'
            + '    %(name)s_can_do, &\n'
            + '    %(name)s_replace_species, &\n'
            + '    %(name)s_del_proc, &\n'
            + '    %(name)s_get_species, &\n') % {'name': 'lattice'})
        out.write('\n\nimplicit none\n\n')
        out.write('\n\n ! Species constants\n\n')
        for i, species in enumerate(data.species_list):
            out.write('integer(kind=iint), parameter, public, :: %s = %s\n' % (species.name, i +1))

        out.write('\n\n! Process constants\n\n')
        for i, process in enumerate(self.data.process_list):
            out.write('integer(kind=iint), parameter, public :: %s = %s\n' % (process.name, i + 1))


        
            

        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_proc = %s\n'\
            % (len(data.process_list)))
        out.write('character(len=2000), dimension(%s) :: processes, rates')
        out.write('\n\ncontains\n\n')
        out.write(('subroutine init(input_system_size, system_name)\n'
            + '    integer(kind=iint), dimension(%s), intent(in) :: input_system_size\n'
            + '    character(len=400), intent(in) :: system_name\n'
            + '    print *, "This kMC Model \'%s\' was written by %s (%s)"\n'
            + '    print *, "and implemented with the help of kmos,"\n'
            + '    print *, "which is distributed under"\n'
            + '    print *, "GNU/GPL Version 3 (C) Max J. Hoffmann mjhoffmann@gmail.com"\n'
            + '    print *, "Currently kmos is in a very alphaish stage and there is"\n'
            + '    print *, "ABSOLUTELY NO WARRANTY for correctness."\n'
            + '    print *, "Please check back with the author prior to using"\n'
            + '    print *, "results in a publication."\n')\
            % (data.meta.model_dimension, data.meta.model_name, data.meta.author, data.meta.email, ))

        # TODO: finish init function
        out.write('end subroutine init\n\n')
        

        # TODO: subroutine do_kmc_step

        # TODO: subroutine run_proc_nr

        # TODO: atomistic updates

        # TODO: maybe check_... function (as far as touchup functions rely on it)

        for species in data.species_list:
            if species.name == data.species_list_iter.default_species:
                continue # don't put/take 'empty'
            # iterate over all layers, sites, operations, process, and conditions ...
            for layer in data.layer_list:
                for site in layer.sites:
                    for op in ['put','take']:
                        enabled_procs = []
                        disabled_procs = []
                        # op = operation
                        routine_name = '%s_%s_%s_%s' % (op, species.name, layer.name, site.name)
                        out.write('subroutine %s(species, site)\n' % routine_name)
                        for process in data.process_list:
                            for condition in process.condition_list:
                                if site.name == condition.coord.name:
                                    # first let's check if we could be enabling any site
                                    # this can be the case if we put down a particle, and 
                                    # it is the right one, or if we lift one up and the process
                                    # needs an empty site
                                    if op == 'put' \
                                        and  species.name == condition.species \
                                        or op == 'take' \
                                        and condition.species == data.species_list_iter.default_species  :

                                        other_conditions = filter(lambda x: x.coord != condition.coord, process.condition_list)
                                        # note how '-' operation is defined for Coord class !
                                        # we change the coordinate part to already point at 
                                        # the right relative site
                                        other_conditions = [ConditionAction(
                                                species=other_condition.species,
                                                coord=(other_condition.coord-condition.coord)) for 
                                                other_condition in other_conditions]
                                        enabled_procs.append((other_conditions, (process.name, -condition.coord)))
                                    # and we disable something whenever we put something down, and the process
                                    # needs an empty site here or if we take something and the process needs
                                    # something else
                                    elif op == 'put' \
                                        and condition.species == data.species_list_iter.default_species \
                                        or op == 'take' \
                                        and species.name == condition.species :
                                            disabled_procs.append((process, condition))
                        # updating disabled procs is easy to do efficiently
                        # because we don't ask any questions twice, so we do it immediately
                        if disabled_procs:
                            out.write('    ! disable affected processes\n')
                        for process, condition in disabled_procs:
                            out.write(('    if(can_do(%(site)s, %(proc)s)then\n'
                            + '        call del_site(%(proc)s, %(site)s)\n'
                            + '    endif\n\n') % {'site':(-condition.coord).ff(), 'proc':process.name})

                        # updating enabled procs is not so simply, because meeting one condition
                        # is not enough. We need to know if all other conditions are met as well
                        # so we collect  all questions first and build a tree, where the most
                        # frequent questions are closer to the top
                        if enabled_procs:
                            out.write('    ! enable affected processes\n')
                        if not enabled_procs + disabled_procs:
                            print("Warning: site %s_%s is not used at all!" %(layer.name, site.name))

                        self._write_optimal_iftree(items=enabled_procs, indent=4,out=out)
                        out.write('end subroutine %s\n\n' % routine_name)

        # TODO: subroutine touchup functions
        for layer in data.layer_list:
            for site in layer.sites:
                routine_name = 'touchup_%s_%s' % (layer.name, site.name)
                out.write('subroutine %s(species, site)\n' % routine_name)
                out.write('end subroutine %s\n\n' % routine_name)

        # TODO: subroutine get_char fuctions, the crumpy part
            
        out.close()

    def _write_optimal_iftree(self, items, indent, out):
        # this function is called recursively
        # so first we define the ANCHORS or SPECIAL CASES
        # if no conditions are left, enable process immediately
        # I actually don't know if this tree is optimal
        # So consider this a heuristic solution which should give
        # on average better results than the brute force way

        # DEBUGGING
        #print(len(items))
        #print(items)
        for item in filter(lambda x: not x[0], items):
            out.write('%scall add_site(%s, %s)\n' % (' '*indent, item[1][0], item[1][1].ff()))

        # and only keep those that have conditions
        items = filter(lambda x: x[0], items)
        if not items:
            return

        # DEBUGGING
        #print(len(items))
        #print(items)

        # now the GENERAL CASE
        # first find site, that is most sought after
        most_common_coord = most_common([y.coord for y in flatten([x[0] for x in items])])

        #DEBUGGING
        #print("MOST_COMMON_COORD: %s" % most_common_coord)

        # filter out list of uniq answers for this site
        answers = [ y.species for y in filter(lambda x: x.coord.ff()==most_common_coord.ff(), flatten([x[0] for x in items]))]
        uniq_answers = list(set(answers))

        #DEBUGGING
        #print("ANSWERS %s" % answers)
        #print("UNIQ_ANSWERS %s" % uniq_answers)

        out.write('%sselect case(get_species(%s))\n' % ((indent)*' ', most_common_coord.ff()))
        for answer in uniq_answers:
            out.write('%scase(%s)\n' % ((indent)*' ', answer))
            # this very crazy expression matches at items that contain
            # a question for the same coordinate and have the same answer here
            nested_items = filter(
                lambda x: (most_common_coord.ff() in [y.coord.ff() for y in x[0]]
                and answer == filter(lambda y: y.coord.ff() == most_common_coord.ff(), x[0])[0].species),
                items)
            # pruned items are almost identical to nested items, except the have
            # the one condition removed, that we just met
            pruned_items = []
            for nested_item in nested_items:
                conditions = filter( lambda x: most_common_coord.ff()!=x.coord.ff(), nested_item[0])
                pruned_items.append((conditions,nested_item[1]))


            items = filter(lambda x: x not in nested_items, items)
            #print(len(nested_items))
            #print(nested_items)
            self._write_optimal_iftree(pruned_items, indent+4, out)
        out.write('%send case\n\n' % (indent*' ',))

        if items:
            # if items are left
            # the RECURSION II
            self._write_optimal_iftree(items, indent, out)

        
    def _gpl_message(self):
        """Prints the GPL statement at the top of the source file"""
        data = self.data
        out = ''
        out += "!  This file was generated by kMOS (kMC modelling on steroids)\n"
        out += "!  written by Max J. Hoffmann mjhoffmann@gmail.com (C) 2009-2011.\n"
        if hasattr(data.meta,'author') :
            out += '!  The model was written by ' + data.meta.author + '.\n'
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
        return out
