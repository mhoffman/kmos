import os
gpl = self._gpl_message()
#@ {gpl}!****h* kmos/proclist
#@ ! FUNCTION
#@ !    Implements the kMC process list.
#@ !
#@ !******
#@
#@
#@ module {module_name}
#@ use kind_values
if code_generator == 'local_smart':
    #@ use base, only: &
    #@     update_accum_rate, &
    #@     update_integ_rate, &
    #@     determine_procsite, &
    #@     update_clocks, &
    #@     avail_sites, &
    if len(data.layer_list) == 1 : # multi-lattice mode
        #@     null_species, &
    else:
        #@     set_null_species, &
    #@     increment_procstat
    #@
#@ use lattice, only: &
site_params = []
for layer in data.layer_list:
    #@     {layer.name}, &
    for site in layer.sites:
        site_params.append((site.name, layer.name))

for i, (site, layer) in enumerate(site_params):
    #@     {layer}_{site}, &
if code_generator == 'local_smart':
    #@     allocate_system, &
    #@     nr2lattice, &
    #@     lattice2nr, &
    #@     add_proc, &
    #@     can_do, &
    #@     set_rate_const, &
    #@     replace_species, &
    #@     del_proc, &
    #@     reset_site, &
    #@     system_size, &
    #@     spuck, &
#@     get_species
#@ 
#@ 
#@ implicit none
#@ 
#@ 
#@ 

# initialize various parameter kind of data
#@  ! Species constants
#@
#@
#@
len_species_list = len(data.species_list)
len_species_list_p1 = len(data.species_list) + 1
if len(data.layer_list) > 1 : # multi-lattice mode
    #@ integer(kind=iint), parameter, public :: nr_of_species = {len_species_list_p1}
else:
    #@ integer(kind=iint), parameter, public :: nr_of_species = {len_species_list}
for i, species in enumerate(sorted(data.species_list, key=lambda x: x.name)):
    #@ integer(kind=iint), parameter, public :: {species.name} = {i}
if len(data.layer_list) > 1 : # multi-lattice mode
    #@ integer(kind=iint), parameter, public :: null_species = {len_species_list}
    #@
#@ integer(kind=iint), public :: default_species = {data.species_list.default_species}
#@
#@
#@ ! Process constants
#@
for i, process in enumerate(self.data.process_list):
    ip1 = i + 1
    #@ integer(kind=iint), parameter, public :: {process.name} = {ip1}

if code_generator == 'local_smart':
    representation_length = max([len(species.representation) for species in data.species_list])
    #@
    #@
    #@ integer(kind=iint), parameter, public :: representation_length = {representation_length}
    if os.name == 'posix':
        #@ integer(kind=iint), public :: seed_size = 12
    elif os.name == 'nt':
        #@ integer(kind=iint), public :: seed_size = 12
    else:
        #@ integer(kind=iint), public :: seed_size = 8
    #@ integer(kind=iint), public :: seed ! random seed
    #@ integer(kind=iint), public, dimension(:), allocatable :: seed_arr ! random seed
    #@
    #@
    len_process_list = len(data.process_list)
    #@ integer(kind=iint), parameter, public :: nr_of_proc = {len_process_list}

if close_module:
    #@
    #@
    #@ end module
