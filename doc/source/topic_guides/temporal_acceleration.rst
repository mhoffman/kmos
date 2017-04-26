Temporal acceleration
===============

  NOTICE: The temporal acceleration is still on an EXPERIMENTAL state. Please 
  report any bugs encountered.


This implementation of a temporal acceleration algortihm attempts to deal 
with the low barrier problem often encountered in kinetic Monte Carlo 
simuations. It is based on the acceleration algorithm developed by 
Eric Christopher Dybeck, Craig Patrick Plaisance and Matthew Neurock,
Journal of Chemical Theory and Computation (just accepted),
DOI: 10.1021/acs.jctc.6b00859

In order for the scheme to work, it needs to be able to pair all processes 
into forward/reverse reactions. This is done according to the 
actions/conditions, where the forward process has the same actions as the 
conditions of the reverse process and vice versa.
See the example model `render_co_oxidation_ruo2_processes_paired.py` from
the examples folder for an example.

To enable acceleration, compile with the command: `kmos export model.xml -t` 
or if using the backend for lateral interactions: `kmos export model.xml -b 
lat_int -t`.

The model has four adjustable parameters (c.f. article):

Buffer_parameter (default: 1000): The smaller the value, the more 
aggresively the rate constants are scaled. Note that a good starting point is 
around the number of sites in the system. 

Sampling_steps (default: 20): The number of kmc steps to take between each 
reassessment of the scaling factors. This parameter seems neither to be 
important for the accuracy nor the efficiency of the code. The default value
should be fine.

Execution_steps (default: 200): The number of previous executions of either 
the forward or reverse process that is used to assess equilibrium. This 
parameter is also the number of executions of a forward/reverse process that 
must have occured in the current superbasin for a process pair to be locally 
equilibrated. The default value seems to be close to the optimum efficiency 
for most systems tested so far.

Threshold_parameter (default: 0.2): This parameter is used to assess 
whether a given process pair is equilibrated. The efficiency of the algorithm
worsens considerably if going below the default value of 0.2, whereas the 
accuracy of the algorithm is typically not too sensitive to the exact value.

Overall, the buffer_parameter seems to be the most important parameter for the 
accuracy of the algortihm, and one should always perform a careful convergence 
test with respect to this parameter before trusting the results. In the limit 
of an infinite value for the buffer_parameter, no scaling of the rate constants 
will be done.

It is possible to set these four parameters either when initiating a model: 
`model = KMC_Model(print_rates=False, banner=False, buffer_parameter=1000)` 
or one can use the set functions: `model.set_buffer_parameter(1000)`.
Get functions are also implemented: `model.get_buffer_parameter()`.
Note that if you change the execution_steps after initializing the model, 
the model will be reset (as this parameter controls the length of some 
fortran arrays).

Accelerated kmc steps are run using the command: `model.do_acc_steps(nsteps)`.

In order to see what has happened during the simulations, one can use the 
commands `model.print_scaling_stats()` or `model.get_scaling_stats()`, 
which print/return the names of the paired processes as well as the average 
used scaling factors and the last set scaling factors (where the averages are 
typically higher (closer to 1), since scaling factors are reset to 1 every 
time a non-equilibrated reaction is carried out).
Further implemented methods include `model.print_scaling_factors` and 
`model.print_proc_pair_eq`.

You can also use the command `model.set_debug_level(value: 0, 1 or 2)` to 
activate printing of certain fortran variables.

For models containing many different diffusion processes, the efficiency of 
the algorithm can be significantly increased by considering these 
processes to be equilibrated (but not locally equilibrated) by default. 
In practice this means that the execution of a diffusion process cannot cause 
the unscaling of all processes, as is normally the case whenever a 
non-equilibrated reaction occurs. However, diffusion processes still need to 
execute at least `execution_steps` times within the superbasin before being 
labeled as locally equilibrated and possible being subject to scaling.
This above described behaviour is default for any process containing `diff` 
in the process name.
