#!/usr/bin/env python

import os
import filecmp

def test_build_model():
    import os
    import sys
    import kmos.cli
    import time
    import pprint
    import filecmp

    old_path = os.path.abspath(os.getcwd())

    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    for backend in ['local_smart','lat_int','otf']:
        export_dir = '_tmp_export_{backend}'.format(**locals())

        print(os.getcwd())
        print(os.listdir('.'))

        kmos.cli.main('export 2d_grid.xml {export_dir} -o --acf -b {backend}'.format(**locals()))

        os.chdir('..')

        print(os.getcwd())
        print(os.listdir('.'))

        sys.path.insert(0, os.path.abspath('.'))

        import kmos.run
        import kmos.run.acf as acf
        
        if kmos.run.settings is None:
            import kmc_settings as settings
            kmos.run.settings = settings

        if kmos.run.lattice is None:
            from kmc_model import base, lattice, proclist, base_acf, proclist_acf
            import kmc_model
            kmos.run.kmc_model = kmc_model
            kmos.run.base = base
            kmos.run.lattice = lattice
            kmos.run.proclist = proclist
            kmos.run.base_acf = base_acf
            kmos.run.proclist_acf = proclist_acf

        with kmos.run.KMC_Model(print_rates=False, banner=False) as model:
            print("Model compilation successfull")
            nr_of_steps = 100
            trace_species = 'ion'

            acf.initialize_msd(model,trace_species)
            acf.allocate_trajectory(model,nr_of_steps)

            acf.do_kmc_steps_displacement(model,nr_of_steps,True)
            traj = acf.get_trajectory(model)

        ## Regenerate reference trajectory files -- comment out
        ## Comment to make test useful
        #with open('ref_traj_{backend}.log'.format(**locals()), 'w') as outfile:
            #outfile.write(pprint.pformat(traj))

        with open('test_traj_{backend}.log'.format(**locals()), 'w') as outfile:
            #outfile.write(pprint.pformat(traj))
            outfile.write(pprint.pformat(list(traj.flatten())))

        # check if both trajectories are equal
        assert filecmp.cmp(
            'test_traj_{backend}.log'.format(**locals()),
            'ref_traj_{backend}.log'.format(**locals()),
        )

        for src_filename in ['base_acf', 'proclist_acf']:
            assert filecmp.cmp('src/{src_filename}.f90'.format(**locals()),
                               'ref_src/{src_filename}.f90'.format(**locals()))
        # Clean-up action
        os.chdir('..')

        #kmos.run.lattice = None
        #kmos.run.settings = None

    os.chdir(old_path)

if __name__ == '__main__':
    test_build_model()
