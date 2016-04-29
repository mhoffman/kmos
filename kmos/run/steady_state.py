#!/usr/bin/env python
# coding: utf-8
"""
## Initial Bias Detection

In the following we will run some numerical experiments using the
initial bias detection proposed by M. Rossetti (Univ. Arkansas)
[link](http://dx.doi.org/10.1109/WSC.2005.1574321)

Helpful literature:
“Wiley: Introduction to Statistical Quality Control, 7th Edition - Douglas C. Montgomery.” Accessed March 8, 2016. http://www.wiley.com/WileyCDA/WileyTitle/productCd-EHEP002023.html.
Hoad, Kathryn, Stewart Robinson, and Ruth Davies. “Automating Warm-up Length Estimation.” In Proceedings of the 40th Conference on Winter Simulation, 532–40. WSC ’08. Miami, Florida: Winter Simulation Conference, 2008. http://dl.acm.org/citation.cfm?id=1516744.1516846.
Rossetti, M. D., Zhe Li, and Peng Qu. “Exploring Exponentially Weighted Moving Average Control Charts to Determine the Warm-up Period.” In Simulation Conference, 2005 Proceedings of the Winter, 10 pp. – , 2005. doi:10.1109/WSC.2005.1574321.

"""
# import the necessary python modules
import pprint
import itertools
import os
import glob

import numpy as np


# Calculate the LCL, and UCL according to expontially weighted moving
# average (EWMA)

def ewma_alpha(y, alpha, prev_ewma=None, adjust=True):
    """Adapted from pandas.algos.ewma

    """
    old_wt_factor = 1. - alpha
    old_wt = 1.
    new_wt = 1. if adjust else alpha

    alpha = np.double(alpha)
    if prev_ewma is not None:
        return alpha * y[-1] + (1 - alpha) * prev_ewma
    else:
        ewma = np.zeros_like(y, dtype=np.double)
        ewma[0] = y[0]
        # for i in range(len(y) - 1, -1, -1):
        for i in range(1, len(y)):
            old_wt *= old_wt_factor
            ewma[i] = (new_wt * y[i] + old_wt * ewma[i - 1]) / \
                (old_wt + new_wt)
            if adjust:
                old_wt += new_wt
            else:
                old_wt = 1.
        return ewma


def lcl_ucl(y, cutoff, L, lambda_factor):
    """Calculate the lower and upper control limit.

    cf. Rossetti, M. D., Zhe Li, and Peng Qu. “Exploring Exponentially Weighted Moving Average Control Charts to Determine the Warm-up Period.” In Simulation Conference, 2005 Proceedings of the Winter, 10 pp. – , 2005. doi:10.1109/WSC.2005.1574321.
    cf. “Wiley: Introduction to Statistical Quality Control, 7th Edition - Douglas C. Montgomery.” Accessed March 8, 2016. http://www.wiley.com/WileyCDA/WileyTitle/productCd-EHEP002023.html.

    """

    mu0 = np.mean(y[cutoff:]) * np.ones_like(y)
    sigma = np.std(y[cutoff:])
    N = len(y)
    delta = L * sigma * \
        np.sqrt(lambda_factor / (2 - lambda_factor)
                * (1 - (1 - lambda_factor)**np.arange(0., N, 1)))
    #print(N, d)
    return mu0, mu0 - delta, mu0 + delta


def p2d(y, cutoff, L, alpha):
    """Define the control function: this function estimates what how many
    points are under control if the corresponding EWMA falls into the LCL
    and UCL window.

    cf. Rossetti, M. D., Zhe Li, and Peng Qu. “Exploring Exponentially Weighted Moving Average Control Charts to Determine the Warm-up Period.” In Simulation Conference, 2005 Proceedings of the Winter, 10 pp. – , 2005. doi:10.1109/WSC.2005.1574321.
    """

    ewma = ewma_alpha(y, alpha)
    _, lcl, ucl = lcl_ucl(y, cutoff, L, alpha)
    return ((lcl[cutoff:] < ewma[cutoff:]) & (ewma[cutoff:] < ucl[cutoff:])).sum() / (float(len(y) - cutoff))


