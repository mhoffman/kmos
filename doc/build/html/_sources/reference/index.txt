********************
Reference
********************

Data Types
==========

kmos.types
^^^^^^^^^^

.. automodule:: kmos.types
.. autoclass:: kmos.types.Project
.. automethod:: kmos.types.Project.export_xml_file
.. autoclass:: kmos.types.Meta
.. autoclass:: kmos.types.Parameter
.. autoclass:: kmos.types.Layer
.. autoclass:: kmos.types.Site
.. autoclass:: kmos.types.Species
.. autoclass:: kmos.types.Process
.. autoclass:: kmos.types.ConditionAction
.. autoclass:: kmos.types.Coord

kmos.io
^^^^^^^

.. automodule:: kmos.io
   :members: export_source, import_xml, export_xml

Editor frontend
===============

kmos.gui
^^^^^^^^^^

.. automodule:: kmos.gui
.. autoclass:: kmos.gui.Editor
.. autoclass:: kmos.gui.GTKProject

kmos.forms
^^^^^^^^^^

.. automodule:: kmos.forms
   :members: MetaForm, SpeciesListForm, SpeciesForm, ParameterForm,
             LatticeForm, LayerEditor, SiteForm, ProcessForm, 
             parse_chemical_expression, BatchProcessForm


Runtime frontend
================


kmos.run
^^^^^^^^

.. automodule:: kmos.run
  
.. autoclass:: kmos.run.KMC_Model
  :members: deallocate, do_steps, get_atoms, get_occupation_header,
            get_tof_header, parameters, print_rates, put, rate_constants,
            run, start, view, xml
  

kmos.view
^^^^^^^^^

.. automodule:: kmos.view
   :members: KMC_Viewer


kmos kMC project DTD
====================

The central storage and exchange format is XML. XML was chosen over
JSON, pickle or alike because it still seems as the most flexible
and universal format with good methods to define the overall
structure of the data.

One way to define an XML format is by using a document type description
(DTD) and in fact at every import a kmos file is validated against
the DTD below.

.. literalinclude:: kmc_project_v0.2.dtd


Backend
========

.. include:: base.rst

.. include:: lattice.rst

.. include:: proclist.rst
