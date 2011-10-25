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
    "co_desorption_bridge":("1000", True),
    "co_desorption_cus":("1000", True),
    "co_diffusion_bridge_bridge_down":("10**8", True),
    "co_diffusion_bridge_bridge_up":("10**8", True),
    "co_diffusion_bridge_cus_left":("10000", True),
    "co_diffusion_bridge_cus_right":("1000", True),
    "co_diffusion_cus_bridge_left":("10000", True),
    "co_diffusion_cus_bridge_right":("10000", True),
    "co_diffusion_cus_cus_down":("1000", True),
    "co_diffusion_cus_cus_up":("10000", True),
    "oxygen_adsorption_bridge_bridge":("100000", True),
    "oxygen_adsorption_bridge_cus_left":("100000", True),
    "oxygen_adsorption_bridge_cus_right":("100000", True),
    "oxygen_adsorption_cus_cus":("100000", True),
    "oxygen_desorption_bridge_bridge":("100000", True),
    "oxygen_desorption_bridge_cus_left":("100000", True),
    "oxygen_desorption_bridge_cus_right":("100000", True),
    "oxygen_desorption_cus_cus":("100000", True),
    "oxygen_diffusion_bridge_bridge_down":("100000", True),
    "oxygen_diffusion_bridge_bridge_up":("10000", True),
    "oxygen_diffusion_bridge_cus_left":("100000", True),
    "oxygen_diffusion_bridge_cus_right":("100000", True),
    "oxygen_diffusion_cus_bridge_left":("100000", True),
    "oxygen_diffusion_cus_bridge_right":("100000", True),
    "oxygen_diffusion_cus_cus_down":("100000", True),
    "oxygen_diffusion_cus_cus_up":("100000", True),
    "reaction_oxygen_bridge_co_bridge_down":("100000", True),
    "reaction_oxygen_bridge_co_bridge_up":("100000", True),
    "reaction_oxygen_bridge_co_cus_left":("100000", True),
    "reaction_oxygen_bridge_co_cus_right":("100000", True),
    "reaction_oxygen_cus_co_bridge_left":("100000", True),
    "reaction_oxygen_cus_co_bridge_right":("100000", True),
    "reaction_oxygen_cus_co_cus_down":("100000", True),
    "reaction_oxygen_cus_co_cus_up":("100000", True),
    }

tof_count = {
    }

