#!/usr/bin/env python
# Standard library imports
import re
import copy
#gtk import
import pygtk
pygtk.require('2.0')
import gtk
import goocanvas

#kiwi imports
from kiwi.ui.delegates import ProxySlaveDelegate, GladeDelegate, SlaveDelegate, ProxyDelegate
from kiwi.ui.views import SlaveView
from kiwi.datatypes import ValidationError
from kiwi.ui.objectlist import Column
import kiwi.ui.dialogs

# own modules
from config import GLADEFILE
from utils import CorrectlyNamed, get_ase_constructor
from models import *

# ASE import
import numpy as np
from ase.atoms import Atoms
from ase.data import covalent_radii
from ase.data.colors import jmol_colors

# Canvas Import
from kmos.pygtkcanvas.canvas import Canvas
from kmos.pygtkcanvas.canvaslayer import CanvasLayer
from kmos.pygtkcanvas.canvasitem import *

def col_str2tuple(hex_string):
    """Convenience function that turns a HTML type color
    into a tuple of three float between 0 and 1
    """
    color = gtk.gdk.Color(hex_string)
    return (color.red_float, color.green_float, color.blue_float)


def jmolcolor_in_hex(i):
    from ase.data.colors import jmol_colors
    color = map(int, 255*jmol_colors[i])
    r, g, b = color
    a = 255
    color = (r << 24) | (g << 16) | (b << 8) | a
    return color
        
