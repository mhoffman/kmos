#!/usr/bin/env python

XML = """<?xml version="1.0" ?>
<kmc version="(0, 2)">
    <meta author="Max J. Hoffmann" debug="0" email="mjhoffmann@gmail.com" model_dimension="2" model_name="my_model"/>
    <species_list default_species="empty">
        <species color="#000000" name="co" representation=""/>
        <species color="#ffffff" name="empty" representation=""/>
        <species color="#ff0000" name="oxygen" representation=""/>
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
    <lattice cell_size="10.0 10.0 3.0" default_layer="ruo2" representation="">
        <layer color="#ffffff" grid="1 1 1" grid_offset="0.0 0.0 0.0" name="ruo2">
            <site default_species="default_species" type="bridge" pos="0.0 0.0 0.5"/>
            <site default_species="default_species" type="cus" pos="0.0 0.5 0.5"/>
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
        <output item="kmc_time"/>
        <output item="co@bridge"/>
        <output item="oxygen"/>
        <output item="co"/>
        <output item="walltime"/>
        <output item="co_adsorption_bridge"/>
    </output_list>
</kmc>
"""

def run(i=0):
    from kmos.run import KMC_Model
    model = KMC_Model(banner=False, print_rates=False)
    model.settings.random_seed = i
    assert not model.do_steps(1000)
    assert not model.deallocate()

def run_in_serial():
    for i in xrange(20):
        run(i)

def run_in_parallel():
    from multiprocessing import Process
    for i in xrange(8):
        process = Process(target=run)
        process.start()

def export_and_run_many_models():
    """Test if export of a model including initiating,
    running, and deallocating works many times in serial
    """
    from os import system, chdir, remove
    from os.path import abspath
    from shutil import rmtree
    from sys import path

    import tempfile

    EXPORT_DIR = tempfile.mkdtemp()
    XML_FILENAME = '%s.xml' % tempfile.mktemp()
    XML_FILE = file(XML_FILENAME, 'w')
    XML_FILE.write(XML)
    XML_FILE.close()

    system('kmos export %s %s' % (XML_FILENAME, EXPORT_DIR))

    path.append(abspath(EXPORT_DIR))

    try:
        run_in_serial()
        run_in_parallel()
    finally:
        rmtree(abspath(EXPORT_DIR))
        remove(XML_FILENAME)

if __name__ == '__main__':
    test_export_and_run_many_models()
