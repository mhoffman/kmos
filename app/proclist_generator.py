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
        out.write('    increment_procstat, &\n')
        out.write('    base_add_proc => add_proc, &\n')
        out.write('    base_reset_site => reset_site, &\n')
        out.write('    base_allocate_system => allocate_system, &\n')
        out.write('    base_can_do => can_do, &\n')
        out.write('    base_del_proc => del_proc, &\n')
        out.write('    determine_procsite, &\n')
        out.write('    base_replace_species => replace_species, &\n')
        out.write('    base_get_species => get_species, &\n')
        out.write('    base_get_volume => get_volume, &\n')
        out.write('    reload_system => reload_system, &\n')
        out.write('    save_system, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    null_species, &\n')
        out.write('    set_rate_const, &\n')
        out.write('    update_accum_rate, &\n')
        out.write('    update_clocks\n\n')

        #out.write('use proclist, only: &\n')
        #if len(data.layer_list) > 1 :
            #for layer in data.layer_list[:-1]:
                #for site in layer.sites:
                    #out.write('    touchup_%s_%s, &\n' % (layer.name, site.name))
        #for site in data.layer_list[-1].sites[:-1]:
            #out.write('    touchup_%s_%s, &\n' % (data.layer_list[-1].name, site.name))
        #out.write('    touchup_%s_%s\n' % (data.layer_list[-1].name, data.layer_list[-1].sites[-1].name))
                
        out.write('\n\nimplicit none\n\n')

        out.write('integer(kind=iint), dimension(3), public :: system_size\n')
        out.write('integer(kind=iint), parameter, public :: nr_of_layers = %s\n' % len(data.layer_list))
        out.write('\n ! Layer constants\n\n')
        out.write('integer(kind=iint), parameter, public :: model_dimension = %s\n' % (data.meta.model_dimension))
        for i, layer in enumerate(data.layer_list):
            out.write('integer(kind=iint), parameter, public :: %s = %s\n'
                % (layer.name, i + 1))
        out.write('integer(kind=iint), parameter, public :: default_layer = %s\n' % data.layer_list_iter.default_layer)
        out.write('\n ! Site constants\n\n')
        site_params = []
        for layer in data.layer_list:
            for site in layer.sites:
                site_params.append((site.name, layer.name))
        for i,(site,layer) in enumerate(site_params):
            out.write(('integer(kind=iint), parameter, public :: %s_%s = %s\n')
                % (layer,site,i + 1))
        out.write('\n ! spuck = Sites Per Unit Cell Konstant\n')
        out.write('integer(kind=iint), parameter, public :: spuck = %s\n' % len(site_params))
        out.write('\n\ncontains\n\n')
        out.write('pure function lattice2nr(site)\n\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n')
        out.write('    integer(kind=iint) :: lattice2nr\n\n')
        out.write('    ! site = (x,y,z,local_index)\n')

        if data.meta.model_dimension == 1 :
            out.write('    lattice2nr = spuck*(modulo(site(1), system_size(1)))+site(4)')
        elif data.meta.model_dimension == 2 :
            out.write('    lattice2nr = spuck*(&\n'
                + '      modulo(site(1), system_size(1))&\n'
                + '      + system_size(1)*modulo(site(2), system_size(2)))&\n' 
                + '      + site(4)\n')
        elif data.meta.model_dimension == 3 :
            out.write('    lattice2nr = spuck*(&\n'
                + '      modulo(site(1), system_size(1))&\n'
                + '      + system_size(1)*modulo(site(2), system_size(2))&\n'
                + '      + system_size(1)*system_size(2)*modulo(site(3), system_size(3)))&\n'
                + '      + site(4)\n')
        out.write('\nend function lattice2nr\n\n')

        out.write('pure function nr2lattice(nr)\n\n')
        out.write('    integer(kind=iint), intent(in) :: nr\n')
        out.write('    integer(kind=iint), dimension(4) :: nr2lattice\n\n')

        if data.meta.model_dimension == 3 :
            out.write('    nr2lattice(3) = (nr - 1) /  (system_size(1)*system_size(2)*spuck)\n')
            out.write('    nr2lattice(2) = (nr - 1 - system_size(1)*system_size(2)*spuck*nr2lattice(3)) / (system_size(1)*spuck)\n')
            out.write('    nr2lattice(1) = (nr - 1 - spuck*(system_size(1)*system_size(2)*nr2lattice(3) + system_size(1)*nr2lattice(2))) / spuck\n')
            out.write('    nr2lattice(4) = nr - spuck*(system_size(1)*system_size(2)*nr2lattice(3) + system_size(2)*nr2lattice(2) + nr2lattice(1))\n')
        elif data.meta.model_dimension == 2 :
            out.write('    nr2lattice(3) = 0\n')
            out.write('    nr2lattice(2) = (nr -1) / (system_size(1)*spuck)\n')
            out.write('    nr2lattice(1) = (nr - 1 - spuck*system_size(1)*nr2lattice(2)) / spuck\n')
            out.write('    nr2lattice(4) = nr - spuck*(system_size(1)*nr2lattice(2) + nr2lattice(1))\n')
        elif data.meta.model_dimension == 1 :
            out.write('    nr2lattice(3) = 0\n')
            out.write('    nr2lattice(2) = 0\n')
            out.write('    nr2lattice(1) = (nr - 1) / spuck\n')
            out.write('    nr2lattice(4) = nr - spuck*nr2lattice(1)\n')
        out.write('\nend function nr2lattice\n\n')

        out.write('subroutine allocate_system(nr_of_proc, input_system_size, system_name)\n\n')
        out.write('    integer(kind=iint), intent(in) :: nr_of_proc\n')
        out.write('    integer(kind=iint), dimension(%s), intent(in) :: input_system_size\n' % data.meta.model_dimension)
        out.write('    character(len=200), intent(in) :: system_name\n\n')
        out.write('    integer(kind=iint) :: volume\n\n')
        out.write('    ! Copy to module wide variable\n')
        if data.meta.model_dimension == 3 :
            out.write('    system_size = input_system_size\n')
        elif data.meta.model_dimension == 2 :
            out.write('    system_size = (/input_system_size(1), input_system_size(2), 1/)\n')
        elif data.meta.model_dimension == 1 :
            out.write('    system_size = (/input_system_size(1), 1, 1/)\n')

        out.write('    volume = system_size(1)*system_size(2)*system_size(3)*spuck\n')

        out.write('    call base_allocate_system(nr_of_proc, volume, system_name)\n\n')
        out.write('end subroutine allocate_system\n\n')  

        out.write('subroutine add_proc(proc, site)\n\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site)\n')
        out.write('    call base_add_proc(proc, nr)\n\n')
        out.write('end subroutine add_proc\n\n')

        out.write('subroutine del_proc(proc, site)\n\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site)\n')
        out.write('    call base_del_proc(proc, nr)\n\n')
        out.write('end subroutine del_proc\n\n')

        out.write('pure function can_do(proc, site)\n\n')
        out.write('    logical :: can_do\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site)\n')
        out.write('    can_do = base_can_do(proc, nr)\n\n')
        out.write('end function can_do\n\n')

        out.write('subroutine replace_species(site,  old_species, new_species)\n\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) ::site\n')
        out.write('    integer(kind=iint), intent(in) :: old_species, new_species\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site)\n')
        out.write('    call base_replace_species(nr, old_species, new_species)\n\n')
        out.write('end subroutine replace_species\n\n')

        out.write('pure function get_species(site)\n\n')
        out.write('    integer(kind=iint) :: get_species\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site)\n')
        out.write('    get_species = base_get_species(nr)\n\n')
        out.write('end function get_species\n\n')

        out.write('subroutine reset_site(site, old_species)\n\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n')
        out.write('    integer(kind=iint), intent(in) :: old_species\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site)\n')
        out.write('    call base_reset_site(nr, old_species)\n\n')
        out.write('end subroutine reset_site\n\n')


        out.write('end module lattice\n')
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
            + '    increment_procstat\n\n')
        out.write('use lattice, only: &\n')
        site_params = []
        for layer in data.layer_list:
            out.write('    %s, &\n' % layer.name)
            for site in layer.sites:
                site_params.append((site.name, layer.name))
        for i,(site,layer) in enumerate(site_params):
            out.write(('    %s_%s, &\n') % (layer,site))
        out.write('    allocate_system, &\n'
            + '    nr2lattice, &\n'
            + '    lattice2nr, &\n'
            + '    add_proc, &\n'
            + '    can_do, &\n'
            + '    set_rate_const, &\n'
            + '    replace_species, &\n'
            + '    del_proc, &\n'
            + '    reset_site, &\n'
            + '    system_size, &\n'
            + '    spuck, &\n'
            + '    null_species, &\n'
            + '    get_species\n' )
        out.write('\n\nimplicit none\n\n')
        out.write('\n\n ! Species constants\n\n')
        for i, species in enumerate(data.species_list):
            out.write('integer(kind=iint), parameter, public :: %s = %s\n' % (species.name, i +1))
        out.write('integer(kind=iint), parameter, public :: default_species = %s' % (data.species_list_iter.default_species))

        out.write('\n\n! Process constants\n\n')
        for i, process in enumerate(self.data.process_list):
            out.write('integer(kind=iint), parameter, public :: %s = %s\n' % (process.name, i + 1))


        
            

        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_proc = %s\n'\
            % (len(data.process_list)))
        out.write('character(len=2000), dimension(%s) :: processes, rates' % (len(data.process_list)))
        out.write('\n\ncontains\n\n')

        out.write('subroutine do_kmc_step()\n\n')
        out.write('    real(kind=rsingle) :: ran_proc, ran_time, ran_site\n')
        out.write('    integer(kind=iint) :: nr_site, proc_nr\n\n')
        out.write('    call random_number(ran_time)\n')
        out.write('    call random_number(ran_proc)\n')
        out.write('    call random_number(ran_site)\n')
        out.write('    call update_accum_rate\n')
        out.write('    call determine_procsite(ran_proc, ran_time, proc_nr, nr_site)\n')
        out.write('    call run_proc_nr(proc_nr, nr_site)\n')
        out.write('    call update_clocks(ran_time)\n\n')
        out.write('end subroutine do_kmc_step\n\n')


        out.write('subroutine run_proc_nr(proc, nr_site)\n\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), intent(in) :: nr_site\n\n')
        out.write('    integer(kind=iint), dimension(4) :: lsite\n\n')
        out.write('    call increment_procstat(proc)\n\n')
        out.write('    ! lsite = lattice_site, (vs. scalar site)\n')
        out.write('    lsite = nr2lattice(nr_site)\n\n')
        out.write('    select case(proc)\n')
        for process in data.process_list:
            out.write('    case(%s)\n' % process.name)
            for action in process.action_list:
                if action.coord == process.executing_coord():
                    relative_coord = 'lsite'
                else:
                    relative_coord = 'lsite%s' % (action.coord-process.executing_coord()).radd_ff()


                if action.species == data.species_list_iter.default_species:
                    try:
                        previous_species = filter(lambda x: x.coord.ff()==action.coord.ff(), process.condition_list)[0].species
                    except:
                        UserWarning("Process %s seems to be ill-defined\n" % process.name)
                    out.write('        call take_%s_%s_%s(%s)\n' % (previous_species, action.coord.layer, action.coord.name, relative_coord))
                else:
                    out.write('        call put_%s_%s_%s(%s)\n' % (action.species, action.coord.layer, action.coord.name, relative_coord))

            out.write('\n')
                    
        out.write('    end select\n\n')

        out.write('end subroutine run_proc_nr\n\n')


        out.write(('subroutine init(input_system_size, system_name, layer, species)\n\n'
            + '    integer(kind=iint), intent(in) :: layer, species\n'
            + '    integer(kind=iint), dimension(%s), intent(in) :: input_system_size\n\n'
            + '    character(len=400), intent(in) :: system_name\n\n'
            + '    print *, "This kMC Model \'%s\' was written by %s (%s)"\n'
            + '    print *, "and implemented with the help of kmos,"\n'
            + '    print *, "which is distributed under"\n'
            + '    print *, "GNU/GPL Version 3 (C) Max J. Hoffmann mjhoffmann@gmail.com"\n'
            + '    print *, "Currently kmos is in a very alphaish stage and there is"\n'
            + '    print *, "ABSOLUTELY NO WARRANTY for correctness."\n'
            + '    print *, "Please check back with the author prior to using"\n'
            + '    print *, "results in a publication."\n\n')\
            % (data.meta.model_dimension, data.meta.model_name, data.meta.author, data.meta.email, ))
        out.write('    call allocate_system(nr_of_proc, input_system_size, system_name)\n')
        out.write('    call initialize_state(layer, species)\n')
        out.write('    call set_rate_constants\n\n')
        out.write('end subroutine init\n\n')

        out.write('subroutine set_rate_constants()\n\n')
        for process in data.process_list:
            rate_constant = process.rate_constant if process.rate_constant else 0.
            out.write('    call set_rate_const(%s, real(%s))\n' % (process.name, rate_constant))

        out.write('\nend subroutine set_rate_constants\n\n')

        out.write('subroutine initialize_state(layer, species)\n\n')
        out.write('    integer(kind=iint), intent(in) :: layer, species\n\n')
        out.write('    integer(kind=iint) :: i, j, k, nr\n')
        out.write('    integer(kind=iint) :: check_nr, check_site(4)\n\n')

        out.write('    ! Let\'s check if the works correctly, first\n')
        out.write('    do k = 0, system_size(3)-1\n')
        out.write('        do j = 0, system_size(2)-1\n')
        out.write('            do i = 0, system_size(1)-1\n')
        out.write('                do nr = 1, spuck\n')
        out.write('                    if(.not.all((/i,j,k,nr/).eq. &\n'
        + '                    nr2lattice(lattice2nr((/i,j,k,nr/)))))then\n')
        out.write('                        print *,"Error in Mapping:"\n')
        out.write('                        print *, (/i,j,k,nr/), "was mapped on", lattice2nr((/i,j,k,nr/))\n')
        out.write('                        print *, "but that was mapped on", nr2lattice(lattice2nr((/i,j,k,nr/)))\n')
        out.write('                        stop\n')
        out.write('                    endif\n')
        out.write('                end do\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')

        out.write('    do check_nr=1, system_size(1)*system_size(2)*system_size(3)*spuck\n')
        out.write('        if(.not.check_nr.eq.lattice2nr(nr2lattice(check_nr)))then\n')
        out.write('            print *, "ERROR in Mapping:", check_nr\n')
        out.write('            print *, "was mapped on", nr2lattice(check_nr)\n')
        out.write('            print *, "but that was mapped on",lattice2nr(nr2lattice(check_nr))\n')
        out.write('            stop\n')
        out.write('        endif\n')
        out.write('    end do\n\n')

        out.write('    do k = 0, system_size(3)-1\n')
        out.write('        do j = 0, system_size(2)-1\n')
        out.write('            do i = 0, system_size(1)-1\n')
        out.write('                do nr = 1, spuck\n')
        out.write('                    call reset_site((/i, j, k, nr/), null_species)\n')
        out.write('                    call replace_species((/i, j, k, nr/), null_species, species)\n')
        out.write('                end do\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')

        out.write('    do k = 0, system_size(3)-1\n')
        out.write('        do j = 0, system_size(2)-1\n')
        out.write('            do i = 0, system_size(1)-1\n')
        out.write('                select case(layer)\n')
        for layer in data.layer_list:
            out.write('                case(%s)\n' % layer.name)
            for site in layer.sites:
                out.write('                    call touchup_%s_%s((/i, j, k, %s_%s/))\n' % (2*(layer.name, site.name)))
        out.write('                end select\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')
        out.write('end subroutine initialize_state\n\n')



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
                        out.write('subroutine %s(site)\n\n' % routine_name)
                        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                        out.write('    ! update lattice\n')
                        if op == 'put':
                            out.write('    call replace_species(site, %s, %s)\n\n' % (data.species_list_iter.default_species, species.name))
                        elif op == 'take':
                            out.write('    call replace_species(site, %s, %s)\n\n' % (species.name, data.species_list_iter.default_species))
                        for process in data.process_list:
                            for condition in process.condition_list:
                                if site.name == condition.coord.name :
                                    # first let's check if we could be enabling any site
                                    # this can be the case if we put down a particle, and 
                                    # it is the right one, or if we lift one up and the process
                                    # needs an empty site
                                    if op == 'put' \
                                        and  species.name == condition.species \
                                        or op == 'take' \
                                        and condition.species == data.species_list_iter.default_species  :

                                        # filter out the current condition, because we know we set it to true 
                                        # right now
                                        other_conditions = filter(lambda x: x.coord != condition.coord, process.condition_list)
                                        # note how '-' operation is defined for Coord class !
                                        # we change the coordinate part to already point at 
                                        # the right relative site
                                        other_conditions = [ConditionAction(
                                                species=other_condition.species,
                                                coord=('site%s' % (other_condition.coord-condition.coord).radd_ff())) for 
                                                other_condition in other_conditions]
                                        enabled_procs.append((other_conditions, (process.name, 'site%s' % (process.executing_coord()-condition.coord).radd_ff(), True)))
                                    # and we disable something whenever we put something down, and the process
                                    # needs an empty site here or if we take something and the process needs
                                    # something else
                                    elif op == 'put' \
                                        and condition.species == data.species_list_iter.default_species \
                                        or op == 'take' \
                                        and species.name == condition.species :
                                            coord = process.executing_coord() - condition.coord
                                            disabled_procs.append((process, coord))
                        # updating disabled procs is easy to do efficiently
                        # because we don't ask any questions twice, so we do it immediately
                        if disabled_procs:
                            out.write('    ! disable affected processes\n')
                        for process, coord in disabled_procs:
                            out.write(('    if(can_do(%(proc)s, site%(coord)s))then\n'
                            + '        call del_proc(%(proc)s, site%(coord)s)\n'
                            + '    endif\n\n') % {'coord':(coord).radd_ff(), 'proc':process.name})

                        # updating enabled procs is not so simply, because meeting one condition
                        # is not enough. We need to know if all other conditions are met as well
                        # so we collect  all questions first and build a tree, where the most
                        # frequent questions are closer to the top
                        if enabled_procs:
                            out.write('    ! enable affected processes\n')

                        self._write_optimal_iftree(items=enabled_procs, indent=4,out=out)
                        out.write('\nend subroutine %s\n\n' % routine_name)

        for layer in data.layer_list:
            for site in layer.sites:
                routine_name = 'touchup_%s_%s' % (layer.name, site.name)
                out.write('subroutine %s(site)\n\n' % routine_name)
                out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                items = []
                for process in data.process_list:
                    executing_coord = process.executing_coord()
                    if executing_coord.layer == layer.name \
                        and executing_coord.name == site.name:
                        condition_list = [ ConditionAction(
                            species=condition.species,
                            coord='site%s' % (condition.coord-executing_coord).radd_ff(),
                            ) for condition in process.condition_list ]
                        items.append((condition_list, (process.name, 'site', True)))

                self._write_optimal_iftree(items=items, indent=4, out=out)
                out.write('end subroutine %s\n\n' % routine_name)

        # TODO: subroutine get_char fuctions, the crumpy part
            
        out.write('end module proclist\n')
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
            # [1][2] field of the item determine if this search is intended for enabling (=True) or
            # disabling (=False) a process
            if item[1][2]:
                out.write('%scall add_proc(%s, %s)\n' % (' '*indent, item[1][0], item[1][1]))
            else:
                out.write('%scall del_proc(%s, %s)\n' % (' '*indent, item[1][0], item[1][1]))

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
        answers = [ y.species for y in filter(lambda x: x.coord==most_common_coord, flatten([x[0] for x in items]))]
        uniq_answers = list(set(answers))

        #DEBUGGING
        #print("ANSWERS %s" % answers)
        #print("UNIQ_ANSWERS %s" % uniq_answers)

        out.write('%sselect case(get_species(%s))\n' % ((indent)*' ', most_common_coord))
        for answer in uniq_answers:
            out.write('%scase(%s)\n' % ((indent)*' ', answer))
            # this very crazy expression matches at items that contain
            # a question for the same coordinate and have the same answer here
            nested_items = filter(
                lambda x: (most_common_coord in [y.coord for y in x[0]]
                and answer == filter(lambda y: y.coord == most_common_coord, x[0])[0].species),
                items)
            # pruned items are almost identical to nested items, except the have
            # the one condition removed, that we just met
            pruned_items = []
            for nested_item in nested_items:
                conditions = filter( lambda x: most_common_coord !=x.coord, nested_item[0])
                pruned_items.append((conditions,nested_item[1]))


            items = filter(lambda x: x not in nested_items, items)
            #print(len(nested_items))
            #print(nested_items)
            self._write_optimal_iftree(pruned_items, indent+4, out)
        out.write('%send select\n\n' % (indent*' ',))

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