def parse_chemical_expression(eq, process, project_tree):
    """Evaluates a chemical expression 'eq' and adds
    conditions and actions accordingly. Rules are:
        - each chemical expression has the form
           conditions -> actions
        - each condition or action term has the form (regex)
          [$^]*SPECIES@SITE\.OFFSET
        - each SPECIES must have been defined before. The special
          species 'empty' exists by default
        - each SITE must have been defined before via the 
          layer form
        - an offset in units of units cell can be given as 
          tuple such as '(0,0)'
        - a condition or action term containing the default species,
          i.e. by default 'empty' may be omitted. However a term containing
          the omitted site and a species other then the default must exist
          on the opposite side of the expression
        - ^ and $ are special prefixes for the 'creation' and
          'annihilation' of a site, respectively. In case of '$'
           the species can be always omitted. In case of ^ the default
           species may be omitted. Creation and annihilation is only
           needed for lattice reconstructions/multi-lattice models and
           they only stand on the right-hand (i.e. action) side of
           the expression
        - white spaces may be used for readability but have no effect

        Examples:
            oxygen@cus -> oxygen@bridge #diffusion
            co@bridge -> co@cus.(-1,0) # diffusion
            -> oxygen@cus + oxygen@bridge # adsorption
            oxygen@cus + co@bridge -> # reaction
    """
    # remove spaces
    eq = re.sub(' ', '', eq)

    # remove comments
    if '#' in eq:
        eq = eq[:eq.find('#')]
    

    # split at ->
    if eq.count('->') != 1 :
        raise StandardError, 'Chemical expression must contain exactly one "->"\n%s'  % eq
    eq = re.split('->', eq)
    left, right = eq


    # split terms
    left = left.split('+')
    right = right.split('+')

    # Delete term, which contain nothing
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

    # check if species is defined
    for term in left + right:
        if term[0][0] in ['$','^'] and term[0][1 :]:
            if not  filter(lambda x: x.name == term[0][1 :], project_tree.species_list):
                raise UserWarning('Species %s unknown ' % term[0 :])
        elif not filter(lambda x: x.name == term[0], project_tree.species_list):
            raise UserWarning('Species %s unknown ' % term[0])

    condition_list = []
    action_list = []

    for i, term in enumerate(left + right):
        #parse coordinate
        coord_term = term[1].split('.')
        if len(coord_term) == 1 :
            coord_term.append('(0,0)')

        if len(coord_term) == 2 :
            name = coord_term[0]
            active_layers = filter(lambda x: x.active, project_tree.layer_list)
            if len(active_layers) == 1 :
                layer = active_layers[0].name
            else: # if more than one active try to guess layer from name
                possible_sites = []
                # if no layer visible choose among all of them
                # else choose among visible
                if not len(active_layers):
                    layers = project_tree.layer_list
                else:
                    layers = active_layers
                for ilayer in layers:
                    for jsite in ilayer.sites:
                        if jsite.name == name:
                            possible_sites.append((jsite.name,ilayer.name))
                if not possible_sites :
                    raise UserWarning("Site %s not known" % name)
                elif len(possible_sites) == 1 :
                    layer = possible_sites[0][1]
                else:
                    raise UserWarning("Site %s is ambiguous because it"+
                        "exists on the following lattices: %" %
                        (name, [x[1] for x  in possible_sites]))
            coord_term.append(layer)
                    
        if len(coord_term) == 3 :
            name = coord_term[0]
            offset = eval(coord_term[1])
            layer = coord_term[2]
            layer_names = [ x.name for x in project_tree.layer_list]
            if layer not in layer_names:
                raise UserWarning("Layer %s not known, must be one of %s" % (layer, layer_names))
            else:
                layer_instance = filter(lambda x: x.name==layer, project_tree.layer_list)[0]
                site_names = [x.name for x in layer_instance.sites]
                if name not in site_names:
                    raise UserWarning("Site %s not known, must be one of %s" % (name, site_names))
                
                
        species = term[0]
        coord = Coord(name=name,offset=offset,layer=layer)
        if i < len(left):
            condition_list.append(ConditionAction(species=species, coord=coord))
        else:
            action_list.append(ConditionAction(species=species, coord=coord))

    default_species = project_tree.species_list_iter.default_species
    # every condition that does not have a corresponding action on the 
    # same coordinate gets complemented with a 'default_species' action
    for condition in condition_list:
        if not filter(lambda x: x.coord == condition.coord, action_list):
            action_list.append(ConditionAction(species=default_species, coord=condition.coord))

    # every action that does not have a corresponding condition on
    # the same coordinate gets complemented with a 'default_species'
    # condition
    for action in action_list:
        if not filter(lambda x: x.coord == action.coord, condition_list)\
            and not action.species[0] in ['^', '$']:
            condition_list.append(ConditionAction(species=default_species, coord=action.coord))

    # species completion and consistency check for site creation/annihilation
    for action in action_list:
        # for a annihilation the following rules apply:
        #   -  if no species is gives, it will be complemented with the corresponding
        #      species as on the left side
        #   -  if a species is given, it must be equal to the corresponding one on the 
        #      left side. if no corresponding condition is given on the left side,
        #      the condition will be added with the same species as the annihilated one
        if action.species[0] == '$':
            corresponding_condition = filter(lambda x: x.coord == action.coord, condition_list)
            if action.species[1 :]:
                if not corresponding_condition:
                    condition_list.append(ConditionAction(species=action.species[1 :], coord=action.coord))
                else:
                    if corresponding_condition[0].species != action.species[1 :]:
                        raise UserWarning('When annihilating a site, species must be the same for condition\n'
                            + 'and action.\n')
            else:
                if corresponding_condition:
                    action.species = '$%s' % corresponding_species[0].species
                else:
                    raise UserWarning('When omitting the species in the site annihilation, a species must\n'
                        + 'must be given in a corresponding condition.')
        elif action.species == '^' :
            raise UserWarning('When creating a site, the species on the new site must be stated.')
            
            
    process.condition_list += condition_list
    process.action_list += action_list


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
        output_form.set_flags(gtk.CAN_DEFAULT | gtk.CAN_FOCUS)
        output_form.set_default_response(gtk.RESPONSE_OK)
        output_form.set_default(output_form.get_widget_for_response(gtk.RESPONSE_OK))
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
            if len(line) == 1 :
                eq = ''
                rate_constant = ''
            elif len(line) == 2 :
                eq = line[1]
                rate_constant = ''
            elif len(line) == 3 :
                eq = line[1]
                rate_constant = line[2]
            else:
                raise UserWarning("There are too many ';' in your expression %s" % line)
            process = Process(name=name, rate_constant=rate_constant)
            try:
                parse_chemical_expression(eq=line[1], process=process, project_tree=self.project_tree)
                self.draw_from_data()
            except:
                print("Found an error in your chemical expression(line %s):\n   %s" % (i+1, line[1]))
                raise
            else:
                # replace any existing process with identical names
                for dublette_proc in filter(lambda x: x.name == name, self.project_tree.process_list):
                    self.project_tree.process_list.remove(dublette_proc)
                self.project_tree.append(self.project_tree.process_list_iter, process)
        buffer.delete(*bounds)
    
    
