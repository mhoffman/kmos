#!/usr/bin/env python
"""The main part of the kmc gui project
"""
import re
import optparse
from ConfigParser import SafeConfigParser
from app.config import *
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
import kiwi.ui
from kiwi.ui.delegates import Delegate, SlaveDelegate, ProxyDelegate, ProxySlaveDelegate, GladeDelegate, GladeSlaveDelegate
from kiwi.python import Settable
from kiwi.ui.objectlist import ObjectList, ObjectTree, Column
from kiwi.datatypes import ValidationError
import kiwi.ui.dialogs 

# Canvas Import
from pygtkcanvas.canvas import Canvas
from pygtkcanvas.canvaslayer import CanvasLayer
from pygtkcanvas.canvasitem import *


KMCPROJECT_DTD = '/kmc_project.dtd'
PROCESSLIST_DTD = '/process_list.dtd'
SRCDIR = './fortran_src'
GLADEFILE = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')

def prettify_xml(elem):
    """This function takes an XML document, which can have one or many lines
    and turns it into a well-breaked, nicely-indented string
    """
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='    ')


def verbose(func):
    """Debugging helper that allows to track input and output of function
    via decoration"""
    print >> sys.stderr, "monitor %r" % (func.func_name)
    def wrapper_func(*args, **kwargs):
        """The wrapping function
        """
        print >> sys.stderr, "call(\033[0;31m%s.%s\033[0;30m): %r\n" % (type(args[0]).__name__, func.func_name, args[1 :]), sys.stderr.flush()
        ret = func(*args, **kwargs)
        print >> sys.stderr, "    ret(%s): \033[0;32m%r\033[0;30m\n" % (func.func_name, ret)
        return ret
    return wrapper_func


class Attributes:
    """Handy class that easily allows to define data structures
    that can only hold a well-defined set of fields
    """
    attributes = []
    def __init__(self, **kwargs):
        for attribute in self.attributes:
            if kwargs.has_key(attribute):
                self.__dict__[attribute] = kwargs[attribute]
        for key in kwargs:
            if key not in self.attributes:
                raise AttributeError, 'Tried to initialize illegal attribute %s' % key
    def __setattr__(self, attrname, value):
        if attrname in self.attributes:
            self.__dict__[attrname] = value
        else:
            raise AttributeError, 'Tried to set illegal attribute %s' % attrname

class CorrectlyNamed:
    """Syntactic Sugar class for use with kiwi, that makes sure that the name
    field of the class has a name field, that always complys with the rules for variables
    """
    def __init__(self):
        pass

    def on_name__validate(self, _, name):
        """Called by kiwi upon chaning a string
        """
        if ' ' in name:
            return ValidationError('No spaces allowed')
        elif name and not name[0].isalpha():
            return ValidationError('Need to start with a letter')

class Site(Attributes):
    """A class holding exactly one lattice site
    """
    attributes = ['index', 'name', 'site_x', 'site_y']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return '%s %s %s %s' % (self.name, self.index, self.site_x, self.site_y)

class Lattice(Attributes, CorrectlyNamed):
    """A class that defines exactly one lattice
    """
    attributes = ['name', 'unit_cell_size_x', 'unit_cell_size_y', 'sites']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.sites = []
        self.name = kwargs['name'] if 'name' in kwargs else ''

    def __repr__(self):
        return "%s %s %s\n\n%s" % (self.name, self.unit_cell_size_x, self.unit_cell_size_y, self.sites)

    def add_site(self, site):
        """Add a new site to a lattice
        """
        self.sites.append(site)

    def get_coords(self, site):
        """Return simple numerical representation of coordinates
        """
        local_site = filter(lambda x: x.name == site.coord.name, self.sites)[0]
        local_coords = local_site.site_x, local_site.site_y
        global_coords = site.coord.offset[0]*self.unit_cell_size_x, site.coord.offset[1]*self.unit_cell_size_y
        coords = [ x + y for (x, y) in zip(global_coords, local_coords) ]
        return coords


class ConditionAction(Attributes):
    """Class that holds either a condition or an action
    """
    attributes = ['species', 'coord']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return "Species: %s Coord:%s\n" % (self.species, self.coord)

class Coord(Attributes):
    """Class that hold exactly one coordinate as used in the description
    of a process
    """
    attributes = ['offset', 'name']
    def __init__(self, **kwargs):
        if kwargs.has_key('string'):
            raw = kwargs['string'].split('.')
            if len(raw) == 2 :
                self.name = raw[0]
                self.offset = eval(raw[1])
            elif len(raw) == 1 :
                self.name = raw[0]
                self.offset = [0, 0]
            else:
                raise TypeError, "Coordinate specification %s does not match the expected format" % raw

        else:
            Attributes.__init__(self, **kwargs)

    def __repr__(self):
        if filter(lambda x:x != 0, self.offset):
            return '%s.%s' % (self.name, self.offset)
        else:
            return '%s' % self.name

    def __eq__(self, other):
        return str(self) == str(other)


class Species(Attributes):
    """Class that represent a species such as oxygen, empty, ... . Not empty
    is treated just like a species.
    """
    attributes = ['name', 'color', 'id']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return 'Name: %s Color: %s ID: %s\n' % (self.name, self.color, self.id)


class SpeciesList(Attributes):
    """A list of species
    """
    attributes = ['default_species', 'name']
    def __init__(self, **kwargs):
        kwargs['name'] = 'Species'
        Attributes.__init__(self, **kwargs)


class ProcessList(Settable):
    """A list of processes
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Processes'
        Settable.__init__(self, **kwargs)

    def __lt__(self, other):
        return self.name < other.name
        

class ParameterList(Settable):
    """A list of parameters
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Parameters'
        Settable.__init__(self, **kwargs)


