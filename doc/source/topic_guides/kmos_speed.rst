How the kmos kMC algorithm works
================================

kmos asks you to describe your model to the processor
in seemingly arcane ways. It can save model descriptions
in XML but they are basically unreadable and a pain to edit.
The API has some glitches and is probably incomplete: so why learn it?

Because it is fast (in two ways).

The code it produces is commonly faster than naive implementations
of the kMC method. Most straightforwards implementations of kMC take a time
proportional to 2*N  per kMC step,
where N is the number of sites in the system.
However the code that kmos produces is O(1) until the RAM
of your system is exceeded. As benchmarks have shown this may happen when
100,000 or more sites are required. However tests have also shown
that kmos can be faster than O(N) implementations from around
60-100 sites. If you have different experiences please let me know
but I think this gives some rule of thumb.


Why is it faster? Straightforward implementations of kMC scan the
entire system twice per kMC step. First to determine the total
rate, then to determine the next process to be executed. The
present implementation does not. kmos keeps a database of available
processes which allow to quickly pick the next process. It also
updates the database of available processes which cost additional
overhead. However this overhead is independent of the system's size
and only scales with the degree of interaction between sites, which
is seems hard to define in general terms.


.. TODO:: explain algorithm underlying kmos.base
