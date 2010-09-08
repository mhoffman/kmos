#!/usr/bin/env python
import pdb
import re
from optparse import OptionParser
from app.config import *
from copy import copy, deepcopy
import sys
import os, os.path
import shutil
sys.path.append(APP_ABS_PATH)
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
# XML handling
from lxml import etree as ET
#Need to pretty print XML
from xml.dom import minidom
from kmc_generator import ProcessList as ProcListWriter


#Kiwi imports
from kiwi.ui.views import SlaveView, BaseView
from kiwi.controllers import BaseController
from kiwi.ui.delegates import Delegate, SlaveDelegate, ProxyDelegate, ProxySlaveDelegate, GladeDelegate, GladeSlaveDelegate
from kiwi.python import Settable
from kiwi.ui.objectlist import ObjectTree, Column
from kiwi.datatypes import ValidationError


KMCPROJECT_DTD = '/kmc_project.dtd'
PROCESSLIST_DTD = '/process_list.dtd'
XMLFILE = './default.xml'
SRCDIR = './fortran_src'
GLADEFILE = os.path.join(APP_ABS_PATH, 'kmc_editor2.glade')


class Attributes:
    attributes = []
    def __init__(self, **kwargs):
        for attribute in self.attributes:
            if kwargs.has_key(attribute):
                self.__dict__[attribute] = kwargs[attribute]
        for key in kwargs:
            if key not in self.attributes:
                raise AttributeError, 'Tried to initialize illegal attribute'
    def __setattr__(self, attrname, value):
        if attrname in self.attributes:
            self.__dict__[attrname] = value
        else:
            raise AttributeError, 'Tried to initialize illegal attribute'

class CorrectlyNamed:
    def on_name__validate(self, widget, name):
        if ' ' in name:
            return ValidationError('No spaces allowed')
        elif name and not name[0].isalpha():
            return ValidationError('Need to start with a letter')

class Lattice(Settable):
    def __init__(self, **kwargs):
        Settable.__init__(self, **kwargs)
        self.sites = []

    def add_site(self, site):
        self.sites.append(site)


class Species(Attributes):
    attributes = ['name', 'color', 'id']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

class SpeciesList(Settable):
    def __init__(self, **kwargs):
        kwargs['name'] = 'Species'
        Settable.__init__(self, **kwargs)


class ProcessList(Settable):
    def __init__(self, **kwargs):
        kwargs['name'] = 'Processes'
        Settable.__init__(self, **kwargs)

class ParameterList(Settable):
    def __init__(self, **kwargs):
        kwargs['name'] = 'Parameters'
        Settable.__init__(self, **kwargs)


class LatticeList(Settable):
    def __init__(self, **kwargs):
        kwargs['name'] = 'Lattices'
        Settable.__init__(self, **kwargs)


class Parameter(Attributes, CorrectlyNamed):
    attributes = ['name', 'value']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def on_name__content_changed(self, text):
        self.project_tree.update(self.process)



class ParameterList(Settable):
    def __init__(self, **kwargs):
        kwargs['name'] = 'Parameters'
        Settable.__init__(self, **kwargs)

class Meta(Settable, object):
    name = 'Meta'
    def __init__(self):
        Settable.__init__(self, email='', author='', debug=0, model_name='', model_dimension = 0)

    def add(self, attrib):
        for key in attrib:
            if key in ['debug', 'model_dimension']:
                self.__setattr__(key, int(attrib[key]))
            else:
                self.__setattr__(key, attrib[key])



class Process(Attributes):
    attributes = ['name','center_site', 'rate_constant','condition_list','action_list']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.condition_list=[]
        self.action_list=[]
        self.center_site = ()

    def add_condition(self, condition):
        self.condition_list.append(condition)

    def add_action(self, action):
        self.action_list.append(action)

class Output():
    def __init__(self):
        self.name = 'Output'