def get_scrap_fraction(y, L, alpha, warm_up):
    """Calculate which part of the data should be scrapped because it does not yet appear
    to be in steady-state.

    """

    if (y[0] == y).all():
        return 0.
    D = np.array([p2d(y, cutoff, L, alpha) for cutoff in range(len(y))])
    if len(D[warm_up:])> 0:
        return (np.argmax(D[warm_up:])) / float(len(y[warm_up:]))
    else:
        return 1.


def plot_normal(y, n=-1, *args, **kwargs):
    """Plot normalized data with the nth value
    """
    from matplotlib import pyplot as plt
    plt.plot(y / y[n], *args, **kwargs)


def make_ewma_plots(data, L, alpha, bias_threshold, seed):
    """Make so-called EWMA plots.

    “Wiley: Introduction to Statistical Quality Control, 7th Edition - Douglas C. Montgomery.” Accessed March 8, 2016. http://www.wiley.com/WileyCDA/WileyTitle/productCd-EHEP002023.html.

    Most for debugging purposes if the EWMA based steady-state analysis makes was sensible.
    """
    from matplotlib import pyplot as plt

    for key, y in data.items():
        if not 'time' in key or 'step' in key:
            y = np.array(y)
            plt.clf()
            cutoff0 = int(bias_threshold * len(y))
            mu0, lcl, ucl = lcl_ucl(y, cutoff0, L, alpha)
            D = np.array([p2d(y, cutoff, L, alpha) for cutoff in range(len(y))])
            plot_normal(ewma_alpha(y, alpha), label='EWMA')
            y_final = y[-1]
            plt.plot(y / ewma_alpha(y, alpha), label="signal {y_final}".format(**locals()))
            plot_normal(mu0, label='mean'.format(**locals()))
            plot_normal(lcl, n=0, label='LCL@{cutoff0}'.format(**locals()))
            plot_normal(ucl, n=0, label='UCL@{cutoff0}'.format(**locals()))
            plt.plot(D, 'k-', label='p2d')
            plt.text(len(D), .5, str(y[-1]))
            plt.text(np.argmax(D), .5, str(np.argmax(D)))
            legend = plt.legend()
            legend.get_frame().set_alpha(0.5)
            plt.savefig("{seed}_{key}.png".format(**locals()))


