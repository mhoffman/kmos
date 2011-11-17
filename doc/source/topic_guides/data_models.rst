The kmos data model
===================

The guide explains how kmos handles represent
a kmc model internally, which is important to know
if one wants to write new functionality.

The different functions and front-ends of
kmos all interact in some way or another
with instances of the Project class. A
Project instance is a representation of
a kmc model. If you fire up 'kmos edit' with
an xml file, kmos validates the XML file and
stores the content in a Project instance.
If you export source code, kmos runs over the
Project and creates the necessary Fortran 90
source code.


So the following things are in a Project::
 * meta
 * lattice(layers)
 * species
 * parameters
 * processes

The language used here stems from modelling atomic
movement on a fixed or evolving lattice like
structure. In a more general
context one may translates them as::
  * meta -> information about project
  * geometry
  * states
  * parameters
  * transitions
