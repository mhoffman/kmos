model_name = 'simple_model'
simulation_size = 1
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
    }

rate_constants = {
    "adsA":("1", True),
    "adsB":("20", True),
    "desA":("10", True),
    "desB":("1", True),
    "react":("1", True),
    "unreact":("10", True),
    }

site_names = ['default_s']
representations = {
    "A":"""""",
    "B":"""""",
    "empty":"""""",
    }

lattice_representation = """"""

species_tags = {
    "A":"""""",
    "B":"""""",
    "empty":"""""",
    }

tof_count = {
    "react":{'react': 1},
    "unreact":{'unreact': 1},
    }

xml = """<?xml version="1.0" ?>
<kmc version="(0, 2)">
    <meta author="Felix Engelmann" debug="0" email="felix.engelmann@tum.de" model_dimension="1" model_name="simple_model"/>
    <species_list default_species="empty">
        <species color="" name="A" representation="" tags=""/>
        <species color="" name="B" representation="" tags=""/>
        <species color="" name="empty" representation="" tags=""/>
    </species_list>
    <parameter_list/>
    <lattice cell_size="1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0" default_layer="default" representation="" substrate_layer="default">
        <layer color="#ffffff" name="default">
            <site default_species="default_species" pos="0.0 0.0 0.0" tags="" type="s"/>
        </layer>
    </lattice>
    <process_list>
        <process enabled="True" name="adsA" rate_constant="1">
            <condition coord_layer="default" coord_name="s" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="default" coord_name="s" coord_offset="0 0 0" species="A"/>
        </process>
        <process enabled="True" name="adsB" rate_constant="20">
            <condition coord_layer="default" coord_name="s" coord_offset="0 0 0" species="empty"/>
            <action coord_layer="default" coord_name="s" coord_offset="0 0 0" species="B"/>
        </process>
        <process enabled="True" name="desA" rate_constant="10">
            <condition coord_layer="default" coord_name="s" coord_offset="0 0 0" species="A"/>
            <action coord_layer="default" coord_name="s" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="desB" rate_constant="1">
            <condition coord_layer="default" coord_name="s" coord_offset="0 0 0" species="B"/>
            <action coord_layer="default" coord_name="s" coord_offset="0 0 0" species="empty"/>
        </process>
        <process enabled="True" name="react" rate_constant="1" tof_count="{'react': 1}">
            <condition coord_layer="default" coord_name="s" coord_offset="0 0 0" species="A"/>
            <action coord_layer="default" coord_name="s" coord_offset="0 0 0" species="B"/>
        </process>
        <process enabled="True" name="unreact" rate_constant="10" tof_count="{'unreact': 1}">
            <condition coord_layer="default" coord_name="s" coord_offset="0 0 0" species="B"/>
            <action coord_layer="default" coord_name="s" coord_offset="0 0 0" species="A"/>
        </process>
    </process_list>
    <output_list/>
</kmc>
"""
