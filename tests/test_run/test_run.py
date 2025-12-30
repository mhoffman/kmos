#!/usr/bin/env python


def test_build_model():
    import os
    import sys
    import kmos.cli
    import pprint
    import filecmp

    old_path = os.path.abspath(os.getcwd())

    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    for backend in ["local_smart", "lat_int", "otf"]:
        export_dir = "_tmp_export_{backend}".format(**locals())

        print(os.getcwd())
        print(os.listdir("."))

        kmos.cli.main(
            "export AB_model.ini {export_dir} -o -b{backend}".format(**locals())
        )

        os.chdir("..")

        print(os.getcwd())
        print(os.listdir("."))

        # os.chdir(export_dir)
        sys.path.insert(0, os.path.abspath("."))

        import kmos.run

        if kmos.run.settings is None:
            import kmc_settings as settings

            kmos.run.settings = settings

        if kmos.run.lattice is None:
            from kmc_model import base, lattice, proclist

            kmos.run.base = base
            kmos.run.lattice = lattice
            kmos.run.proclist = proclist

        procs_sites = []
        with kmos.run.KMC_Model(print_rates=False, banner=False) as model:
            print("Model compilation successfull")
            for i in range(10000):
                proc, site = model.get_next_kmc_step()
                procs_sites.append((proc.real, site.real))
                model.run_proc_nr(proc, site)

        ## Regenerate reference trajectory files -- comment out
        ## Comment to make test useful
        # Generate reference file for new backends
        if backend == "otf" and not os.path.exists(
            "ref_procs_sites_{backend}.log".format(**locals())
        ):
            with open(
                "ref_procs_sites_{backend}.log".format(**locals()), "w"
            ) as outfile:
                outfile.write(pprint.pformat(procs_sites))

        with open("test_procs_sites_{backend}.log".format(**locals()), "w") as outfile:
            outfile.write(pprint.pformat(procs_sites))

        # check if both trajectories are equal
        assert filecmp.cmp(
            "test_procs_sites_{backend}.log".format(**locals()),
            "ref_procs_sites_{backend}.log".format(**locals()),
        ), "Trajectories differ for backend {backend}".format(**locals())
        # Clean-up action
        os.chdir("..")

        kmos.run.lattice = None
        kmos.run.settings = None

    os.chdir(old_path)


if __name__ == "__main__":
    test_build_model()
