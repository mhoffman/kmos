#!/usr/bin/python
"""Some small test program to explore the characteristics of a drawing area
"""

from app.config import *
import sys
sys.path.append(APP_ABS_PATH)
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import os


class DrawingArea:
    """Main Dialog set up a lattice and its adsorption sites
    """
    def __init__(self, callback):
        self.callback = callback
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.window = self.wtree.get_widget('wndCellEdit')
        self.statbar = self.wtree.get_widget('statusbar')
        self.statbar.push(1, 'Click to select first corner of cell.')
        self.cell_started = False
        self.cell_finished = False

        self.sites = []
        self.unit_cell_size = [1, 1]

        dic = {'on_dwMain_button_press_event' : self.lattice_editor_click,
                'on_wndCellEdit_destroy_event' :self.quit,
                'on_btnCancel_clicked' : self.quit,
                'on_dwMain_expose_event' : self.lattice_editor_expose,
                'on_dwMain_configure_event' : self.lattice_editor_configure,
                'on_dwMain_motion_notify_event' : self.lattice_editor_motion,
                }
        self.wtree.signal_autoconnect(dic)
        self.window.show()

    def lattice_editor_motion(self, widget, event):
        """Catches event, if mouse is moving inside drawing area
        """
        if self.cell_started and not self.cell_finished:
            rect = self.corner1[0], self.corner1[1], int(event.x), int(event.y)
            self.pixmap.draw_rectangle(widget.get_style().white_gc, True, 0, 0, self.lattice_editor_width, self.lattice_editor_height)
            self.pixmap.draw_line(widget.get_style().black_gc, rect[0], rect[1], rect[2], rect[1])
            self.pixmap.draw_line(widget.get_style().black_gc, rect[0], rect[1], rect[0], rect[3])
            self.pixmap.draw_line(widget.get_style().black_gc, rect[2], rect[1], rect[2], rect[3])
            self.pixmap.draw_line(widget.get_style().black_gc, rect[0], rect[3], rect[2], rect[3])
            widget.queue_draw_area(0, 0, self.lattice_editor_width, self.lattice_editor_height)

    def lattice_editor_expose(self, widget, event):
        """Redraws drawing area everytime something changes abot the window
        """
        site_x, site_y, self.lattice_editor_width, self.lattice_editor_height = widget.get_allocation()
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL], self.pixmap, site_x, site_y, site_x, site_y, self.lattice_editor_width, self.lattice_editor_height)

    def lattice_editor_configure(self, widget, event):
        """Some initial adjustments, when the drawing area is loaded first
        """
        self.lattice_editor_width, self.lattice_editor_height = widget.get_allocation()[2], widget.get_allocation()[3]
        self.pixmap = gtk.gdk.Pixmap(widget.window, self.lattice_editor_width, self.lattice_editor_height)
        self.pixmap.draw_rectangle(widget.get_style().white_gc, True, 0, 0, self.lattice_editor_width, self.lattice_editor_height)
        return True

    def lattice_editor_click(self, widget, event):
        """Catches event, if user clicks with mouse into drawing area
        """
        if not self.cell_started:
            self.cell_started = True
            self.statbar.push(1,'Click to select second coner of cell.')
            self.corner1 = (int(event.x), int(event.y))
        elif not self.cell_finished:
            self.cell_finished = True
            self.statbar.push(1,'Click inside the cell to define sites.')
            self.corner2 = (int(event.x), int(event.y))
            #put corners in normal order
            corner1 = min(self.corner1[0], self.corner2[0]), min(self.corner1[1], self.corner2[1])
            corner2 = max(self.corner1[0], self.corner2[0]), max(self.corner1[1], self.corner2[1])
            self.corner1 = corner1
            self.corner2 = corner2
            #Call Dialog to get unit cell size
            cell_size_dialog = DialogCellSize()
            result, data = cell_size_dialog.run()
            if result == gtk.RESPONSE_OK:
                self.unit_cell_size = data['x'], data['y']
                self.lattice_name = data['name']
                for i in xrange(data['x']):
                    xline = self.corner1[0] + i*(self.corner2[0] - self.corner1[0]) / data['x']
                    self.pixmap.draw_line(widget.get_style().black_gc, xline, self.corner1[1], xline, self.corner2[1])
                for j in xrange(data['y']):
                    yline = self.corner1[1] + j*(self.corner2[1] - self.corner1[1]) / data['y']
                    self.pixmap.draw_line(widget.get_style().black_gc, self.corner1[0], yline, self.corner2[0], yline)
                self.window.queue_draw_area(0, 0, self.lattice_editor_width, self.lattice_editor_height)
        else:
            site_dialog = DialogDefineSite(self, event)
            result, data = site_dialog.run()
            if result == gtk.RESPONSE_OK:
                if data['type'] == 'remove':
                    for site in self.sites:
                        if site['x'] == data['x'] and site['y'] == data['y']:
                            self.sites.remove(site)
                else:
                    for site in self.sites:
                        if site['x'] == data['x'] and site['y'] == data['y']:
                            self.sites.remove(site)
                    self.sites.append(data)
                # Redraw dots
                for i in range(self.unit_cell_size[0]+1):
                    for j in range(self.unit_cell_size[1]+1):
                        center = []
                        center.append(self.corner1[0] + i*(self.corner2[0]-self.corner1[0])/self.unit_cell_size[0] - 5)
                        center.append(self.corner2[1] - j*(self.corner2[1]-self.corner1[1])/self.unit_cell_size[1] - 5)
                        for site in self.sites:
                            if (i % self.unit_cell_size[0]) == site['x'] and (j % self.unit_cell_size[1]) == site['y']:
                                self.pixmap.draw_arc(widget.get_style().black_gc, True, center[0], center[1], 10, 10, 0, 64*360)
                                break
                        else:
                            self.pixmap.draw_arc(widget.get_style().white_gc, True, center[0], center[1], 10, 10, 0, 64*360)
                            self.pixmap.draw_arc(widget.get_style().black_gc, False, center[0], center[1], 10, 10, 0, 64*360)
                widget.queue_draw_area(0, 0, self.lattice_editor_width, self.lattice_editor_height)



    def quit(self, *a):
        """Quits main program
        """
        self.callback(self)
        self.window.destroy()
        #gtk.main_quit()


