import numpy as np
import kmc_model

def get_id_arr():
    id_arr = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        id_arr[i] = kmc_model.base_acf.get_id_arr(i + 1)
    return id_arr

def get_site_arr():
    site_arr = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        site_arr[i] = kmc_model.base_acf.get_site_arr(i + 1)
    return site_arr

def get_property_o():
    property_o = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        property_o[i] = kmc_model.base_acf.get_property_o(i + 1)
    return property_o

def get_property_acf():
    property_acf = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        property_acf[i] = kmc_model.base_acf.get_property_acf(i + 1)
    return property_acf

def get_buffer_acf():
    buffer_acf = np.zeros((kmc_model.base.get_volume()))
    for i in range(kmc_model.base.get_volume()):
        buffer_acf[i] = kmc_model.base_acf.get_buffer_acf(i + 1)
    return buffer_acf

def get_config_bin_acf():
    config_bin = np.zeros((kmc_model.base_acf.extended_nr_of_bins))
    for i in range(kmc_model.base_acf.extended_nr_of_bins):
        config_bin[i] = kmc_model.base_acf.get_config_bin_acf(i + 1)
    return config_bin

def get_counter_write_in_bin_acf():
    contribution_bin = np.zeros((kmc_model.base_acf.extended_nr_of_bins))
    for i in range(kmc_model.base_acf.extended_nr_of_bins):
        contribution_bin[i] = kmc_model.base_acf.get_counter_write_in_bin(i + 1)
    return contribution_bin

def get_acf():
    acf = np.zeros((kmc_model.base_acf.nr_of_bins))
    for i in range(kmc_model.base_acf.nr_of_bins):
        acf[i] = kmc_model.base_acf.calc_acf(i + 1)
    return acf

def get_types_acf():
    types_arr = np.zeros((kmc_model.base_acf.nr_of_types))
    for i in range(kmc_model.base_acf.nr_of_types):
        types_arr[i] = kmc_model.base_acf.get_types(i + 1)
    return types_arr

def get_product_property():
    product_property = np.zeros((1,kmc_model.base_acf.nr_of_types,kmc_model.base_acf.nr_of_types))
    for i in range(kmc_model.base_acf.nr_of_types):
        for j in range(kmc_model.base_acf.nr_of_types):
            product_property[0,i,j] = kmc_model.base_acf.get_product_property(i + 1, j + 1)
    return product_property

def allocate_acf(nr_of_types,t_bin,t_f,safety_factor=None,extending_factor=None):
    kmc_model.base_acf.allocate_tracing_arr(nr_of_types)
    kmc_model.base_acf.allocate_config_bin_acf(t_bin,t_f,safety_factor,extending_factor)
    
def set_types_acf(site_property):
    types = get_types_acf()
    for i in range(len(types)):
        if  types[i] == 0:
            kmc_model.base_acf.set_types(i + 1,site_property)
            break
    
def calc_product_property():
    types = get_types_acf()
    for i in range(kmc_model.base_acf.nr_of_types):
        for j in range(kmc_model.base_acf.nr_of_types):
            kmc_model.base_acf.set_product_property(i + 1,j + 1,types[i]*types[j])

def do_kmc_steps_acf(n):
    kmc_model.proclist_acf.do_kmc_steps_acf(n)

def initialize_acf(species):
    trace_species = getattr(kmc_model.proclist,species.lower())
    kmc_model.base_acf.initialize_acf(trace_species)
     

def set_property_acf(layer_site_name,property_type):
    for i in range((kmc_model.base.get_volume())): 
        if i + 1 % kmc_model.lattice.spuck == getattr(kmc_model.lattice,layer_site_name.lower()):
           kmc_model.base_acf.set_property_acf(i + 1,property_type)

def get_acf(normalization = False):
    acf = np.zeros((kmc_model.base_acf.nr_of_bins))
    for i in range(kmc_model.base_acf.nr_of_bins):
        acf[i] = kmc_model.base_acf.calc_acf(i + 1)
    if normalization == True:
       acf = acf/acf[0]
    return acf
   