class LatticeList(Settable):
    """A list of lattices
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Lattices'
        Settable.__init__(self, **kwargs)


class Parameter(Attributes, CorrectlyNamed):
    """A parameter that can be used in a rate constant expression
    and defined via some init file
    """
    attributes = ['name', 'value']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return 'Name: %s Value: %s\n' % (self.name, self.value)

    def on_name__content_changed(self, _):
        self.project_tree.update(self.process)

    def get_extra(self):
        return self.value


class Meta(Settable, object):
    """Class holding the meta-information about the kMC project
    """
    name = 'Meta'
    def __init__(self):
        Settable.__init__(self, email='', author='', debug=0, model_name='', model_dimension=0)

    def add(self, attrib):
        for key in attrib:
            if key in ['debug', 'model_dimension']:
                self.__setattr__(key, int(attrib[key]))
            else:
                self.__setattr__(key, attrib[key])


class Process(Attributes):
    """One process in a kMC process list
    """
    attributes = ['name', 'rate_constant', 'condition_list', 'action_list']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.condition_list = []
        self.action_list = []
            
    def __repr__(self):
        return 'Name:%s Rate: %s\nConditions: %s\nActions: %s' % (self.name, self.rate_constant, self.condition_list, self.action_list)

    def add_condition(self, condition):
        self.condition_list.append(condition)

    def add_action(self, action):
        self.action_list.append(action)

    def get_extra(self):
        return self.rate_constant


class ProjectTree(SlaveDelegate):
    """A rather complex class holding all the information of a kMC project that provides
    a treelike view for the gui
    """
    def __init__(self, parent):
        self.project_data = ObjectTree([Column('name', data_type=str, sorted=True), Column('extra', data_type=str)])
        self.set_parent(parent)
        self.meta = self.project_data.append(None, Meta())
        self.lattice_list_iter = self.project_data.append(None, LatticeList())
        self.parameter_list_iter = self.project_data.append(None, ParameterList())
        self.species_list_iter = self.project_data.append(None, SpeciesList())
        self.process_list_iter = self.project_data.append(None, ProcessList())
        self.output_list = self.project_data.append(None, OutputList())
        self.output_list = []

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
        elif attr == 'output_list':
            return self.project_data.get_descendants(self.output_list_iter)
        elif attr == 'meta':
            return self.meta
        elif attr == 'append':
            return self.project_data.append
        elif attr == 'expand':
            return self.project_data.expand
        elif attr == 'update':
            return self.project_data.update
        elif attr == 'select':
            return self.project_data.select
        else:
            raise UserWarning, ('%s not found' % attr)

    def __repr__(self):
        return self._get_xml_string()

    def import_xml_file(self, filename):
        """Takes a filename, validates the content against kmc_project.dtd
        and import all fields into the current project tree
        """
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
                    size = [ int(x) for x in lattice.attrib['unit_cell_size'].split() ]
                    lattice_elem = Lattice(name=name, unit_cell_size_x=size[0], unit_cell_size_y=size[1])
                    for site in lattice:
                        index =  int(site.attrib['index'])
                        name = site.attrib['type']
                        coord = [ int(x) for x in site.attrib['coord'].split() ]
                        site_elem = Site(index=index, name=name, site_x=coord[0], site_y=coord[1])
                        lattice_elem.add_site(site_elem)
                    self.project_data.append(self.lattice_list_iter, lattice_elem)
            elif child.tag == 'meta':
                for attrib in ['author', 'email', 'debug', 'model_name', 'model_dimension']:
                    if child.attrib.has_key(attrib):
                        self.meta.add({attrib:child.attrib[attrib]})
            elif child.tag == 'parameter_list':
                for parameter in child:
                    name = parameter.attrib['name']
                    value = parameter.attrib['value']
                    parameter_elem = Parameter(name=name, value=value)
                    self.project_data.append(self.parameter_list_iter, parameter_elem)
            elif child.tag == 'process_list':
                for process in child:
                    name = process.attrib['name']
                    rate_constant = process.attrib['rate_constant']
                    process_elem = Process(name=name, rate_constant=rate_constant)
                    for sub in process:
                        if sub.tag == 'action' or sub.tag == 'condition':
                            species =  sub.attrib['species']
                            coord = Coord(string=sub.attrib['coord'])
                            condition_action = ConditionAction(species=species, coord=coord)
                            if sub.tag == 'action':
                                process_elem.add_action(condition_action)
                            elif sub.tag == 'condition':
                                process_elem.add_condition(condition_action)
                    self.project_data.append(self.process_list_iter, process_elem)
            elif child.tag == 'species_list':
                self.species_list_iter.default_species = child.attrib['default_species']
                for species in child:
                    name = species.attrib['name']
                    id = species.attrib['id']
                    color = species.attrib['color']
                    species_elem = Species(name=name, color=color, id=id)
                    self.project_data.append(self.species_list_iter, species_elem)
            if child.tag == 'output_list':
                for item in child:
                    output_elem = OutputItem(name=item.attrib['item'], output=True)
                    self.output_list.append(output_elem)

        self.expand_all()
        self.select_meta()


    def expand_all(self):
        """Expand all list of the project tree
        """
        self.project_data.expand(self.species_list_iter)
        self.project_data.expand(self.lattice_list_iter)
        self.project_data.expand(self.parameter_list_iter)
        self.project_data.expand(self.process_list_iter)

    def _export_process_list_xml(self):
        """This basically a legacy function: the part of the source code creator
        existed before and uses a slightly modified XML syntax which was faster to type
        by hand unnecesarily complex when using a GUI. So this function converts
        the current process list to the old form and passes along all essential
        information to the kmc_generator module
        """
        root = ET.Element('kmc')
        lattice = self.lattice_list[0]
        # extract meta information
        meta = ET.SubElement(root, 'meta')
        meta.set('name', self.meta.model_name)
        meta.set('author', self.meta.author)
        meta.set('dimension', str(self.meta.model_dimension))
        meta.set('debug', str(self.meta.debug))
        meta.set('lattice_module', '')
        # extract site_type information
        site_type_list = ET.SubElement(root, 'site_type_list')
        # extract species information
        species_list = ET.SubElement(root, 'species_list')
        for lattice in self.lattice_list:
            for site in lattice.sites:
                type = site.name
                site_type_elem = ET.SubElement(site_type_list, 'type')
                site_type_elem.set('name', type)
        for species in self.species_list:
            species_elem = ET.SubElement(species_list, 'species')
            species_elem.set('name', species.name)
            species_elem.set('id', str(species.id))
        # extract process list
        process_list = ET.SubElement(root, 'process_list')
        process_list.set('lattice', lattice.name)
        for process in self.process_list:
            process_elem = ET.SubElement(process_list, 'process')
            process_elem.set('name', process.name)
            process_elem.set('rate', process.rate_constant)
            condition_list = ET.SubElement(process_elem, 'condition_list')
            action_elem = ET.SubElement(process_elem, 'action')
            center_coord = lattice.get_coords(process.condition_list[0])
            #condition_list.set('center_site', ' '.join([str(x) for x in center_coord] ))
            for index, condition in enumerate(process.condition_list):
                coord = lattice.get_coords(condition)
                diff_coord = ' '.join([ str(x-y) for (x, y) in zip(coord, center_coord) ])
                type = condition.coord.name
                species = condition.species
                condition_elem = ET.SubElement(condition_list, 'condition')
                condition_elem.set('site', 'site_%s' % index)
                condition_elem.set('type', type)
                condition_elem.set('species', species)
                condition_elem.set('coordinate', diff_coord)

                # Create corresponding action field, if available
                actions = filter(lambda x: x.coord == condition.coord, process.action_list)
                if actions:
                    action = actions[0]
                replacement_elem = ET.SubElement(action_elem, 'replacement')
                replacement_elem.set('site', 'site_%s' % index)
                replacement_elem.set('new_species', action.species)



                
                
            # CONTINUE HERE
        return root

    def _get_xml_string(self):
        """Produces an XML representation of the project data
        """
        # build XML Tree
        root = ET.Element('kmc')
        meta = ET.SubElement(root, 'meta')
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
        species_list = ET.SubElement(root, 'species_list')
        if hasattr(self.species_list_iter, 'default_species'):
            species_list.set('default_species', self.species_list_iter.default_species)
        else:
            species_list.set('default_species', '')
            
        for species in self.species_list:
            species_elem = ET.SubElement(species_list, 'species')
            species_elem.set('name', species.name)
            species_elem.set('color', species.color)
            species_elem.set('id', str(species.id))
        parameter_list = ET.SubElement(root, 'parameter_list')
        for parameter in self.parameter_list:
            parameter_elem = ET.SubElement(parameter_list, 'parameter')
            parameter_elem.set('name', parameter.name)
            parameter_elem.set('value', str(parameter.value))
        lattice_list = ET.SubElement(root, 'lattice_list')
        for lattice in self.lattice_list:
            lattice_elem = ET.SubElement(lattice_list, 'lattice')
            size = [lattice.unit_cell_size_x, lattice.unit_cell_size_y ]
            lattice_elem.set('unit_cell_size', str(size)[1 :-1].replace(',', ''))
            lattice_elem.set('name', lattice.name)
            for site in lattice.sites:
                site_elem = ET.SubElement(lattice_elem, 'site')
                site_elem.set('index', str(site.index))
                site_elem.set('type', site.name)
                site_elem.set('coord', '%s %s' % (site.site_x, site.site_y))
        process_list = ET.SubElement(root, 'process_list')
        for process in self.process_list:
            process_elem = ET.SubElement(process_list, 'process')
            process_elem.set('rate_constant', process.rate_constant)
            process_elem.set('name', process.name)
            for condition in process.condition_list:
                condition_elem = ET.SubElement(process_elem, 'condition')
                condition_elem.set('species', condition.species)
                condition_elem.set('coord', str(condition.coord))
            for action in process.action_list:
                action_elem = ET.SubElement(process_elem, 'action')
                action_elem.set('species', action.species)
                action_elem.set('coord', str(action.coord))
        output_list = ET.SubElement(root, 'output_list')
        for output in self.output_list:
            if output.output:
                output_elem = ET.SubElement(output_list,'output')
                output_elem.set('item',output.name)
        return prettify_xml(root)


    def select_meta(self):
        """Make the treeview focus the meta entry
        """
        self.focus_topmost()
        self.on_project_data__selection_changed(0, self.meta)

    def on_key_press(self, _, event):
        """When the user hits the keyboard focusing the treeview
        this event is triggered. Right now the only supported function
        is to deleted the selected item
        """
        selection = self.project_data.get_selected()
        if gtk.gdk.keyval_name(event.keyval) == 'Delete':
            if isinstance(selection, Species) or isinstance(selection, Process) or isinstance(selection, Parameter) or isinstance(selection, Lattice):
                if kiwi.ui.dialogs.yesno("Do you really want to delete '%s'?" % selection.name) == gtk.RESPONSE_YES:
                    self.project_data.remove(selection)
                

    def on_project_data__selection_changed(self, _, elem):
        """When a new item is selected in the treeview this function
        loads the main area of the window with the corresponding form
        and data.
        """
        slave = self.get_parent().get_slave('workarea')
        if slave:
            self.get_parent().detach_slave('workarea')
        if isinstance(elem, Lattice):
            form = LatticeEditor(elem, self.project_data)
            #kiwi.ui.dialogs.warning('Changing lattice retro-actively might break processes.\nYou have been warned.')
            self.get_parent().attach_slave('workarea', form)
            form.on_unit_cell_ok_button__clicked(form.unit_cell_ok_button)
            form.focus_topmost()
        elif isinstance(elem, Meta):
            meta_form = MetaForm(self.meta)
            self.get_parent().attach_slave('workarea', meta_form)
            meta_form.focus_toplevel()
            meta_form.focus_topmost()
        elif isinstance(elem, OutputList):
            form = OutputForm(self.output_list, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Parameter):
            form = ParameterForm(elem, self.project_data)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Process):
            form = ProcessForm(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, ProcessList):
            form = BatchProcessForm(self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Species):
            form = SpeciesForm(elem, self.project_data)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, SpeciesList):
            form = SpeciesListForm(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        else:
            self.get_parent().toast('Not implemented, yet.')

class OutputList():
    """A dummy class, that will hold the values which are to be printed to logfile.
    """
    def __init__(self):
        self.name = 'Output'

class OutputItem(Attributes):
    """Not implemented yet
    """
    attributes = ['name', 'output']
    def __init__(self, *args, **kwargs):
        Attributes.__init__(self, **kwargs)

class OutputForm(GladeDelegate):
    """Not implemented yet
    """
    gladefile = GLADEFILE
    toplevel_name='output_form'
    widgets = ['output_list']
    def __init__(self, output_list, project_tree):
                
        GladeDelegate.__init__(self)
        self.project_tree = project_tree
        self.output_list_data = output_list
        self.output_list.set_columns([Column('name', data_type=str, editable=True, sorted=True), Column('output',data_type=bool, editable=True)])

        for item in self.output_list_data:
            self.output_list.append(item)

        self.output_list.show()
        self.output_list.grab_focus()

    def on_add_output__clicked(self, _):
        output_form = gtk.MessageDialog(parent=None,
                                      flags=gtk.DIALOG_MODAL,
                                      type=gtk.MESSAGE_QUESTION,
                                      buttons=gtk.BUTTONS_OK_CANCEL,
                                      message_format='Please enter a new output: examples are a species or species@site')
        form_entry = gtk.Entry()
        output_form.vbox.pack_start(form_entry)
        output_form.vbox.show_all()
        output_form.run()
        output_str = form_entry.get_text()
        output_form.destroy()
        output_item = OutputItem(name=output_str, output=True)
        self.output_list.append(output_item)
        self.output_list_data.append(output_item)
    

class BatchProcessForm(SlaveDelegate):
    gladefile = GLADEFILE
    toplevel_name = 'batch_process_form'
    def __init__(self, project_tree):
        self.project_tree = project_tree
        SlaveDelegate.__init__(self)

    def on_btn_evaluate__clicked(self, _):
        buffer = self.batch_processes.get_buffer()
        bounds = buffer.get_bounds()
        text = buffer.get_text(*bounds)
        text = text.split('\n')
        for i, line in enumerate(text):
            # Ignore empty lines
            if not line.count(';'):
                continue
            if not line.count(';'):
                raise UserWarning("Line %s: the number of fields you entered is %s, but I expected 3" % (i, line.count(';')+1))
                continue
            line = line.split(';')
            name = line[0]
            rate_constant = line[2]
            process = Process(name=name, rate_constant=rate_constant)
            try:
                parse_chemical_equation(eq=line[1], process=process, project_tree=self.project_tree)
            except:
                print("Found an error in your chemical equation(line %s):\n   %s" % (i+1, line[1]))
                raise
            else:
                self.project_tree.append(self.project_tree.process_list_iter, process)
        buffer.delete(*bounds)
    
    
class ProcessForm(ProxySlaveDelegate, CorrectlyNamed):
    """A form that allows to create and manipulate a process
    """
    gladefile = GLADEFILE
    toplevel_name = 'process_form'
    widgets = ['process_name', 'rate_constant' ]
    z = 4 # z as in zoom
    l = 500 # l as in length
    r_cond = 15.
    r_act = 10.
    r_reservoir = 5.
    r_site  = 5.
    # where the center unit cell is in the drawing
    X = 2; Y = 2
    def __init__(self, process, project_tree):
        self.process = process
        self.project_tree = project_tree
        self.lattice = self.project_tree.lattice_list[0]
        ProxySlaveDelegate.__init__(self, process)
        self.canvas = Canvas()
        self.canvas.set_flags(gtk.HAS_FOCUS | gtk.CAN_FOCUS)
        self.canvas.grab_focus()
        self.canvas.show()
        self.process_pad.add(self.canvas)
        self.lattice_layer = CanvasLayer(); self.canvas.append(self.lattice_layer)
        self.site_layer = CanvasLayer(); self.canvas.append(self.site_layer)
        self.condition_layer = CanvasLayer(); self.canvas.append(self.condition_layer)
        self.action_layer = CanvasLayer(); self.canvas.append(self.action_layer)
        self.frame_layer = CanvasLayer(); self.canvas.append(self.frame_layer)
        self.motion_layer = CanvasLayer(); self.canvas.append(self.motion_layer)

        # draw lattice
        for i in range(self.z):
            CanvasLine(self.lattice_layer, 0, i*(self.l/self.z), 500, i*(self.l/self.z), line_width=1, fg=(.6, .6, .6))
        for i in range(self.z):
            CanvasLine(self.lattice_layer, i*(self.l/self.z), 0, i*(self.l/self.z), 500, line_width=1, fg=(.6, .6, .6))
        for i in range(self.z+1):
            for j in range(self.z+1):
                for site in self.lattice.sites:
                    if i == self.X and j == self.Y:
                        l_site = CanvasOval(self.site_layer, 0, 0, 10, 10, fg=(1., 1., 1.))
                    else:
                        l_site = CanvasOval(self.site_layer, 0, 0, 10, 10, fg=(.6, .6, .6))

                    l_site.set_center(self.l/self.z*(i+float(site.site_x)/self.lattice.unit_cell_size_x), 500-self.l/self.z*(j+float(site.site_y)/self.lattice.unit_cell_size_y))
                    # 500 - ... for having scientific coordinates and note screen coordinates
                    l_site.set_radius(5)
                    l_site.i = i
                    l_site.j = j
                    l_site.name = site.name

        # draw frame
        frame_col = (.21, .35, .42)
        CanvasRect(self.frame_layer, 0, 0, 520, 80, fg=frame_col, bg=frame_col, filled=True)
        CanvasRect(self.frame_layer, 0, 0, 10, 580, fg=frame_col, bg=frame_col, filled=True)
        CanvasRect(self.frame_layer, 510, 0, 520, 580, fg=frame_col, bg=frame_col, filled=True)
        CanvasRect(self.frame_layer, 0, 580, 520, 590, fg=frame_col, bg=frame_col, filled=True)
        CanvasText(self.frame_layer, 10, 10, size=8, text='Reservoir Area')
        CanvasText(self.frame_layer, 10, 570, size=8, text='Lattice Area')

        for k, species in enumerate(self.project_tree.species_list):
            color = col_str2tuple(species.color)
            o = CanvasOval(self.frame_layer, 30+k*50, 30, 50+k*50, 50, filled=True, bg=color)
            o.species = species.name
            o.connect('button-press-event', self.button_press)
            o.connect('motion-notify-event', self.drag_motion)
            o.connect('button-release-event', self.button_release)
            o.state = 'reservoir'

        self.lattice_layer.move_all(10, 80)
        self.site_layer.move_all(10, 80)
        self.draw_from_data()

        # attributes need for moving objects
        self.item = None
        self.prev_pos = None


    def on_lattice(self, x, y):
        """Returns True if (x, y) is in lattice box
        """
        return 10 < x < 510 and 80 < y < 580
        
    def button_press(self, _, item, dummy):
        coords = item.get_coords()
        if item.state == 'reservoir':
            o = CanvasOval(self.motion_layer, *coords, filled=True, bg=item.bg)
            o.connect('button-press-event', self.button_press)
            o.connect('motion-notify-event', self.drag_motion)
            o.connect('button-release-event', self.button_release)
            o.state = 'from_reservoir'
            o.species = item.species
            self.item = o
            self.item.father = item
            self.prev_pos = self.item.get_center()
            self.canvas.redraw()


    def drag_motion(self, widget, item, event):
        d = event.x - self.prev_pos[0], event.y - self.prev_pos[1]
        self.item.move(*d)
        self.prev_pos = event.x, event.y

    #@verbose
    def button_release(self, _, dummy, event):
        if self.item.state == 'from_reservoir':
            if not self.on_lattice(event.x, event.y):
                self.item.delete()
            else:
                close_sites = self.site_layer.find_closest(event.x, event.y, halo=(.2*self.l)/self.z)
                if close_sites:
                    closest_site = min(close_sites, key=lambda i : (i.get_center()[0]-event.x)**2 + (i.get_center()[1]-event.y)**2)
                    coord = closest_site.get_center()
                    self.item.set_center(*coord)
                    if not self.process.condition_list + self.process.action_list:
                    # if no condition or action is defined yet,
                    # we need to set the center of the editor
                        self.X = closest_site.i
                        self.Y = closest_site.j
                    offset = closest_site.i - self.X, closest_site.j - self.Y
                    # name of the site
                    name = closest_site.name
                    species = self.item.species
                    condition_action = ConditionAction(species=species, coord=Coord(offset=offset, name=name))
                    if filter(lambda x: x.get_center() == coord, self.condition_layer):
                        self.item.new_parent(self.action_layer)
                        self.item.set_radius(self.r_act)
                        self.process.action_list.append(condition_action)
                    else:
                        self.item.new_parent(self.condition_layer)
                        self.item.set_radius(self.r_cond)
                        self.process.condition_list.append(condition_action)
                else:
                    self.item.delete()

                    
        self.canvas.redraw()


    def draw_from_data(self):
        """Places circles on the current lattice according
        to the conditions and actions defined
        """
        for elem in self.process.condition_list:
            coords = filter(lambda x: isinstance(x, CanvasOval) and x.i==self.X+elem.coord.offset[0] and x.j==self.Y+elem.coord.offset[1] and x.name==elem.coord.name, self.site_layer)[0].get_coords()
            color = filter(lambda x: x.name == elem.species, self.project_tree.species_list)[0].color
            color = col_str2tuple(color)
            o = CanvasOval(self.condition_layer, bg=color, filled=True)
            o.coords = coords
            o.set_radius(self.r_cond)

        for elem in self.process.action_list:
            coords = filter(lambda x: isinstance(x, CanvasOval) and x.i==self.X+elem.coord.offset[0] and x.j==self.Y+elem.coord.offset[1] and x.name==elem.coord.name, self.site_layer)[0].get_coords()
            color = filter(lambda x: x.name == elem.species, self.project_tree.species_list)[0].color
            color = col_str2tuple(color)
            o = CanvasOval(self.action_layer, bg=color, filled=True)
            o.coords = coords
            o.set_radius(self.r_act)

        
    def on_process_name__content_changed(self, text):
        self.project_tree.project_data.sort_by_attribute('name')
        self.project_tree.update(self.process)

    def on_rate_constant__content_changed(self, text):
        self.project_tree.update(self.process)

    def on_btn_chem_eq__clicked(self, button):
        """ get chemical expression from user
        """
        chem_form = gtk.MessageDialog(parent=None,
                                      flags=gtk.DIALOG_MODAL,
                                      type=gtk.MESSAGE_QUESTION,
                                      buttons=gtk.BUTTONS_OK_CANCEL,
                                      message_format='Please enter a chemical equation, e.g.:\n\nspecies1@site->species2@site')
        form_entry = gtk.Entry()
        chem_form.vbox.pack_start(form_entry)
        chem_form.vbox.show_all()
        chem_form.run()
        eq = form_entry.get_text()
        chem_form.destroy()

        parse_chemical_equation(eq, self.process, self.project_tree)

        self.draw_from_data()
        self.canvas.redraw()


class SiteForm(ProxyDelegate):
    """A form which allows to create or modify a site
    when setting up a unit cell
    """
    gladefile = GLADEFILE
    toplevel_name = 'site_form'
    widgets = ['site_name', 'site_index', 'site_x', 'site_y']
    def __init__(self, site, parent):
        ProxyDelegate.__init__(self, site)
        self.site = site
        self.parent = parent
        self.site_x.set_value(site.site_x)
        self.site_y.set_value(site.site_y)
        self.site_x.set_sensitive(False)
        self.site_y.set_sensitive(False)
        self.site_index.set_sensitive(False)
        self.show_all()



    def on_site_name__validate(self, widget, site_name):
        # check if other site already has the name
        if  filter(lambda x : x.name == site_name, self.parent.model.sites):
            self.site_ok.set_sensitive(False)
            return ValidationError('Site name needs to be unique')
        else:
            self.site_ok.set_sensitive(True)


    def on_site_ok__clicked(self, button):
        if len(self.site_name.get_text()) == 0 :
            self.parent.model.sites.remove(self.model)
            for node in self.parent.site_layer:
                if node.coord[0] == self.site_x.get_value_as_int() and node.coord[1] == self.site_y.get_value_as_int():
                    node.filled = False
        else:
            for node in self.parent.site_layer:
                if node.coord[0] == self.site_x.get_value_as_int() and node.coord[1] == self.site_y.get_value_as_int():
                    node.filled = True
        self.parent.canvas.redraw()
        self.hide()


class LatticeEditor(ProxySlaveDelegate, CorrectlyNamed):
    """Widget to define a lattice and the unit cell
    """
    gladefile = GLADEFILE
    toplevel_name = 'lattice_form'
    widgets = ['lattice_name', 'unit_x', 'unit_y']
    def __init__(self, lattice, project_tree):
        ProxySlaveDelegate.__init__(self, lattice)
        self.project_tree = project_tree
        self.canvas = Canvas()
        self.canvas.set_flags(gtk.HAS_FOCUS | gtk.CAN_FOCUS)
        self.canvas.grab_focus()
        self.grid_layer = CanvasLayer()
        self.site_layer = CanvasLayer()
        self.canvas.append(self.grid_layer)
        self.canvas.append(self.site_layer)
        self.lattice_pad.add(self.canvas)

        self.unit_cell_ok_button.set_sensitive(False)
        self.on_lattice_name__content_changed(self.lattice_name)

    def on_unit_cell_ok_button__clicked(self, button):
        if button.get_label() == 'gtk-ok':
            X, Y = 400, 400
            button.set_label('Reset')
            button.set_tooltip_text('Delete all sites and start anew')
            x = self.unit_x.get_value_as_int()
            y = self.unit_y.get_value_as_int()
            self.unit_x.set_sensitive(False)
            self.unit_y.set_sensitive(False)
            self.canvas.show()
            for i in range(x+1):
                lx = CanvasLine(self.grid_layer,  i*(X/x), 0, i*(X/x), Y, bg=(0., 0., 0.))
            for i in range(y+1):
                ly = CanvasLine(self.grid_layer, 0 , i*(Y/y), X, i*(Y/y), bg=(0., 0., 0.))
            for i in range(x+1):
                for j in range(y+1):
                    r = 10
                    o = CanvasOval(self.site_layer, i*(X/x)-r, j*(Y/y)-r, i*(X/x)+r, j*(Y/y)+r, bg=(1., 1., 1.))
                    o.coord = i % x, (y-j) % y
                    o.connect('button-press-event', self.site_press_event)
                    for node in self.model.sites:
                        if node.site_x == o.coord[0] and node.site_y == o.coord[1]:
                            o.filled = True

            self.canvas.move_all(50, 50)
        elif button.get_label()=='Reset':
            while self.site_layer:
                self.site_layer.pop()
            while self.grid_layer:
                self.grid_layer.pop()
            button.set_label('gtk-ok')
            button.set_tooltip_text('Add sites')
            self.model.sites = []
            self.unit_x.set_sensitive(True)
            self.unit_y.set_sensitive(True)

            self.canvas.redraw()
            self.canvas.hide()

    def on_lattice_name__validate(self, widget, lattice_name):
        return self.on_name__validate(widget, lattice_name)

    def on_lattice_name__content_changed(self, widget):
        self.project_tree.update(self.model)
        if  widget.get_text_length() == 0 :
            self.unit_cell_ok_button.set_sensitive(False)
        else:
            self.unit_cell_ok_button.set_sensitive(True)

    def site_press_event(self, widget, item, event):
        if item.filled:
            new_site = filter(lambda x: (x.site_x, x.site_y) == item.coord, self.model.sites)[0]
        else:
            # choose the smallest number that is not given away
            indexes = [x.index for x in self.model.sites]
            for i in range(1, len(indexes)+2):
                if i not in indexes:
                    index = i
                    break
            new_site = Site(site_x=item.coord[0], site_y=item.coord[1], name='', index=index)
            self.model.sites.append(new_site)
        site_form = SiteForm(new_site, self)


class MetaForm(ProxySlaveDelegate, CorrectlyNamed):
    """A form  that allows to enter meta information about the project
    """
    gladefile = GLADEFILE
    toplevel_name = 'meta_form'
    widgets = ['author', 'email', 'model_name', 'model_dimension', 'debug']
    def __init__(self, model):
        ProxySlaveDelegate.__init__(self, model)
        self.model_dimension.set_sensitive(False)

    def on_model_name__validate(self, widget, model_name):
        return self.on_name__validate(widget, model_name)


class InlineMessage(SlaveView):
    """Return a nice little field with a text message on it
    """
    gladefile = GLADEFILE
    toplevel_name = 'inline_message'
    widgets = ['message_label']
    def __init__(self, message=''):
        SlaveView.__init__(self)
        self.message_label.set_text(message)


class ParameterForm(ProxySlaveDelegate, CorrectlyNamed):
    gladefile = GLADEFILE
    toplevel_name = 'parameter_form'
    widgets = ['parameter_name', 'value']
    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        self.name.grab_focus()

    def on_value__content_changed(self, text):
        self.project_tree.update(self.model)

    def on_parameter_name__content_changed(self, text):
        self.project_tree.project_data.sort_by_attribute('name')
        self.project_tree.update(self.model)


class SpeciesListForm(ProxySlaveDelegate):
    gladefile = GLADEFILE
    toplevel_name = 'species_list_form'
    widgets = ['default_species']
    def __init__(self, model, project_tree):
        # this _ugly_ implementation is due to an apparent catch 22 bug in ProxyComboBox:
        # if the value is set already __init__ expect the value in the list but
        # you cannot fill the list before calling __init__
        default_species = model.default_species
        model.default_species = None
        ProxySlaveDelegate.__init__(self, model)
        self.default_species.prefill([ x.name for x in project_tree.species_list], sort=True)
        self.default_species.select(default_species)


class SpeciesForm(ProxySlaveDelegate, CorrectlyNamed):
    gladefile = GLADEFILE
    toplevel_name = 'species_form'
    widgets = ['name', 'color', 'id']
    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        self.id.set_sensitive(False)
        self.name.grab_focus()
        self.default_species

    def on_name__content_changed(self, text):
        self.project_tree.update(self.model)


class KMC_Editor(GladeDelegate):
    widgets = ['workarea', 'statbar']
    gladefile = GLADEFILE
    toplevel_name = 'main_window'
    def __init__(self):
        self.project_tree = ProjectTree(parent=self)
        GladeDelegate.__init__(self, delete_handler=self.on_btn_quit__clicked)
        self.attach_slave('overviewtree', self.project_tree)
        self.set_title(self.project_tree.get_name())
        self.project_tree.show()

        self.saved_state = str(self.project_tree)
        # Cast initial message
        self.toast('Start a new project by filling in\n'
        + '    * meta information\n    * lattice \n    * species\n    * parameters\n    * processes \n    * output fields\n in roughly this order or open an existing one by opening a kMC XML file.\n\n\n'+
        'If you want to run the model run hit "Export Source", where\n'+
        'you will get a fully self-contained Fortran source code\n'+
        'of the model and further instructions'
        )

    def add_defaults(self):
        """This function adds some useful defaults that are probably need in every simulation
        """
        # add dimension
        self.project_tree.meta.add({'model_dimension':'2'})
        # add an empty species
        empty = Species(name='empty', color='#fff', id='0')
        # set empty as default species
        self.project_tree.species_list_iter.default_species = 'empty'
        self.project_tree.append(self.project_tree.species_list_iter, empty)
        # add standard parameter
        param = Parameter(name='lattice_size', value='40 40')
        self.project_tree.append(self.project_tree.parameter_list_iter, param)

        param = Parameter(name='print_every', value='1.e5')
        self.project_tree.append(self.project_tree.parameter_list_iter, param)

        param = Parameter(name='total_steps', value='1.e7')
        self.project_tree.append(self.project_tree.parameter_list_iter, param)

        # add output entries
        self.output_list.append(OutputItem(name='kmc_time',output=True))
        self.output_list.append(OutputItem(name='walltime',output=False))
        self.output_list.append(OutputItem(name='kmc_step',output=False))

        self.project_tree.expand_all()


    def toast(self, toast):
        """Present a nice little text in the middle of the workarea
        as a standard way write inline messages to the user
        """
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        inline_message = InlineMessage(toast)
        self.attach_slave('workarea', inline_message)
        inline_message.show()

    def on_btn_new_project__clicked(self, button):
        """Start a new project
        """
        if str(self.project_tree) != self.saved_state:
            # if there are unsaved changes, ask what to do first
            save_changes_dialog = gtk.Dialog(
                                    buttons=(gtk.STOCK_DISCARD, gtk.RESPONSE_DELETE_EVENT, 
                                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                                    title='Saved unsaved changes?')
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
        # Instantiate new project data
        self.project_tree = ProjectTree(parent=self)
        if self.get_slave('overviewtree'):
            self.detach_slave('overviewtree')
        self.attach_slave('overviewtree', self.project_tree)
        self.project_tree.show()
        self.toast('Start a new project by filling in meta information,\nlattice, species, parameters, and processes or open an existing one\nby opening a kMC XML file')

    def on_btn_add_lattice__clicked(self, button):
        """Add a new lattice to the model
        """
        if len(self.project_tree.lattice_list) < 2 :
            new_lattice = Lattice()
            self.project_tree.append(self.project_tree.lattice_list_iter, new_lattice)
            lattice_form = LatticeEditor(new_lattice, self.project_tree)
            self.project_tree.expand(self.project_tree.lattice_list_iter)
            if self.get_slave('workarea'):
                self.detach_slave('workarea')
            self.attach_slave('workarea', lattice_form)
            lattice_form.focus_topmost()
        else:
            self.toast('Sorry, no multi-lattice support, yet.')

    def on_btn_add_species__clicked(self, button):
        """Add a new species to the model
        """
        new_species = Species(color='#fff', name='')
        self.project_tree.append(self.project_tree.species_list_iter, new_species)
        self.project_tree.expand(self.project_tree.species_list_iter)
        self.project_tree.select(new_species)
        new_species.id = "%s" % (len(self.project_tree.species_list))
        species_form = SpeciesForm(new_species, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', species_form)
        species_form.focus_topmost()

    def on_btn_add_process__clicked(self, button):
        """Add a new process to the model
        """
        if not self.project_tree.lattice_list:
            self.toast("No lattice defined, yet!")
            return
        new_process = Process(name='', rate_constant='')
        self.project_tree.append(self.project_tree.process_list_iter, new_process)
        self.project_tree.expand(self.project_tree.process_list_iter)
        self.project_tree.select(new_process)
        process_form = ProcessForm(new_process, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', process_form)
        process_form.focus_topmost()

    def on_btn_add_parameter__clicked(self, button):
        new_parameter = Parameter(name='', value='')
        self.project_tree.append(self.project_tree.parameter_list_iter, new_parameter)
        self.project_tree.expand(self.project_tree.parameter_list_iter)
        self.project_tree.select(new_parameter)
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
            save_changes_dialog = gtk.Dialog(
                                buttons=(gtk.STOCK_DISCARD, gtk.RESPONSE_DELETE_EVENT,
                                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                                title='Saved unsaved changes?')
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
            self.import_file(filename)

    def import_file(self, filename):
        # Import
        self.project_tree.import_xml_file(filename)
        self.set_title(self.project_tree.get_name())
        self.toast('Imported model %s' % self.project_tree.meta.model_name)
        self.saved_state = str(self.project_tree)

    def on_btn_save_model__clicked(self, button, force_save=False):
        #Write Out XML File
        xml_string = str(self.project_tree)
        if xml_string == self.saved_state and not force_save:
            self.toast('Nothing to save')
        else:
            if not self.project_tree.filename:
                self.on_btn_save_as__clicked(None)
            outfile = open(self.project_tree.filename, 'w')
            outfile.write(xml_string)
            outfile.write('<!-- This is an automatically generated XML file, representing a kMC model ' + \
                            'please do not change this unless you know what you are doing -->\n')
            outfile.close()
            self.saved_state = xml_string
            self.toast('Saved %s' % self.project_tree.filename)


    def on_btn_save_as__clicked(self, button):
        filechooser = gtk.FileChooserDialog(title='Save Project As ...',
            action = gtk.FILE_CHOOSER_ACTION_SAVE,
            parent=None,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK ))
        filechooser.set_property('do-overwrite-confirmation', True)
        resp = filechooser.run()
        if resp == gtk.RESPONSE_OK:
            self.project_tree.filename = filechooser.get_filename()
            self.on_btn_save_model__clicked(None, force_save=True)
        filechooser.destroy()

    #@verbose
    def on_btn_export_src__clicked(self, button, export_dir=''):
        self.toast('Exporting ...')
        if not export_dir:
            export_dir = kiwi.ui.dialogs.selectfolder(title='Select folder for F90 source code.')
        if not export_dir:
            self.toast('No folder selected')
            return
        if not os.path.exists(export_dir):
            os.mkdir(export_dir)

        # copy files
        for filename in [ 'base.f90', 'kind_values_f2py.f90', 'units.f90', 'assert.ppc', 'compile_for_f2py', 'run_kmc.py']:
            shutil.copy(APP_ABS_PATH + '/%s' % filename, export_dir)



        lattice_source = open(APP_ABS_PATH + '/lattice_template.f90').read()
	if len(self.project_tree.lattice_list)==0:
            self.toast("No lattice defined, yet. Cannot complete source")
            return
        # more processing steps ...
        # species definition
        if not self.project_tree.species_list:
            self.toast('No species defined, yet, cannot complete source')
            return
        species_definition = "integer(kind=iint), public, parameter :: &\n "
        for species in self.project_tree.species_list[:-1]:
            species_definition += '    %(species)s =  %(id)s, &\n' % {'species':species.name, 'id':species.id}
        species_definition += '     %(species)s = %(id)s\n' % {'species':self.project_tree.species_list[-1].name, 'id':self.project_tree.species_list[-1].id}
        species_definition += 'character(len=800), dimension(%s) :: species_list\n' % len(self.project_tree.species_list)
        species_definition += 'integer(kind=iint), parameter :: nr_of_species = %s\n' % len(self.project_tree.species_list)
        species_definition += 'integer(kind=iint), parameter :: nr_of_lattices = %s\n' % len(self.project_tree.lattice_list)
        species_definition += 'character(len=800), dimension(%s) :: lattice_list\n' % len(self.project_tree.lattice_list)
	list_nr_of_sites = ', '.join([ str(len(lattice.sites)) for lattice in self.project_tree.lattice_list ])
	species_definition += 'integer(kind=iint), parameter, dimension(%s) :: nr_of_sites = (/%s/)\n' % (len(self.project_tree.lattice_list), list_nr_of_sites)
	species_definition += 'character(len=800), dimension(%s, %s) :: site_list\n' % (len(self.project_tree.lattice_list), lattice.name)

        # unit vector definition
        unit_vector_definition = 'integer(kind=iint), dimension(2, 2) ::  lattice_matrix = reshape((/%(x)s, 0, 0, %(y)s/), (/2, 2/))' % {'x':lattice.unit_cell_size_x, 'y':lattice.unit_cell_size_y}
        # lookup table initialization
        indexes = [ x.index for x in lattice.sites ]
        lookup_table_definition = ''
        lattice_mapping_functions = ''
	lattice_mapping_template = open(APP_ABS_PATH + '/lattice_mapping_template.f90').read()
	for lattice_nr, lattice in enumerate(self.project_tree.lattice_list):
            lattice_mapping_functions += lattice_mapping_template % {'lattice_name':lattice.name,
            'sites_per_cell':max(indexes)-min(indexes)+1,}
	    
            lookup_table_init = 'integer(kind=iint), dimension(0:%(x)s, 0:%(y)s) :: lookup_%(lattice)s2nr\n' % {'x':lattice.unit_cell_size_x-1, 'y':lattice.unit_cell_size_y-1, 'lattice':lattice.name}
            lookup_table_init += 'integer(kind=iint), dimension(%(min)s:%(max)s, 2) :: lookup_nr2%(lattice)s\n' % {'min':min(indexes), 'max':max(indexes), 'lattice':lattice.name}

            # lookup table definition
            lookup_table_definition += '! Fill lookup table nr2%(name)s\n' % {'name':lattice.name }
            for i, site in enumerate(lattice.sites):
                lookup_table_definition +=  '    site_list(%s) = "%s"\n' % (i+1, site.name)
                lookup_table_definition += '    lookup_nr2%(name)s(%(index)s, :) = (/%(x)s, %(y)s/)\n' % {'name': lattice.name,
                                                                                                    'x':site.site_x,
                                                                                                    'y':site.site_y,
                                                                                                    'index':site.index}
            lookup_table_definition += '\n\n    ! Fill lookup table %(name)s2nr\n' % {'name':lattice.name }
            for site in lattice.sites:
                lookup_table_definition += '    lookup_%(name)s2nr(%(x)s, %(y)s) = %(index)s\n'  % {'name': lattice.name,
                                                                                                    'x':site.site_x,
                                                                                                    'y':site.site_y,
                                                                                                    'index':site.index}
        for i, species in enumerate(self.project_tree.species_list):
            lookup_table_definition +=  '    species_list(%s) = "%s_%s"\n' % (10*lattice_nr + i+1, species.name, lattice.name)
            lookup_table_definition +=  '    lattice_list(%s) = "%s"\n' % (i+1, lattice.name)



        #lattice mappings
        lattice_source = lattice_source % {
            'species_definition':species_definition,
            'lookup_table_init':lookup_table_init,
            'lookup_table_definition':lookup_table_definition,
            'unit_vector_definition':unit_vector_definition,
            'sites_per_cell':max(indexes)-min(indexes)+1,
            'lattice_mapping_functions':lattice_mapping_functions}

        lattice_mod_file = open(export_dir + '/lattice.f90', 'w')
        lattice_mod_file.write(lattice_source)
        lattice_mod_file.close()

        # export parameters
        config = SafeConfigParser()
        # Prevent configparser from turning options to lowercase
        config.optionxform = str
        config.add_section('Main')
        config.set('Main','default_species',self.project_tree.species_list_iter.default_species)
        config.set('Main','system_name',self.project_tree.meta.model_name)
        config.set('Main','output_fields',' '.join([x.name for x in self.project_tree.output_list ]))
        config.add_section('User Params')
        for parameter in self.project_tree.parameter_list:
            config.set('User Params',parameter.name,str(parameter.value))

        with open(export_dir + '/params.cfg','w') as configfile:
            config.write(configfile)
            


        # generate process list source via existing code
        proclist_xml = open(export_dir + '/process_list.xml', 'w')
        pretty_xml = prettify_xml(self.project_tree._export_process_list_xml())
        proclist_xml.write(pretty_xml)
        proclist_xml.close()
        class Options(): pass
        options = Options()
        options.xml_filename = proclist_xml.name
        options.dtd_filename = APP_ABS_PATH + '/process_list.dtd'
        options.force_overwrite = True
        options.proclist_filename = export_dir + '/proclist.f90'

        ProcListWriter(options)


        # return directory name
        self.toast('Wrote FORTRAN sources to %s\n' % export_dir
         + 'Please go to the directory and run ./compile_for_f2py,\n'+
           'which you might have to adapt slightly.\n' +
           'If this finished successfully you can run the simulation\n'+
           'by executing ./run_kmc.py')


    def validate_model(self):
        pass
        # check if all  lattice sites are unique
        # check if all lattice names are unique
        # check if all parameter names are unique
        # check if all process names are unique
        # check if all processes have at least one condition
        # check if all processes have at least one action
        # check if all processes have a rate expression 
        # check if all rate expressions are valid
        # check if all species have a unique name
        # check if all species have a unique id
        # check if all species used in condition_action are defined
        # check if all sites used in processes are defined: actions, conditions

    def on_btn_help__clicked(self, button):
        self.toast('"Help" is not implemented, yet.')


    def on_btn_quit__clicked(self, button, *args):
        if self.saved_state != str(self.project_tree):
            save_changes_dialog = gtk.Dialog(
                                  buttons=(gtk.STOCK_DISCARD, gtk.RESPONSE_DELETE_EVENT,
                                  gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                                  title='Saved unsaved changes?')
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



def parse_chemical_equation(eq, process, project_tree):
    """Evaluates a chemical equation 'eq' and adds
    conditions and actions accordingly
    """
    # remove spaces
    eq = re.sub(' ', '', eq)

    # split at ->
    if eq.count('->') > 1 :
        raise StandardError, 'Chemical expression may contain at most one "->"\n%s'  % eq
    eq = re.split('->', eq)
    if len(eq) == 2 :
        left = eq[0]
        right = eq[1]
    elif len(eq) == 1 :
        left = eq[0]
        right = ''

    # split terms
    left = left.split('+')
    right = right.split('+')

    while '' in left:
        left.remove('')

    while '' in right:
        right.remove('')

    # small validity checking
    for term in left+right:
        if term.count('@') != 1 :
            raise StandardError, 'Each term needs to contain exactly one @:\n%s' % term

    # split each term again at @
    for i, term in enumerate(left):
        left[i] = term.split('@')
    for i, term in enumerate(right):
        right[i] = term.split('@')

    for term in left + right:
        if not filter(lambda x: x.name == term[0], project_tree.species_list):
            raise UserWarning('Species %s unknown ' % term[0])
        if not filter(lambda x: x.name == term[1].split('.')[0], project_tree.lattice_list[0].sites):
            raise UserWarning('Site %s unknown' % term[1])

    condition_list = []
    action_list = []
    for term in left:
        condition_list.append(ConditionAction(species=term[0], coord=Coord(string=term[1])))
    for term in right:
        action_list.append(ConditionAction(species=term[0], coord=Coord(string=term[1])))

    default_species = project_tree.species_list_iter.default_species
    # every condition that does not have a corresponding action on the 
    # same coordinate gets complemented with a 'default_species' action
    for condition in condition_list:
        if not filter(lambda x: x.coord == condition.coord, action_list):
            action_list.append(ConditionAction(species=default_species, coord=Coord(string=str(condition.coord))))

    # every action that does not have a corresponding condition on
    # the same coordinate gets complemented with a 'default_species'
    # condition
    for action in action_list:
        if not filter(lambda x: x.coord == action.coord, condition_list):
            condition_list.append(ConditionAction(species=default_species, coord=Coord(string=str(action.coord))))
    process.condition_list += condition_list
    process.action_list += action_list


def col_str2tuple(hex_string):
    color = gtk.gdk.Color(hex_string)
    return (color.red_float, color.green_float, color.blue_float)




if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-o', '--open', dest='import_file', help='Immediately import store kmc file')
    parser.add_option('-x', '--export-dir', dest='export_dir', type=str, default='')
    (options, args) = parser.parse_args()
    editor = KMC_Editor()
    if options.import_file:
        editor.import_file(options.import_file)
        editor.toast('Imported %s' % options.import_file)
	if hasattr(options, 'export_dir'):
            print('Exporting right-away')
            editor.on_btn_export_src__clicked(button='', export_dir=options.export_dir)
            exit()
		
    else:
        editor.add_defaults()
        editor.saved_state = str(editor.project_tree)
    editor.show_and_loop()