class DialogAddParameter():
    """Small dialog that allows to enter a new parameter
    """
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog_add_parameter = self.wtree.get_widget('dlgAddParameter')

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog_add_parameter.show()
        # define fields
        parameter_name = self.wtree.get_widget('parameterName')
        parameter_type = self.wtree.get_widget('parameterType')
        parameter_value = self.wtree.get_widget('parameterValue')
        # run
        result = self.dialog_add_parameter.run()
        # extract fields
        data = {}
        data['name'] = parameter_name.get_text()

        type_model = parameter_type.get_model()
        type_index = parameter_type.get_active()
        data['type'] = type_model[type_index][0]

        data['value'] = parameter_value.get_text()
        # close
        self.dialog_add_parameter.destroy()
        return result, data

class DialogCellSize():
    """Small dialog to obtain the unit cell size from the user
    """
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog_cell_size = self.wtree.get_widget('wndCellSize')

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog_cell_size.show()
        # define fields
        site_x = self.wtree.get_widget('spb_cell_size_X')
        site_y = self.wtree.get_widget('spb_cell_size_Y')
        lattice_name = self.wtree.get_widget('lattice_name')
        # run
        result = self.dialog_cell_size.run()
        # extract fields
        data = {}
        data['x'] = site_x.get_value_as_int()
        data['y'] = site_y.get_value_as_int()
        data['name'] = lattice_name.get_text()
        # close
        self.dialog_cell_size.destroy()
        return result, data


