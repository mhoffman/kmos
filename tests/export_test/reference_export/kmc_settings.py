model_name = 'my_model'
simulation_size = 20
representations = {
    "co":"",
    "empty":"",
    "oxygen":"",
    }

lattice_representation = ""

parameters = {
    "A":{"value":"20.e-19", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_co_bridge":{"value":".1", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_co_cus":{"value":"0.5", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_o_bridge_bridge":{"value":"2.0", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_o_cus_bridge":{"value":"1.8", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_o_cus_cus":{"value":"1.7", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "T":{"value":"600", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "lattice_size":{"value":"20 20", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "m_co":{"value":"4.651235e-26", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "m_o2":{"value":"5.313525e-26", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "p_co":{"value":"1.0", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "p_o2":{"value":"1.0", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "print_every":{"value":"100000", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "total_steps":{"value":"10000000", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    }

rate_constants = {
    "co_adsorption_bridge":("10**8", True),
    "co_adsorption_cus":("10**8", True),
    "co_desorption_bridge":("", True),
    "co_desorption_cus":("", True),
    "co_diffusion_bridge_bridge_down":("10**8", True),
    "co_diffusion_bridge_bridge_up":("10**8", True),
    "co_diffusion_bridge_cus_left":("", True),
    "co_diffusion_bridge_cus_right":("", True),
    "co_diffusion_cus_bridge_left":("", True),
    "co_diffusion_cus_bridge_right":("", True),
    "co_diffusion_cus_cus_down":("", True),
    "co_diffusion_cus_cus_up":("", True),
    "oxygen_adsorption_bridge_bridge":("", True),
    "oxygen_adsorption_bridge_cus_left":("", True),
    "oxygen_adsorption_bridge_cus_right":("", True),
    "oxygen_adsorption_cus_cus":("", True),
    "oxygen_desorption_bridge_bridge":("", True),
    "oxygen_desorption_bridge_cus_left":("", True),
    "oxygen_desorption_bridge_cus_right":("", True),
    "oxygen_desorption_cus_cus":("", True),
    "oxygen_diffusion_bridge_bridge_down":("", True),
    "oxygen_diffusion_bridge_bridge_up":("", True),
    "oxygen_diffusion_bridge_cus_left":("", True),
    "oxygen_diffusion_bridge_cus_right":("", True),
    "oxygen_diffusion_cus_bridge_left":("", True),
    "oxygen_diffusion_cus_bridge_right":("", True),
    "oxygen_diffusion_cus_cus_down":("", True),
    "oxygen_diffusion_cus_cus_up":("", True),
    "reaction_oxygen_bridge_co_bridge_down":("", True),
    "reaction_oxygen_bridge_co_bridge_up":("", True),
    "reaction_oxygen_bridge_co_cus_left":("", True),
    "reaction_oxygen_bridge_co_cus_right":("", True),
    "reaction_oxygen_cus_co_bridge_left":("", True),
    "reaction_oxygen_cus_co_bridge_right":("", True),
    "reaction_oxygen_cus_co_cus_down":("", True),
    "reaction_oxygen_cus_co_cus_up":("", True),
    }

tof_count = {
    }

