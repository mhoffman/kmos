import numpy as np

"""
A  module to run the acf features for a compiled kMC model.

The model can be used directly like so::

    import kmos.run.acf as acf
    from kmos.run import KMC_Model
    import kmos.run.acf as acf

    model = KMC_Model()

    nr_of_steps = 1e7

    nr_of_types = 2

    t_bin = 0.0005
    t_f = 0.022
    safety_factor = 1
    extending_factor = 3 

    types = [0.5,1]
    site_types = [['default_a_1','default_a_2','default_b_1','default_b_2'],[1,1,2,2]]

    acf.allocate_acf(model,nr_of_types,t_bin,t_f,safety_factor,extending_factor)

    for i in range(len(types)):
  	 acf.set_types_acf(model,types[i])

    acf.calc_product_property(model)

    for i in range(len(site_types[0])):
    	acf.set_property_acf(model,site_types[0][i],site_types[1][i])

    acf.initialize_acf(model,species = 'ion')

    acf.do_kmc_steps_acf(model,nr_of_steps)

    ACF = acf.get_acf(model,normalization = False)

which, of course can also be part of a python script.
"""

#    Copyright 2015-2016 Andreas Garhammer
#    This file is part of kmos.

def get_id_arr(kmc_model):
    """Return the id's from id_arr.
    """
    id_arr = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        id_arr[i] = kmc_model.base_acf.get_id_arr(i + 1)
    return id_arr


def get_site_arr(kmc_model):
    """Return the site indices from site_arr.
    """
    site_arr = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        site_arr[i] = kmc_model.base_acf.get_site_arr(i + 1)
    return site_arr


def get_property_o(kmc_model):
    """Return the property_o (g(0)) for each tracked particle
    from property_o.
    """
    property_o = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        property_o[i] = kmc_model.base_acf.get_property_o(i + 1)
    return property_o


def get_property_acf(kmc_model):
    """Return the type indices for each site from property_acf.
    """
    property_acf = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        property_acf[i] = kmc_model.base_acf.get_property_acf(i + 1)
    return property_acf


def get_buffer_acf(kmc_model):
    """Return the product of properties (g(0)(g(t))) for each
    tracked particle from buffer_acf.
    """
    buffer_acf = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        buffer_acf[i] = kmc_model.base_acf.get_buffer_acf(i + 1)
    return buffer_acf


def get_config_bin_acf(kmc_model):
    """Return the entries for each bin from config_bin.
    """
    config_bin = np.zeros((kmc_model.base_acf.extended_nr_of_bins))
    for i in range(kmc_model.base_acf.extended_nr_of_bins):
        config_bin[i] = kmc_model.base_acf.get_config_bin_acf(i + 1)
    return config_bin


def get_counter_write_in_bin_acf(kmc_model):
    """Return the number of contributions to each bin from
    counter_write_in_bin.
    """
    contribution_bin = np.zeros((kmc_model.base_acf.extended_nr_of_bins))
    for i in range(kmc_model.base_acf.extended_nr_of_bins):
        contribution_bin[
            i] = kmc_model.base_acf.get_counter_write_in_bin(i + 1)
    return contribution_bin


def get_acf(kmc_model):
    """Returns the ACF.
    """
    acf = np.zeros((kmc_model.base_acf.nr_of_bins))
    for i in range(kmc_model.base_acf.nr_of_bins):
        acf[i] = kmc_model.base_acf.calc_acf(i + 1)
    return acf


def get_types_acf(kmc_model):
    """Return the properties of each type from
    from types.
    """
    types_arr = np.zeros((kmc_model.base_acf.nr_of_types))
    for i in range(kmc_model.base_acf.nr_of_types):
        types_arr[i] = kmc_model.base_acf.get_types(i + 1)
    return types_arr


def get_product_property(kmc_model):
    """Return the matrix with all possible combinations of products
    between two properties (g(0)g(t)).
    """
    product_property = np.zeros(
        (1, kmc_model.base_acf.nr_of_types, kmc_model.base_acf.nr_of_types))
    for i in range(kmc_model.base_acf.nr_of_types):
        for j in range(kmc_model.base_acf.nr_of_types):
            product_property[
                0, i, j] = kmc_model.base_acf.get_product_property(i + 1, j + 1)
    return product_property


def get_trajectory(kmc_model):
    """Return the trajectory for each tracked particle from
    from trajectory.
    """
    trajectory = np.zeros(
        (1, kmc_model.base_acf.nr_of_ions, kmc_model.base_acf.nr_of_steps + 1),
        'int')
    for i in range(kmc_model.base_acf.nr_of_ions):
        for j in range(kmc_model.base_acf.nr_of_steps + 1):
            trajectory[0, i, j] = kmc_model.base_acf.get_trajectory(
                i + 1, j + 1)
    return trajectory


