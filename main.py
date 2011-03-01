#!/usr/bin/env python
"""The main part of the kmc gui project
"""
# standard modules
import optparse
from ConfigParser import SafeConfigParser
import sys
import os, os.path
# import own modules
from app.config import *
from app.models import *
from app.forms import *
from app.proclist_generator import ProcListWriter as MLProcListWriter
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
from app.kmc_generator import ProcessList as ProcListWriter


#Kiwi imports
from kiwi.ui.views import BaseView
from kiwi.controllers import BaseController
import kiwi.ui
from kiwi.ui.delegates import Delegate, SlaveDelegate, GladeDelegate, GladeSlaveDelegate
from kiwi.ui.objectlist import ObjectList, ObjectTree, Column
import kiwi.ui.dialogs 


KMCPROJECT_DTD = '/kmc_project.dtd'
MLKMCPROJECT_DTD = '/ml_kmc_project.dtd'
PROCESSLIST_DTD = '/process_list.dtd'

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


class ProjectTree(SlaveDelegate):
    """A rather complex class holding all the information of a kMC project that provides
    a treelike view for the gui
    """
    def __init__(self, parent):
        self.project_data = ObjectTree([Column('name',use_markup=True, data_type=str, sorted=True), Column('info')])

        self.project_data.connect('row-activated',self.on_row_activated)


        self.set_parent(parent)
        self.meta = self.project_data.append(None, Meta())
        self.layer_list_iter = self.project_data.append(None, LayerList())
        self.lattice = self.layer_list_iter
        self.parameter_list_iter = self.project_data.append(None, ParameterList())
        self.species_list_iter = self.project_data.append(None, SpeciesList())
        self.process_list_iter = self.project_data.append(None, ProcessList())
        self.output_list = self.project_data.append(None, OutputList())
        self.output_list = []

        self.filename = ''

        SlaveDelegate.__init__(self, toplevel=self.project_data)

    def update(self, model):
        self.project_data.update(model)


    def on_row_activated(self, tree, data):
        if isinstance(data, Layer):
            data.active = not data.active

    def get_name(self):
        if self.filename:
            return os.path.basename(self.filename)
        else:
            return 'Untitled'
    def __getattr__(self, attr):
        if attr == 'species_list':
            return sorted(self.project_data.get_descendants(self.species_list_iter), key=lambda species: species.name)
        elif attr == 'layer_list':
            return sorted(self.project_data.get_descendants(self.layer_list_iter), key=lambda layer: layer.name)
        elif attr == 'process_list':
            return sorted(self.project_data.get_descendants(self.process_list_iter), key=lambda process: process.name)
        elif attr == 'parameter_list':
            return sorted(self.project_data.get_descendants(self.parameter_list_iter), key=lambda parameter: parameter.name)
        elif attr == 'output_list':
            return sorted(self.project_data.get_descendants(self.output_list_iter), key=lambda output: output.name)
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
        if root.tag == 'ml_kmc':
            self.ml = True
        else:
            self.ml = False
        if self.ml:
            dtd = ET.DTD(APP_ABS_PATH + MLKMCPROJECT_DTD)
        else:
            dtd = ET.DTD(APP_ABS_PATH + KMCPROJECT_DTD)
            raise UserWarning('This is a single-lattice kmc project which is not supported in this development\n' +
                'version of kmos\n')
        if not dtd.validate(root):
            print(dtd.error_log.filter_from_errors()[0])
            return
        for child in root:
            if child.tag == 'lattice':
                cell_size = [float(x) for x in child.attrib['cell_size'].split()]
                self.lattice.cell_size_x = cell_size[0]
                self.lattice.cell_size_y = cell_size[1]
                self.lattice.cell_size_z = cell_size[2]
                self.lattice.default_layer = child.attrib['default_layer']
                if 'representation' in child.attrib:
                    self.lattice.representation = child.attrib['representation']
                else:
                    self.lattice.representation = ''
                for elem in child:
                    if elem.tag == 'layer':
                        name = elem.attrib['name']
                        x, y, z = [int(i) for i in elem.attrib['grid'].split()]
                        ox, oy, oz = [float(i) for i in elem.attrib['grid_offset'].split()]
                        grid = Grid(x=x, y=y, z=z,
                            offset_x=ox, offset_y=oy, offset_z=oz)
                        layer = Layer(name=name, grid=grid)
                        self.project_data.append(self.layer_list_iter, layer)
                        for site in elem:
                            name = site.attrib['type']
                            x, y, z = [ float(x) for x in site.attrib['vector'].split() ]
                            site_class = site.attrib['class']
                            if 'default_species' in site.attrib:
                                default_species = site.attrib['default_species']
                            else:
                                default_species = 'default_species'
                            site_elem = Site(name=name,
                                x=x, y=y, z=z,
                                site_class=site_class,
                                default_species=default_species)
                            layer.sites.append(site_elem)
                    elif elem.tag == 'site_class':
                        # ignored for now
                        pass
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
                    if 'enabled' in process.attrib:
                        try:    
                            proc_enabled = bool(eval(process.attrib['enabled']))
                        except:
                            proc_enabled = True
                    else:
                        proc_enabled = True
                    process_elem = Process(name=name, rate_constant=rate_constant,enabled=proc_enabled)
                    for sub in process:
                        if sub.tag == 'action' or sub.tag == 'condition':
                            species =  sub.attrib['species']
                            coord_layer = sub.attrib['coord_layer']
                            coord_name = sub.attrib['coord_name']
                            coord_offset = tuple(
                                [int(i) for i in 
                                sub.attrib['coord_offset'].split()])
                            coord = Coord(layer=coord_layer,
                                          name=coord_name,
                                          offset=coord_offset)
                            condition_action = ConditionAction(
                                species=species,coord=coord)
                            if sub.tag == 'action':
                                process_elem.add_action(condition_action)
                            elif sub.tag == 'condition':
                                process_elem.add_condition(condition_action)
                    self.project_data.append(self.process_list_iter, process_elem)
            elif child.tag == 'species_list':
                self.species_list_iter.default_species = child.attrib['default_species']
                for species in child:
                    name = species.attrib['name']
                    color = species.attrib['color']
                    representation = species.attrib['representation'] if 'representation' in species.attrib else ''
                    species_elem = Species(name=name, color=color, representation=representation)
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
        self.project_data.expand(self.layer_list_iter)
        self.project_data.expand(self.parameter_list_iter)
        self.project_data.expand(self.process_list_iter)


    def _get_xml_string(self):
        """Produces an XML representation of the project data
        """
        # build XML Tree
        root = ET.Element('ml_kmc')
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
            species_elem.set('representation', species.representation)
        parameter_list = ET.SubElement(root, 'parameter_list')
        for parameter in self.parameter_list:
            parameter_elem = ET.SubElement(parameter_list, 'parameter')
            parameter_elem.set('name', parameter.name)
            parameter_elem.set('value', str(parameter.value))
        lattice_elem = ET.SubElement(root, 'lattice')
        if (hasattr(self.layer_list_iter, 'cell_size_x') and \
            hasattr(self.layer_list_iter, 'cell_size_y') and
            hasattr(self.layer_list_iter, 'cell_size_z')):
            lattice_elem.set('cell_size', '%s %s %s' %
            (self.layer_list_iter.cell_size_x,
            self.layer_list_iter.cell_size_y,
            self.layer_list_iter.cell_size_z))
            lattice_elem.set('default_layer', self.layer_list_iter.default_layer)
        if hasattr(self.lattice, 'representation'):
            lattice_elem.set('representation', self.lattice.representation)
        for layer in self.layer_list:
            layer_elem = ET.SubElement(lattice_elem, 'layer')
            layer_elem.set('name', layer.name)
            if (hasattr(layer.grid, 'x') and\
            hasattr(layer.grid, 'y') and
            hasattr(layer.grid, 'z')):
                layer_elem.set('grid',
                    '%s %s %s' % (layer.grid.x,
                                  layer.grid.y,
                                  layer.grid.z))
            if (hasattr(layer.grid, 'offset_x') and\
            hasattr(layer.grid, 'offset_y') and
            hasattr(layer.grid, 'offset_z')):
                layer_elem.set('grid_offset',
                    '%s %s %s' % (layer.grid.offset_x,
                                  layer.grid.offset_y,
                                  layer.grid.offset_z))
                
            for site in layer.sites:
                site_elem = ET.SubElement(layer_elem, 'site')
                site_elem.set('vector', '%s %s %s' % (site.x, site.y, site.z))
                site_elem.set('type', site.name)
                site_elem.set('class', site.site_class)
                site_elem.set('default_species', site.default_species)


        process_list = ET.SubElement(root, 'process_list')
        for process in self.process_list:
            process_elem = ET.SubElement(process_list, 'process')
            process_elem.set('rate_constant', process.rate_constant)
            process_elem.set('name', process.name)
            process_elem.set('enabled',str(process.enabled))
            for condition in process.condition_list:
                condition_elem = ET.SubElement(process_elem, 'condition')
                condition_elem.set('species', condition.species)
                condition_elem.set('coord_layer', condition.coord.layer)
                condition_elem.set('coord_name', condition.coord.name)
                condition_elem.set('coord_offset', 
                    ' '.join([str(i) for i in condition.coord.offset]))
            for action in process.action_list:
                action_elem = ET.SubElement(process_elem, 'action')
                action_elem.set('species', action.species)
                action_elem.set('coord_layer', action.coord.layer)
                action_elem.set('coord_name', action.coord.name)
                action_elem.set('coord_offset',
                    ' '.join([str(i) for i in action.coord.offset]))
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
            if(isinstance(selection, Species)
            or isinstance(selection, Process)
            or isinstance(selection, Parameter)
            or isinstance(selection, Layer)):
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
        if isinstance(elem, Layer):
            if self.meta.model_dimension in [1,3]:
                self.get_parent().toast('Only 2d supported')
                return
            form = LayerEditor(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Meta):
            meta_form = MetaForm(self.meta, self)
            self.get_parent().attach_slave('workarea', meta_form)
            meta_form.focus_toplevel()
            meta_form.focus_topmost()
        elif isinstance(elem, OutputList):
            form = OutputForm(self.output_list, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Parameter):
            form = ParameterForm(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Process):
            if self.meta.model_dimension in [1,3]:
                self.get_parent().toast('Only 2d supported')
                return
            form = ProcessForm(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, ProcessList):
            if self.meta.model_dimension in [1,3]:
                self.get_parent().toast('Only 2d supported')
                return
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
        elif isinstance(elem, LayerList):
            dimension = self.meta.model_dimension
            form = LatticeForm(elem, dimension, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        else:
            self.get_parent().toast('Not implemented, yet(%s).' % type(elem))


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

        # add layer
        default_layer_name = 'default'
        default_layer = Layer(name=default_layer_name,)
        self.project_tree.append(self.project_tree.layer_list_iter, default_layer)
        self.project_tree.lattice.default_layer = default_layer_name
        
        # add an empty species
        empty_species = 'empty'
        empty = Species(name=empty_species, color='#fff')
        # set empty as default species
        self.project_tree.species_list_iter.default_species = empty_species
        self.project_tree.append(self.project_tree.species_list_iter, empty)
        # add standard parameter
        param = Parameter(name='lattice_size', value='40 40 1')
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

    def on_btn_add_layer__clicked(self, button):
        """Add a new layer to the model
        """
        if self.project_tree.meta.model_dimension in [1,3]:
            self.toast('Only 2d supported')
            return
        new_layer = Layer()
        self.project_tree.append(self.project_tree.layer_list_iter, new_layer)
        layer_form = LayerEditor(new_layer, self.project_tree)
        self.project_tree.expand(self.project_tree.layer_list_iter)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', layer_form)
        layer_form.focus_topmost()

    def on_btn_add_species__clicked(self, button):
        """Add a new species to the model
        """
        new_species = Species(color='#fff', name='')
        self.project_tree.append(self.project_tree.species_list_iter, new_species)
        self.project_tree.expand(self.project_tree.species_list_iter)
        self.project_tree.select(new_species)
        species_form = SpeciesForm(new_species, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', species_form)
        species_form.focus_topmost()

    def on_btn_add_process__clicked(self, button):
        """Add a new process to the model
        """
        if self.project_tree.meta.model_dimension in [1,3]:
            self.toast('Only 2d supported')
            return
        if not self.project_tree.layer_list:
            self.toast("No layer defined, yet!")
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
        self.toast('Exporting source code ...')
        if not export_dir:
            export_dir = kiwi.ui.dialogs.selectfolder(title='Select folder for F90 source code.')
        if not export_dir:
            self.toast('No folder selected.')
            return
        if not os.path.exists(export_dir):
            os.mkdir(export_dir)

        # copy files
        for filename in [ 'assert.ppc', 'base.f90', 'compile_for_f2py', 'compile_for_fortran', 'kind_values_f2py.f90', 'run_kmc.f90', 'units.f90', 'view_kmc.py' ]:
            shutil.copy(APP_ABS_PATH + '/%s' % filename, export_dir)


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
            

        self.toast("Multi-lattice mode, not fully supported, yet!")
        writer = MLProcListWriter(self.project_tree, export_dir)
        writer.write_lattice()
        writer.write_proclist()
        writer.write_settings()


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





if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-o', '--open', dest='import_file', help='Immediately import store kmc file')
    parser.add_option('-x', '--export-dir', dest='export_dir', type=str)
    (options, args) = parser.parse_args()
    editor = KMC_Editor()
    if len(args) >= 1 :
        options.import_file = args[0]

    if options.import_file:
        editor.import_file(options.import_file)
        editor.toast('Imported %s' % options.import_file)
    else:
        editor.add_defaults()
        editor.saved_state = str(editor.project_tree)
    if hasattr(options, 'export_dir') and options.export_dir:
        print('Exporting right-away')
        editor.on_btn_export_src__clicked(button='', export_dir=options.export_dir)
        exit()
    editor.show_and_loop()
