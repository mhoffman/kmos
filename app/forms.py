#!/usr/bin/env python
import re
#gtk import
import pygtk
pygtk.require('2.0')
import gtk

#kiwi imports
from kiwi.ui.delegates import ProxySlaveDelegate, GladeDelegate, SlaveDelegate, ProxyDelegate
from kiwi.ui.views import SlaveView

# own modules
from config import GLADEFILE
from utils import CorrectlyNamed
from models import *


# Canvas Import
from pygtkcanvas.canvas import Canvas
from pygtkcanvas.canvaslayer import CanvasLayer
from pygtkcanvas.canvasitem import *

def col_str2tuple(hex_string):
    """Convenience function that turns a HTML type color
    into a tuple of three float between 0 and 1
    """
    color = gtk.gdk.Color(hex_string)
    return (color.red_float, color.green_float, color.blue_float)


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
        #self.lattice = self.project_tree.lattice_list[0]
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
                for lattice in self.project_tree.lattice_list:
                    for site in lattice.sites:
                        if i == self.X and j == self.Y:
                            l_site = CanvasOval(self.site_layer, 0, 0, 10, 10, fg=(1., 1., 1.))
                        else:
                            l_site = CanvasOval(self.site_layer, 0, 0, 10, 10, fg=(.6, .6, .6))

                        l_site.set_center(self.l/self.z*(i+float(site.site_x)/lattice.unit_cell_size_x), 500-self.l/self.z*(j+float(site.site_y)/lattice.unit_cell_size_y))
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

        # draw reservoir circles
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


class InlineMessage(SlaveView):
    """Return a nice little field with a text message on it
    """
    gladefile = GLADEFILE
    toplevel_name = 'inline_message'
    widgets = ['message_label']
    def __init__(self, message=''):
        SlaveView.__init__(self)
        self.message_label.set_text(message)


