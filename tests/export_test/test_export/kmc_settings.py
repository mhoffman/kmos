model_name = 'my_model'
simulation_size = 20
random_seed = 1

def setup_model(model):
    """Write initialization steps here.
       e.g. ::
    model.put([0,0,0,model.lattice.default_a], model.proclist.species_a)
    """
    #from setup_model import setup_model
    #setup_model(model)
    pass

# Default history length in graph
hist_length = 30

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

site_names = ['ruo2_bridge', 'ruo2_cus']
representations = {
    "co":"""""",
    "empty":"""""",
    "oxygen":"""""",
    }

lattice_representation = """"""

species_tags = {
    "co":"""""",
    "empty":"""""",
    "oxygen":"""""",
    }

tof_count = {
    }

xml = """<?xml version="1.0" ?>
<kmc version="(0, 2)">
    <meta author="Max J. Hoffmann" debug="0" email="mjhoffmann@gmail.com" model_dimension="2" model_name="my_model"/>
    <species_list default_species="empty">
        <species color="#000000" name="co" representation="" tags=""/>
        <species color="#ffffff" name="empty" representation="" tags=""/>
        <species color="#ff0000" name="oxygen" representation="" tags=""/>
    </species_list>
    <parameter_list>
        <parameter adjustable="False" max="0.0" min="0.0" name="A" scale="linear" value="20.e-19"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_co_bridge" scale="linear" value=".1"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_co_cus" scale="linear" value="0.5"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_o_bridge_bridge" scale="linear" value="2.0"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_o_cus_bridge" scale="linear" value="1.8"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_o_cus_cus" scale="linear" value="1.7"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="T" scale="linear" value="600"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="lattice_size" scale="linear" value="20 20"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="m_co" scale="linear" value="4.651235e-26"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="m_o2" scale="linear" value="5.313525e-26"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="p_co" scale="linear" value="1.0"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="p_o2" scale="linear" value="1.0"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="print_every" scale="linear" value="100000"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="total_steps" scale="linear" value="10000000"/>
    </parameter_list>
    <lattice cell_size="10.0 0.0 0.0 0.0 10.0 0.0 0.0 0.0 3.0" default_layer="ruo2" representation="" substrate_layer="ruo2">
        <layer color="#ffffff" name="ruo2">
            <site default_species="default_species" pos="0.0 0.0 0.5" tags="" type="bridge"/>
            <site default_species="default_species" pos="0.0 0.5 0.5" tags="" type="cus"/>
        </layer>
    </lattice>
    <process_list>
        <process enabled="True" name="co_adsorption_bridge" rate_constant="10**8">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
        </process>
        <process enabled="True" name="co_adsorption_cus" rate_constant="10**8">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
        </process>
        <process enabled="True" name="co_desorption_bridge" rate_constant="1000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="co_desorption_cus" rate_constant="1000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="co_diffusion_bridge_bridge_down" rate_constant="10**8">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0" species="co"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="co_diffusion_bridge_bridge_up" rate_constant="10**8">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="co"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="co_diffusion_bridge_cus_left" rate_constant="10000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="co"/>
        </process>
        <process enabled="True" name="co_diffusion_bridge_cus_right" rate_constant="1000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
        </process>
        <process enabled="True" name="co_diffusion_cus_bridge_left" rate_constant="10000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="co_diffusion_cus_bridge_right" rate_constant="10000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0" species="co"/>
        </process>
        <process enabled="True" name="co_diffusion_cus_cus_down" rate_constant="1000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0" species="co"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="co_diffusion_cus_cus_up" rate_constant="10000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="co"/>
        </process>
        <process enabled="True" name="oxygen_adsorption_bridge_bridge" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_adsorption_bridge_cus_left" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_adsorption_bridge_cus_right" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_adsorption_cus_cus" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_desorption_bridge_bridge" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxygen_desorption_bridge_cus_left" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxygen_desorption_bridge_cus_right" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxygen_desorption_cus_cus" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_bridge_bridge_down" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_bridge_bridge_up" rate_constant="10000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_bridge_cus_left" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_bridge_cus_right" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_cus_bridge_left" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_cus_bridge_right" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0" species="oxygen"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_cus_cus_down" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxygen_diffusion_cus_cus_up" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="oxygen"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_bridge_co_bridge_down" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0" species="co"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_bridge_co_bridge_up" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="co"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_bridge_co_cus_left" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="co"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_bridge_co_cus_right" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="co"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_cus_co_bridge_left" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="co"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_cus_co_bridge_right" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0" species="co"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_cus_co_cus_down" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0" species="co"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0" species="empty"/>
        </process>
        <process enabled="True" name="reaction_oxygen_cus_co_cus_up" rate_constant="100000">
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="co"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0" species="empty"/>
        </process>
    </process_list>
    <output_list>
        <output item="co"/>
        <output item="co@bridge"/>
        <output item="co_adsorption_bridge"/>
        <output item="kmc_time"/>
        <output item="oxygen"/>
        <output item="walltime"/>
    </output_list>
</kmc>
"""