class ProcessForm(ProxySlaveDelegate, CorrectlyNamed):
    """A form that allows to create and manipulate a process
    """
    gladefile = GLADEFILE
    toplevel_name = 'process_form'
    widgets = ['process_name', 'rate_constant', 'process_enabled','chemical_expression']
    z = 5 # z as in zoom
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
        ProxySlaveDelegate.__init__(self, process)
        expression = self.generate_expression()
        self.chemical_expression.update(expression, )
        self.draw_from_data()

        self.process_name.set_tooltip_text('This name has to uniquely identify the process e.g. co_diff_right')
        self.chemical_expression.set_tooltip_text('This is a fast way to define a process e.g. CO@cus->CO@bridge ' +
        'to declare a CO diffusion from site br to site cus or ' +
        'CO@cus->CO@cus.(0,1) for a CO diffusion in the up direction. Hit ENTER to update the graphical'
        'representation.')
        self.rate_constant.set_tooltip_text('Python has to be able to evaluate this expression to a simple real ' +
        'number. One can use standard mathematical functions, parameters that are defined under "Parameters" or ' +
        'constants and conversion factor such as c, h, e, kboltzmann, pi, bar, angstrom')
        rate_constant_terms = ['exp','kboltzmann']
        for param in self.project_tree.parameter_list:
            rate_constant_terms.append(param.name)
        self.rate_constant.prefill(rate_constant_terms)

        chem_exp_terms = ['->',]
        for species in self.project_tree.species_list:
            chem_exp_terms.append(species.name)
        self.chemical_expression.prefill(chem_exp_terms)
        

    def generate_expression(self):
        expr = ''
        if not self.process.condition_list + self.process.action_list:
            return expr
        for i, condition in enumerate(self.process.condition_list):
            if i > 0 :
                expr += ' + '
            expr += '%s@%s' % ( condition.species, condition.coord.name)
        expr += ' -> '
        for i, action in enumerate(self.process.action_list):
            if i > 0 :
                expr += ' + '
            expr += '%s@%s' % (action.species, action.coord.name)
        return expr

        
    def on_chemical_expression__activate(self, entry, **kwargs):
        text = entry.get_text()
        if not text:
            self.process.condition_list = []
            self.process.action_list = []
            self.draw_from_data()
            return
        # Delete trailing plusses
        text = re.sub(r'\s*\+\s', '', text)
        # default to empty right-hand side if not existent
        while text and text[-1] in '-.':
            text = text[:-1]
        if not '->' in text:
            text += '->'
        try:
            parse_chemical_expression(eq=text, process=self.process, project_tree=self.project_tree)
            self.process.condition_list = []
            self.process.action_list = []
            parse_chemical_expression(eq=text, process=self.process, project_tree=self.project_tree)
        except Exception as e:
            # first remove last term and try again
            try:
                print("Error ...")
                text = re.sub(r'+[^+]*$', '', text)
                parse_chemical_expression(eq=text, process=self.process, project_tree=self.project_tree)
                self.process.condition_list = []
                self.process.action_list = []
                parse_chemical_expression(eq=text, process=self.process, project_tree=self.project_tree)

            except Exception as e:
                print("Fatal Error ... %s" % e)
                self.process.condition_list = []
                self.process.action_list = []
        finally:
            self.draw_from_data()

    def query_tooltip(self, canvas, widget, tooltip):
        tooltip.set_text(widget.tooltip_text)
        return True

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
            self.item.clicked = True
            self.item.father = item
            self.prev_pos = self.item.get_center()
            self.canvas.redraw()


    def drag_motion(self, widget, item, event):
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
                    species = self.item.species
                    offset = closest_site.i - self.X, closest_site.j - self.Y
                    name = closest_site.name
                    layer = closest_site.layer
                    kmc_coord = Coord(offset=offset,
                                  name=name,
                                  layer=layer)
                    condition_action = ConditionAction(species=species,
                                                       coord=kmc_coord)


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

                    
        self.chemical_expression.update(self.generate_expression(), )
        self.canvas.redraw()


    def draw_from_data(self):
        """Places circles on the current lattice according
        to the conditions and actions defined
        """
        white = col_str2tuple('#ffffff')
        black = col_str2tuple('#000000')
        if hasattr(self, 'canvas'):
            self.process_pad.remove(self.canvas)
        self.canvas = Canvas(bg=white,fg=white)
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
        active_layers = filter(lambda x: x.active==True, self.project_tree.layer_list)
        site_list = []
        for active_layer in active_layers:
            for site in active_layer.sites:
                form_site = ProcessFormSite(name=site.name,x=site.x, y=site.y, z=site.z, layer=active_layer.name, color=active_layer.color)
                site_list.append(form_site)
        for i in range(self.z+1):
            for j in range(self.z+1):
                for site in site_list:
                    color =  col_str2tuple(site.color)
                    if i == self.X and j == self.Y:
                        l_site = CanvasOval(self.site_layer, 0, 0, 10, 10, fg=color)
                    else:
                        l_site = CanvasOval(self.site_layer, 0, 0, 10, 10, fg=color)

                    l_site.set_center(self.l/self.z*(i+float(site.x)), 500-self.l/self.z*(j+float(site.y)))
                    l_site.connect('query-tooltip', self.query_tooltip)
                    # 500 - ... for having scientific coordinates and not screen coordinates
                    l_site.set_radius(5)
                    l_site.i = i
                    l_site.j = j
                    if len(active_layers) > 1 :
                        l_site.tooltip_text = '%s.(%s,%s).%s' % (site.name, i-self.X, j-self.Y, site.layer)
                    else:
                        l_site.tooltip_text = '%s.(%s,%s)' % (site.name, i-self.X, j-self.Y)
                    l_site.name = site.name
                    l_site.offset = (i-self.X, j-self.Y)
                    l_site.layer = site.layer

        # draw frame
        frame_col = (.21, .35, .42)
        CanvasRect(self.frame_layer, 0, 0, 520, 80, fg=frame_col, bg=frame_col, filled=True)
        CanvasRect(self.frame_layer, 0, 0, 10, 580, fg=frame_col, bg=frame_col, filled=True)
        CanvasRect(self.frame_layer, 510, 0, 520, 580, fg=frame_col, bg=frame_col, filled=True)
        CanvasRect(self.frame_layer, 0, 580, 520, 590, fg=frame_col, bg=frame_col, filled=True)
        CanvasText(self.frame_layer, 10, 10, size=8, text='Reservoir Area')
        CanvasText(self.frame_layer, 10, 570, size=8, text='Lattice Area')

        # draw reservoir circles
        for k, species in enumerate(self.project_tree.species_list):
            color = col_str2tuple(species.color)
            o = CanvasOval(self.frame_layer, 30+k*50, 30, 50+k*50, 50, filled=True, bg=color)
            o.species = species.name
            o.tooltip_text = species.name # for tooltip
            o.connect('button-press-event', self.button_press)
            #o.connect('motion-notify-event', self.drag_motion)
            o.connect('button-release-event', self.button_release)
            o.connect('query-tooltip',self.query_tooltip)
            o.state = 'reservoir'

        self.lattice_layer.move_all(10, 80)
        self.site_layer.move_all(10, 80)

        # attributes need for moving objects
        self.item = None
        self.prev_pos = None
        black=col_str2tuple('#003333')
        for elem in self.process.condition_list:
            matching_sites = filter(lambda x: isinstance(x, CanvasOval)
                                    and x.i==self.X+elem.coord.offset[0]
                                    and x.j==self.Y+elem.coord.offset[1]
                                    and x.name==elem.coord.name
                                    and x.layer == elem.coord.layer, self.site_layer)
            if matching_sites:
                coords = matching_sites[0].get_coords()
                color = filter(lambda x: x.name == elem.species, self.project_tree.species_list)[0].color
                color = col_str2tuple(color)
                o = CanvasOval(self.condition_layer, bg=color, fg=black, filled=True, outline=True)
                o.coords = coords
                o.connect('button-press-event', self.on_condition_action_clicked)
                o.set_radius(self.r_cond)
                o.type = 'condition'
                o.condition = elem

        for elem in self.process.action_list:
            matching_sites = filter(lambda x: isinstance(x, CanvasOval)
                                    and x.i==self.X+elem.coord.offset[0]
                                    and x.j==self.Y+elem.coord.offset[1]
                                    and x.name==elem.coord.name
                                    and x.layer == elem.coord.layer, self.site_layer)
            if matching_sites:
                coords = matching_sites[0].get_coords()
                if elem.species[0] ==  '^':
                    color = filter(lambda x: x.name == elem.species[1 :], self.project_tree.species_list)[0].color
                elif elem.species[0] == '$':
                    # Don't draw the disappearing particle
                    continue
                else:
                    color = filter(lambda x: x.name == elem.species, self.project_tree.species_list)[0].color
                color = col_str2tuple(color)
                o = CanvasOval(self.action_layer, bg=color, fg=black, filled=True, outline=True)
                o.coords = coords
                o.connect('button-press-event', self.on_condition_action_clicked)
                o.set_radius(self.r_act)
                o.type = 'action'
                o.action = elem

        #if not site_list and not hasattr(self,'infoed'):
            #self.infoed = True
            #kiwi.ui.dialogs.info('No sites found', 'You either have not defined any sites or you switched all ' +
                #'layers to invisible. Double-click on a layer to change its visibility.')
        
    def on_condition_action_clicked(self, canvas, widget, event):
        if event.button == 2 :
            if widget.type == 'action':
                self.process.action_list.remove(widget.action)
            elif widget.type == 'condition':
                self.process.condition_list.remove(widget.condition)
            widget.delete()

    def on_process_name__content_changed(self, text):
        self.project_tree.project_data.sort_by_attribute('name')
        self.project_tree.update(self.process)

    def on_rate_constant__content_changed(self, text):
        self.project_tree.update(self.process)


