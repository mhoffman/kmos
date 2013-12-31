#!/usr/bin/env python
"""A GUI frontend to create and edit kMC models.
"""
#    Copyright 2009-2013 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.
#
#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.

# standard modules
import optparse
import StringIO
import sys
import os

from kmos.types import Project, Layer, LayerList, Meta, OutputList, \
                       Parameter, Process, ProcessList, SpeciesList, \
                       OutputItem, Species
from kmos.gui.forms import LayerEditor, MetaForm, InlineMessage, OutputForm, \
                       ParameterForm, ProcessForm, BatchProcessForm, \
                       SpeciesForm, SpeciesListForm, LatticeForm
from kmos.config import GLADEFILE
import kmos.io

import gobject
import pygtk
pygtk.require('2.0')
import gtk

#Kiwi imports
import kiwi.ui
from kiwi.ui.delegates import SlaveDelegate, GladeDelegate
from kiwi.ui.objectlist import ObjectTree, Column
import kiwi.ui.dialogs


menu_layout = """\
<ui>
  <menubar name="MainMenuBar">
    <menu action="MenuFile">
      <menuitem action="FileNew"/>
      <menuitem action="FileOpenProject"/>
      <menuitem action="FileSave"/>
      <menuitem action="FileSaveAs"/>
      <menuitem action="FileExportSource"/>
      <separator/>
      <menuitem action="FileQuit"/>
    </menu>
    <menu action="MenuEdit">
      <menuitem action="EditUndo"/>
      <menuitem action="EditRedo"/>
    </menu>
    <menu action="MenuInsert">
      <menuitem action="InsertLayer"/>
      <menuitem action="InsertSpecies"/>
      <menuitem action="InsertParameter"/>
      <menuitem action="InsertProcess"/>
    </menu>
    <menu action="MenuHelp">
      <menuitem action="HelpAbout"/>
    </menu>
  </menubar>
</ui>
"""


def verbose(func):
    """Debugging helper that allows to track input and output of function
    via decoration"""
    print >> sys.stderr, "monitor %r" % (func.func_name)

    def wrapper_func(*args, **kwargs):
        """The wrapping function
        """
        print >> sys.stderr, "call(\033[0;31m%s.%s\033[0;30m): %r\n" % \
                (type(args[0]).__name__, func.func_name, args[1:]), \
                sys.stderr.flush()
        ret = func(*args, **kwargs)
        print >> sys.stderr, "    ret(%s): \033[0;32m%r\033[0;30m\n" % \
                 (func.func_name, ret)
        return ret
    return wrapper_func


