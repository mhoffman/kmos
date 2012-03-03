#!/usr/bin/env python

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

def test_export_and_run_many_models():
    """Test if export of a model including initiating,
    running, and deallocating works many times in serial
    """
    from os import system, chdir, curdir
    from os.path import abspath
    from shutil import rmtree
    from sys import path

    EXPORT_DIR = 'build_run'
    assert not system('kmos export default.xml %s' % EXPORT_DIR)

    path.append(abspath(EXPORT_DIR))


    try:
        run_in_serial()
        run_in_parallel()
    finally:
        rmtree(EXPORT_DIR)

if __name__ == '__main__':
    test_export_and_run_many_models()