class SiteForm(ProxyDelegate, CorrectlyNamed):
    """A form which allows to create or modify a site
    when setting up a unit cell
    """
    gladefile = GLADEFILE
    toplevel_name = 'site_form'
    widgets = ['site_name', 'sitevect_x', 'sitevect_y', 'sitevect_z','default_species']
    def __init__(self, site, parent, project_tree, layer):
        self.saved_state = copy.deepcopy(site)
        self.project_tree = project_tree
        default_species = site.default_species
        site.default_species = None
        ProxyDelegate.__init__(self, site)

        self.site_default_species.prefill( [ x.name for x in project_tree.species_list], sort=True)

        if default_species == 'default_species':
            self.site_default_species.select(self.project_tree.species_list_iter.default_species)
        else:
            self.site_default_species.select(default_species)
        self.model.default_species = self.site_default_species.get_selected()

        self.site_ok.grab_default()
        self.site = site
        self.parent = parent
        self.project_tree = project_tree
        self.layer = layer
        self.show_all()
        self.site_name.set_tooltip_text('The site name has to be uniquely identify a site (at least' +
        'within each layer for multi-lattice mode). You may have to type this name a lot, so keep' +
        'it short but unambiguous')

    def on_site_name__validate(self, widget, name):
        return self.on_name__validate(widget, model_name)

    def on_sitevect_x__validate(self, widget, value):
        if not 0 <= value <= 1 :
            return ValidationError('Each component must be between 0 and 1.')

    def on_sitevect_y__validate(self, widget, value):
        if not 0 <= value <= 1 :
            return ValidationError('Each component must be between 0 and 1.')

    def on_sitevect_z__validate(self, widget, value):
        if not 0 <= value <= 1 :
            return ValidationError('Each component must be between 0 and 1.')

    def on_sitevect_x__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_sitevect_y__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_sitevect_z__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_site_name__activate(self, _):
        self.on_site_ok__clicked(_)

    def on_site_name__validate(self, widget, site_name):
        """check if other site already has the name"""
        if filter(lambda x : x.name == site_name, self.layer.sites):
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

    def on_site_ok__clicked(self, button):
        self.model.default_species = self.site_default_species.get_selected()
        if not len(self.site_name.get_text()) :
            self.layer.sites.remove(self.model)
        self.hide()
        self.parent.redraw()



