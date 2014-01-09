#!/usr/bin/env python
"""kmos.gui.forms - GUI forms used by kmos.gui
The classes defined here heavily draw on the interface provided by
python-kiwi.
In the language of underlying MVC (Model-View-Controller) pattern these
classes form the controller. The view is defined through a *.glade XML file
and the models are instances of kmos.types.*
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
# Standard library imports
import re
import copy
#gtk import
import pygtk
pygtk.require('2.0')
import gtk
import goocanvas

#kiwi imports
from kiwi.ui.delegates import ProxySlaveDelegate, GladeDelegate, \
                              SlaveDelegate, ProxyDelegate

from kiwi.ui.views import SlaveView
from kiwi.datatypes import ValidationError
from kiwi.ui.objectlist import Column

# own modules
from kmos.config import GLADEFILE
from kmos.utils import CorrectlyNamed, \
                       get_ase_constructor, \
                       col_str2tuple, \
                       jmolcolor_in_hex

from kmos.types import ProcessFormSite, Process, OutputItem, Coord, \
                       ConditionAction, Site

from kmos import evaluate_rate_expression
from kmos.types import parse_chemical_expression

# ASE import
import numpy as np
from ase.atoms import Atoms
from ase.data import covalent_radii


class MetaForm(ProxySlaveDelegate, CorrectlyNamed):
    """
    Allows to enter meta information about the project.
    Please enter author and email so people can credit you for the model.

    Increasing the debug level makes the kmos backed create a lot of
    output but is typically not needed.
    """
    gladefile = GLADEFILE
    toplevel_name = 'meta_form'
    widgets = ['author', 'email', 'model_name', 'model_dimension', 'debug', ]

    def __init__(self, model, project_tree):
        ProxySlaveDelegate.__init__(self, model)
        #self.model_dimension.set_sensitive(False)
        self.project_tree = project_tree
        self.author.set_tooltip_text(
            'Give a name so people know who to credit for the model.')
        self.email.set_tooltip_text(
            'Enter an email address so people can get in touch with you.')
        self.model_name.set_tooltip_text(
            'Give a clear unique name, to identify the model.')
        self.model_dimension.set_tooltip_text(
            'The source code export function can generate ' +
            '1d, 2d, and 3d programs. However this GUI currently only ' +
            'supports 2d. 3d is still possible ' +
            'by manipulating the project XML file by hand. The algorithm ' +
            'though is fast but very memory consuming ' +
            'so a 3d simulation might require considerably more RAM.')
        self.debug.set_tooltip_text(
            'Increasing the debug level might give hints if one suspects ' +
            'errors in kmos itself. It does not help to debug your model. ' +
            'So usually one wants to keep it a 0.')
        self.author.grab_focus()

    def on_model_name__validate(self, widget, model_name):
        return self.on_name__validate(widget, model_name)

    def on_model_name__content_changed(self, _text):
        self.project_tree.update(self.model)

    def on_model_dimension__content_changed(self, _widget):
        self.project_tree.update(self.model)


class SpeciesListForm(ProxySlaveDelegate):
    """Allows to set the default species, `i. e.` the
    system will be globally initialized with this species if
    nothing else is set on a per site basis.
    """
    gladefile = GLADEFILE
    toplevel_name = 'species_list_form'
    widgets = ['default_species']

    def __init__(self, model, project_tree):
        # this _ugly_ implementation is due to an apparent catch 22 bug in
        # ProxyComboBox: if the value is set already __init__ expect
        # the value in the list but you cannot fill the list before
        # calling __init__
        default_species = model.default_species
        model.default_species = None
        ProxySlaveDelegate.__init__(self, model)
        self.default_species.prefill([x.name
                                      for x in project_tree.get_speciess()],
                                      sort=True)
        self.default_species.select(default_species)
        self.default_species.set_tooltip_text(
            'The lattice will be initialized with this species by default\n'
            + 'but also every unspecified condition or action wil be'
            + 'completed with this choice.\n'
            + 'So better only change this once at the begining if at all!')


class SpeciesForm(ProxySlaveDelegate, CorrectlyNamed):
    """Allows to define a new species. Required attribute is name. The
    chosen color will only shop up in the process editor. So choose something
    you will remember and recognize.
    The representation string is meant to be a ASE ase.atoms.Atoms constructor
    that will show up in the ASE visualization.
    """
    gladefile = GLADEFILE
    toplevel_name = 'species_form'
    widgets = ['name', 'color', 'representation']

    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        self.name.grab_focus()
        self.name.set_tooltip_text(
        'The name here is arbitrary but you will have to type it many times.'
        + 'So you might want to use e.g. CO instead carbon_monoxide')
        self.color.set_tooltip_text(
            'Choose a color a represent this species in the process editor')
        self.representation.set_tooltip_text(
        'Set an ASE Atoms(\n\'...\') like string to representation in the '
        + 'auto-generated movie. Please only use \'\' for quotation')

    def on_name__content_changed(self, _text):
        self.project_tree.update(self.model)


class ParameterForm(ProxySlaveDelegate, CorrectlyNamed):
    """Allows to set parameter. These
    parameters can be used in e.g. Transition State Theory
    formula to calculate rate constants.

    If 'adjustable' is activated then they maybe be changed via
    the `kmos view` front end while watching the model run.
    """
    gladefile = GLADEFILE
    toplevel_name = 'parameter_form'
    widgets = ['parameter_name',
               'value',
               'parameter_adjustable',
               'parameter_min',
               'parameter_max']

    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        value = self.parameter_adjustable.get_active()
        self.parameter_max.set_sensitive(value)
        self.parameter_min.set_sensitive(value)
        self.name.grab_focus()
        self.parameter_adjustable.set_tooltip_text(
        'Settings this adjustable will create a bar in the auto-generated ' +
        'movie. Dragging this bar will adapt the barrier and recalculate ' +
        'all rate constants. This only makes sense for physical ' +
        'parameters such a partial pressure but not for e.g. lattice size')
        self.parameter_name.set_tooltip_text(
        'Choose a sensible name that you remember later when typing rate ' +
        'constant formulae. This should not contain spaces')
        self.value.set_tooltip_text(
            'This defines the initial value for the parameter.')

    def on_parameter_adjustable__content_changed(self, _form):
        value = self.parameter_adjustable.get_active()
        self.parameter_max.set_sensitive(value)
        self.parameter_min.set_sensitive(value)

    def on_value__content_changed(self, _text):
        self.project_tree.update(self.model)

    def on_parameter_name__content_changed(self, _text):
        self.project_tree.update(self.model)
        self.project_tree.project_data.sort_by_attribute('name')


class LatticeForm(ProxySlaveDelegate):
    """Allows to set global lattice parameter such as the lattice vector,
    a ASE representation string, and the default layer. The program will
    be initialized using the default layer.
    """
    gladefile = GLADEFILE
    toplevel_name = 'lattice_form'
    widgets = ['default_layer',
               'lattice_representation']

    def __init__(self, model, dimension, project_tree):
        default_layer = model.default_layer
        model.default_layer = None
        ProxySlaveDelegate.__init__(self, model)
        self.default_layer.prefill([x.name
                                    for x in project_tree.get_layers()],
                                   sort=True)
        self.default_layer.select(default_layer)
        self.default_layer.set_tooltip_text(
        'By default the system will be initialized with this layer.'
        + 'This only matters if using using more than one layer'
        + '(multi-lattice kMC).')

    def on_add_structure__clicked(self, _):
        try:
            import ase.io
        except:
            print('Need ASE to do this.')
            return

        filechooser = gtk.FileChooserDialog(
            title='Open structure file',
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OK, gtk.RESPONSE_OK))
        resp = filechooser.run()
        filename = filechooser.get_filename()
        filechooser.destroy()
        if resp == gtk.RESPONSE_OK and filename:
            try:
                structure = ase.io.read(filename)
                if structure is list:
                    structure = structure[-1]
            except:
                print('Could not open this file. Please choose')
                print('a format that ASE can understand')
                return
            cur_text = self.lattice_representation.get_buffer().get_text(
                self.lattice_representation.get_buffer().get_start_iter(),
                self.lattice_representation.get_buffer().get_end_iter())
            if not cur_text:
                structures = []
            else:
                structures = eval(cur_text)
            structures.append(structure)
            self.lattice_representation.get_buffer().set_text(
                '[%s]' % (
                ', '.join(
                        [get_ase_constructor(x) for x in structures])))


class LayerEditor(ProxySlaveDelegate, CorrectlyNamed):
    """Widget to define a lattice through the sites
    in the unit cell (i.e. the `basis` in solid state language).
    """
    gladefile = GLADEFILE
    toplevel_name = 'layer_form'
    widgets = ['layer_name', 'layer_color']

    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        self.canvas = goocanvas.Canvas()
        self.root = self.canvas.get_root_item()
        self.canvas.set_size_request(400, 400)
        self.canvas.set_flags(gtk.HAS_FOCUS | gtk.CAN_FOCUS)
        self.canvas.connect('button-press-event', self.on_button_press)

        self.layer_nr = self.project_tree.get_layers().index(model)

        self.radius_scale = 20
        self.scale = 20
        self.offset = np.array([150, 300, 0])
        self.lattice_pad.add(self.canvas)
        self.previous_layer_name = self.layer_name.get_text()
        self.redraw()

        self.layer_name.set_tooltip_text(
            'A name is only relevant if you are using more than one\n'
            + 'layer in your model.')

    def _get_atoms(self):
        if self.project_tree.lattice.representation:
            representations = eval(self.project_tree.lattice.representation)
            if len(representations) > self.layer_nr:
                atoms = representations[self.layer_nr]
            else:
                atoms = representations[0]
        else:
            atoms = Atoms()
        return atoms

    def redraw(self):
        """Draw the current lattice with unit cell
           and sites defined on it.
        """

        # draw atoms in background
        atoms = self._get_atoms()

        self.lower_left = (self.offset[0],
                           self.offset[1]
                           + self.scale * atoms.cell[1, 1])
        self.upper_right = (self.offset[0]
                           + self.scale * atoms.cell[0, 0],
                           self.offset[1])
        big_atoms = atoms * (3, 3, 1)
        for atom in sorted(big_atoms, key=lambda x: x.position[2]):
            i = atom.number
            radius = self.radius_scale * covalent_radii[i]
            color = jmolcolor_in_hex(i)
            X = atom.position[0]
            Y = - atom.position[1]
            goocanvas.Ellipse(parent=self.root,
                              center_x=(self.offset[0] + self.scale * X),
                              center_y=(self.offset[1] + self.scale * Y),
                              radius_x=radius,
                              radius_y=radius,
                              stroke_color='black',
                              fill_color_rgba=color,
                              line_width=1.0)

        # draw unit cell
        A = tuple(self.offset[:2])
        B = (self.offset[0] + self.scale * (atoms.cell[0, 0]),
             self.offset[1] + self.scale * (atoms.cell[0, 1]))

        C = (self.offset[0] + self.scale * (atoms.cell[0, 0]
                                       + atoms.cell[1, 0]),
             self.offset[1] - self.scale * (atoms.cell[0, 1]
                                       + atoms.cell[1, 1]))

        D = (self.offset[0] + self.scale * (atoms.cell[1, 0]),
             self.offset[1] - self.scale * (atoms.cell[1, 1]))
        goocanvas.Polyline(parent=self.root,
                           close_path=True,
                           points=goocanvas.Points([A, B, C, D]),
                           stroke_color='black',)

        # draw sites
        for x in range(3):
            for y in range(3):
                for site in self.model.sites:

                    # convert to screen coordinates
                    pos = np.dot(site.pos + np.array([x, y, 0]), atoms.cell)
                    pos *= np.array([1, -1, 1])
                    pos *= self.scale
                    pos += self.offset
                    X = pos[0]
                    Y = pos[1]

                    o = goocanvas.Ellipse(parent=self.root,
                                          center_x=X,
                                          center_y=Y,
                                          radius_x=.3 * self.radius_scale,
                                          radius_y=.3 * self.radius_scale,
                                          stroke_color='black',
                                          fill_color='white',
                                          line_width=1.0,)

                    o.site = site
                    o.connect('query-tooltip', self.query_tooltip)
                self.canvas.hide()
                self.canvas.show()

    def query_tooltip(self, _canvas, widget, tooltip):
        tooltip.set_text(widget.site.name)
        return True

    def on_button_press(self, _item, event):
        atoms = self._get_atoms()
        pos = (np.array([event.x, event.y, 0]) - self.offset)

        # convert from screen coordinates
        pos *= [1, -1, 1]
        pos /= self.scale
        pos = np.linalg.solve(atoms.cell.T, pos)

        for site in self.model.sites:
            d = np.sqrt((pos[0] - site.pos[0]) ** 2 +
                        (pos[1] - site.pos[1]) ** 2)
            if d < 0.10:
                SiteForm(site, self, self.project_tree, self.model)
                break
        else:
            new_site = Site()
            new_site.name = ''
            new_site.pos = pos

            # Put z position slightly above
            # top atom as a first guess.
            # Assumes a binding distance of 1.3 Angstrom
            atoms = self._get_atoms()
            z_pos = atoms.get_positions()[:, 2]
            z_pos = z_pos if len(z_pos) else [0]
            Z = max(z_pos) + 1.3
            z = Z / atoms.cell[2, 2]
            new_site.pos[2] = z

            new_site.layer = self.model.name
            self.model.sites.append(new_site)
            SiteForm(new_site, self, self.project_tree, self.model)

    def on_layer_name__validate(self, widget, layer_name):
        # TODO: validate lattice name to be unique
        return self.on_name__validate(widget, layer_name)

    def on_layer_name__content_changed(self, widget):
        # Sync layer names in process coords
        new_layer_name = widget.get_text()
        for process in self.project_tree.get_processes():
            for elem in process.condition_list:
                if elem.coord.layer == self.previous_layer_name:
                    elem.coord.layer = new_layer_name
            for elem in process.action_list:
                if elem.coord.layer == self.previous_layer_name:
                    elem.coord.layer = new_layer_name
        self.previous_layer_name = new_layer_name

        self.project_tree.update(self.model)


class SiteForm(ProxyDelegate, CorrectlyNamed):
    """Allows to create or modify a site when setting up a unit cell.
    """
    gladefile = GLADEFILE
    toplevel_name = 'site_form'
    widgets = ['site_name',
               'default_species',
               'site_tags']

    def __init__(self, site, parent, project_tree, layer):
        self.saved_state = copy.deepcopy(site)
        self.project_tree = project_tree
        default_species = site.default_species
        site.default_species = None
        ProxyDelegate.__init__(self, site)

        # fill species dialog with correct available choices
        self.site_default_species.prefill([x.name
                                            for x in
                                            project_tree.get_speciess()],
                                            sort=True)
        if default_species == 'default_species':
            self.site_default_species.select(
                        self.project_tree.species_list.default_species)
        else:
            self.site_default_species.select(default_species)
        self.model.default_species = self.site_default_species.get_selected()

        self.site_ok.grab_default()
        self.site = site

        # set site coordinates
        self.sitevect_x.set_text(str(site.pos[0]))
        self.sitevect_y.set_text(str(site.pos[1]))
        self.sitevect_z.set_text(str(site.pos[2]))

        self.parent = parent
        self.project_tree = project_tree
        self.layer = layer
        self.show_all()
        self.site_name.set_tooltip_text(
            'The site name has to be uniquely identify a site (at least '
            'within each layer for multi-lattice mode). You may have to '
            'type this name a lot, so keep '
            'it short but unambiguous. '
            'To delete a site, erase name.')

    def on_sitevect_x__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_sitevect_y__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_sitevect_z__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_site_name__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_site_name__validate(self, _widget, site_name):
        """check if other site already has the name"""
        if [x for x in self.layer.sites if x.name == site_name]:
            self.site_ok.set_sensitive(False)
            return ValidationError('Site name needs to be unique')
        else:
            self.site_ok.set_sensitive(True)

    def on_site_cancel__clicked(self, _):
        """If we click cancel revert to previous state
        or don't add site, if new."""
        if self.saved_state.name:
            # if site existed, reset to previous state
            self.layer.sites.remove(self.site)
            self.layer.sites.append(self.saved_state)
        else:
            # if site did not exist previously, remove completely
            self.layer.sites.remove(self.site)
        self.hide()
        self.parent.redraw()

    def on_site_ok__clicked(self, _button):
        self.model.default_species = self.site_default_species.get_selected()
        if not len(self.site_name.get_text()):
            self.layer.sites.remove(self.model)
        self.hide()
        self.parent.redraw()


