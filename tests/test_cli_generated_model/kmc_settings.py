model_name = 'test_cli_generated_model'
simulation_size = 20
representations = {
    "CO":"",
    "empty":"",
    "oxygen":"",
    }

lattice_representation = ""

site_names = ['default_cus']
parameters = {
    "p_CO":{"value":"0.2", "adjustable":False, "min":"0.0", "max":"0.0","scale":"log"},
    "T":{"value":"500", "adjustable":True, "min":"0.0", "max":"0.0","scale":"linear"},
    "p_O2":{"value":"1.0", "adjustable":True, "min":"0.0", "max":"0.0","scale":"linear"},
    }

rate_constants = {
    "CO_adsorption":("1000.", True),
    "CO_desorption":("1000.", True),
    }

tof_count = {
    }