class MetaForm(ProxySlaveDelegate, CorrectlyNamed):
    """A form  that allows to enter meta information about the project
    """
    gladefile = GLADEFILE
    toplevel_name = 'meta_form'
    widgets = ['author', 'email', 'model_name', 'model_dimension', 'debug', ]
    def __init__(self, model, project_tree):
        ProxySlaveDelegate.__init__(self, model)
        #self.model_dimension.set_sensitive(False)
        self.project_tree = project_tree
        self.author.set_tooltip_text('Give a name so people know who to credit for the model.')
        self.email.set_tooltip_text('Enter an email address so people can get in touch with you.')
        self.model_name.set_tooltip_text('Give a clear unique name, so identify the model.')
        self.model_dimension.set_tooltip_text('The source code export function can generate ' +
        '1d, 2d, and 3d programs. However this GUI currently only supports 2d. 3d is still possibble ' +
        'by manipulating the project XML file by hand. The algorithm though is fast but very memory consuming ' +
        'so a 3d simulation might require on the order of 10GB or RAM or more')
        self.debug.set_tooltip_text('Increasing the debug level might give hints if one suspects errors in ' +
        'kmos itself. It does not help to debug your model. So usually one wants to keep it a 0.')
        self.author.grab_focus()


    def on_model_name__validate(self, widget, model_name):
        return self.on_name__validate(widget, model_name)

    def on_model_name__content_changed(self, text):
        self.project_tree.update(self.model)

    def on_model_dimension__content_changed(self, widget):
        dimension = int(widget.get_text())
        self.project_tree.update(self.model)