class ProcessForm(ProxySlaveDelegate, CorrectlyNamed):
    """Allows to create and manipulate a process by dragging
    species onto respective sites. The the lower species
    represents a condition the upper one an action.

    Rate constants can be entered directly using all defined parameters.
    The tooltip shows the current value if all is entered correctly.
    """
    gladefile = GLADEFILE
    toplevel_name = 'process_form'
    widgets = ['process_name',
               'rate_constant',
               'process_enabled',
               'chemical_expression']
    z = 5  # z as in zoom
    l = 500  # l as in length
    r_cond = 15.
    r_act = 10.
    r_reservoir = 5.
    r_site = 5.  # where the center unit cell is in the drawing
    X = 2
    Y = 2

    def __init__(self, process, project_tree):
        self.process = process
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, process)
        expression = self.generate_expression()
        self.chemical_expression.update(expression, )

        self.radius_scale = 20
        self.scale = 20
        self.offset = np.array([150, 300, 0])
        self.draw_from_data()

        self.process_name.set_tooltip_text(
        'This name has to uniquely identify the process e.g. co_diff_right')
        self.chemical_expression.set_tooltip_text(
        'This is a fast way to define a process e.g. CO@cus->CO@bridge ' +
        'to declare a CO diffusion from site br to site cus or ' +
        'CO@cus->CO@cus.(0,1) for a CO diffusion in the up direction. Hit ' +
        'ENTER to update the graphical representation.')

        self.rate_constant.curr_value = 0.0
        expr = self.rate_constant.get_text()
        if not expr:
            # if nothing entered show explanation
            self.rate_constant.set_tooltip_text((
                'Python has to be able to evaluate this expression to a ' +
                'plain real number. One can use standard mathematical ' +
                'functions, parameters that are defined under "Parameters"' +
                'or constants and conversion factor such as c, h, e, ' +
                'kboltzmann, pi, bar, angstrom'))
        else:
            try:
                self.rate_constant.set_tooltip_text(
                    'Current value: %.5e s^{-1}' %
                    evaluate_rate_expression(expr,
                        self.project_tree.get_parameters()))
            except Exception, e:
                self.rate_constant.set_tooltip_text(str(e))
        rate_constant_terms = ['bar',
                               'beta',
                               'eV',
                               'exp',
                               'h',
                               'kboltzmann',
                               'umass']
        for param in self.project_tree.get_parameters():
            rate_constant_terms.append(param.name)
        self.rate_constant.prefill(rate_constant_terms)

        chem_exp_terms = ['->', ]
        for species in self.project_tree.get_speciess():
            chem_exp_terms.append(species.name)
        self.chemical_expression.prefill(chem_exp_terms)

    def generate_expression(self):
        expr = ''
        if not self.process.condition_list + self.process.action_list:
            return expr
        for i, condition in enumerate(self.process.condition_list):
            if i > 0:
                expr += ' + '
            expr += '%s@%s' % (condition.species, condition.coord.name)
        expr += ' -> '
        for i, action in enumerate(self.process.action_list):
            if i > 0:
                expr += ' + '
            expr += '%s@%s' % (action.species, action.coord.name)
        return expr

    def on_rate_constant__validate(self, _widget, expr):
        try:
            self.rate_constant.set_tooltip_text('Current value: %.2e s^{-1}' %
                evaluate_rate_expression(expr,
                    self.project_tree.get_parameters()))
        except Exception, e:
            return ValidationError(e)

    def on_chemical_expression__activate(self, entry):
        text = entry.get_text()
        if not text:
            self.process.condition_list = []
            self.process.action_list = []
            self.traw_from_data()
            return
        # Delete trailing plusses
        text = re.sub(r'\s*\+\s', '', text)
        # default to empty right-hand side if not existent
        while text and text[-1] in '-.':
            text = text[:-1]
        if not '->' in text:
            text += '->'
        try:
            parse_chemical_expression(eq=text,
                                      process=self.process,
                                      project_tree=self.project_tree)
            self.process.condition_list = []
            self.process.action_list = []
            parse_chemical_expression(eq=text,
                                      process=self.process,
                                      project_tree=self.project_tree)
        except Exception, e:
            # first remove last term and try again
            try:
                print("Error ...")
                text = re.sub(r'+[^+]*$', '', text)
                parse_chemical_expression(eq=text,
                                          process=self.process,
                                          project_tree=self.project_tree)
                self.process.condition_list = []
                self.process.action_list = []
                parse_chemical_expression(eq=text,
                                          process=self.process,
                                          project_tree=self.project_tree)

            except Exception, e:
                print("Fatal Error ... %s" % e)
                self.process.condition_list = []
                self.process.action_list = []
        finally:
            self.draw_from_data()

    def query_tooltip(self, item, x, y, keyboard_mode, tooltip, *args, **kwargs):
        tooltip.set_text(item.tooltip_text)
        return True

    def on_lattice(self, x, y):
        """Returns True if (x, y) is in lattice box
        """
        return 10 < x < 510 and 80 < y < 580

    def button_press(self, _, item, dummy):
        coords = item.get_coords()
        if item.state == 'reservoir':
            o = CanvasOval(self.motion_layer,
                           *coords, filled=True, bg=item.bg)
            o.connect('button-press-event', self.button_press)
            o.connect('motion-notify-event', self.drag_motion)
            o.connect('button-release-event', self.button_release)
            o.state = 'from_reservoir'
            o.species = item.species
            self.item = o
            self.item.clicked = True
            self.item.father = item
            self.prev_pos = self.item.get_center()
            self.canvas.redraw()

    def drag_motion(self, _widget, _item, event):
        if self.item.clicked:
            d = event.x - self.prev_pos[0], event.y - self.prev_pos[1]
            self.item.move(*d)
            self.prev_pos = event.x, event.y

    #@verbose
    def button_release(self, _, dummy, event):
        self.item.clicked = False
        if self.item.state == 'from_reservoir':
            if not self.on_lattice(event.x, event.y):
                self.item.delete()
            else:
                close_sites = self.site_layer.find_closest(
                                               event.x,
                                               event.y,
                                               halo=(.2 * self.l) / self.z)
                if close_sites:
                    closest_site = min(close_sites,
                                       key=lambda i:
                                        (i.get_center()[0] - event.x) ** 2
                                        + (i.get_center()[1] - event.y) ** 2)
                    coord = closest_site.get_center()
                    self.item.set_center(*coord)
                    if not self.process.condition_list \
                           + self.process.action_list:
                    # if no condition or action is defined yet,
                    # we need to set the center of the editor
                        self.X = closest_site.i
                        self.Y = closest_site.j
                    species = self.item.species
                    offset = closest_site.i - self.X, closest_site.j - self.Y
                    name = closest_site.name
                    layer = closest_site.layer
                    kmc_coord = Coord(offset=offset,
                                  name=name,
                                  layer=layer)
                    condition_action = ConditionAction(species=species,
                                                       coord=kmc_coord)

                    if [x for x in self.condition_layer
                        if x.get_center() == coord]:
                        self.item.new_parent(self.action_layer)
                        self.item.set_radius(self.r_act)
                        self.process.action_list.append(condition_action)
                    else:
                        self.item.new_parent(self.condition_layer)
                        self.item.set_radius(self.r_cond)
                        self.process.condition_list.append(condition_action)
                else:
                    self.item.delete()

        self.chemical_expression.update(self.generate_expression(), )
        self.canvas.redraw()

    def draw_from_data_old(self):
        """Places circles on the current lattice according
        to the conditions and actions defined
        """

        def get_species_color(species):
            return [x for x in self.project_tree.get_speciess()
                    if x.name == species][0].color

        white = col_str2tuple('#ffffff')
        black = col_str2tuple('#000000')
        if hasattr(self, 'canvas'):
            self.process_pad.remove(self.canvas)
        self.canvas = Canvas(bg=white, fg=white)
        self.canvas.set_flags(gtk.HAS_FOCUS | gtk.CAN_FOCUS)
        self.canvas.grab_focus()
        self.canvas.show()
        self.process_pad.add(self.canvas)
        self.lattice_layer = CanvasLayer()
        self.canvas.append(self.lattice_layer)
        self.site_layer = CanvasLayer()
        self.canvas.append(self.site_layer)
        self.condition_layer = CanvasLayer()
        self.canvas.append(self.condition_layer)
        self.action_layer = CanvasLayer()
        self.canvas.append(self.action_layer)
        self.frame_layer = CanvasLayer()
        self.canvas.append(self.frame_layer)
        self.motion_layer = CanvasLayer()
        self.canvas.append(self.motion_layer)

        # draw lattice
        for i in range(self.z):
            CanvasLine(self.lattice_layer,
                       0, i * (self.l / self.z),
                       500, i * (self.l / self.z),
                       line_width=1, fg=(.6, .6, .6))
        for i in range(self.z):
            CanvasLine(self.lattice_layer,
                       i * (self.l / self.z), 0,
                       i * (self.l / self.z), 500,
                       line_width=1, fg=(.6, .6, .6))
        active_layers = [x for x in self.project_tree.get_layers()
                         if x.active]
        site_list = []
        for active_layer in active_layers:
            for site in active_layer.sites:
                form_site = ProcessFormSite(name=site.name,
                                            pos=site.pos,
                                            layer=active_layer.name,
                                            color=active_layer.color)
                site_list.append(form_site)
        for i in range(self.z + 1):
            for j in range(self.z + 1):
                for site in site_list:
                    color = col_str2tuple(site.color)
                    if i == self.X and j == self.Y:
                        l_site = CanvasOval(self.site_layer, 0, 0, 10, 10,
                                                                    fg=color)
                    else:
                        l_site = CanvasOval(self.site_layer, 0, 0, 10, 10,
                                                                    fg=color)

                    l_site.set_center(self.l /
                                      self.z * (i + float(site.pos[0])),
                                      500 - self.l /
                                      self.z * (j + float(site.pos[1])))
                    l_site.connect('query-tooltip', self.query_tooltip)
                    # 500 - ... for having scientific coordinates
                    # and not screen coordinates
                    l_site.set_radius(5)
                    l_site.i = i
                    l_site.j = j
                    if len(active_layers) > 1:
                        l_site.tooltip_text = '%s.(%s,%s).%s' % (site.name,
                                                                 i - self.X,
                                                                 j - self.Y,
                                                                 site.layer)
                    else:
                        l_site.tooltip_text = '%s.(%s,%s)' % (site.name,
                                                              i - self.X,
                                                              j - self.Y)
                    l_site.name = site.name
                    l_site.offset = (i - self.X, j - self.Y)
                    l_site.layer = site.layer

        # draw frame
        frame_col = (.21, .35, .42)
        CanvasRect(self.frame_layer, 0, 0, 520, 80, fg=frame_col,
                                                    bg=frame_col,
                                                    filled=True)
        CanvasRect(self.frame_layer, 0, 0, 10, 580, fg=frame_col,
                                                    bg=frame_col,
                                                    filled=True)
        CanvasRect(self.frame_layer, 510, 0, 520, 580, fg=frame_col,
                                                       bg=frame_col,
                                                       filled=True)
        CanvasRect(self.frame_layer, 0, 580, 520, 590, fg=frame_col,
                                                       bg=frame_col,
                                                       filled=True)
        CanvasText(self.frame_layer, 10, 10, size=8, text='Reservoir Area')
        CanvasText(self.frame_layer, 10, 570, size=8, text='Lattice Area')

        # draw reservoir circles
        for k, species in enumerate(self.project_tree.get_speciess()):
            color = col_str2tuple(species.color)
            o = CanvasOval(self.frame_layer,
                           30 + k * 50,
                           30, 50 + k * 50,
                           50,
                           filled=True,
                           bg=color)
            o.species = species.name
            o.tooltip_text = species.name  # for tooltip
            o.connect('button-press-event', self.button_press)
            #o.connect('motion-notify-event', self.drag_motion)
            o.connect('button-release-event', self.button_release)
            o.connect('query-tooltip', self.query_tooltip)
            o.state = 'reservoir'

        self.lattice_layer.move_all(10, 80)
        self.site_layer.move_all(10, 80)

        # attributes need for moving objects
        self.item = None
        self.prev_pos = None
        black = col_str2tuple('#003333')
        for elem in self.process.condition_list:
            matching_sites = [x for x in self.site_layer
                              if isinstance(x, CanvasOval)
                              and x.i == self.X + elem.coord.offset[0]
                              and x.j == self.Y + elem.coord.offset[1]
                              and x.name == elem.coord.name
                              and x.layer == elem.coord.layer]
            if matching_sites:
                coords = matching_sites[0].get_coords()
                color = get_species_color(elem.species)
                color = col_str2tuple(color)
                o = CanvasOval(self.condition_layer,
                               bg=color,
                               fg=black,
                               filled=True, outline=True)
                o.coords = coords
                o.connect('button-press-event',
                          self.on_condition_action_clicked)
                o.set_radius(self.r_cond)
                o.type = 'condition'
                o.condition = elem
                o.tooltip_text = '%s@%s' % (elem.species, elem.coord)  # for tooltip
                o.connect('query-tooltip', self.query_tooltip)

        for elem in self.process.action_list:
            matching_sites = [x for x in self.site_layer
                              if isinstance(x, CanvasOval)
                              and x.i == self.X + elem.coord.offset[0]
                              and x.j == self.Y + elem.coord.offset[1]
                              and x.name == elem.coord.name
                              and x.layer == elem.coord.layer]
            if matching_sites:
                coords = matching_sites[0].get_coords()
                if elem.species[0] == '^':
                    color = get_species_color(elem.species[1:])
                    layer = self.action_layer
                    radius = self.r_act
                    line_width = 2.0
                elif elem.species[0] == '$':
                    color = get_species_color(elem.species[1:])
                    layer = self.condition_layer
                    radius = self.r_cond
                    line_width = 2.0
                else:
                    color = get_species_color(elem.species)
                    layer = self.action_layer
                    radius = self.r_act
                    line_width = 1.0
                color = col_str2tuple(color)
                o = CanvasOval(layer,
                               bg=color,
                               fg=black,
                               line_width=line_width,
                               filled=True,
                               outline=True)
                o.coords = coords
                o.connect('button-press-event',
                          self.on_condition_action_clicked)
                o.set_radius(radius)
                o.type = 'action'
                o.action = elem
                o.tooltip_text = '%s@%s' % (elem.species, elem.coord)  # for tooltip
                o.connect('query-tooltip', self.query_tooltip)

    def draw_from_data(self):
        atoms = self._get_atoms()
        def toscrn(coord,
                   screen_size=(500, 500),
                   scale=None,
                   offset=None):

            if scale is None:
                scale = min(screen_size[0]/(atoms.cell[0] + atoms.cell[1])[0],
                            screen_size[1]/(atoms.cell[0] + atoms.cell[1])[1])
                scale /= (zoom + 1)

            if offset is None:
                offset = ((screen_size[0] - zoom*scale*(atoms.cell[0] + atoms.cell[1])[0])/2,
                          (screen_size[1] - zoom*scale*(atoms.cell[0] + atoms.cell[1])[1])/2,)
            return (scale * coord[0] + offset[0],
                    screen_size[1] - (scale * coord[1] + offset[1]))

        zoom = 3

        center_x = zoom / 2
        center_y = zoom / 2
        if hasattr(self, 'canvas'):
            self.process_pad.remove(self.canvas)
        canvas = goocanvas.Canvas()
        self.canvas = canvas
        root = canvas.get_root_item()
        canvas.set_flags(gtk.HAS_FOCUS | gtk.CAN_FOCUS)
        canvas.set_property('has-tooltip', True)
        #canvas.grab_focus()
        canvas.show()
        self.process_pad.add(canvas)

        radius = 10

        # draw lattice
        for i in range(zoom + 1):
            for _0, _1, _2, _3 in [[i, i, 0, zoom],
                                   [0, zoom, i, i]]:
                points = goocanvas.Points([
                    toscrn(atoms.cell[0]*_0 + atoms.cell[1]*_2),
                    toscrn(atoms.cell[0]*_1 + atoms.cell[1]*_3),
                ])
                goocanvas.Polyline(parent=root,
                                  points=points,
                                  stroke_color='black',
                                  fill_color='white',
                                  line_width=1.0)
        # emphasize central cell
        points = goocanvas.Points([
            toscrn(atoms.cell[0]*center_x + atoms.cell[1]*center_x),
            toscrn(atoms.cell[0]*center_x + atoms.cell[1]*(center_x + 1)),
            toscrn(atoms.cell[0]*(center_x + 1) + atoms.cell[1]*(center_x + 1)),
            toscrn(atoms.cell[0]*(center_x + 1) + atoms.cell[1]*center_x),
            toscrn(atoms.cell[0]*center_x + atoms.cell[1]*center_x),
        ])
        goocanvas.Polyline(parent=root,
                          points=points,
                          stroke_color='black',
                          fill_color='white',
                          line_width=2.0)
        # draw sites
        for x in range(zoom):
            for y in range(zoom):
                sites = self.project_tree.get_layers()[0].sites
                for site in sites:
                    X, Y = toscrn(x*atoms.cell[0]
                                  + y*atoms.cell[1]
                                  + np.inner(atoms.cell.T, site.pos))
                    tooltip = '%s.(%s, %s, 0).%s' % (site.name,
                                                     x-1, y-1,
                                                     self.project_tree.get_layers()[0].name
                                                     )

                    o = goocanvas.Ellipse(parent=root,
                                          center_x=X,
                                          center_y=Y,
                                          radius_x=.4 * radius,
                                          radius_y=.4 * radius,
                                          stroke_color='black',
                                          fill_color='white',
                                          line_width=1.0,
                                          tooltip=tooltip,
                                          )

        # draw reservoir circles
        for k, species in enumerate(self.project_tree.get_speciess()):
            color = col_str2tuple(species.color)
            o = goocanvas.Ellipse(parent=root,
                           center_x=30 + k * 50,
                           center_y=30,
                           radius_x=0.8*radius,
                           radius_y=0.8*radius,
                           stroke_color='black',
                           fill_color_rgba=eval('0x' + species.color[1:] + 'ff' ),
                           tooltip=species.name,
                           )

        for elem in self.process.condition_list:
            pos = [x.pos
                   for layer in self.project_tree.get_layers()
                   for x in layer.sites
                   if x.name == elem.coord.name
                      ][0]
            species_color = [x.color for x in self.project_tree.get_speciess()
                             if x.name == elem.species.split(' or ')[0]][0]
            center = toscrn(np.inner(pos + elem.coord.offset + center_x, atoms.cell.T))

            tooltip = 'Condition: %s@%s.%s.%s' % (elem.species,
                                       elem.coord.name,
                                       tuple(elem.coord.offset),
                                       elem.coord.layer)  # for tooltip
            o = goocanvas.Ellipse(parent=root,
                                  center_x=center[0],
                                  center_y=center[1],
                                  radius_x=0.8*radius,
                                  radius_y=0.8*radius,
                                  stroke_color='black',
                                  fill_color_rgba=eval('0x' + species_color[1:] + 'ff' ),
                                  tooltip=tooltip,
                                  )


        for elem in self.process.action_list:
            species_color = [x.color for x in self.project_tree.get_speciess()
                             if x.name == elem.species][0]
            pos = [x.pos
                   for layer in self.project_tree.get_layers()
                   for x in layer.sites
                   if x.name == elem.coord.name
                      ][0]

            center = toscrn(np.inner(pos + elem.coord.offset + center_x, atoms.cell.T))
            tooltip = 'Action: %s@%s.%s.%s' % (elem.species,
                                       elem.coord.name,
                                       tuple(elem.coord.offset),
                                       elem.coord.layer)  # for tooltip
            o = goocanvas.Ellipse(parent=root,
                                  center_x=center[0],
                                  center_y=center[1],
                                  radius_x=0.4*radius,
                                  radius_y=0.4*radius,
                                  stroke_color='black',
                                  fill_color_rgba=eval('0x' + species_color[1:] + 'ff' ),
                                  tooltip=tooltip,
                                  )




    def _get_atoms(self, layer_nr=0):
        if self.project_tree.lattice.representation:
            representations = eval(self.project_tree.lattice.representation)
            if len(representations) > layer_nr:
                atoms = representations[layer_nr]
            else:
                atoms = representations[0]
        else:
            atoms = Atoms()
        return atoms

    def on_condition_action_clicked(self, _canvas, widget, event):
        if event.button == 2:
            if widget.type == 'action':
                self.process.action_list.remove(widget.action)
            elif widget.type == 'condition':
                self.process.condition_list.remove(widget.condition)
            widget.delete()

    def on_process_name__content_changed(self, _text):
        self.project_tree.project_data.sort_by_attribute('name')
        self.project_tree.update(self.process)

    def on_rate_constant__content_changed(self, _text):
        self.project_tree.update(self.process)