class DialogDefineSite():
    """Small dialog to obtain characteristics of an adsorption site from the user
    """
    def __init__(self, lattice_dialog, event):
        self.lattice_dialog = lattice_dialog
        self.event = event
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog_site = self.wtree.get_widget('wndSite')
        if event.x < lattice_dialog.corner1[0] or event.x > lattice_dialog.corner2[0] or event.y < lattice_dialog.corner1[1] or event.y > lattice_dialog.corner2[1]:
            self.coord_x = 0
            self.coord_y = 0
        else:
            self.coord_x = int((event.x-lattice_dialog.corner1[0])/(lattice_dialog.corner2[0]-lattice_dialog.corner1[0])*lattice_dialog.unit_cell_size[0])
            self.coord_y = lattice_dialog.unit_cell_size[1] - int((event.y-lattice_dialog.corner1[1])/(lattice_dialog.corner2[1]-lattice_dialog.corner1[1])*lattice_dialog.unit_cell_size[1]) - 1


    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog_site.show()
        # define field and set defaults
        type_field = self.wtree.get_widget('defineSite_type')
        type_field.set_text('default')
        index_field = self.wtree.get_widget('defineSite_index')
        index_adjustment = gtk.Adjustment(value=len(self.lattice_dialog.sites), lower=0, upper=1000, step_incr=1, page_incr=4, page_size=0)
        index_field.set_adjustment(index_adjustment)
        index_field.set_value(len(self.lattice_dialog.sites))
        site_x = self.wtree.get_widget('spb_site_x')
        x_adjustment = gtk.Adjustment(value=0, lower=0, upper=self.lattice_dialog.unit_cell_size[0]-1, step_incr=1, page_incr=4, page_size=0)
        site_x.set_adjustment(x_adjustment)
        site_x.set_value(self.coord_x)
        site_y = self.wtree.get_widget('spb_site_y')
        y_adjustment = gtk.Adjustment(value=0, lower=0, upper=self.lattice_dialog.unit_cell_size[1]-1, step_incr=1, page_incr=4, page_size=0)
        site_y.set_adjustment(y_adjustment)
        y_adjustment.set_value(self.coord_y)
        #run dialog
        result = self.dialog_site.run()
        # extract fields
        data = {}
        data['x'] = site_x.get_value_as_int()
        data['y'] = site_y.get_value_as_int()
        data['index'] = index_field.get_value_as_int()
        data['type'] = type_field.get_text()
        # close
        self.dialog_site.destroy()
        return result, data