class ParameterForm(ProxySlaveDelegate, CorrectlyNamed):
    """The parameter form allows to set parameter. These
    parameter can be used in e.g. Transition State Theory
    formula to calculate rate constants.
    They might later also be adjustable via a visualization
    GUI
    """
    gladefile = GLADEFILE
    toplevel_name = 'parameter_form'
    widgets = ['parameter_name', 'value','parameter_adjustable','parameter_min','parameter_max']
    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        value = self.parameter_adjustable.get_active()
        self.parameter_max.set_sensitive(value)
        self.parameter_min.set_sensitive(value)
        self.name.grab_focus()
        self.parameter_adjustable.set_tooltip_text(
        'Settings this adjustable will create a bar in the auto-generated movie .' +
        'Dragging this bar will adapt the barrier and recalculate all rate constants. This only makes sense for ' +
        'physical parameters such a partial pressure but not for e.g. lattice size')
        self.parameter_name.set_tooltip_text(
        'Choose a sensible name that you remember later when typing rate constant ' +
        'formulae. This should not contain spaces')
        self.value.set_tooltip_text('This defines the initial value for the parameter.')

    def on_parameter_adjustable__content_changed(self, form):
        value = self.parameter_adjustable.get_active()
        self.parameter_max.set_sensitive(value)
        self.parameter_min.set_sensitive(value)
            

    def on_value__content_changed(self, text):
        self.project_tree.update(self.model)

    def on_parameter_name__content_changed(self, text):
        self.project_tree.update(self.model)
        self.project_tree.project_data.sort_by_attribute('name')


class SpeciesListForm(ProxySlaveDelegate):
    """This form only allows to set the default species, that is 
    a system will be globally initialized with this species if 
    nothing else is set on a per site basis
    """
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
        self.default_species.set_tooltip_text('The lattice will be initialized with this species by default\n'
            + 'but also every unspecified condition or action wil be completed with this choice.\n'
            + 'So better only change this once at the begining if at all!')