def sample_steady_state(model, batch_size=1000000,
                        L=4,
                        alpha=0.05,
                        bias_threshold=0.15,
                        tof_method='integ',
                        start_batch=0,
                        warm_up=20,
                        increase_batch_attempts=2,
                        check_frequency=10,
                        show_progress=True,
                        make_plots=False,
                        output='str',
                        seed='EWMA',
                        renormalizations=None
                        log_filename=None):
    """
        Run kMC model and continuously deploy steady-state detection to ensure that an initial bias does not enter the data.
        The steady-state detection is based on
        Rossetti, M. D., Zhe Li, and Peng Qu.
        "Exploring Exponentially Weighted Moving Average Control Charts to Determine the Warm-up Period."
        In Simulation Conference, 2005 Proceedings of the Winter, 10
        pp. – , 2005. doi:10.1109/WSC.2005.1574321.

        Define $L$  and $\\alpha$ as in source as method parameters. Source
        suggesst ($L=3$, $\\alpha=0.05$). Thorough tests showed that for $L=3$
        can fail to give accurate estimate if the statistical noise on the
        function is extremely small ($0<0.01$) because the $3\sigma$ environment
        was estimated too narrow. It was therefore decided that $L=4$ give more
        robust outcomes.

        Arguments:

            :param batch_size: This is the number of kMC steps per sampling batch. The number should be equal of larger to an average auto-correlation length of the kMC trajectory. A larger batch-size is inefficient, the shorter batch-size will confuse the exponentially weighted moving average (EWMA). If the progress is turned on and the progress-bar just jumps erratically even after 100s of batches, the number should be increased. The ideal batch-size can also depend on simulations and generally grow larger around phase-transitions.
            :type batch_size: int
            :param L: This sets the confidence range of the lower control limit (LCL) and upper control limit (UCL) of the EWMA. The source recommends a value of $L=3$. Test have shown that $L=4$ leads to more stable outcomes when noise is very small.
            :type L: int
            :param alpha: The scaling factor of the EWMA. Values between 0.01 and 0.1 have shown to give good performance.
            :type alpha: float
            :param show_progress: Show status of convergence in ASCII status bar (default: True)
            :type show_progress: bool
            :param make_plots: If True the steady-state estimator will make EWMA plots at every 100 steps as well as after convergence (default: False)
            :type make_plots: bool
            :param seed: Prefix string for EWMA plots (default: EWMA)
            :type seed: str
            :param tof_method: Forward of the same named option in get_std_sampled_data. Choose 'integ' to calculate rate based on coverages, choose 'procrates' to calculate rates based on actual events.
            :type tof_method: str
            :param warm_up: Number of batches to run before checking for steady-state (default: 20). When you begin checking to early, result usually have little statistical bearing and may mostly likely lead to erroneous results.
            :type warm_up: int
            :param check_frequency: Number specifying after every how many batches we check for steady-state. This is to reduce the computational cost of checking for steady-state. (default: 20).
            :type check_frequency: int
    """
    hist = {}

    # Temporarily change TOF matrix to reflect slowing down of fast processes
    renormalizations = np.ones([model.proclist.nr_of_proc]) if renormalizations == None else renormalizations
    tof_matrix0 = model.tof_matrix.copy()
    model.tof_matrix *= renormalizations


    batch_doubling = 0

    if show_progress:
        import kmos.utils.progressbar
        progress_bar = kmos.utils.progressbar.ProgressBar()

    for batch in itertools.count(start_batch):
        try:
            data = model.get_std_sampled_data(
                100, batch_size, tof_method=tof_method, output='dict', reset_time_overrun=False,
                )
        except ZeroDivisionError:
            _tee("Warning: encountered zero-division error at batch {batch} (size {batch_size:.2e}). Will double batch-size and retry.".format(**locals()), log_filename)
            model.print_accum_rate_summation()
            model.print_coverages()
            model.print_procstat()
            data = {}
            batch_size *= 2

            if batch_doubling >= increase_batch_attempts:
                _tee("Doubled batch-size {increase_batch_attempts} times, giving up".format(**locals()), log_filename)
                if output == 'dict':
                    return {}
                elif output == 'str':
                    return '\n'
                elif output == 'both':
                    return {}, '\n'
            batch_doubling += 1
            continue

        for key, data_point in data.items():
            hist.setdefault(key, []).append(data_point)

        max_scrap = 0.
        critical_key = ''
        if batch < warm_up + start_batch:
            wstart = warm_up + start_batch
            if show_progress:
                progress_bar.render(
                    int(0), "Warm-up phase {batch}/{wstart}".format(**locals()))

        else:
            if batch % check_frequency == 0:
                for key, y in hist.items():
                    if 'time' in key or 'step' in key:
                        continue
                    scrap_fraction = get_scrap_fraction(
                        np.array(y), L, alpha, warm_up + start_batch)
                    if scrap_fraction > max_scrap:
                        max_scrap = scrap_fraction
                        critical_key = key
                completed_percent = float(
                    1 - max_scrap) / (1 - bias_threshold) * 100.

                if make_plots and batch % 100 == 0:
                    # remove existing EWMA plots to reduce hard-drive space
                    map(os.remove, glob.glob("{seed}_*.png".format(**locals())))
                    make_ewma_plots(
                        hist, L, alpha, bias_threshold, seed="{seed}_{batch}".format(**locals()))
                if show_progress:
                    progress_bar.render(int(
                        completed_percent), "Limited by {critical_key:40s} ({batch})".format(**locals()))

                if completed_percent >= 100 and batch >= warm_up + start_batch :
                    if show_progress:
                        _tee("Done after {batch} batches!".format(**locals()), log_filename)
                    if make_plots:
                        map(os.remove, glob.glob("{seed}_*.png".format(**locals())))
                        make_ewma_plots(
                            hist, L, alpha, bias_threshold, seed="{seed}_final".format(**locals()))
                    break

    if show_progress:
        progress_bar.clear()

    steady_state_start = int(batch * bias_threshold)
    for key, value in hist.items():
        hist[key] = np.array(value[steady_state_start:])

    data = {}
    for key, values in hist.items():
        if len(values) == 0 :
            continue
        if 'time' in key:
            data[key] = values[-1]
            #data['debug_{key}'.format(**locals())] = values
        elif 'step' in key:
            data[key] = sum(values)
        else:
            data[key] = np.average(values, weights=hist['kmc_time'])

    # Change TOF matrix back to original value
    model.tof_matrix = tof_matrix0

    if output == 'dict':
        return data
    elif output == 'str':
        return ' '.join(format(data[key.replace('#', '')], '.5e') for key in model.get_std_header().split()) + '\n'
    elif output == 'both':
        data_str = ' '.join(format(data[key.replace('#', '')], '.5e') for key in model.get_std_header().split()) + '\n'
        return data, data_str