class ProjectTree(SlaveDelegate):
    def __init__(self, parent):
        self.project_data = ObjectTree(Column('name', data_type=str))
        self.set_parent(parent)
        self.meta = self.project_data.append(None,Meta())
        self.meta.add({'model_dimension':2})
        self.lattice_list_iter = self.project_data.append(None, LatticeList())
        self.parameter_list_iter = self.project_data.append(None, ParameterList())
        self.process_list_iter = self.project_data.append(None, ProcessList())
        self.species_list_iter = self.project_data.append(None, SpeciesList())
        self.output_iter = self.project_data.append(None, Output())

        self.filename = ''

        SlaveDelegate.__init__(self, toplevel=self.project_data)

    def update(self, model):
        self.project_data.update(model)

    def get_name(self):
        if self.filename:
            return os.path.basename(self.filename)
        else:
            return 'Untitled'
    def __getattr__(self, attr):
        if attr == 'species_list':
            return self.project_data.get_descendants(self.species_list_iter)
        elif attr == 'lattice_list':
            return self.project_data.get_descendants(self.lattice_list_iter)
        elif attr == 'process_list':
            return self.project_data.get_descendants(self.process_list_iter)
        elif attr == 'parameter_list':
            return self.project_data.get_descendants(self.parameter_list_iter)
        elif attr == 'meta':
            return self.meta
        elif attr == 'append':
            return self.project_data.append
        elif attr == 'expand':
            return self.project_data.expand
        elif attr == 'update':
            return self.project_data.update
        else:
            raise AttributeError, attr

    def __repr__(self):
        return self._get_xml_string()

    def import_xml_file(self,filename):
        self.filename = filename
        xmlparser = ET.XMLParser(remove_comments=True)
        root = ET.parse(filename, parser=xmlparser).getroot()
        dtd = ET.DTD(APP_ABS_PATH + KMCPROJECT_DTD)
        if not dtd.validate(root):
            print(dtd.error_log.filter_from_errors()[0])
            return
        for child in root:
            if child.tag == 'lattice_list':
                for lattice in child:
                    name = lattice.attrib['name']
                    unit_cell_size = [ int(x) for x in lattice.attrib['unit_cell_size'].split() ]
                    lattice_elem = Lattice(name=name, unit_cell_size=unit_cell_size)
                    for site in lattice:
                        index =  int(site.attrib['index'])
                        name = site.attrib['type']
                        coord = [ int(x) for x in site.attrib['coord'].split() ]
                        site_elem = Settable(index=index, name=name, coord=coord)
                        lattice_elem.add_site(site_elem)
                    self.project_data.append(self.lattice_list_iter, lattice_elem)
            elif child.tag == 'meta':
                for attrib in ['author','email', 'debug','model_name','model_dimension']:
                    if child.attrib.has_key(attrib):
                        self.meta.add({attrib:child.attrib[attrib]})
            elif child.tag == 'parameter_list':
                for parameter in child:
                    name = parameter.attrib['name']
                    value = parameter.attrib['value']
                    parameter_elem = Settable(name=name,type=type,value=value)
                    self.project_data.append(self.parameter_list_iter, parameter_elem)
            elif child.tag == 'process_list':
                for process in child:
                    center_site = [ int(x) for x in  process.attrib['center_site'].split() ]
                    name = process.attrib['name']
                    rate_constant = process.attrib['rate_constant']
                    process_elem = Process(name=name, center_site=center_site, rate_constant=rate_constant)
                    for sub in process:
                        if sub.tag == 'action' or sub.tag == 'condition':
                            species =  sub.attrib['species']
                            coord = [ int(x) for x in sub.attrib['coord'].split() ]
                            condition_action = Settable(species=species, coord=coord)
                            if sub.tag == 'action':
                                process_elem.add_action(condition_action)
                            elif sub.tag == 'condition':
                                process_elem.add_condition(condition_action)
                    self.project_data.append(self.process_list_iter, process_elem)
            elif child.tag == 'species_list':
                for species in child:
                    name = species.attrib['name']
                    id = species.attrib['id']
                    color = species.attrib['color']
                    species_elem = Species(name=name, color=color, id=id)
                    self.project_data.append(self.species_list_iter, species_elem)
        self.expand_all()
        self.select_meta()

    def expand_all(self):
        self.project_data.expand(self.species_list_iter)
        self.project_data.expand(self.lattice_list_iter)
        self.project_data.expand(self.parameter_list_iter)
        self.project_data.expand(self.process_list_iter)

    def _get_xml_string(self):
        def prettify_xml(elem):
            rough_string = ET.tostring(elem,encoding='utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent='    ')
        # build XML Tree
        root = ET.Element('kmc')
        meta = ET.SubElement(root,'meta')
        if hasattr(self.meta, 'author'):
            meta.set('author', self.meta.author)
        if hasattr(self.meta, 'email'):
            meta.set('email', self.meta.email)
        if hasattr(self.meta, 'model_name'):
            meta.set('model_name', self.meta.model_name)
        if hasattr(self.meta, 'model_dimension'):
            meta.set('model_dimension', str(self.meta.model_dimension))
        if hasattr(self.meta, 'debug'):
            meta.set('debug', str(self.meta.debug))
        species_list = ET.SubElement(root,'species_list')
        for species in self.species_list:
            species_elem = ET.SubElement(species_list,'species')
            species_elem.set('name',species.name)
            species_elem.set('color',species.color)
            species_elem.set('id',str(species.id))
        parameter_list = ET.SubElement(root,'parameter_list')
        for parameter in self.parameter_list:
            parameter_elem = ET.SubElement(parameter_list, 'parameter')
            parameter_elem.set('name', parameter.name)
            parameter_elem.set('value', str(parameter.value))
        lattice_list = ET.SubElement(root, 'lattice_list')
        for lattice in self.lattice_list:
            lattice_elem = ET.SubElement(lattice_list,'lattice')
            lattice_elem.set('unit_cell_size', str(lattice.unit_cell_size)[1 :-1].replace(',',''))
            lattice_elem.set('name', lattice.name)
            for site in lattice.sites:
                site_elem = ET.SubElement(lattice_elem, 'site')
                site_elem.set('index',str(site.index))
                site_elem.set('type',site.name)
                site_elem.set('coord',str(site.coord)[1 :-1].replace(',',''))
        process_list = ET.SubElement(root, 'process_list')
        for process in self.process_list:
            process_elem = ET.SubElement(process_list,'process')
            process_elem.set('rate_constant', process.rate_constant)
            process_elem.set('name', process.name)
            process_elem.set('center_site', str(process.center_site)[1 :-1].replace(',',''))
            for condition in process.condition_list:
                condition_elem = ET.SubElement(process_elem, 'condition')
                condition_elem.set('species', condition.species)
                condition_elem.set('coord', str(condition.coord)[1 :-1].replace(',', ''))
            for action in process.action_list:
                action_elem = ET.SubElement(process_elem, 'action')
                action_elem.set('species', action.species)
                action_elem.set('coord', str(action.coord)[1 :-1].replace(',',''))
        return prettify_xml(root)

    def select_meta(self):
        self.focus_topmost()
        self.on_project_data__selection_changed(0, self.meta)

    def on_project_data__selection_changed(self, item, elem):
        slave = self.get_parent().get_slave('workarea')
        if slave:
            self.get_parent().detach_slave('workarea')
        if isinstance(elem, Meta):
            meta_form = MetaForm(self.meta)
            self.get_parent().attach_slave('workarea', meta_form)
            meta_form.focus_toplevel()
            meta_form.focus_topmost()
        elif isinstance(elem, Process):
            form = ProcessForm(elem, self.project_data)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Species):
            form = SpeciesForm(elem, self.project_data)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Parameter):
            form = ParameterForm(elem, self.project_data)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        else:
            self.get_parent().toast('Not implemented, yet.')



