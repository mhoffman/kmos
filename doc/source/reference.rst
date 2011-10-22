====================
Reference
====================

==========
Data Types
==========

kmos.types
==========

.. automodule:: kmos.types
   :members: ProjectTree, Parameter, Layer, Species, Process, ConditionAction, Coord

kmos.io
=======

.. automodule:: kmos.io
   :members: export_source, import_xml, export_xml

===============
Editor frontend
===============

kmos.gui
==========

.. automodule:: kmos.gui

kmos.forms
==========

.. automodule:: kmos.forms
   :members: MetaForm, SpeciesListForm, SpeciesForm, ParameterForm,
             LatticeForm, LayerEditor, SiteForm, ProcessForm, 
             parse_chemical_expression, BatchProcessForm


================
Runtime frontend
================


kmos.model
==========

.. automodule:: kmos.model

kmos.view
=========

.. automodule:: kmos.view
   :members: KMC_Viewer


====================
kmos kMC project DTD
====================

The central storage and exchange format is XML. XML was chosen over
JSON, pickle or alike because it still seems as the most flexible
and universal format with good methods to define the overall
structure of the data.

One way to define an XML format is by using a document type description
(DTD) and in fact at every import a kmos file is validated against
the DTD below.

.. literalinclude:: ../../kmos/kmc_project_v0.2.dtd