class GTKProject(SlaveDelegate):
    """A facade of kmos.types.Project so that
    pygtk can display in a TreeView.
    """

    def __init__(self, parent, menubar):
        self.project_data = ObjectTree([Column('name',
                                               use_markup=True,
                                               data_type=str,
                                               sorted=True),
                                        Column('info')])

        self.project_data.connect('row-activated', self.on_row_activated)
        self.model_tree = Project()
        self._set_treeview_hooks()

        self.menubar = menubar

        self.set_parent(parent)

        self.filename = ''

        self.undo_stack = UndoStack(
            self.model_tree.__repr__,
            self.import_xml_file,
            self.project_data.select,
            menubar,
            self.meta,
            'Initialization')

        SlaveDelegate.__init__(self, toplevel=self.project_data)

    def _set_treeview_hooks(self):
        """Fudge function to import to access function to kmos.types.Project
        to kmos.gui.GTKProject.
        """
        self.project_data.clear()
        # Meta
        self.meta = self.project_data.append(None, self.model_tree.meta)
        self.model_tree.meta = self.meta

        # Layer List
        self.model_tree.add_layer = self.add_layer
        self.layer_list = self.project_data.append(None,
                                   self.model_tree.layer_list)
        self.get_layers = lambda: \
            sorted(self.project_data.get_descendants(self.layer_list),
                   key=lambda x: x.name)
        self.model_tree.get_layers = self.get_layers
        self.lattice = self.layer_list

        # Parameter List
        self.parameter_list = self.project_data.append(None,
                                       self.model_tree.parameter_list)
        self.add_parameter = lambda parameter: \
            self.project_data.append(self.parameter_list, parameter)
        self.model_tree.add_parameter = self.add_parameter
        self.get_parameters = lambda: \
            sorted(self.project_data.get_descendants(self.parameter_list),
                   key=lambda x: x.name)
        self.model_tree.get_parameters = self.get_parameters

        # Species List
        self.species_list = self.project_data.append(None,
                                   self.model_tree.species_list)
        self.add_species = lambda species: \
            self.project_data.append(self.species_list, species)
        self.model_tree.add_species = self.add_species
        self.get_speciess = lambda: \
            sorted(self.project_data.get_descendants(self.species_list),
                   key=lambda x: x.name)
        self.model_tree.get_speciess = self.get_speciess

        # Process List
        self.process_list = self.project_data.append(None,
                                     self.model_tree.process_list)
        self.add_process = lambda process:\
            self.project_data.append(self.process_list, process)
        self.model_tree.add_process = self.add_process
        self.get_processes = lambda: \
            sorted(self.project_data.get_descendants(self.process_list),
                   key=lambda x: x.name)
        self.model_tree.get_processes = self.get_processes

        # Output List
        self.output_list = self.project_data.append(None,
                                self.model_tree.output_list)
        self.add_output = lambda output:\
            self.project_data.append(self.output_list, output)
        self.model_tree.add_output = self.add_output
        self.get_outputs = lambda:  \
            sorted(self.project_data.get_descendants(self.output_list),
                   key=lambda x: x.name)
        self.model_tree.get_outputs = self.get_outputs

    def add_layer(self, layer):
        self.project_data.append(self.layer_list, layer)
        if len(self.get_layers()) == 1:
            self.set_default_layer(layer.name)
            self.set_substrate_layer(layer.name)

    def set_default_species(self, species):
        self.model_tree.species_list.default_species = species

    def set_substrate_layer(self, layer):
        self.model_tree.layer_list.substrate_layer = layer

    def set_default_layer(self, layer):
        self.model_tree.layer_list.default_layer = layer

    def update(self, model):
        """Update the object tree."""
        self.project_data.update(model)

    def on_row_activated(self, _tree, data):
        if isinstance(data, Layer):
            data.active = not data.active

    def get_name(self):
        """Return project name."""
        if self.filename:
            return os.path.basename(self.filename)
        else:
            return 'Untitled'

    def __repr__(self):
        return str(self.model_tree)

    def import_xml_file(self, filename):
        """Import XML project file into editor GUI,
        unfolding the object tree.

        """
        self.filename = filename
        self.model_tree.import_xml_file(filename)
        self.expand_all()

    def expand_all(self):
        """Expand all list of the project tree
        """
        self.project_data.expand(self.species_list)
        self.project_data.expand(self.layer_list)
        self.project_data.expand(self.parameter_list)
        self.project_data.expand(self.process_list)
        self.project_data.expand(self.output_list)

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
                if kiwi.ui.dialogs.yesno(
                    "Do you really want to delete '%s'?" \
                        % selection.name) == gtk.RESPONSE_YES:
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
            if self.meta.model_dimension in [1, 3]:
                self.get_parent().toast('Only 2d supported')
                return
            self.undo_stack.start_new_action('Edit Layer %s' % elem.name,
                                                               elem)
            form = LayerEditor(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Meta):
            self.undo_stack.start_new_action('Edit Meta', elem)
            meta_form = MetaForm(self.meta, self)
            self.get_parent().attach_slave('workarea', meta_form)
            meta_form.focus_toplevel()
            meta_form.focus_topmost()
        elif isinstance(elem, OutputList):
            self.undo_stack.start_new_action('Edit Output', elem)
            form = OutputForm(self.output_list, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Parameter):
            self.undo_stack.start_new_action('Edit Parameter %s' % elem.name,
                                                                   elem)
            form = ParameterForm(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Process):
            if self.meta.model_dimension in [1, 3]:
                self.get_parent().toast('Only 2d supported')
                return
            self.undo_stack.start_new_action('Edit Process %s' % elem.name,
                                                                 elem)
            form = ProcessForm(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, ProcessList):
            if self.meta.model_dimension in [1, 3]:
                self.get_parent().toast('Only 2d supported')
                return
            self.undo_stack.start_new_action('Batch process editing', elem)
            form = BatchProcessForm(self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, Species):
            self.undo_stack.start_new_action('Edit species', elem)
            form = SpeciesForm(elem, self.project_data)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, SpeciesList):
            self.undo_stack.start_new_action('Edit default species', elem)
            form = SpeciesListForm(elem, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        elif isinstance(elem, LayerList):
            self.undo_stack.start_new_action('Edit lattice', elem)
            dimension = self.meta.model_dimension
            form = LatticeForm(elem, dimension, self)
            self.get_parent().attach_slave('workarea', form)
            form.focus_topmost()
        else:
            self.get_parent().toast('Not implemented, yet(%s).' % type(elem))


class UndoStack():
    """Work in progress attempt to have a 'back' button
    for the editor.

    """

    def __init__(self, get_state_cb, set_state_from_file_cb,
                    select_elem_cb, menubar, elem, action=''):
        self.menubar = menubar
        self.get_state_cb = get_state_cb
        self.set_state_from_file_cb = set_state_from_file_cb
        self.select_elem_cb = select_elem_cb
        actions = gtk.ActionGroup('Actions')
        actions.add_actions([
        ('EditUndo', None, '_Undo', '<control>Z', 'Undo the last edit',
                                                            self.undo),
        ('EditRedo', None, '_Redo', '<control>Y', 'Redo and undo',
                                                           self.redo)])
        menubar.insert_action_group(actions, 0)
        self.menubar.ensure_update()
        self.stack = []
        self.head = -1
        self.current_action = action
        self.current_elem = elem
        self.get_state_cb = get_state_cb
        self.origin = self.get_state_cb()
        self.state = self.get_state_cb()
        self.menubar.get_widget(
                        '/MainMenuBar/MenuEdit/EditUndo').set_sensitive(False)
        self.menubar.get_widget(
                        '/MainMenuBar/MenuEdit/EditRedo').set_sensitive(False)

    def _set_state_cb(self, string):
        tmpfile = StringIO.StringIO()
        tmpfile.write(string)
        tmpfile.seek(0)
        self.set_state_from_file_cb(tmpfile)

    def start_new_action(self, action, elem):
        """Puts a new diff on the stack of actions."""
        #if self.get_state_cb() != self.state:
            #self.head += 1
            #self.stack = self.stack[:self.head] + [{
                #'action':self.current_action,
                #'state':self.get_state_cb(),
                #'elem':self.current_elem,
                #}]
            #self.state = self.get_state_cb()
        self.current_action = action
        self.current_elem = elem
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditUndo').set_label('Undo %s' % action)
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditUndo').set_sensitive(True)
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditRedo').set_label('Redo')
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditRedo').set_sensitive(False)

    def undo(self, _):
        """Undo one action."""
        if self.head < 0:
            return
        if self.state != self.get_state_cb():
            # if unstashed changes, first undo those
            self.start_new_action(self.current_action, self.get_state_cb())
            self.head += -1

        self.head += -1
        self.state = self.stack[self.head]['state']
        self._set_state_cb(self.state)

        self.current_action = self.stack[self.head + 1]['action']
        self.current_elem = self.stack[self.head + 1]['elem']

        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditUndo').set_label(
                'Undo %s' % self.stack[self.head]['action'])
        if self.head <= 0:
            self.menubar.get_widget(
                '/MainMenuBar/MenuEdit/EditUndo').set_sensitive(False)
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditRedo').set_label(
                'Redo %s' % (self.stack[self.head + 1]['action']))
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditRedo').set_sensitive(True)

    def redo(self, _):
        """Repeat an undone action."""
        if self.head >= len(self.stack) - 1:
            return UserWarning('TopReached')
        else:
            self.head += 1
            self.state = self.stack[self.head]['state']
            self._set_state_cb(self.state)
            self.current_action = self.stack[self.head]['action']
            self.current_elem = self.stack[self.head]['elem']
            #self.select_elem_cb(self.current_elem)

        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditUndo').set_label(
                self.stack[self.head]['action'])
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditUndo').set_sensitive(True)
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditRedo').set_label('Redo')
        self.menubar.get_widget(
            '/MainMenuBar/MenuEdit/EditRedo').set_sensitive(False)