class MainWindow():
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.window = self.wtree.get_widget('wndMain')
        self.statbar = self.wtree.get_widget('stb_process_editor')
        self.da_widget = self.wtree.get_widget('dwLattice')
        self.lattices = []
        self.processes = []
        self.parameters = []
        self.keywords = ['exp','sin','cos','sqrt','log']
        self.species = []
        self.new_process = {}
        dic = {'on_btnAddLattice_clicked' : self.new_lattice ,
                'on_btnMainQuit_clicked' : lambda w: gtk.main_quit(),
                'on_btnAddParameter_clicked': self.add_parameter,
                'on_btnAddSpecies_clicked' : self.add_species,
                'on_btnAddProcess_clicked' : self.create_process,
                'on_eventbox1_button_press_event' : self.statbar_clicked,
                'on_dwLattice_button_press_event' : self.dw_lattice_clicked,
                'on_dwLattice_configure_event' : self.dw_lattice_configure,
                'on_dwLattice_expose_event' : self.dw_lattice_expose,
                'on_btnImportXML_clicked' : self.import_xml,
                'on_btnExportXML_clicked' : self.export_xml,
                'on_btnExportSource_clicked': self.export_source,
                'on_btnExportProgram_clicked' : self.export_program,
                'on_btnHelp_clicked' : self.display_help,
                }

        self.wtree.signal_autoconnect(dic)
        self.window.show()
        self.statbar.push(1,'Add a new lattice first.')
        self.lattice_ready = False

    def import_xml(self, widget):
        self.statbar.push(1,'Not implemented yet!')

    def export_xml(self, widget):
        self.statbar.push(1,'Not implemented yet!')

    def export_source(self, widget):
        self.statbar.push(1,'Not implemented yet!')

    def export_program(self, widget):
        self.statbar.push(1,'Not implemented yet!')

    def display_help(self, widget):
        self.statbar.push(1,'Not implemented yet!')


    def dw_lattice_clicked(self, widget, event):
        if self.lattice_ready:
            width, height = self.process_editor_width, self.process_editor_height
            lattice = self.lattices[0]
            unit_x = lattice['unit_cell_size'][0]
            unit_y = lattice['unit_cell_size'][1]
            zoom = 3
            for i in range(zoom+1):
                for j in range(3):
                    for x in range(unit_x):
                        for y in range(unit_y):
                            for site in lattice['sites']:
                                if site['x'] == x and site['y'] == y:
                                    center = []
                                    coordx = int((i+ float(x)/unit_x)*width/zoom)
                                    coordy = int(height - (j+ float(y)/unit_y)*height/zoom)
                                    if (coordx - event.x)**2 + (coordy - event.y)**2 < 30 :
                                        self.species_menu = gtk.Menu()
                                        if event.button == 3 :
                                            data = 'action', i, j, x, y
                                        elif event.button == 1 :
                                            data = 'condition', i, j, x, y

                                        for species in self.species:
                                            menu_item = gtk.MenuItem(species['species'])
                                            self.species_menu.append(menu_item)
                                            menu_item.connect("activate", self.add_condition, (species, list(data)))
                                        self.species_menu.show_all()
                                        self.species_menu.popup(None, None, None, event.button, event.time)


    def new_lattice(self, widget):
        lattice_editor = DrawingArea(self.add_lattice)

    def add_species(self, widget):
        dialog_new_species = DialogNewSpecies()
        result, data = dialog_new_species.run()
        if result == gtk.RESPONSE_OK:

            if not data['color']:
                self.statbar.push(1,'Species not added because no color was specified!')
            elif data not in self.species:
                self.species.append(data)
                self.statbar.push(1,'Added species "'+ data['species'] + '"')
                print(self.species)

    def add_parameter(self, widget):
        parameter_editor = DialogAddParameter()
        result, data = parameter_editor.run()
        if result == gtk.RESPONSE_OK:
            print("Adding new parameter")
            print(data)
            self.parameters.append(data)


    def add_lattice(self, data):
        if not data.cell_finished:
            self.statbar.push(1,'Could not add lattice: cell not defined!')
            return
        if 'lattice_name' not in dir(data) or not data.__dict__['lattice_name']:
            self.statbar.push(1,'Could not add lattice: lattice name not specified!')
            return
        if 'sites' not in dir(data) or not data.__dict__['sites']:
            self.statbar.push(1,'Could not add lattice: no sites specified!')
            return
        if 'unit_cell_size' not in dir(data) or not data.__dict__['unit_cell_size']:
            self.statbar.push(1,'Could not add lattice: no unit cell size specified!')
            return
        lattice = {}
        lattice['name'] = data.__dict__['lattice_name']
        lattice['sites'] = data.__dict__['sites']
        lattice['unit_cell_size'] = data.__dict__['unit_cell_size']
        self.lattices.append(lattice)
        self.statbar.push(1,'Added lattice "' + data.__dict__['lattice_name'] + '"')

    def dw_lattice_configure(self, widget, event):
        self.process_editor_width, self.process_editor_height = widget.get_allocation()[2], widget.get_allocation()[3]
        self.pixmap = gtk.gdk.Pixmap(widget.window, self.process_editor_width, self.process_editor_height)
        self.pixmap.draw_rectangle(widget.get_style().white_gc, True, 0, 0, self.process_editor_width, self.process_editor_height)
        return True

    def dw_lattice_expose(self, widget, event):
        site_x, site_y, self.process_editor_width, self.process_editor_height = widget.get_allocation()
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL], self.pixmap, 0, site_y, 0, site_y, self.process_editor_width, self.process_editor_height)


    def create_process(self, widget):
        self.new_process = {}
        self.new_process['conditions'] = []
        self.new_process['actions'] = []
        self.new_process['name'] = ''
        self.new_process['rate_constant'] = 0.
        self.new_process['center_site'] = ()

        if len(self.lattices) < 1 :
            self.statbar.push(1,'No lattice defined!')
            return
        dlg_process_name = DialogProcessName()
        result, data = dlg_process_name.run()
        if result == gtk.RESPONSE_CANCEL:
            return
        else:
            self.new_process['name'] = data['process_name']

        self.draw_lattices()
        self.lattice_ready = True
        self.statbar.push(1,'Left-click sites for condition, right-click site for changes, click here if finished.')

        #uimanager = gtk.UIManager()
        #ui = "<ui>\n<popup>\n"
        #for species in self.species:
            #ui += "<menuitem name='" + species + "' action='return_species'/>\n"
        #ui += "</popup>\n</ui>\n"
        #uimanager.add_ui_from_string(ui)
        #self.popup = uimanager.get_widget('/popup')