class SpeciesForm(ProxySlaveDelegate, CorrectlyNamed):
    """Widget to define a new species. Required attribute is name. The
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
        self.name.set_tooltip_text('The name here is arbitrary but you will have to type it many times. ' +
        'So you might want to use e.g. CO instead carbon_monoxide' )
        self.color.set_tooltip_text('Choose a color a represent this species in the process editor')
        self.representation.set_tooltip_text('Set an ASE Atoms(\n\'...\') like string to representation in the ' +
        'auto-generated movie. Please only use \'\' for quotation')

    def on_name__content_changed(self, text):
        self.project_tree.update(self.model)


class GridForm(ProxyDelegate):
    """Widget to set the grid for defining the lattice. The grid itself has
    no meaning for the model but it is merely there to assist setting sites
    at specific locations
    """
    gladefile = GLADEFILE
    toplevel_name = 'grid_form'
    widgets = ['grid_x', 'grid_y', 'grid_z', 'grid_offset_x', 'grid_offset_y', 'grid_offset_z']
    def __init__(self, grid, project_tree, layer):
        self.old_grid = copy.deepcopy(grid)
        self.project_tree = project_tree
        self.layer = layer
        ProxyDelegate.__init__(self, grid)
        self.grid_x.grab_focus()
        if self.project_tree.meta.model_dimension < 3 :
            self.grid_z.hide()
            self.grid_offset_z.hide()

    def on_grid_x__content_changed(self, widget):
        self.layer.redraw()

    def on_grid_y__content_changed(self, widget):
        self.layer.redraw()

    def on_grid_offset_x__validate(self, widget, offset):
        if not 0 <= offset <= 1 :
            return ValidationError('Offset must between 0 and 1.')

    def on_grid_offset_y__validate(self, widget, offset):
        if not 0 <= offset <= 1 :
            return ValidationError('Offset must between 0 and 1.')

    def on_grid_offset_x__content_changed(self, widget):
        self.layer.redraw()

    def on_grid_offset_y__content_changed(self, widget):
        self.layer.redraw()

    def on_grid_form_cancel__clicked(self, button):
        self.hide()

    def on_grid_form_ok__clicked(self, button):
        self.layer.redraw()
        self.hide()

    def on_grid_x__activate(self, widget):
        self.on_grid_form_ok__clicked(widget)

    def on_grid_y__activate(self, widget):
        self.on_grid_form_ok__clicked(widget)

    def on_grid_offset_x__activate(self, widget):
        self.on_grid_form_ok__clicked(widget)

    def on_grid_offset_y__activate(self, widget):
        self.on_grid_form_ok__clicked(widget)

        
class LatticeForm(ProxySlaveDelegate):
    """Widget to set global lattice parameter such as the lattice vector,
    a ASE representation string, and the default layer. The program will
    be initialized using the default layer
    """
    gladefile = GLADEFILE
    toplevel_name = 'lattice_form'
    widgets = ['cell_size_x', 'cell_size_y', 'cell_size_z', 'default_layer','lattice_representation']
    def __init__(self, model, dimension, project_tree):
        default_layer = model.default_layer
        model.default_layer = None
        ProxySlaveDelegate.__init__(self, model)
        self.default_layer.prefill([x.name for x in project_tree.layer_list], sort=True)
        self.default_layer.select(default_layer)
        self.default_layer.set_tooltip_text(
        'By default the system will be initialized with this layer. This only matters if using ' +
        'using more than one layer (multi-lattice kMC)')
        self.cell_size_label.set_tooltip_text(
        'Set the size of your unit cell in Angstrom for the auto-generated movie')

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
            except:
                print('Could not open this file. Please choose')
                print('a format that ASE can understand')
                return
            cur_text = self.lattice_representation.get_buffer().get_text(
                self.lattice_representation.get_buffer().get_start_iter(),
                self.lattice_representation.get_buffer().get_end_iter())
            if not cur_text:
                self.lattice_representation.get_buffer().set_text(
                    '[%s]' % get_ase_constructor(structure))
            else:
                structures = eval(cur_text)
                structures.append(structure)
                self.lattice_representation.get_buffer().set_text(
                    '%s' % [get_ase_constructor(x) for x in structures])


class LayerEditor(ProxySlaveDelegate, CorrectlyNamed):
    """Widget to define a lattice and the unit cell
    """
    gladefile = GLADEFILE
    toplevel_name = 'layer_form'
    widgets = ['layer_name', 'layer_color' ]
    def __init__(self, model, project_tree):
        self.project_tree = project_tree
        ProxySlaveDelegate.__init__(self, model)
        self.grid = self.model.grid
        self.canvas = goocanvas.Canvas()
        self.root = self.canvas.get_root_item()
        self.canvas.set_size_request(400,400)
        self.canvas.set_flags(gtk.HAS_FOCUS | gtk.CAN_FOCUS)
        self.canvas.connect('button-press-event', self.on_button_press)

        self.layer_nr = self.project_tree.layer_list.index(model)

        #self.grid_layer = CanvasLayer()
        #self.site_layer = CanvasLayer()
        #self.canvas.append(self.grid_layer)
        #self.canvas.append(self.site_layer)

        self.radius_scale = 22
        self.scale = 20
        self.offset_x, self.offset_y = (200, 200)
        self.lattice_pad.add(self.canvas)
        self.previous_layer_name = self.layer_name.get_text()
        self.redraw()

        self.layer_name.set_tooltip_text('A name is only relevant if you are using more than one\n' +
            'layer in your model.')
        self.set_grid_button.set_tooltip_text('The grid set here help to put sites at specific locations.\n'
            + 'The position has no direct meaning for the lattice kMC model.\n'
            + 'Meaning such as nearest neighbor etc. is only gained\n'
            + 'through corresponding processes')
            

    def redraw(self):
        white = col_str2tuple(self.model.color)
        black = col_str2tuple('#000000')

        atoms = []
        if self.project_tree.lattice.representation:
            representations = eval(self.project_tree.lattice.representation)
            if len(representations) > self.layer_nr:
                atoms = representations[self.layer_nr]
            else:
                atoms = representations[0]
        else:
            atoms = Atoms()
        self.lower_left = (self.offset_x, self.offset_y+self.scale*atoms.cell[1,1])
        self.upper_right= (self.offset_x + self.scale*atoms.cell[0,0], self.offset_y)
        big_atoms = atoms*(3,3,1)
        big_atoms.translate(-atoms.cell.diagonal())
        for atom in sorted(big_atoms, key=lambda x: x.position[2]):
            i = atom.number
            radius = self.radius_scale*covalent_radii[i]
            color = jmolcolor_in_hex(i)

            X = atom.position[0]
            Y = atoms.cell[1,1] - atom.position[1]
            ellipse = goocanvas.Ellipse(parent=self.root,
                                center_x=(self.offset_x+self.scale*X),
                                center_y=(self.offset_y+self.scale*Y),
                                radius_x=radius,
                                radius_y=radius,
                                stroke_color='black',
                                fill_color_rgba=color,
                                line_width=1.0)
        cell = goocanvas.Rect(parent=self.root,
                              x=self.offset_x,
                              y=self.offset_y,
                              height=self.scale*atoms.cell[1,1],
                              width=self.scale*atoms.cell[0,0],
                              stroke_color='black',
                              )


        for site in self.model.sites:
            X = self.scale*np.dot(site.x,atoms.cell[0,0])
            Y = self.scale*np.dot(1-site.y,atoms.cell[1,1])
            o = goocanvas.Ellipse(parent=self.root,
                                  center_x=self.offset_x+X,
                                  center_y=self.offset_y+Y,
                                  radius_x=.3*self.radius_scale,
                                  radius_y=.3*self.radius_scale,
                                  stroke_color='black',
                                  fill_color='white',
                                  line_width=1.0,)

            o.site = site
            o.connect('query-tooltip', self.query_tooltip)
        self.canvas.hide()
        self.canvas.show()
        #if self.project_tree.lattice.cell_size_x > self.project_tree.lattice.cell_size_y :
            #X = 400.
            #Y = 400.*self.project_tree.lattice.cell_size_y/self.project_tree.lattice.cell_size_x
        #else:
            #Y = 400.
            #X = 400.*self.project_tree.lattice.cell_size_x/self.project_tree.lattice.cell_size_y


        # draw frame
        #CanvasLine(self.grid_layer, 0,0,0,Y, fg=white)
        #CanvasLine(self.grid_layer, X,0,X,Y, fg=white)
        #CanvasLine(self.grid_layer, 0,0,X,0, fg=white)
        #CanvasLine(self.grid_layer, 0,Y,X,Y, fg=white)

        # draw grid lines
        #for i in range(self.grid.x+1):
            #xprime = (float(i)/self.grid.x+self.grid.offset_x)*X % X
            #CanvasLine(self.grid_layer,xprime ,0, xprime, Y, fg=white)
        #for i in range(self.grid.y+1):
            #yprime = (float(i)/(self.grid.y)+self.grid.offset_y)*Y % Y
            #CanvasLine(self.grid_layer, 0, Y-yprime , X, Y-yprime, fg=white)
        #for i in range(self.grid.x+1):
            #for j in range(self.grid.y+1):
                #xprime = (float(i)/self.grid.x+self.grid.offset_x)*X % X
                #yprime = (float(j)/(self.grid.y)+self.grid.offset_y)*Y % Y
                #o = CanvasOval(self.grid_layer, 0, 0, 10, 10, fg=white)
                #o.set_center(xprime, Y-yprime)
                #o.set_radius(5)
                #o.frac_coords = (xprime/X, yprime/Y)
                #o.connect('button-press-event', self.grid_point_press_event)

    def query_tooltip(self, canvas, widget, tooltip):
        tooltip.set_text(widget.site.name)
        return True

    def on_button_press(self, item, event):
        pos_x = (event.x-self.lower_left[0])/(self.upper_right[0]-self.lower_left[0])
        pos_y = (event.y-self.lower_left[1])/(self.upper_right[1]-self.lower_left[1])

        for site in self.model.sites:
            d = np.sqrt((pos_x-site.x)**2 + (pos_y-site.y)**2)
            if d < 0.03 :
                SiteForm(site, self, self.project_tree, self.model)
                break
        else:
            new_site = Site()
            new_site.name = ''
            new_site.x = pos_x
            new_site.y = pos_y
            new_site.z = 0.
            new_site.layer = self.model.name

            self.model.sites.append(new_site)
            SiteForm(new_site, self, self.project_tree, self.model)




      

    def on_set_grid_button__clicked(self, button):
        grid_form = GridForm(self.model.grid, self.project_tree, self)
        grid_form.show()

    def on_layer_name__validate(self, widget, layer_name):
        # TODO: validate lattice name to be unique
        return self.on_name__validate(widget, layer_name)

    def on_layer_name__content_changed(self, widget):
        # Sync layer names in process coords
        new_layer_name = widget.get_text()
        for process in self.project_tree.process_list:
            for elem in process.condition_list:
                if elem.coord.layer == self.previous_layer_name:
                    elem.coord.layer = new_layer_name
            for elem in process.action_list:
                if elem.coord.layer == self.previous_layer_name:
                    elem.coord.layer = new_layer_name
        self.previous_layer_name = new_layer_name

                    
        self.project_tree.update(self.model)



class InlineMessage(SlaveView):
    """Return a nice little field with a text message on it
    """
    gladefile = GLADEFILE
    toplevel_name = 'inline_message'
    widgets = ['message_label']
    def __init__(self, message=''):
        SlaveView.__init__(self)
        self.message_label.set_text(message)
