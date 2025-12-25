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
<kmc version="(0, 3)">
    <meta author="Max J. Hoffmann" email="mjhoffmann@gmail.com" model_name="my_model" model_dimension="2" debug="0"/>
    <species_list default_species="empty">
        <species name="co" representation="" color="#000000" tags=""/>
        <species name="empty" representation="" color="#ffffff" tags=""/>
        <species name="oxygen" representation="" color="#ff0000" tags=""/>
    </species_list>
    <parameter_list>
        <parameter name="A" value="20.e-19" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="E_co_bridge" value=".1" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="E_co_cus" value="0.5" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="E_o_bridge_bridge" value="2.0" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="E_o_cus_bridge" value="1.8" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="E_o_cus_cus" value="1.7" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="T" value="600" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="lattice_size" value="20 20" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="m_co" value="4.651235e-26" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="m_o2" value="5.313525e-26" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="p_co" value="1.0" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="p_o2" value="1.0" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="print_every" value="100000" adjustable="False" min="0.0" max="0.0" scale="linear"/>
        <parameter name="total_steps" value="10000000" adjustable="False" min="0.0" max="0.0" scale="linear"/>
    </parameter_list>
    <lattice cell_size="10.0 0.0 0.0 0.0 10.0 0.0 0.0 0.0 3.0" default_layer="ruo2" substrate_layer="ruo2" representation="">
        <layer name="ruo2" color="#ffffff">
            <site pos="0.0 0.0 0.5" type="bridge" tags="" default_species="default_species"/>
            <site pos="0.0 0.5 0.5" type="cus" tags="" default_species="default_species"/>
        </layer>
    </lattice>
    <process_list>
        <process rate_constant="10**8" name="co_adsorption_bridge" enabled="True">
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10**8" name="co_adsorption_cus" enabled="True">
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="1000" name="co_desorption_bridge" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="1000" name="co_desorption_cus" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10**8" name="co_diffusion_bridge_bridge_down" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0"/>
            <action species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10**8" name="co_diffusion_bridge_bridge_up" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10000" name="co_diffusion_bridge_cus_left" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="co" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
        </process>
        <process rate_constant="1000" name="co_diffusion_bridge_cus_right" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10000" name="co_diffusion_cus_bridge_left" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10000" name="co_diffusion_cus_bridge_right" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0"/>
        </process>
        <process rate_constant="1000" name="co_diffusion_cus_cus_down" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0"/>
            <action species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10000" name="co_diffusion_cus_cus_up" enabled="True">
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_adsorption_bridge_bridge" enabled="True">
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_adsorption_bridge_cus_left" enabled="True">
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_adsorption_bridge_cus_right" enabled="True">
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_adsorption_cus_cus" enabled="True">
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_desorption_bridge_bridge" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_desorption_bridge_cus_left" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_desorption_bridge_cus_right" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_desorption_cus_cus" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_diffusion_bridge_bridge_down" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="10000" name="oxygen_diffusion_bridge_bridge_up" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_diffusion_bridge_cus_left" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_diffusion_bridge_cus_right" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_diffusion_cus_bridge_left" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_diffusion_cus_bridge_right" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_diffusion_cus_cus_down" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="oxygen_diffusion_cus_cus_up" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
            <action species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_bridge_co_bridge_down" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 -1 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_bridge_co_bridge_up" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_bridge_co_cus_left" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="-1 0 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_bridge_co_cus_right" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_cus_co_bridge_left" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="0 0 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_cus_co_bridge_right" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="bridge" coord_offset="1 0 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_cus_co_cus_down" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 -1 0"/>
        </process>
        <process rate_constant="100000" name="reaction_oxygen_cus_co_cus_up" enabled="True">
            <condition species="oxygen" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <condition species="co" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 0 0"/>
            <action species="empty" coord_layer="ruo2" coord_name="cus" coord_offset="0 1 0"/>
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