#
        #for elem in self.popup:
            #print(elem)
            #for subelem in elem:
                #print(subelem)

    def statbar_clicked(self, widget, event):
        if self.new_process:
            dlg_rate_constant = DialogRateConstant(self.parameters, self.keywords)
            result, data = dlg_rate_constant.run()
            #Check if process is sound
            if not self.new_process['name'] :
                self.statbar.push(1,'New process has no name')
                return
            elif not self.new_process['conditions']:
                self.statbar.push(1,'New process has no conditions')
                return
            elif not self.new_process['actions']:
                self.statbar.push(1,'New process has no actions')


            if result == gtk.RESPONSE_OK:
                self.new_process['rate_constant'] = data['rate_constant']
            self.processes.append(self.new_process)
            self.statbar.push(1,'New process "'+ self.new_process['name'] + '" added')
            print(self.new_process)
            self.new_process = {}
            self.lattice_ready = False
            self.draw_lattices(blank=True)


    def add_condition(self, event, data):

        if data[1][0] == 'condition':
            data = data[0], data[1][1 :]
            # if this is the first condition, make it the center site
            # all other sites will be measure relative to this site
            if not self.new_process['conditions']:
                self.new_process['center_site'] = data[1]
            self.new_process['conditions'].append(data)
        elif data[1][0] == 'action':
            data = data[0], data[1][1 :]
            self.new_process['actions'].append(data)
        self.draw_lattices()



    def draw_lattices(self,blank=False):
        gc = self.da_widget.get_style().black_gc
        lattice = self.lattices[0]
        width, height = self.process_editor_width, self.process_editor_height
        self.pixmap.draw_rectangle(self.da_widget.get_style().white_gc, True, 0, 0, width, height)
        if blank:
            return
        unit_x = lattice['unit_cell_size'][0]
        unit_y = lattice['unit_cell_size'][1]
        zoom = 3
        for sup_i in range(zoom+1):
            for i in range(-1,1):
                self.pixmap.draw_line(gc, 0, i+sup_i*height/zoom, width, i+(sup_i*height/zoom))
                self.pixmap.draw_line(gc, i+sup_i*width/zoom, 0, i+(sup_i*width/zoom), height)
            for sup_j in range(3):
                for x in range(unit_x):
                    for y in range(unit_y):
                        for site in lattice['sites']:
                            if site['x'] == x and site['y'] == y:
                                center = []
                                coordx = int((sup_i+ float(x)/unit_x)*width/zoom )
                                coordy = int(height - (sup_j+ float(y)/unit_y)*height/zoom )
                                center = [ coordx, coordy ]
                                self.pixmap.draw_arc(gc, True, center[0]-5, center[1]-5, 10, 10, 0, 64*360)
                                if self.new_process.has_key('conditions'):
                                    for entry in self.new_process['conditions']:
                                        if entry[1] == [sup_i, sup_j, x, y ]:
                                            color = filter((lambda x : x['species'] == entry[0]['species']), self.species)[0]['color']
                                            gc.set_rgb_fg_color(color)
                                            self.pixmap.draw_arc(gc, True, center[0]-15, center[1]-15, 30, 30, 64*90, 64*360)
                                            gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
                                            self.pixmap.draw_arc(gc, False, center[0]-15, center[1]-15, 30, 30, 64*90, 64*360)
                                if self.new_process.has_key('actions'):
                                    for entry in self.new_process['actions']:
                                        if entry[1] == [sup_i, sup_j, x, y ]:
                                            color = filter((lambda x : x['species'] == entry[0]['species']), self.species)[0]['color']
                                            gc.set_rgb_fg_color(color)
                                            self.pixmap.draw_arc(gc, True, center[0]-10, center[1]-10, 20, 20, 64*270, 64*360)
                                            gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
                                            self.pixmap.draw_arc(gc, False, center[0]-10, center[1]-10, 20, 20, 64*270, 64*360)
                                gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))


        self.da_widget.queue_draw_area(0, 0, width, height)