class BatchProcessForm(SlaveDelegate):
    """Allows to enter many processes at once. The format is one
    process per line in the form::

        [process name] ; [chemical expression] ; [rate constant]

    One can omit the fields but not the semicolon.
    """
    gladefile = GLADEFILE
    toplevel_name = 'batch_process_form'

    def __init__(self, project_tree):
        self.project_tree = project_tree
        SlaveDelegate.__init__(self)

    def on_btn_evaluate__clicked(self, _):
        batch_buffer = self.batch_processes.get_buffer()
        bounds = batch_buffer.get_bounds()
        text = batch_buffer.get_text(*bounds)
        text = text.split('\n')
        for i, line in enumerate(text):
            # Ignore empty lines
            if not line.count(';'):
                continue
            if not line.count(';'):
                raise UserWarning(
                    ("Line %s: the number of fields you entered is %s, " \
                     "but I expected 3") % (i, line.count(';') + 1))
            line = line.split(';')
            name = line[0]
            if len(line) == 1:
                rate_constant = ''
            elif len(line) == 2:
                rate_constant = ''
            elif len(line) == 3:
                rate_constant = line[2]
            else:
                raise UserWarning(
                    "There are too many ';' in your expression %s" % line)
            process = Process(name=name, rate_constant=rate_constant)
            try:
                parse_chemical_expression(eq=line[1],
                                          process=process,
                                          project_tree=self.project_tree)
                self.draw_from_data()
            except:
                raise Exception(
                    ("Found an error in your chemical expression(line %s):\n"\
                    "%s") % (i + 1, line[1]))
            else:
                # replace any existing process with identical names
                for dublette_proc in [x for x in
                                      self.project_tree.process_list
                                      if x.name == name]:
                    self.project_tree.process_list.remove(dublette_proc)
                self.project_tree.append(self.project_tree.process_list_iter,
                                                                     process)
        batch_buffer.delete(*bounds)