def _tee(string, filename=None, mode='a'):
    print(string)
    if filename is not None:
        with open(filename, mode) as outfile:
            outfile.write(string + '\n')



def _dict_to_str(data, header):
    return ' '.join(format(data[key.replace('#', '')], '.5e') for key in header.split()) + '\n'


def find_pairs(project):
    """Find pairs of elementary processes that are reverse processes with respect
    to each others from a kmos.types.Project

    """
    pairs = []
    for p1 in sorted(project.process_list):
        for p2 in sorted(project.process_list):
            if p1.condition_list == p2.action_list and p2.condition_list == p1.action_list:
                if not (p1, p2) in pairs and not (p2, p1) in pairs:
                    pairs.append((p1, p2))
    return pairs

def report_equilibration(model):
    """Iterate over pairs of reverse proceses and print
        rate1 * rho1 / rate2 * rho2

      for each.
    """
    import kmos.types
    import StringIO

    project = kmos.types.Project()
    if model.settings.xml.strip().startswith('<?xml'):
        project.import_xml_file(model.settings.xml, string=True)
    else:
        project.import_ini_file(StringIO.StringIO(model.settings.xml))

    pairs = find_pairs(project)

    atoms = model.get_atoms(geometry=False)

    procstat = dict(zip(sorted(model.settings.rate_constants), atoms.procstat))
    rate_constants = dict(zip(sorted(model.settings.rate_constants), (model.base.get_rate(i+1) for i in range(len(procstat)))))

    report = ''
    data = []
    for pair in pairs:
        pn1, pn2 = pair[0].name, pair[1].name
        left = procstat[pn1] #* rate_constants[pn1]
        right = procstat[pn2] # * rate_constants[pn2]
        ratio = abs(left/right - 1.)
        left_right_sum = left + right
        report += ('{pn1} : {pn2} => {left:.2f}/{right:.2f} = {ratio:.4e}\n'.format(**locals()))
        data.append([
            ratio, pn1, pn2, left_right_sum
        ])
    return report, data


if __name__ == '__main__':
    import kmos.run
    with kmos.run.KMC_Model(banner=False, print_rates=False) as model:
        hist = sample_steady_state(
            model, 100000, tof_method='integ', show_progress=True, make_plots=True)
    print(model.get_std_header())
    print(hist)