class SpeciesMenu():
    def __init__(self, species):
        self.species = species


class DialogProcessName():
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('dlgProcessName')

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog.show()
        # define fields
        process_name = self.wtree.get_widget('process_name')
        #run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['process_name'] = process_name.get_text()
        self.dialog.destroy()
        return result, data

class DialogNewSpecies():
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('dlgNewSpecies')
        dic = {'on_btnSelectColor_clicked' : self.open_dlg_color_selection,}
        self.wtree.signal_autoconnect(dic)
        self.color = ""


    def open_dlg_color_selection(self, widget):
        dlg_color_selection = DialogColorSelection()
        result, data = dlg_color_selection.run()
        if result == gtk.RESPONSE_OK:
            self.color = data['color']
        dlg_color_selection.close()

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog.show()
        # define fields
        species = self.wtree.get_widget('field_species')
        #run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['species'] = species.get_text()
        data['color'] = self.color
        self.dialog.destroy()
        return result, data

class DialogRateConstant():
    def __init__(self, parameters=[], keywords=[]):
        self.parameters = parameters
        self.keywords = keywords
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('dlgRateConstant')

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog.show()
        # define fields
        rate_constant = self.wtree.get_widget('rate_constant')
        completion = gtk.EntryCompletion()
        liststore = gtk.ListStore(str)
        rate_constant.set_completion(completion)
        completion.set_model(liststore)
        completion.set_text_column(0)
        #Add text to liststore
        for parameter in self.parameters:
            liststore.append([parameter['name']])
        for keyword in self.keywords:
            liststore.append([keyword])
        #run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['rate_constant'] = rate_constant.get_text()
        self.dialog.destroy()
        return result, data

class DialogColorSelection():
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('dlgcolorselection')
        #dic = {'on_btn_colorsel_ok_clicked': (lambda w: self.destroy())}
        #self.wtree.signal_autoconnect(dic)



    def run(self):
        self.dialog.show()
        color = self.wtree.get_widget('colorsel-color_selection1')
        result = self.dialog.run()
        data = {}
        data['color'] = color.get_current_color()
        return result, data

    def close(self):
        self.dialog.destroy()
        return True



def main():
    """Main function, called if scripts called directly
    """
    MainWindow()
    gtk.main()

if __name__ == "__main__":
    main()
