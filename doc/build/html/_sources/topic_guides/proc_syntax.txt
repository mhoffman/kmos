.. _proc_mini_language:

The Process Syntax
=========================


A process in kMC language is defined by a configuration that has to
exist `before` the process, a configuration `after` the process
is executed, and a rate constant. Here we use this model for the
description of a process by giving each process a :
-condition_list
-action_list
-rate_constant


As you might guess each `condition` corresponds to one
`before`, and each `action` coresponds to one `after`.
In fact conditions and actions are actually of the same
class: each condition and action consists of a coordinate
and a species which has to be or will be at the coordinate.

.. TODO:: add single-layer description