class OutputForm(GladeDelegate):
    """Not implemented yet
    """
    gladefile = GLADEFILE
    toplevel_name = 'output_form'
    widgets = ['output_list']

    def __init__(self, output_list, project_tree):
        GladeDelegate.__init__(self)
        self.project_tree = project_tree
        self.output_list_data = output_list
        self.output_list.set_columns([Column('name',
                                          data_type=str,
                                          editable=True, sorted=True),
                                      Column('output',
                                          data_type=bool,
                                          editable=True)])

        for item in self.output_list_data:
            self.output_list.append(item)

        self.output_list.show()
        self.output_list.grab_focus()

    def on_add_output__clicked(self, _):
        output_form = gtk.MessageDialog(parent=None,
                                      flags=gtk.DIALOG_MODAL,
                                      type=gtk.MESSAGE_QUESTION,
                                      buttons=gtk.BUTTONS_OK_CANCEL,
                                      message_format='Please enter a new ' \
                                         + 'output: examples are a species ' \
                                         + 'or species@site')
        output_form.set_flags(gtk.CAN_DEFAULT | gtk.CAN_FOCUS)
        output_form.set_default_response(gtk.RESPONSE_OK)
        output_form.set_default(
                        output_form.get_widget_for_response(gtk.RESPONSE_OK))
        form_entry = gtk.Entry()

        def activate_default(_):
            output_form.activate_default()
        form_entry.connect('activate', activate_default)
        output_form.vbox.pack_start(form_entry)
        output_form.vbox.show_all()
        res = output_form.run()
        output_str = form_entry.get_text()
        output_form.destroy()
        if res == gtk.RESPONSE_OK:
            output_item = OutputItem(name=output_str, output=True)
            self.output_list.append(output_item)
            self.output_list_data.append(output_item)


class InlineMessage(SlaveView):
    """Return a nice little field with a text message on it
    """
    gladefile = GLADEFILE
    toplevel_name = 'inline_message'
    widgets = ['message_label']

    def __init__(self, message=''):
        SlaveView.__init__(self)
        self.message_label.set_text(message)