class ProcessForm(ProxySlaveDelegate, CorrectlyNamed):
    gladefile=GLADEFILE
    toplevel_name='process_form'
    widgets = ['process_name','rate_constant' ]
    def __init__(self, model, project_tree):
        self.model = model
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)

    def on_process_name__content_changed(self, text):
        self.project_tree.update(self.model)

    def on_eval__clicked(self, button):
        print("CLICKED")
        eval_text = self.get_widget('chemical_eq').get_text()
        print("Don't know how to evaluate %s, yet" % eval_text)


class MetaForm(ProxySlaveDelegate, CorrectlyNamed):
    gladefile=GLADEFILE
    toplevel_name='meta_form'
    widgets = ['author','email','model_name','model_dimension','debug']
    def __init__(self, model):
        ProxySlaveDelegate.__init__(self, model)
        self.get_widget('model_dimension').set_sensitive(False)

    def on_model_name__validate(self, widget, model_name):
        return self.on_name__validate(widget, model_name)

class InlineMessage(SlaveView):
    gladefile=GLADEFILE
    toplevel_name = 'inline_message'
    widgets = ['message_label']
    def __init__(self, message=''):
        SlaveView.__init__(self)
        self.get_widget('message_label').set_text(message)


class ParameterForm(ProxySlaveDelegate, CorrectlyNamed):
    gladefile=GLADEFILE
    toplevel_name='parameter_form'
    widgets = ['parameter_name', 'value']
    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        self.get_widget('name').grab_focus()

    def on_parameter_name__content_changed(self, text):
        self.project_tree.update(self.model)

