import numpy as np


def get_id_arr(kmc_model):
    id_arr = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        id_arr[i] = kmc_model.base_acf.get_id_arr(i + 1)
    return id_arr


def get_site_arr(kmc_model):
    site_arr = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        site_arr[i] = kmc_model.base_acf.get_site_arr(i + 1)
    return site_arr


def get_property_o(kmc_model):
    property_o = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        property_o[i] = kmc_model.base_acf.get_property_o(i + 1)
    return property_o


def get_property_acf(kmc_model):
    property_acf = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        property_acf[i] = kmc_model.base_acf.get_property_acf(i + 1)
    return property_acf


def get_buffer_acf(kmc_model):
    buffer_acf = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        buffer_acf[i] = kmc_model.base_acf.get_buffer_acf(i + 1)
    return buffer_acf


def get_config_bin_acf(kmc_model):
    config_bin = np.zeros((kmc_model.base_acf.extended_nr_of_bins))
    for i in range(kmc_model.base_acf.extended_nr_of_bins):
        config_bin[i] = kmc_model.base_acf.get_config_bin_acf(i + 1)
    return config_bin


def get_counter_write_in_bin_acf(kmc_model):
    contribution_bin = np.zeros((kmc_model.base_acf.extended_nr_of_bins))
    for i in range(kmc_model.base_acf.extended_nr_of_bins):
        contribution_bin[
            i] = kmc_model.base_acf.get_counter_write_in_bin(i + 1)
    return contribution_bin


def get_acf(kmc_model):
    acf = np.zeros((kmc_model.base_acf.nr_of_bins))
    for i in range(kmc_model.base_acf.nr_of_bins):
        acf[i] = kmc_model.base_acf.calc_acf(i + 1)
    return acf


def get_types_acf(kmc_model):
    types_arr = np.zeros((kmc_model.base_acf.nr_of_types))
    for i in range(kmc_model.base_acf.nr_of_types):
        types_arr[i] = kmc_model.base_acf.get_types(i + 1)
    return types_arr


def get_product_property(kmc_model):
    product_property = np.zeros(
        (1, kmc_model.base_acf.nr_of_types, kmc_model.base_acf.nr_of_types))
    for i in range(kmc_model.base_acf.nr_of_types):
        for j in range(kmc_model.base_acf.nr_of_types):
            product_property[
                0, i, j] = kmc_model.base_acf.get_product_property(i + 1, j + 1)
    return product_property


def get_trajectory(kmc_model):
    trajectory = np.zeros(
        (1, kmc_model.base_acf.nr_of_ions, kmc_model.base_acf.nr_of_steps + 1))
    for i in range(kmc_model.base_acf.nr_of_ions):
        for j in range(kmc_model.base_acf.nr_of_steps + 1):
            trajectory[0, i, j] = kmc_model.base_acf.get_trajectory(
                i + 1, j + 1)
    return trajectory


def get_displacement(kmc_model):
    displacement = np.zeros((1, kmc_model.base_acf.nr_of_ions, 3))
    for i in range(kmc_model.base_acf.nr_of_ions):
        displacement[0, i] = kmc_model.base_acf.get_displacement(i + 1)
    return displacement


def allocate_acf(kmc_model, nr_of_types, t_bin, t_f, safety_factor=None, extending_factor=None):
    kmc_model.base_acf.allocate_tracing_arr(nr_of_types)
    kmc_model.base_acf.allocate_config_bin_acf(
        t_bin, t_f, safety_factor, extending_factor)


def allocate_trajectory(kmc_model, nr_of_steps):
    kmc_model.base_acf.allocate_trajectory(nr_of_steps)


def set_types_acf(kmc_model, site_property):
    types = get_types_acf()
    for i in range(len(types)):
        if types[i] == 0:
            kmc_model.base_acf.set_types(i + 1, site_property)
            break


def calc_product_property(kmc_model, ):
    types = get_types_acf()
    for i in range(kmc_model.base_acf.nr_of_types):
        for j in range(kmc_model.base_acf.nr_of_types):
            kmc_model.base_acf.set_product_property(
                i + 1, j + 1, types[i] * types[j])


def do_kmc_steps_acf(kmc_model, n, traj_on=False):
    kmc_model.proclist_acf.do_kmc_steps_acf(n, traj_on)


def do_kmc_steps_displacement(kmc_model, n, traj_on=False):
    kmc_model.proclist_acf.do_kmc_steps_displacement(n, traj_on)


def initialize_acf(kmc_model, species):
    trace_species = getattr(kmc_model.proclist, species.lower())
    kmc_model.base_acf.initialize_acf(trace_species)


def initialize_msd(kmc_model, species):
    trace_species = getattr(kmc_model.proclist, species.lower())
    kmc_model.base_acf.initialize_mean_squared_displacement(trace_species)


def calc_msd(kmc_model):
    msd = kmc_model.base_acf.calc_mean_squared_disp()
    return msd


def set_property_acf(kmc_model, layer_site_name, property_type):
    for i in range((kmc_model.base.get_volume())):
        if ((i + 1) % kmc_model.lattice.spuck) + kmc_model.lattice.spuck == getattr(kmc_model.lattice, layer_site_name.lower()):
            kmc_model.base_acf.set_property_acf(i + 1, property_type)
        if (i + 1) % kmc_model.lattice.spuck == getattr(kmc_model.lattice, layer_site_name.lower()):
            kmc_model.base_acf.set_property_acf(i + 1, property_type)


def get_acf(kmc_model, normalization=False):
    acf = np.zeros((kmc_model.base_acf.nr_of_bins))
    for i in range(kmc_model.base_acf.nr_of_bins):
        acf[i] = kmc_model.base_acf.calc_acf(i + 1)
    if normalization == True:
        acf = acf / acf[0]
    return acf


def set_acf_to_zero(kmc_model):
    kmc_model.base_acf.set_acf_to_zero()


def set_displacement_to_zero(kmc_model):
    kmc_model.base_acf.set_displacement_to_zero()