class Editor(GladeDelegate):
    """The editor GUI frontend."""
    widgets = ['workarea', 'statbar', 'vbox1']
    gladefile = GLADEFILE
    toplevel_name = 'main_window'

    def __init__(self):
        GladeDelegate.__init__(self, delete_handler=self.on_btn_quit__clicked)

        # Prepare and fill the menu from XML layout
        self.menubar = gtk.UIManager()
        if gtk.pygtk_version < (2, 12):
            self.set_tip = gtk.Tooltips().set_tip
        actions = gtk.ActionGroup('Actions')
        actions.add_actions([
        ('MenuFile', None, '_File'),
        ('FileNew', None, '_New', '<control>N', 'Start new project',
            self.on_btn_new_project__clicked),
        ('FileOpenProject', None, '_Open', '<control>O', 'Open project',
            self.on_btn_open_model__clicked),
        ('FileSave', None, '_Save', '<control>S', 'Save model',
            self.on_btn_save_model__clicked),
        ('FileSaveAs', None, 'Save _As', '<control><shift>s', 'Save model As',
            self.on_btn_save_as__clicked),
        ('FileExportSource', None, '_Export Source',
            '<control>E', 'Export model to Fortran 90 source code',
            self.on_btn_export_src__clicked),
        ('FileQuit', None, '_Quit', '<control>Q', 'Quit the program',
            self.on_btn_quit__clicked),
        ('MenuEdit', None, '_Edit'),
        ('MenuInsert', None, '_Insert'),
        ('InsertParameter', None, 'Para_meter',
            '<control><shift>M', 'Add a new parameter',
            self.on_btn_add_parameter__clicked),
        ('InsertLayer', None, '_Layer',
            '<control><shift>L', 'Add a new layer',
            self.on_btn_add_layer__clicked),
        ('InsertProcess', None, '_Process', '<control><shift>P',
            'Add a new process', self.on_btn_add_process__clicked),
        ('InsertSpecies', None, '_Species', '<control><shift>E',
            'Add a new species', self.on_btn_add_species__clicked),
        ('MenuHelp', None, '_Help'),
        ('HelpAbout', None, '_About'),
        ])

        self.menubar.insert_action_group(actions, 0)
        try:
            mergeid = self.menubar.add_ui_from_string(menu_layout)
        except gobject.GError, error:
            print('Building menu failed: %s, %s' % (error, mergeid))

        # Initialize the project tree, passing in the menu bar
        self.project_tree = GTKProject(parent=self, menubar=self.menubar)
        self.main_window.add_accel_group(self.menubar.get_accel_group())
        self.attach_slave('overviewtree', self.project_tree)
        self.set_title('%s - kmos' % self.project_tree.get_name())
        self.project_tree.show()

        wid = self.project_tree.menubar.get_widget('/MainMenuBar')
        self.menu_box.pack_start(wid, False, False, 0)
        self.menu_box.show()
        #self.quickbuttons.hide()

        self.saved_state = str(self.project_tree)
        # Cast initial message
        self.toast('Welcome!')

    def add_defaults(self):
        """This function adds some useful defaults that are probably
        needed in every simulation.
        """
        # add dimension
        self.project_tree.meta.add({'model_dimension': '2'})

        # add layer
        default_layer_name = 'default'
        default_layer = Layer(name=default_layer_name,)
        self.project_tree.add_layer(default_layer)
        self.project_tree.lattice.default_layer = default_layer_name

        # add an empty species
        empty_species = 'empty'
        empty = Species(name=empty_species, color='#fff')
        # set empty as default species
        self.project_tree.species_list.default_species = empty_species
        self.project_tree.add_species(empty)
        # add standard parameter
        param = Parameter(name='lattice_size', value='40 40 1')
        self.project_tree.add_parameter(param)

        param = Parameter(name='print_every', value='1.e5')
        self.project_tree.add_parameter(param)

        param = Parameter(name='total_steps', value='1.e7')
        self.project_tree.add_parameter(param)

        # add output entries
        self.project_tree.add_output(OutputItem(name='kmc_time',
                                                output=True))
        self.project_tree.add_output(OutputItem(name='walltime',
                                                output=False))
        self.project_tree.add_output(OutputItem(name='kmc_step',
                                                output=False))

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

    def on_btn_new_project__clicked(self, _button):
        """Start a new project
        """
        if str(self.project_tree) != self.saved_state:
            # if there are unsaved changes, ask what to do first
            save_changes_dialog = gtk.Dialog(
                            buttons=(gtk.STOCK_DISCARD,
                                     gtk.RESPONSE_DELETE_EVENT,
                                     gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                                     title='Saved unsaved changes?')
            save_changes_dialog.vbox.pack_start(
                gtk.Label(
                    "\nThere are unsaved changes.\nWhat shall we do?\n\n"))
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
        self.project_tree = GTKProject(parent=self)
        if self.get_slave('overviewtree'):
            self.detach_slave('overviewtree')
        self.attach_slave('overviewtree', self.project_tree)
        self.project_tree.show()
        self.toast(
            'Start a new project by filling in meta information,\n' +
            'lattice, species, parameters, and processes or open\n' +
            'an existing one by opening a kMC XML file')

    def on_btn_add_layer__clicked(self, _button):
        """Add a new layer to the model
        """
        if len(self.project_tree.layer_list) == 1:
            kiwi.ui.dialogs.warning('Entering multi-lattice mode',
                long='This is an unpublished feature\n' +
                'Please ask me about publishing results obtained\n' +
                'from using this feature mjhoffmann@gmail.com')
        if self.project_tree.meta.model_dimension in [1, 3]:
            self.toast('Only 2d supported')
            return
        new_layer = Layer()
        self.project_tree.undo_stack.start_new_action('Add layer', new_layer)
        self.project_tree.add_layer(new_layer)
        layer_form = LayerEditor(new_layer, self.project_tree)
        self.project_tree.project_data.expand(self.project_tree.layer_list)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', layer_form)
        layer_form.focus_topmost()

    def on_btn_add_species__clicked(self, _button):
        """Add a new species to the model
        """
        new_species = Species(color='#fff', name='')
        self.project_tree.undo_stack.start_new_action('Add species',
                                                      new_species)
        self.project_tree.add_species(new_species)
        self.project_tree.project_data.expand(self.project_tree.species_list)
        self.project_tree.project_data.select(new_species)
        species_form = SpeciesForm(new_species, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', species_form)
        species_form.focus_topmost()

    def on_btn_add_process__clicked(self, _button):
        """Add a new process to the model
        """
        if self.project_tree.meta.model_dimension in [1, 3]:
            self.toast('Only 2d supported')
            return
        if not self.project_tree.get_layers():
            self.toast("No layer defined, yet!")
            return
        new_process = Process(name='', rate_constant='')
        self.project_tree.undo_stack.start_new_action('Add process',
                                                      new_process)
        self.project_tree.add_process(new_process)
        self.project_tree.project_data.expand(self.project_tree.process_list)
        self.project_tree.project_data.select(new_process)
        process_form = ProcessForm(new_process, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', process_form)
        process_form.focus_topmost()

    def on_btn_add_parameter__clicked(self, _button):
        new_parameter = Parameter(name='', value='')
        self.project_tree.undo_stack.start_new_action('Add parameter',
                                                      new_parameter)
        self.project_tree.add_parameter(new_parameter)
        self.project_tree.project_data.expand(
                                       self.project_tree.parameter_list)
        self.project_tree.project_data.select(new_parameter)
        parameter_form = ParameterForm(new_parameter, self.project_tree)
        if self.get_slave('workarea'):
            self.detach_slave('workarea')
        self.attach_slave('workarea', parameter_form)
        parameter_form.focus_topmost()

    def on_btn_open_model__clicked(self, _button):
        """Import project from XML
        """
        if str(self.project_tree) != self.saved_state:
            # if there are unsaved changes, ask what to do first
            save_changes_dialog = gtk.Dialog(
                        buttons=(gtk.STOCK_DISCARD,
                                 gtk.RESPONSE_DELETE_EVENT,
                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                 gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                                 title='Saved unsaved changes?')
            save_changes_dialog.vbox.pack_start(
                gtk.Label(
                    "\nThere are unsaved changes.\nWhat shall we do?\n\n"))
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
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OK, gtk.RESPONSE_OK))
        resp = filechooser.run()
        filename = filechooser.get_filename()
        filechooser.destroy()
        if resp == gtk.RESPONSE_OK and filename:
            # Initialize blank project tree
            self.project_tree = GTKProject(parent=self, menubar=self.menubar)
            if self.get_slave('overviewtree'):
                self.detach_slave('overviewtree')
            self.attach_slave('overviewtree', self.project_tree)
            self.set_title('%s - kmos' % self.project_tree.get_name())
            self.project_tree.show()
            self.import_xml_file(filename)

    def import_xml_file(self, filename):
        self.project_tree._set_treeview_hooks()
        # Import
        self.project_tree.import_xml_file(filename)
        self.set_title('%s - kmos' % self.project_tree.get_name())
        if hasattr(self.project_tree.meta, 'model_name'):
            self.toast('Imported model %s' %
                       self.project_tree.meta.model_name)
        else:
            self.toast('Imported model <Untitled>')
        self.saved_state = str(self.project_tree)

    def on_btn_save_model__clicked(self, _button, force_save=False):
        #Write Out XML File
        xml_string = str(self.project_tree)
        if xml_string == self.saved_state and not force_save:
            self.toast('Nothing to save')
        else:
            if not self.project_tree.filename:
                self.on_btn_save_as__clicked(None)
            outfile = open(self.project_tree.filename, 'w')
            outfile.write(xml_string)
            outfile.write('<!-- This is an automatically generated XML ' +
                          'file, representing a kMC model ' +
                          'please do not change this unless ' +
                          'you know what you are doing -->\n')
            outfile.close()
            self.saved_state = xml_string
            self.toast('Saved %s' % self.project_tree.filename)

    def on_btn_save_as__clicked(self, _button):
        filechooser = gtk.FileChooserDialog(title='Save Project As ...',
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            parent=None,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OK, gtk.RESPONSE_OK))
        filechooser.set_property('do-overwrite-confirmation', True)
        resp = filechooser.run()
        if resp == gtk.RESPONSE_OK:
            self.project_tree.filename = filechooser.get_filename()
            self.on_btn_save_model__clicked(None, force_save=True)
        filechooser.destroy()

    #@verbose
    def on_btn_export_src__clicked(self, _button, export_dir=''):
        self.toast('Exporting source code ...')
        if not export_dir:
            export_dir = kiwi.ui.dialogs.selectfolder(
                title='Select folder for F90 source code.')
        if not export_dir:
            self.toast('No folder selected.')
            return

        kmos.io.export_source(self.project_tree, export_dir)

        # return directory name
        self.toast('Wrote FORTRAN sources to %s\n' % export_dir +
            'Please go to the directory and run "kmos build".\n' +
           'If this finished successfully you can run the simulation\n' +
           'by executing "kmos view"')

    def on_btn_help__clicked(self, _button):
        """Preliminary help function."""
        help_url = 'http://mhoffman.github.com/kmos/doc/build/html/index.html'
        issues_url = 'https://github.com/mhoffman/kmos/issues'
        gtk.show_uri(None, help_url, gtk.gdk.CURRENT_TIME)
        self.toast(('Please refer to online help at\n%s.\n\n'
                    'Or post issues at\n%s.') %
                    (help_url, issues_url))

    def on_btn_quit__clicked(self, _button, *_args):
        """Checks if unsaved changes. If so offer file save dialog.
           Otherwise quit directly.

        """
        if self.saved_state != str(self.project_tree):
            save_changes_dialog = gtk.Dialog(
                      buttons=(gtk.STOCK_DISCARD, gtk.RESPONSE_DELETE_EVENT,
                      gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                      gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                      title='Saved unsaved changes?')
            save_changes_dialog.vbox.pack_start(
                gtk.Label(
                    "\nThere are unsaved changes.\nWhat shall we do?\n\n"))
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
        # the windows anyways
        return True


def main():
    """Main entry point to GUI Editor."""
    parser = optparse.OptionParser()
    parser.add_option('-o', '--open',
                      dest='xml_file',
                      help='Immediately import kmos XML file')
    parser.add_option('-x', '--export-dir',
                      dest='export_dir',
                      type=str)
    (options, args) = parser.parse_args()
    editor = kmos.gui.Editor()
    if len(args) >= 2:
        options.xml_file = args[1]

    if options.xml_file:
        editor.import_xml_file(options.xml_file)
        editor.toast('Imported %s' % options.xml_file)
    else:
        print('No XML file provided, starting a new model.')
        editor.add_defaults()
        editor.saved_state = str(editor.project_tree)
    if hasattr(options, 'export_dir') and options.export_dir:
        print('Exporting right-away')
        editor.on_btn_export_src__clicked(_button='',
                                          export_dir=options.export_dir)
        exit()
    editor.show_and_loop()