class SpeciesForm(ProxySlaveDelegate, CorrectlyNamed):
    gladefile=GLADEFILE
    toplevel_name='species_form'
    widgets = ['name', 'color', 'id']
    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        self.get_widget('id').set_sensitive(False)
        self.get_widget('name').grab_focus()

    def on_name__content_changed(self, text):
        self.project_tree.update(self.model)


class KMC_Editor(GladeDelegate):
    widgets = ['workarea','statbar']
    gladefile=GLADEFILE
    toplevel_name='main_window'
    def __init__(self):
        self.project_tree = ProjectTree(parent=self)
        GladeDelegate.__init__(self, delete_handler=self.on_btn_quit__clicked)
        self.attach_slave('overviewtree', self.project_tree)
        self.set_title(self.project_tree.get_name())
        self.project_tree.show()

        self.saved_state = str(self.project_tree)
        # Cast initial message
        self.toast('Start a new project by filling in meta information,\nlattice, species, parameters, and processes or open an existing one\nby opening a kMC XML file')

    def toast(self, toast):
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        inline_message = InlineMessage(toast)
        self.attach_slave('workarea',inline_message)
        inline_message.show()
    def on_btn_new_project__clicked(self, button):
        if str(self.project_tree) != self.saved_state:
            # if there are unsaved changes, ask what to do first
            save_changes_dialog = gtk.Dialog(buttons=(gtk.STOCK_DISCARD, gtk.RESPONSE_DELETE_EVENT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), title='Saved unsaved changes?')
            save_changes_dialog.vbox.pack_start(gtk.Label("\nThere are unsaved changes.\nWhat shall we do?\n\n"))
            save_changes_dialog.show_all()
            resp = save_changes_dialog.run()
            save_changes_dialog.destroy()
            if resp == gtk.RESPONSE_DELETE_EVENT:
                # nothing to do here
                pass
            elif resp == gtk.RESPONSE_CANCEL:
                return
            elif resp == gtk.RESPONSE_OK:
                self.on_btn_save_model__clicked(None)
        self.project_tree = ProjectTree(parent=self)
        if self.get_slave('overviewtree'):
            self.detach_slave('overviewtree')
        self.attach_slave('overviewtree', self.project_tree)
        self.set_title(self.project_tree.get_name())
        self.project_tree.show()
        self.toast('Start a new project by filling in meta information,\nlattice, species, parameters, and processes or open an existing one\nby opening a kMC XML file')

    def on_btn_add_species__clicked(self, button):
        new_species = Species(color='#fff', name='')
        self.project_tree.append(self.project_tree.species_list_iter, new_species)
        self.project_tree.expand(self.project_tree.species_list_iter)
        new_species.id = "%s" % (len(self.project_tree.species_list))
        species_form = SpeciesForm(new_species, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', species_form)
        species_form.focus_topmost()

    def on_btn_add_process__clicked(self, button):
        new_process = Process(name='', rate_constant='')
        self.project_tree.append(self.project_tree.process_list_iter, new_process)
        self.project_tree.expand(self.project_tree.process_list_iter)
        process_form = ProcessForm(new_process, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', process_form)
        process_form.focus_topmost()

    def on_btn_add_parameter__clicked(self, button):
        new_parameter = Parameter(name='', value='')
        self.project_tree.append(self.project_tree.parameter_list_iter, new_parameter)
        self.project_tree.expand(self.project_tree.parameter_list_iter)
        parameter_form = ParameterForm(new_parameter, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', parameter_form)
        parameter_form.focus_topmost()

    def on_btn_open_model__clicked(self, button):
        """Import project from XML
        """
        if str(self.project_tree) != self.saved_state:
            # if there are unsaved changes, ask what to do first
            save_changes_dialog = gtk.Dialog(buttons=(gtk.STOCK_DISCARD, gtk.RESPONSE_DELETE_EVENT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), title='Saved unsaved changes?')
            save_changes_dialog.vbox.pack_start(gtk.Label("\nThere are unsaved changes.\nWhat shall we do?\n\n"))
            save_changes_dialog.show_all()
            resp = save_changes_dialog.run()
            save_changes_dialog.destroy()
            if resp == gtk.RESPONSE_DELETE_EVENT:
                # nothing to do here
                pass
            elif resp == gtk.RESPONSE_CANCEL:
                return
            elif resp == gtk.RESPONSE_OK:
                self.on_btn_save_model__clicked(None)

        # choose which file to open next
        filechooser = gtk.FileChooserDialog(title='Open Project',
            action = gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK ))
        resp = filechooser.run()
        filename = filechooser.get_filename()
        filechooser.destroy()
        if resp == gtk.RESPONSE_OK and filename:
            # Initialize blank project tree
            self.project_tree = ProjectTree(parent=self)
            if self.get_slave('overviewtree'):
                self.detach_slave('overviewtree')
            self.attach_slave('overviewtree', self.project_tree)
            self.set_title(self.project_tree.get_name())
            self.project_tree.show()
            # Import
            self.project_tree.import_xml_file(filename)
            self.set_title(self.project_tree.get_name())
            self.get_widget('statbar').push(1,'Imported model %s' % self.project_tree.meta.model_name)
            self.saved_state = str(self.project_tree)

    def on_btn_save_model__clicked(self, button, force_save=False):
        #Write Out XML File
        xml_string = str(self.project_tree)
        if xml_string == self.saved_state and not force_save:
            self.get_widget('statbar').push(1, 'Nothing to save')
        else:
            if not self.project_tree.filename:
                self.on_btn_save_as__clicked(None)
            outfile = open(self.project_tree.filename,'w')
            outfile.write(xml_string)
            outfile.write('<!-- This is an automatically generated XML file, representing a kMC model ' + \
                            'please do not change this unless you know what you are doing -->\n')
            outfile.close()
            self.saved_state = xml_string
            self.get_widget('statbar').push(1,'Saved %s' % self.project_tree.filename)


    def on_btn_save_as__clicked(self, button):
        filechooser = gtk.FileChooserDialog(title='Save Project As ...',
            action = gtk.FILE_CHOOSER_ACTION_SAVE,
            parent=None,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK ))
        filechooser.set_property('do-overwrite-confirmation',True)
        resp = filechooser.run()
        if resp == gtk.RESPONSE_OK:
            self.project_tree.filename = filechooser.get_filename()
            self.on_btn_save_model__clicked(None, force_save=True)
        filechooser.destroy()

    def on_btn_export_src__clicked(self, button):
        self.toast('"Export Source" is not implemented, yet.')

    def on_btn_help__clicked(self, button):
        self.toast('"Help" is not implemented, yet.')


    def on_btn_quit__clicked(self, button, *args):
        if self.saved_state != str(self.project_tree):
            save_changes_dialog = gtk.Dialog(buttons=(gtk.STOCK_DISCARD, gtk.RESPONSE_DELETE_EVENT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), title='Saved unsaved changes?')
            save_changes_dialog.vbox.pack_start(gtk.Label("\nThere are unsaved changes.\nWhat shall we do?\n\n"))
            save_changes_dialog.show_all()
            resp = save_changes_dialog.run()
            save_changes_dialog.destroy()
            if resp == gtk.RESPONSE_CANCEL:
                return True
            elif resp == gtk.RESPONSE_DELETE_EVENT:
                self.hide_and_quit()
                gtk.main_quit()
            elif resp == gtk.RESPONSE_OK:
                self.on_btn_save_model__clicked(None)
                self.hide_and_quit()
                gtk.main_quit()
        else:
            self.hide_and_quit()
            gtk.main_quit()
        # Need to return true, or otherwise the window manager destroys 
        # the windows anywas
        return True







if __name__ == '__main__':
    editor = KMC_Editor()
    editor.show_and_loop()