def get_displacement(kmc_model):
    """Return the displacement for each tracked particle from
    from displacement.
    """
    displacement = np.zeros((1, kmc_model.base_acf.nr_of_ions, 3))
    for i in range(kmc_model.base_acf.nr_of_ions):
        displacement[0, i] = kmc_model.base_acf.get_displacement(i + 1)
    return displacement


def allocate_acf(kmc_model, nr_of_types, t_bin, t_f, safety_factor=None, extending_factor=None):
    """Allocate the whole arrays for the tracking process and for
    the sampling of the ACF.
    """
    kmc_model.base_acf.allocate_tracing_arr(nr_of_types)
    kmc_model.base_acf.allocate_config_bin_acf(
        t_bin, t_f, safety_factor, extending_factor)


def allocate_trajectory(kmc_model, nr_of_steps):
    """Allocates the trajectory array for the recording of the trajectory 
    of each tracked particle. The user has to specify for how many kMC steps
    the trajectory should be recorded. 
    """
    kmc_model.base_acf.allocate_trajectory(nr_of_steps)


def set_types_acf(kmc_model, site_property):
    """Set the properties, which are given by the user to 
       a type index.
    """
    types = get_types_acf(kmc_model)
    for i in range(len(types)):
        if types[i] == 0:
            kmc_model.base_acf.set_types(i + 1, site_property)
            break


def calc_product_property(kmc_model, ):
    """Caculate and set all possible combinations of products
    between two properties(g(0)g(t)).
    """
    types = get_types_acf(kmc_model)
    for i in range(kmc_model.base_acf.nr_of_types):
        for j in range(kmc_model.base_acf.nr_of_types):
            kmc_model.base_acf.set_product_property(
                i + 1, j + 1, types[i] * types[j])


def do_kmc_steps_acf(kmc_model, n, traj_on=False):
    """Performs n kMC steps for the sampling of ACF.
    Recording of the trajectory is optional
    (on: traj_on = True, off: traj_on = False).
    """
    kmc_model.proclist_acf.do_kmc_steps_acf(n, traj_on)


def do_kmc_steps_displacement(kmc_model, n, traj_on=False):
    """Performs n kMC steps for the recording of the displacment
    for each tracked particle.
    Recording of the trajectory is optional
    (on: traj_on = True, off: traj_on = False).
    """
    kmc_model.proclist_acf.do_kmc_steps_displacement(n, traj_on)


def initialize_acf(kmc_model, species):
    """Initialize the whole arrays for the tracking process
    and for the sampling of the ACF for a given species.
    """
    trace_species = getattr(kmc_model.proclist, species.lower())
    kmc_model.base_acf.initialize_acf(trace_species)


def initialize_msd(kmc_model, species):
    """Initialize the whole arrays for the tracking process
    and for the recording of displacement for a given species.
    """
    trace_species = getattr(kmc_model.proclist, species.lower())
    kmc_model.base_acf.initialize_mean_squared_displacement(trace_species)


def calc_msd(kmc_model):
    """Calculates the mean squared displacement (msd) as a particle average
    from the displacements of the tracked particles.
    """
    msd = kmc_model.base_acf.calc_mean_squared_disp()
    return msd


def set_property_acf(kmc_model, layer_site_name, property_type):
    """Set types indices of corresponding properties to sites, for which
    the site_names are given by the user.
    """
    for i in range((kmc_model.base.get_volume())):
        if ((i + 1) % kmc_model.lattice.spuck) + kmc_model.lattice.spuck == getattr(kmc_model.lattice, layer_site_name.lower()):
            kmc_model.base_acf.set_property_acf(i + 1, property_type)
        if (i + 1) % kmc_model.lattice.spuck == getattr(kmc_model.lattice, layer_site_name.lower()):
            kmc_model.base_acf.set_property_acf(i + 1, property_type)


def get_acf(kmc_model, normalization=False):
    """Return the ACF.
    The normalization of the ACF is optional.
    (on: normalization = True, off: normalization = False)
    """
    acf = np.zeros((kmc_model.base_acf.nr_of_bins))
    for i in range(kmc_model.base_acf.nr_of_bins):
        acf[i] = kmc_model.base_acf.calc_acf(i + 1)
    if normalization == True:
        acf = acf / acf[0]
    return acf


def set_acf_to_zero(kmc_model):
    """Set all acf arrays and parameters to initial state
    After this, the sampling of ACF can start from new.
    """
    kmc_model.base_acf.set_acf_to_zero()


def set_displacement_to_zero(kmc_model):
    """Sets the displacement vector to zero.
    After this, the recording of the displacement can start
    from new.
    """
    kmc_model.base_acf.set_displacement_to_zero()
