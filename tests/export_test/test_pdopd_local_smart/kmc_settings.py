model_name = 'sqrt5PdO'
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
    "E_adsorption_o2_bridge_bridge":{"value":"1.9", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_co_bridge":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_co_hollow":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_diff_co_bridge_bridge":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_diff_co_hollow_hollow":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_diff_o_bridge_bridge":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_diff_o_bridge_hollow":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_diff_o_hollow_hollow":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_o_bridge":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "E_o_hollow":{"value":"", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "lattice_size":{"value":"10 10 1", "adjustable":False, "min":"0.0", "max":"0.0","scale":"linear"},
    "T":{"value":"600", "adjustable":True, "min":"500.0", "max":"600.0","scale":"linear"},
    "p_co":{"value":"1.", "adjustable":True, "min":"0.0", "max":"0.0","scale":"linear"},
    "p_o2":{"value":"1.", "adjustable":True, "min":"0.0", "max":"0.0","scale":"linear"},
    }

rate_constants = {
    "destruct1":("10E15", False),
    "destruct10":("10E15", False),
    "destruct11":("10E15", False),
    "destruct2":("10E15", False),
    "destruct3":("10E15", False),
    "destruct4":("10E15", False),
    "destruct5":("10E15", False),
    "destruct6":("10E15", False),
    "destruct7":("10E15", False),
    "destruct8":("10E15", False),
    "destruct9":("10E15", False),
    "m_COads_b1":("10E8*p_co", True),
    "m_COads_b10":("10E8*p_co", True),
    "m_COads_b2":("10E8*p_co", True),
    "m_COads_b3":("10E8*p_co", True),
    "m_COads_b4":("10E8*p_co", True),
    "m_COads_b5":("10E8*p_co", True),
    "m_COads_b6":("10E8*p_co", True),
    "m_COads_b7":("10E8*p_co", True),
    "m_COads_b8":("10E8*p_co", True),
    "m_COads_b9":("10E8*p_co", True),
    "m_COdes_b1":("10E8", True),
    "m_COdes_b10":("10E8", True),
    "m_COdes_b2":("10E8", True),
    "m_COdes_b3":("10E8", True),
    "m_COdes_b4":("10E8", True),
    "m_COdes_b5":("10E8", True),
    "m_COdes_b6":("10E8", True),
    "m_COdes_b7":("10E8", True),
    "m_COdes_b8":("10E8", True),
    "m_COdes_b9":("10E8", True),
    "o_COads_bridge1":("10E8", True),
    "o_COads_bridge2":("10E8", True),
    "o_COads_hollow1":("10E8", True),
    "o_COads_hollow2":("10E8", True),
    "o_COdes_bridge1":("10E8", True),
    "o_COdes_bridge2":("10E8", True),
    "o_COdes_hollow1":("10E8", True),
    "o_COdes_hollow2":("10E8", True),
    "o_COdif_h1h2down":("10E8", True),
    "o_COdif_h1h2up":("10E8", True),
    "o_O2ads_h1h2":("10E12*p_o2", False),
    "o_O2ads_h2h1":("10E12*p_o2", False),
    "o_O2des_h1h2":("10E8", True),
    "o_O2des_h2h1":("10E8", True),
    "oxidize1":("10E15", True),
    }

site_names = ['Pd100_h1', 'Pd100_h2', 'Pd100_h4', 'Pd100_h5', 'Pd100_b1', 'Pd100_b2', 'Pd100_b3', 'Pd100_b4', 'Pd100_b5', 'Pd100_b6', 'Pd100_b7', 'Pd100_b8', 'Pd100_b9', 'Pd100_b10', 'Pd100_h3', 'PdO_bridge2', 'PdO_hollow1', 'PdO_hollow2', 'PdO_bridge1', 'PdO_Pd2', 'PdO_Pd3', 'PdO_Pd4', 'PdO_hollow3', 'PdO_hollow4', 'PdO_Pd1']
representations = {
    "CO":"""Atoms('CO',[[0,0,0],[0,0,1.2]])""",
    "Pd":"""Atoms('Pd',[[0,0,0]])""",
    "empty":"""""",
    "oxygen":"""Atoms('O',[[0,0,0]])""",
    }

lattice_representation = """[Atoms(symbols='Pd15',
          pbc=np.array([False, False, False], dtype=bool),
          cell=np.array(
      [[ 1.,  0.,  0.],
       [ 0.,  1.,  0.],
       [ 0.,  0.,  1.]]),
          scaled_positions=np.array(
      [[4.7453659, 0.3423996, -6.2962764], [5.92199, 2.865787, -6.2962764], [0.87534, 5.2190976, -6.2962764], [2.2219785, 1.5190861, -6.2962764], [3.398665, 4.0424111, -6.2962764], [2.820011, 5.9091707, -4.2497057], [0.340976, 0.918238, -4.2436278], [1.5767403, 3.4067118, -4.2507073], [5.2625035, 4.7117339, -4.2996003], [4.0675213, 2.194329, -4.2897029], [4.7417245, 0.3299249, -2.2558073], [5.9969157, 2.8580194, -2.2268554], [0.9748391, 5.2373292, -2.2376649], [2.198544, 1.5397536, -2.2315154], [3.4408186, 4.0677313, -2.3337728]]),
),]"""

species_tags = {
    "CO":"""""",
    "Pd":"""""",
    "empty":"""""",
    "oxygen":"""""",
    }

tof_count = {
    }

xml = """<?xml version="1.0" ?>
<kmc version="(0, 3)">
    <meta author="Max J. Hoffmann" debug="0" email="max.hoffmann@ch.tum.de" model_dimension="2" model_name="sqrt5PdO"/>
    <species_list default_species="empty">
        <species color="#000000" name="CO" representation="Atoms('CO',[[0,0,0],[0,0,1.2]])" tags=""/>
        <species color="#0034be" name="Pd" representation="Atoms('Pd',[[0,0,0]])" tags=""/>
        <species color="#fff" name="empty" representation="" tags=""/>
        <species color="#ff1717" name="oxygen" representation="Atoms('O',[[0,0,0]])" tags=""/>
    </species_list>
    <parameter_list>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_adsorption_o2_bridge_bridge" scale="linear" value="1.9"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_co_bridge" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_co_hollow" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_diff_co_bridge_bridge" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_diff_co_hollow_hollow" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_diff_o_bridge_bridge" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_diff_o_bridge_hollow" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_diff_o_hollow_hollow" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_o_bridge" scale="linear" value=""/>
        <parameter adjustable="False" max="0.0" min="0.0" name="E_o_hollow" scale="linear" value=""/>
        <parameter adjustable="True" max="600.0" min="500.0" name="T" scale="linear" value="600"/>
        <parameter adjustable="False" max="0.0" min="0.0" name="lattice_size" scale="linear" value="10 10 1"/>
        <parameter adjustable="True" max="0.0" min="0.0" name="p_co" scale="linear" value="1."/>
        <parameter adjustable="True" max="0.0" min="0.0" name="p_o2" scale="linear" value="1."/>
    </parameter_list>
    <lattice cell_size="1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0" default_layer="PdO" representation="[Atoms(symbols='Pd15',
          pbc=np.array([False, False, False], dtype=bool),
          cell=np.array(
      [[ 1.,  0.,  0.],
       [ 0.,  1.,  0.],
       [ 0.,  0.,  1.]]),
          scaled_positions=np.array(
      [[4.7453659, 0.3423996, -6.2962764], [5.92199, 2.865787, -6.2962764], [0.87534, 5.2190976, -6.2962764], [2.2219785, 1.5190861, -6.2962764], [3.398665, 4.0424111, -6.2962764], [2.820011, 5.9091707, -4.2497057], [0.340976, 0.918238, -4.2436278], [1.5767403, 3.4067118, -4.2507073], [5.2625035, 4.7117339, -4.2996003], [4.0675213, 2.194329, -4.2897029], [4.7417245, 0.3299249, -2.2558073], [5.9969157, 2.8580194, -2.2268554], [0.9748391, 5.2373292, -2.2376649], [2.198544, 1.5397536, -2.2315154], [3.4408186, 4.0677313, -2.3337728]]),
),]" substrate_layer="PdO">
        <layer color="#6dbf6e" name="Pd100">
            <site default_species="default_species" pos="0.1 0.1 0.0" tags="" type="h1"/>
            <site default_species="default_species" pos="0.3 0.5 0.0" tags="" type="h2"/>
            <site default_species="default_species" pos="0.9 0.7 0.0" tags="" type="h4"/>
            <site default_species="default_species" pos="0.7 0.3 0.0" tags="" type="h5"/>
            <site default_species="default_species" pos="0.2 0.3 0.0" tags="" type="b1"/>
            <site default_species="default_species" pos="0.4 0.7 0.0" tags="" type="b2"/>
            <site default_species="default_species" pos="0.5 0.4 0.0" tags="" type="b3"/>
            <site default_species="default_species" pos="0.9 0.2 0.0" tags="" type="b4"/>
            <site default_species="default_species" pos="0.8 0.5 0.0" tags="" type="b5"/>
            <site default_species="default_species" pos="0.7 0.8 0.0" tags="" type="b6"/>
            <site default_species="default_species" pos="0.1 0.6 0.0" tags="" type="b7"/>
            <site default_species="default_species" pos="0.6 0.1 0.0" tags="" type="b8"/>
            <site default_species="default_species" pos="0.3 0.0 0.0" tags="" type="b9"/>
            <site default_species="default_species" pos="0.0 0.9 0.0" tags="" type="b10"/>
            <site default_species="default_species" pos="0.5 0.9 0.0" tags="" type="h3"/>
        </layer>
        <layer color="#a14b49" name="PdO">
            <site default_species="empty" pos="0.5 0.5 0.1" tags="" type="bridge2"/>
            <site default_species="empty" pos="0.25 0.25 0.2" tags="" type="hollow1"/>
            <site default_species="empty" pos="0.25 0.75 0.2" tags="" type="hollow2"/>
            <site default_species="empty" pos="0.5 0.0 0.1" tags="" type="bridge1"/>
            <site default_species="Pd" pos="0.0 0.5 0.1" tags="" type="Pd2"/>
            <site default_species="Pd" pos="0.5 0.25 0.05" tags="" type="Pd3"/>
            <site default_species="Pd" pos="0.5 0.75 0.05" tags="" type="Pd4"/>
            <site default_species="oxygen" pos="0.75 0.25 0.0" tags="" type="hollow3"/>
            <site default_species="oxygen" pos="0.75 0.75 0.0" tags="" type="hollow4"/>
            <site default_species="Pd" pos="0.0 0.0 0.1" tags="" type="Pd1"/>
        </layer>
    </lattice>
    <process_list>
        <process enabled="False" name="destruct1" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^empty"/>
        </process>
        <process enabled="False" name="destruct10" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^empty"/>
        </process>
        <process enabled="False" name="destruct11" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^CO"/>
        </process>
        <process enabled="False" name="destruct2" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^CO"/>
        </process>
        <process enabled="False" name="destruct3" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^empty"/>
        </process>
        <process enabled="False" name="destruct4" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^empty"/>
        </process>
        <process enabled="False" name="destruct5" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^empty"/>
        </process>
        <process enabled="False" name="destruct6" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^empty"/>
        </process>
        <process enabled="False" name="destruct7" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^CO"/>
        </process>
        <process enabled="False" name="destruct8" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^empty"/>
        </process>
        <process enabled="False" name="destruct9" rate_constant="10E15">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="$CO"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="$CO"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="^CO"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="^CO"/>
        </process>
        <process enabled="True" name="m_COads_b1" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b10" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b10" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b2" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b2" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b2" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b3" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b3" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b3" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b4" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b4" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b4" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b5" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b5" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b5" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b6" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b6" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b6" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b7" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b7" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b8" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b8" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b8" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COads_b9" rate_constant="10E8*p_co">
            <condition coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="m_COdes_b1" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b10" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b10" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b2" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b2" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b2" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b3" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b3" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b3" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b4" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b4" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b4" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b5" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b5" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b5" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b6" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b6" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b6" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b7" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b7" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b8" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b8" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b8" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="m_COdes_b9" rate_constant="10E8">
            <condition coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="o_COads_bridge1" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="o_COads_bridge2" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="o_COads_hollow1" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="o_COads_hollow2" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="CO"/>
        </process>
        <process enabled="True" name="o_COdes_bridge1" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="o_COdes_bridge2" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="bridge2" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="o_COdes_hollow1" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="o_COdes_hollow2" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="o_COdif_h1h2down" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="o_COdif_h1h2up" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="CO"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="CO"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="False" name="o_O2ads_h1h2" rate_constant="10E12*p_o2">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="oxygen"/>
        </process>
        <process enabled="False" name="o_O2ads_h2h1" rate_constant="10E12*p_o2">
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 1 0" species="oxygen"/>
        </process>
        <process enabled="True" name="o_O2des_h1h2" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="o_O2des_h2h1" rate_constant="10E8">
            <condition coord_layer="PdO" coord_name="hollow1" coord_offset="0 1 0" species="oxygen"/>
            <condition coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="oxygen"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 1 0" species="empty"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="oxidize1" rate_constant="10E15">
            <condition coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="oxygen"/>
            <condition coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="empty"/>
            <condition coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="empty"/>
            <condition coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="empty"/>
            <action coord_layer="Pd100" coord_name="h1" coord_offset="0 0 0" species="$oxygen"/>
            <action coord_layer="Pd100" coord_name="b1" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="b9" coord_offset="0 0 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="b10" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="Pd100" coord_name="b7" coord_offset="0 -1 0" species="$empty"/>
            <action coord_layer="PdO" coord_name="hollow1" coord_offset="0 0 0" species="^oxygen"/>
            <action coord_layer="PdO" coord_name="hollow2" coord_offset="0 -1 0" species="^empty"/>
            <action coord_layer="PdO" coord_name="bridge1" coord_offset="0 0 0" species="^empty"/>
            <action coord_layer="PdO" coord_name="bridge2" coord_offset="0 -1 0" species="^empty"/>
        </process>
    </process_list>
    <output_list/>
</kmc>
"""
