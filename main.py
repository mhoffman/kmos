#!/usr/bin/python
"""Some small test program to explore the characteristics of a drawing area
"""

import pdb
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


import os


KMCPROJECT_DTD = '/kmc_project.dtd'
PROCESSLIST_DTD = '/process_list.dtd'
XMLFILE = './default.xml'
SRCDIR = './fortran_src'

def verbose(func):
        print >>sys.stderr,"monitor %r"%(func.func_name)
        def f(*args,**kwargs):
                print >>sys.stderr,"call(\033[0;31m%s.%s\033[0;30m): %r\n"%(type(args[0]).__name__,func.func_name,args[1 :]),
                sys.stderr.flush()
                ret=func(*args,**kwargs)
                print >>sys.stderr,"    ret(%s): \033[0;32m%r\033[0;30m\n"%(func.func_name,ret)
                return ret
        return f

class Attributes:
    attributes = []
    def __setattr__(self, attrname, value):
        if attrname in self.attributes:
            self.__dict__[attrname] = value
        else:
            raise AttributeError


class KMC_Model(gtk.GenericTreeModel):
    def __init__(self, processes=[], species=[]):
        gtk.GenericTreeModel.__init__(self)
        self.lattice_list = LatticeList(self.callback,node_index=0)
        self.meta = Meta(self.callback,node_index=1)
        self.parameter_list = ParameterList(self.callback,node_index=2)
        self.process_list = ProcessList(self.callback,node_index=3)
        self.species_list = SpeciesList(self.callback,node_index=4)
        self.column_types = (str,)
        self.notifier = Notifier()
        self.save_changes_view = SaveChangesView()
        self.notifier.add_listener(self.save_changes_view)


    #@verbose
    def callback(self, signal, *args, **kwargs):
        if signal == 'row-inserted':
            path = args[0]
            self.row_inserted(path, self.get_iter(path))
            self.notifier('changed')
        elif signal == 'changed':
            self.notifier('changed')


    #@verbose
    def on_get_flags(self):
        return 0

    #@verbose
    def on_get_n_columns(self):
        return len(self.column_types)

    #@verbose
    def on_get_column_type(self, index):
        return self.column_types[index]

    #@verbose
    def on_get_iter(self, path):
        if path == None:
            return None
        elif path[0] == 0 :
            if len(path) == 1 :
                return self.lattice_list
            else:
                return self.lattice_list.on_get_iter((path[1], ))
        elif path[0] == 1 :
            if len(path) == 1 :
                return self.meta
            else:
                return None
        elif path[0] == 2 :
            if len(path) == 1 :
                return self.parameter_list
            else:
                return self.parameter_list.on_get_iter((path[1], ))
        elif path[0] ==  3 :
            if len(path) == 1 :
                return self.process_list
            else:
                return self.process_list.on_get_iter((path[1], ))
        elif path[0] == 4 :
            if len(path) == 1 :
                return self.species_list
            else:
                return self.species_list.on_get_iter((path[1],))
        else:
            return IndexError

    #@verbose
    def on_get_path(self, rowref):
        if rowref is None:
            return None
        elif isinstance(rowref, LatticeList):
            return (0, )
        elif isinstance(rowref, Lattice):
            return (0, self.lattice_list.on_get_path(rowref))
        elif isinstance(rowref, Meta):
            return (1,)
        elif isinstance(rowref, ParameterList):
            return (2, )
        elif isinstance(rowref, Parameter):
            return (2, self.parameter_list.on_get_path(rowref))
        elif isinstance(rowref, ProcessList):
            return (3, )
        elif isinstance(rowref, Process):
            return (3, self.process_list.on_get_path(rowref))
        elif isinstance(rowref, SpeciesList):
            return (4, )
        elif isinstance(rowref, Species):
            return (4, self.species_list.on_get_path(rowref))
        else:
            raise TypeError

    #@verbose
    def on_get_value(self, rowref, column):
        if isinstance(rowref, LatticeList):
            return 'Lattices'
        elif  isinstance(rowref, Lattice):
            return self.lattice_list.on_get_value(rowref, column)
        elif isinstance(rowref, Meta):
            return 'Meta'
        elif isinstance(rowref, ParameterList):
            return 'Parameters'
        elif isinstance(rowref, Parameter):
            return self.parameter_list.on_get_value(rowref, column)
        elif isinstance(rowref, ProcessList):
            return 'Processes'
        elif isinstance(rowref, Process):
            return self.process_list.on_get_value(rowref, column)
        elif isinstance(rowref, SpeciesList):
            return 'Species'
        elif isinstance(rowref, Species):
            return self.species_list.on_get_value(rowref, column)
        else:
            print(rowref, type(rowref))
            raise TypeError

    #@verbose
    def on_iter_next(self, rowref):
        if rowref is None:
            return None
        elif isinstance(rowref, LatticeList):
            return self.meta
        elif isinstance(rowref, Lattice):
            return self.lattice_list.on_iter_next(rowref)
        elif isinstance(rowref, Meta):
            return self.parameter_list
        elif isinstance(rowref, ParameterList):
            return self.process_list
        elif isinstance(rowref, Parameter):
            return self.parameter_list.on_iter_next(rowref)
        elif isinstance(rowref, ProcessList):
            return self.species_list
        elif isinstance(rowref, Process):
            return self.process_list.on_iter_next(rowref)
        elif isinstance(rowref, SpeciesList):
            return None
        elif isinstance(rowref, Species):
            return self.species_list.on_iter_next(rowref)



    #@verbose
    def on_iter_children(self, rowref):
        if rowref is None:
            return self.lattice_list
        elif isinstance(rowref, LatticeList):
            return self.lattice_list[0]
        elif isinstance(rowref, Meta):
            return None
        elif isinstance(rowref, ParameterList):
            return self.parameter_list[0]
        elif isinstance(rowref, ProcessList):
            return self.process_list[0]
        elif isinstance(rowref, SpeciesList):
            return self.species_list[0]

    #@verbose
    def on_iter_has_child(self, rowref):
        if rowref is None:
             return True
        elif isinstance(rowref, LatticeList):
            return self.lattice_list.has_elem()
        elif isinstance(rowref, Lattice):
            return False
        elif isinstance(rowref, Meta):
            return False
        elif isinstance(rowref, ParameterList):
            return self.parameter_list.has_elem()
        elif isinstance(rowref, Parameter):
            return False
        elif isinstance(rowref, ProcessList):
            return self.process_list.has_elem()
        elif isinstance(rowref, Process):
            return False
        elif isinstance(rowref, SpeciesList):
            return self.species_list.has_elem()
        elif isinstance(rowref, Species):
            return False
        else:
            raise TypeError

    #@verbose
    def on_iter_n_children(self, rowref):
        if rowref is None:
            return 6
        elif isinstance(rowref, LatticeList):
            return len(self.lattice_list)
        elif isinstance(rowref, Lattice):
            return 0
        elif isinstance(rowref, Meta):
            return 0
        elif isinstance(rowref, ParameterList):
            return len(self.parameter_list)
        elif isinstance(rowref, Parameter):
            return 0
        elif isinstance(rowref, ProcessList):
            return len(self.process_list)
        elif isinstance(rowref, Process):
            return 0
        elif isinstance(rowref, SpeciesList):
            return len(self.species_list)
        elif isinstance(rowref, Species):
            return 0
        else:
            raise TypeError


    #@verbose
    def on_iter_nth_child(self, parent, n):
        if not parent:
            if n == 0 :
                return self.lattice_list
            elif n == 1 :
                return self.meta
            elif n == 2 :
                return self.parameter_list
            elif n == 3 :
                return self.process_list
            elif n == 4 :
                return self.species_list
        elif isinstance(parent,LatticeList):
            return self.lattice_list[n]
        elif isinstance(parent,Meta):
            return None
        elif isinstance(parent, ParameterList):
            return self.parameter_list[n]
        elif isinstance(parent, ProcessList):
            return self.process_list[n]
        elif isinstance(parent,SpeciesList):
            return self.species_list[n]
        else:
            raise TypeError

    #@verbose
    def on_iter_parent(self, rowref):
        if rowref is None:
            return None
        elif isinstance(rowref, LatticeList):
            return None
        elif isinstance(rowref, Lattice):
            return self.lattice_list
        elif isinstance(rowref, Meta):
            return None
        elif isinstance(rowref, ParameterList):
            return None
        elif isinstance(rowref, Parameter):
            return self.parameter_list
        elif isinstance(rowref, ProcessList):
            return None
        elif isinstance(rowref, Process):
            return self.process_list
        elif isinstance(rowref, SpeciesList):
            return None
        elif isinstance(rowref, Species):
            return self.species_list
        else:
            raise TypeError

    def has_meta(self):
        """Transitional method, to comply with devel style GUI
        """
        return self.meta.set()


    def export_source(self, dir=''):
        if not dir:
            dir = SRCDIR
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

        # create new files
        shutil.copy(APP_ABS_PATH + '/libkmc.f90', dir)
        shutil.copy(APP_ABS_PATH + '/kind_values.f90', dir)

        lattice_source = open(APP_ABS_PATH + '/lattice_template.f90').read()
        lattice = self.lattices[0]
        # more processing steps ...
        # SPECIES DEFINITION
        if not self.species:
            print('No species defined, yet, cannot complete source')
            return
        species_definition = "integer(kind=iint), public, parameter :: &\n "
        for species in self.species[:-1]:
            species_definition += '    %(species)s =  %(id)s, &\n' % {'species':species.name, 'id':species.id}
        species_definition += '     %(species)s = %(id)s\n' % {'species':self.species[-1].species, 'id':self.species[-1].id}
        # UNIT VECTOR DEFINITION
        unit_vector_definition = 'integer(kind=iint), dimension(2,2) ::  lattice_%(name)s_matrix = reshape((/%(x)s,0,0,%(y)s/),(/2,2/))' % {'x':lattice['unit_cell_size'][0], 'y':lattice['unit_cell_size'][1],'name':lattice['name']}
        # LOOKUP TABLE INITIALIZATION
        indexes = [ x['index'] for x in lattice['sites'] ]
        lookup_table_init = 'integer(kind=iint), dimension(0:%(x)s, 0:%(y)s) :: lookup_%(lattice)s2nr\n' % {'x':lattice['unit_cell_size'][0]-1,'y':lattice['unit_cell_size'][1]-1,'lattice':lattice['name']}
        lookup_table_init += 'type(tuple), dimension(%(min)s:%(max)s) :: lookup_nr2%(lattice)s\n' % {'min':min(indexes), 'max':max(indexes), 'lattice':lattice['name']}

        # LOOKUP TABLE DEFINITION
        lookup_table_definition = ''
        lookup_table_definition += '! Fill lookup table nr2%(name)s\n' % {'name':lattice['name'] }
        for site in lattice['sites']:
            lookup_table_definition += '    lookup_nr2%(name)s(%(index)s)%%t = (/%(x)s,%(y)s/)\n' % {'name': lattice['name'],
                                                                                                'x':site['coord'][0],
                                                                                                'y':site['coord'][1],
                                                                                                'index':site['index']}
        lookup_table_definition += '\n\n    ! Fill lookup table %(name)s2nr\n' % {'name':lattice['name'] }
        for site in lattice['sites']:
            lookup_table_definition += '    lookup_%(name)s2nr(%(x)s, %(y)s) = %(index)s\n'  % {'name': lattice['name'],
                                                                                                'x':site['coord'][0],
                                                                                                'y':site['coord'][1],
                                                                                                'index':site['index']}


        #LATTICE MAPPINGS


        lattice_source = lattice_source % {'lattice_name': lattice['name'],
            'species_definition':species_definition,
            'lookup_table_init':lookup_table_init,
            'lookup_table_definition':lookup_table_definition,
            'unit_vector_definition':unit_vector_definition,
            'sites_per_cell':max(indexes)-min(indexes)+1}

        lattice_mod_file = open(dir + '/lattice.f90','w')
        lattice_mod_file.write(lattice_source)
        lattice_mod_file.close()
        # generate process list source via existing code
        proclist_xml = open(dir + '/process_list.xml','w')
        pretty_xml = prettify_xml(self.export_process_list_xml())
        proclist_xml.write(pretty_xml)
        print(pretty_xml)
        proclist_xml.close()
        class Options(): pass
        options = Options()
        options.xml_filename = proclist_xml.name
        options.dtd_filename = APP_ABS_PATH + '/process_list.dtd'
        options.force_overwrite = True
        options.proclist_filename = SRCDIR + '/proclist.f90'

        ProcListWriter(options)



        # return directory name
        return dir


    def lattice_module_source(self):
        pass



    def import_xml(self, filename):
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
                        site_elem = Site(index=index, name=name, coord=coord)
                        lattice_elem.add_site(site_elem)
                    self.lattice_list.append(lattice_elem)
            elif child.tag == 'meta':
                for attrib in ['author','email', 'debug','model_name','model_dimension']:
                    if child.attrib.has_key(attrib):
                        self.meta.add({attrib:child.attrib[attrib]})
            elif child.tag == 'parameter_list':
                for parameter in child:
                    name = parameter.attrib['name']
                    type = parameter.attrib['type']
                    value = parameter.attrib['value']
                    parameter_elem = Parameter(name=name,type=type,value=value)
                    self.parameter_list.append(parameter_elem)
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
                            condition_action = ConditionAction(species=species, coord=coord)
                            if sub.tag == 'action':
                                process_elem.add_action(condition_action)
                            elif sub.tag == 'condition':
                                process_elem.add_condition(condition_action)
                    self.process_list.append(process_elem)
            elif child.tag == 'species_list':
                for species in child:
                    name = species.attrib['name']
                    id = species.attrib['id']
                    color = species.attrib['color']
                    species_elem = Species(name=name, id=id, color=color)
                    self.species_list.append(species_elem)


    def __repr__(self):
        out = ''
        out += "\nMETA"
        out += str(self.meta)
        out += "\nLATTICES"
        out += str(self.lattice_list)
        out += "\nPARAMETERS"
        out += str(self.parameter_list)
        out += "\nPROCESSES"
        out += str(self.process_list)
        out += "\nSPECIES"
        out += str(self.species_list)
        return out

    def export_process_list_xml(self):
        """Ok, this is basically a function dealing with 'legacy' code. Since the
        module writing the process list has been tested before but is rather complex
        I refrain from rewriting this and instead generate an XML file that fits the old program
        """
        root = ET.Element('kmc')
        lattice = self.lattices[0]
        # extract meta information
        meta = ET.SubElement(root,'meta')
        meta.set('name',self.meta['model_name'])
        meta.set('dimension',self.meta['model_dimension'])
        meta.set('lattice_module','')
        # extract site_type information
        site_type_list = ET.SubElement(root,'site_type_list')
        recorded_types = []
        # extract species information
        species_list = ET.SubElement(root,'species_list')
        for species in self.species:
            species_elem = ET.SubElement(species_list, 'species')
            species_elem.set('name',species['species'])
            species_elem.set('id',species['id'])

        # extract process list
        process_list = ET.SubElement(root, 'process_list')
        process_list.set('lattice',lattice['name'])
        for process in self.processes:
            process_elem = ET.SubElement(process_list,'process')
            process_elem.set('name',process['name'])
            condition_list = ET.SubElement(process_elem, 'condition_list')
            site_index = 1
            for condition in process['conditions']:
                coord = condition[1][0]*lattice['unit_cell_size'][0] + condition[1][2], condition[1][1]*lattice['unit_cell_size'][1] + condition[1][3]
                local_coord = [ x % y for (x,y) in zip(coord, lattice['unit_cell_size']) ]
                coord = ' '.join([ str(x) for x in coord ])
                type = '_'.join([ str(x) for x in local_coord ])
                species = condition[0]
                condition_elem = ET.SubElement(condition_list,'condition')
                condition_elem.set('site','site_' + str(site_index))
                site_index += 1
                condition_elem.set('type', type)
                condition_elem.set('species', species)
                condition_elem.set('coordinate', coord)
                # Also add to site type list if necessary
                if type not in recorded_types:
                    site_type_elem = ET.SubElement(site_type_list,'type')
                    site_type_elem.set('name',type)
                    recorded_types.append(type)
            action_elem = ET.SubElement(process_elem,'action')
            for action in process['actions']:
                action_coord = action[1][0]*lattice['unit_cell_size'][0] + action[1][2], action[1][1]*lattice['unit_cell_size'][1] + action[1][3]
                action_coord = ' '.join([ str(x) for x in action_coord ])
                corresp_condition = filter(lambda x:x.attrib['coordinate'] == action_coord, condition_list.getchildren())[0]
                site_index = corresp_condition.attrib['site']
                new_species = action[0]
                replacement_elem = ET.SubElement(action_elem,'replacement')
                replacement_elem.set('site', site_index)
                replacement_elem.set('new_species', new_species)

        return root

    def check_dependencies(self):
        pass
        # check if all  lattice sites are unique
        # check if all lattice names are unique
        # check if all parameter names are unique
        # check if all process names are unique
        # check if all processes have at least one condition
        # check if all processes have at least one action
        # check if all species have a unique name
        # check if all species have a unique id
        # check if all species used in condition_action are defined
        # check if all sites used in processes are defined: actions, conditions, center_site

    def export_xml(self, filename):
        # build XML Tree
        root = ET.Element('kmc')
        meta = ET.SubElement(root,'meta')
        print(self.meta)
        for key in self.meta:
            meta.set(key,str(self.meta[key]))
        species_list = ET.SubElement(root,'species_list')
        for species in self.species_list.data:
            species_elem = ET.SubElement(species_list,'species')
            species_elem.set('name',species.name)
            species_elem.set('color',species.color)
            species_elem.set('id',str(species.id))
        parameter_list = ET.SubElement(root,'parameter_list')
        for parameter in self.parameter_list.data:
            parameter_elem = ET.SubElement(parameter_list, 'parameter')
            parameter_elem.set('name', parameter.name)
            parameter_elem.set('type', parameter.type)
            parameter_elem.set('value', parameter.value)
        lattice_list = ET.SubElement(root, 'lattice_list')
        for lattice in self.lattice_list.data:
            lattice_elem = ET.SubElement(lattice_list,'lattice')
            lattice_elem.set('unit_cell_size', str(lattice.unit_cell_size)[1 :-1].replace(',',''))
            lattice_elem.set('name', lattice.name)
            for site in lattice.sites:
                site_elem = ET.SubElement(lattice_elem, 'site')
                site_elem.set('index',str(site.index))
                site_elem.set('type',site.name)
                site_elem.set('coord',str(site.coord)[1 :-1].replace(',',''))
        process_list = ET.SubElement(root, 'process_list')
        for process in self.process_list.data:
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
        #Write Out XML File
        tree = ET.ElementTree(root)
        outfile = open(filename,'w')
        outfile.write(prettify_xml(root))
        outfile.write('<!-- This is an automatically generated XML file, representing a kMC model ' + \
                        'please do not change this unless you know what you are doing -->\n')
        outfile.close()

    def compile():
        """"Should figure out a locally installed fortran compiler and compiler exported
        source code
        TODO
        """
        pass

    def export_control_script():
        """Export a standard python export script useful to run and control a kmc model library
        TODO
        """
        pass


class MainWindow():
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.window = self.wtree.get_widget('wndMain')
        self.statbar = self.wtree.get_widget('stb_process_editor')
        self.da_widget = self.wtree.get_widget('dwLattice')
        self.keywords = ['exp','sin','cos','sqrt','log']
        self.kmc_model = KMC_Model()
        dic = {'on_btnAddLattice_clicked' : self.new_lattice ,
                'on_btnMainQuit_clicked' : self.close,
                'destroy' : self.close,
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
        self.statbar.push(1,'Add a new lattice first.')
        self.lattice_ready = False


        #setup overview tree
        self.treeview = self.wtree.get_widget('overviewtree')
        self.treeview.connect('row-activated', self.treeitem_clicked)
        self.tvcolumn = gtk.TreeViewColumn('Project Data')
        self.cell = gtk.CellRendererText()
        self.cell.set_property('editable', True)
        self.cell.connect('edited',self.treeitem_edited)
        self.tvcolumn.pack_start(self.cell, expand=True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.append_column(self.tvcolumn)
        self.treeview.set_model(self.kmc_model)
        self.window.show()



    def import_xml(self, *args):
        if self.kmc_model.save_changes_view.unsaved_changes:
            dialog_save_changes = DialogSaveChanges(self)
            response = dialog_save_changes.run()
            if response == gtk.RESPONSE_CANCEL:
                return
        self.kmc_model = KMC_Model()
        self.treeview.set_model(self.kmc_model)
        self.new_process = Process()
        self.kmc_model.import_xml(XMLFILE)
        self.kmc_model.save_changes_view.unsaved_changes = False
        self.treeview.expand_all()
        self.statbar.push(1,'KMC project loaded')



    def export_xml(self, *args):
        if self.kmc_model.save_changes_view.unsaved_changes:
            self.kmc_model.export_xml(XMLFILE)
            self.kmc_model.save_changes_view.unsaved_changes = False
            self.statbar.push(1,'KMC project saved')
        else:
            self.statbar.push(1,'No changes to save')
            


    def export_source(self, widget):
        print(kmc_model.export_source())
        self.statbar.push(1,'Exported FORTRAN source code!')

    def export_program(self, widget):
        self.statbar.push(1,'Not implemented yet!')

    def display_help(self, widget):
        self.statbar.push(1,'Not implemented yet!')
        print("META: ", self.meta)
        print("LATTICES: ", self.lattices)
        print("SPECIES: ", self.species)
        print("PARAMETERS: ", self.parameters)
        print("PROCESSES: ", self.processes)

    def treeitem_clicked(self, widget, row,col):
        item = self.kmc_model.on_get_iter(row)

        if isinstance(item, Meta):
            print("You clicked on Meta")
        elif isinstance(item, Parameter):
            print("we have a parameter")
        elif isinstance(item, Species):
            print("we have a species")
        elif isinstance(item, Lattice):
            print("it's a lattice")
        elif isinstance(item, Process):
            print("and finally we have a process")

    def treeitem_edited(self, cell, path, new_text):
        path = tuple([int(x) for x in path.split(':')])
        item = self.kmc_model.on_get_iter(path)
        print(path)
        print(type(path))
        print(item)
        if isinstance(item, Process):
            item.name = new_text
            self.kmc_model.notifier('changed')

    def create_process(self, widget):
        self.new_process = Process()

        if len(self.kmc_model.lattice_list) < 1 :
            self.statbar.push(1,'No lattice defined!')
            return
        dlg_process_name = DialogProcessName()
        result, data = dlg_process_name.run()
        if result == gtk.RESPONSE_CANCEL:
            return
        else:
            self.new_process.name = data['process_name']

        self.draw_lattices()
        self.lattice_ready = True
        self.statbar.push(1,'Left-click sites for condition, right-click site for changes, click here if finished.')

    def dw_lattice_configure(self, widget, event):
        self.process_editor_width, self.process_editor_height = widget.get_allocation()[2], widget.get_allocation()[3]
        self.pixmap = gtk.gdk.Pixmap(widget.window, self.process_editor_width, self.process_editor_height)
        self.pixmap.draw_rectangle(widget.get_style().white_gc, True, 0, 0, self.process_editor_width, self.process_editor_height)
        return True

    def dw_lattice_expose(self, widget, event):
        site_x, site_y, self.process_editor_width, self.process_editor_height = widget.get_allocation()
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL], self.pixmap, 0, site_y, 0, site_y, self.process_editor_width, self.process_editor_height)

    def dw_lattice_clicked(self, widget, event):
        if self.lattice_ready:
            width, height = self.process_editor_width, self.process_editor_height
            lattice = self.kmc_model.lattice_list[0]
            unit_x = lattice.unit_cell_size[0]
            unit_y = lattice.unit_cell_size[1]
            zoom = 3
            for i in range(zoom+1):
                for j in range(3):
                    for x in range(unit_x):
                        for y in range(unit_y):
                            for site in lattice.sites:
                                if site.coord[0] == x and site.coord[1] == y:
                                    center = []
                                    coordx = int((i+ float(x)/unit_x)*width/zoom)
                                    coordy = int(height - (j+ float(y)/unit_y)*height/zoom)
                                    if (coordx - event.x)**2 + (coordy - event.y)**2 < 30 :
                                        self.species_menu = gtk.Menu()
                                        if event.button == 3 :
                                            menu_header = gtk.MenuItem('Select action')
                                            data = 'action', i, j, x, y
                                        elif event.button == 1 :
                                            menu_header = gtk.MenuItem('Select condition')
                                            data = 'condition', i, j, x, y

                                        menu_header.set_sensitive(False)
                                        self.species_menu.append(menu_header)
                                        self.species_menu.append(gtk.SeparatorMenuItem())
                                        for species in self.kmc_model.species_list.data:
                                            menu_item = gtk.MenuItem(species.name)
                                            self.species_menu.append(menu_item)
                                            menu_item.connect("activate", self.add_condition, (species, list(data)))
                                        self.species_menu.show_all()
                                        if event.button == 1 :
                                            self.species_menu.popup(None, None, None, event.button, event.time)
                                        elif event.button == 3 and filter(lambda cond: cond.coord == [i, j, x, y], self.new_process.condition_list):
                                            self.species_menu.popup(None, None, None, event.button, event.time)
                                    else:
                                        pass
                                        #Catch events outside dots


    def add_condition(self, event, data):

        #Test if point is condition or action
        is_condition = data[1][0] == 'condition'

        # weed out data
        data = [ data[0].name, data[1][1 :] ]
        # new_ca stands for 'new condition/action'
        new_ca = ConditionAction(coord=data[1], species=data[0])
        # if this is the first condition, make it the center site
        # all other sites will be measure relative to this site
        if not self.new_process.condition_list:
            self.new_process.center_site = new_ca.coord

        # Save in appropriate slot
        if is_condition :
            for elem in self.new_process.condition_list:
                if elem.coord == new_ca.coord:
                    self.new_process.condition_list.remove(elem)
            self.new_process.condition_list.append(new_ca)
        else:
            for elem in self.new_process.action_list:
                if elem.coord == new_ca.coord:
                    self.new_process.action_list.remove(elem)
            self.new_process.action_list.append(new_ca)

        self.draw_lattices()



    def draw_lattices(self,blank=False):
        gc = self.da_widget.get_style().black_gc
        lattice = self.kmc_model.lattice_list[0]
        width, height = self.process_editor_width, self.process_editor_height
        self.pixmap.draw_rectangle(self.da_widget.get_style().white_gc, True, 0, 0, width, height)
        if blank:
            return
        unit_x = lattice.unit_cell_size[0]
        unit_y = lattice.unit_cell_size[1]
        zoom = 3
        for sup_i in range(zoom+1):
            for i in range(-1,1):
                self.pixmap.draw_line(gc, 0, i+sup_i*height/zoom, width, i+(sup_i*height/zoom))
                self.pixmap.draw_line(gc, i+sup_i*width/zoom, 0, i+(sup_i*width/zoom), height)
        for sup_i in range(zoom+1):
            for sup_j in range(3):
                for x in range(unit_x):
                    for y in range(unit_y):
                        for site in lattice.sites:
                            if site.coord[0] == x and site.coord[1] == y:
                                center = []
                                coordx = int((sup_i+ float(x)/unit_x)*width/zoom )
                                coordy = int(height - (sup_j+ float(y)/unit_y)*height/zoom )
                                center = [ coordx, coordy ]
                                self.pixmap.draw_arc(gc, True, center[0]-5, center[1]-5, 10, 10, 0, 64*360)
                                for entry in self.new_process.condition_list:
                                    if entry.coord == [sup_i, sup_j, x, y ]:
                                        color = filter((lambda x : x.name == entry.species), self.kmc_model.species_list.data)[0].color
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse(color))
                                        self.pixmap.draw_arc(gc, True, center[0]-15, center[1]-15, 30, 30, 64*90, 64*360)
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
                                        self.pixmap.draw_arc(gc, False, center[0]-15, center[1]-15, 30, 30, 64*90, 64*360)
                                for entry in self.new_process.action_list:
                                    if entry.coord == [sup_i, sup_j, x, y ]:
                                        color = filter((lambda x : x.name == entry.species), self.kmc_model.species_list.data)[0].color
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse(color))
                                        self.pixmap.draw_arc(gc, True, center[0]-10, center[1]-10, 20, 20, 64*270, 64*360)
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
                                        self.pixmap.draw_arc(gc, False, center[0]-10, center[1]-10, 20, 20, 64*270, 64*360)
                                gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
        self.da_widget.queue_draw_area(0, 0, width, height)

    def add_meta_information(self):
        dlg_meta_info = DialogMetaInformation()
        result, data = dlg_meta_info.run()
        if result == gtk.RESPONSE_OK:
            self.kmc_model.meta.add(data)
            self.statbar.push(1,'Meta information added')
        else:
            self.statbar.push(1,'Could not complete meta information')

    def new_lattice(self, widget):
        if not self.kmc_model.has_meta():
            self.add_meta_information()
        lattice_editor = UnitCellEditor(self.add_lattice)

    def add_species(self, widget):
        if not self.kmc_model.species_list.has_elem():
            empty_species = Species(color='#fff',name='empty',id=0)
            self.kmc_model.species_list.append(empty_species)
        if not self.kmc_model.meta:
            self.add_meta_information()
        dialog_new_species = DialogNewSpecies(len(self.kmc_model.species_list))
        result, data = dialog_new_species.run()
        if result == gtk.RESPONSE_OK:
            if not data['color']:
                self.statbar.push(1,'Species not added because no color was specified!')
            elif data not in self.kmc_model.species_list:
                new_species = Species(name=data['name'],color=data['color'],id=data['id'])
                self.kmc_model.species_list.append(new_species)
                self.statbar.push(1,'Added species "'+ data['name'] + '"')
                print(data)

    def add_parameter(self, widget):
        parameter_editor = DialogAddParameter()
        result, data = parameter_editor.run()
        if result == gtk.RESPONSE_OK:
            name = data['name']
            type = data['type']
            value = data['value']
            parameter = Parameter(name=name, type=type, value=value)
            self.kmc_model.parameter_list.append(parameter)


    def add_lattice(self, data):
        #validate new lattice
        if not data.cell_finished:
            self.statbar.push(1,'Could not add lattice: cell not defined!')
            return
        if not hasattr(data.lattice, 'name') or not data.lattice.name:
            self.statbar.push(1,'Could not add lattice: lattice name not specified!')
            return
        if not hasattr(data.lattice, 'sites') or not data.lattice.sites:
            self.statbar.push(1,'Could not add lattice: no sites specified!')
            return
        if not hasattr(data.lattice, 'unit_cell_size') or not data.lattice.unit_cell_size:
            self.statbar.push(1,'Could not add lattice: no unit cell size specified!')
            return
        # if validated, add lattice
        self.kmc_model.lattice_list.append(data.lattice)
        self.statbar.push(1,'Added lattice "' + data.lattice.name + '"')




    # Serves to finish process input
    def statbar_clicked(self, widget, event):
        if self.new_process:
            dlg_rate_constant = DialogRateConstant(self.kmc_model.parameter_list.data, self.keywords)
            result, data = dlg_rate_constant.run()
            #Check if process is sound
            if not self.new_process.name :
                self.statbar.push(1,'New process has no name')
                return
            elif not self.new_process.center_site:
                self.statbar.push(1,'No sites defined!')
                return
            elif not self.new_process.condition_list:
                self.statbar.push(1,'New process has no conditions')
                return
            elif not self.new_process.action_list:
                self.statbar.push(1,'New process has no actions')

            if result == gtk.RESPONSE_OK:
                self.new_process.rate_constant = data['rate_constant']
                center_site = self.new_process.center_site
                for condition in self.new_process.condition_list + self.new_process.action_list :
                    condition.coord = [ x - y for (x, y) in zip(condition.coord, center_site) ]
                # Re-center center site: it doesnt make sense, to have the enter site in another unit
                # cell than (0, 0)
                self.new_process.center_site[0:1] = [0,0]
                self.kmc_model.process_list.append(self.new_process)
                self.statbar.push(1,'New process "'+ self.new_process.name + '" added')
                print(self.new_process)
                del(self.new_process)
                self.draw_lattices(blank=True)
                self.lattice_ready = False


    def close(self, *args):
        if self.kmc_model.save_changes_view.unsaved_changes:
            dialog_save_changes = DialogSaveChanges(self)
            response = dialog_save_changes.run()
            if response == gtk.RESPONSE_OK:
                self.window.destroy()
                gtk.main_quit()
        else:
            self.window.destroy()
            gtk.main_quit()


class UnitCellEditor():
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

        self.lattice = Lattice()

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
                self.lattice.unit_cell_size = data['x'], data['y']
                self.lattice.name = data['name']
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
                if data['name'] == 'remove':
                    for site in self.lattice.sites:
                        if site.coord[0] == data['coord'][0] and site.coord[1] == data['coord'][1]:
                            self.lattice.remove_site(site)
                else:
                    for site in self.lattice.sites:
                        if site.coord[0] == data['coord'][0] and site.coord[1] == data['coord'][1]:
                            self.lattice.remove_site(site)
                    new_site = Site(name=data['name'], coord=data['coord'], index=data['index'])
                    self.lattice.add_site(new_site)
                # Redraw dots
                for i in range(self.lattice.unit_cell_size[0]+1):
                    for j in range(self.lattice.unit_cell_size[1]+1):
                        center = []
                        center.append(self.corner1[0] + i*(self.corner2[0]-self.corner1[0])/self.lattice.unit_cell_size[0] - 5)
                        center.append(self.corner2[1] - j*(self.corner2[1]-self.corner1[1])/self.lattice.unit_cell_size[1] - 5)
                        for site in self.lattice.sites:
                            if (i % self.lattice.unit_cell_size[0]) == site.coord[0] and (j % self.lattice.unit_cell_size[1]) == site.coord[1]:
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






class DialogSaveChanges():
    def __init__(self,main_window):
        self.main_window = main_window
        self.dialog = gtk.MessageDialog(
            parent=self.main_window.window,
            type=gtk.DIALOG_MODAL,
            buttons = gtk.BUTTONS_NONE,
            message_format='Save unsaved changes?'
        )
        self.dialog.add_button(gtk.STOCK_DISCARD, gtk.RESPONSE_NO)
        self.dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.dialog.add_button(gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()
        if response == gtk.RESPONSE_NO:
            return gtk.RESPONSE_OK
        elif response == gtk.RESPONSE_CANCEL:
            return gtk.RESPONSE_CANCEL
        elif response == gtk.RESPONSE_OK:
            self.main_window.export_xml()
            return gtk.RESPONSE_OK

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
            self.coord_x = int((event.x-lattice_dialog.corner1[0])/(lattice_dialog.corner2[0]-lattice_dialog.corner1[0])*lattice_dialog.lattice.unit_cell_size[0])
            self.coord_y = lattice_dialog.lattice.unit_cell_size[1] - int((event.y-lattice_dialog.corner1[1])/(lattice_dialog.corner2[1]-lattice_dialog.corner1[1])*lattice_dialog.lattice.unit_cell_size[1]) - 1


    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog_site.show()
        # define field and set defaults
        name_field = self.wtree.get_widget('defineSite_type')
        name_field.set_text('default')
        index_field = self.wtree.get_widget('defineSite_index')
        index_adjustment = gtk.Adjustment(value=len(self.lattice_dialog.lattice.sites), lower=0, upper=1000, step_incr=1, page_incr=4, page_size=0)
        index_field.set_adjustment(index_adjustment)
        index_field.set_value(len(self.lattice_dialog.lattice.sites))
        index_field.set_sensitive(False)
        site_x = self.wtree.get_widget('spb_site_x')
        x_adjustment = gtk.Adjustment(value=0, lower=0, upper=self.lattice_dialog.lattice.unit_cell_size[0]-1, step_incr=1, page_incr=4, page_size=0)
        site_x.set_adjustment(x_adjustment)
        site_x.set_value(self.coord_x)
        site_y = self.wtree.get_widget('spb_site_y')
        y_adjustment = gtk.Adjustment(value=0, lower=0, upper=self.lattice_dialog.lattice.unit_cell_size[1]-1, step_incr=1, page_incr=4, page_size=0)
        site_y.set_adjustment(y_adjustment)
        y_adjustment.set_value(self.coord_y)
        #run dialog
        result = self.dialog_site.run()
        # extract fields
        data = {}
        data['coord'] = site_x.get_value_as_int(), site_y.get_value_as_int()
        data['index'] = index_field.get_value_as_int()
        data['name'] = name_field.get_text()
        # close
        self.dialog_site.destroy()
        return result, data

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
    def __init__(self, nr_of_species):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('dlgNewSpecies')
        dic = {'on_btnSelectColor_clicked' : self.open_dlg_color_selection,}
        self.wtree.signal_autoconnect(dic)
        self.nr_of_species = nr_of_species
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
        species_id = self.wtree.get_widget('species_id')
        species_id.set_text(str(self.nr_of_species))
        species_id.set_sensitive(False)
        #run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['name'] = species.get_text()
        data['id'] = species_id.get_text()
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
            liststore.append([parameter.name])
        for keyword in self.keywords:
            liststore.append([keyword])
        #run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['rate_constant'] = rate_constant.get_text()
        self.dialog.destroy()
        return result, data

class DialogMetaInformation():
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('meta_info')

    def run(self):
        self.dialog.show()
        # define field
        author = self.wtree.get_widget('metaAuthor')
        email = self.wtree.get_widget('metaEmail')
        model_name = self.wtree.get_widget('metaModelName')
        model_dimension = self.wtree.get_widget('metaDimension')
        model_dimension.set_sensitive(False)
        debug_level = self.wtree.get_widget('metaDebug')
        # run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['author'] = author.get_text()
        data['email'] = email.get_text()
        data['model_name'] = model_name.get_text()
        data['model_dimension'] = str(model_dimension.get_value_as_int())
        data['debug'] = debug_level.get_value_as_int()
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
        data['color'] = color.get_current_color().to_string()
        return result, data

    def close(self):
        self.dialog.destroy()
        return True


def validate_xml(xml_filename, dtd_filename):
    """Validate a given XML file with a given external DTD.
       If the XML file is not valid, an exception will be 
         printed with an error message.
    """
    dtd = et.DTD(dtd_filename)
    root = et.parse(xml_filename)
    dtd.assertValid(root)

class SimpleList(gtk.GenericTreeModel):
    def __init__(self, callback, node_index):
        gtk.GenericTreeModel.__init__(self)
        self.data = []
        self.callback = callback
        self.node_index = node_index
        self.column_type = (str, )

    #@verbose
    def __getitem__(self, i):
        return self.data[i]

    def sort(self):
        self.data.sort()

    #@verbose
    def append(self, elem):
        if elem not in self.data:
            self.data.append(elem)
            full_path = (self.node_index, self.data.index(elem))
            self.callback('row-inserted', full_path)
        self.data.sort()

    def __len__(self):
        return len(self.data)


    def has_elem(self):
        return len(self.data) > 0

    #@verbose
    def on_get_flags(self):
        return 0

    #@verbose
    def on_get_n_columns(self):
        return len(self.column_type)

    #@verbose
    def on_get_column_type(self, n):
        return self.column_type[n]

    #@verbose
    def on_get_iter(self, path):
        return self.data[path[0]]

    #@verbose
    def on_get_path(self, rowref):
        return self.data.index(rowref)

    #@verbose
    def on_iter_next(self, rowref):
        try:
            i = self.data.index(rowref) + 1
            return self.data[i]
        except IndexError:
            return None

    #@verbose
    def on_iter_children(self, parent):
        return self.data[0]

    #@verbose
    def on_iter_has_child(self, rowref):
        return False

    #@verbose
    def on_iter_n_children(self, rowref):
        return len(self.data)

    #@verbose
    def on_iter_nth_child(self, parent, n):
        try:
            return self.data[n]
        except IndexError:
            return None

    #@verbose
    def on_iter_parent(self, child):
        return None


class Lattice(Attributes):
    attributes = ['name','unit_cell_size','sites']
    def __init__(self, name='', unit_cell_size=[]):
        self.name = name
        self.unit_cell_size = unit_cell_size
        self.sites = []

    def __repr__(self):
        return '    %s %s' % (self.name, self.unit_cell_size)

    def __cmp__(self, other):
        if self.name > other.name :
            return 1
        elif self.name == other.name :
            return 0
        else:
            return -1

    def set_name(self, name):
        self.name = name

    def set_unit_cell_size(self, unit_cell_size):
        self.unit_cell_size = unit_cell_size


    def add_site(self, site):
        self.sites.append(site)

    def remove_site(self, site):
        if site in self.sites:
            self.sites.remove(site)

class LatticeList(SimpleList):
    def __init__(self, callback, node_index):
        SimpleList.__init__(self, callback, node_index)
        self.lattices = self.data

    def __repr__(self):
        out = ''
        for lattice in self.lattices:
            out += str(lattice) + '\n'
        return out

    def on_get_value(self, rowref, column):
        i = self.lattices.index(rowref)
        return self.lattices[i].name


class Meta(Attributes):
    attributes = ['author','debug','email','model_name','model_dimension']
    def __init__(self, callback, node_index):
        self.author = ''
        self.debug = 0
        self.email = ''
        self.model_name = ''
        self.model_dimension = 0
        self.__dict__['callback'] = callback
        self.__dict__['node_index'] = node_index

    def __repr__(self):
        return '    %s %s %s %s\n' % (self.model_name, self.model_dimension, self.author, self.email)

    def add(self, data):
        if type(data) != dict:
            raise TypeError
        if data.has_key('author'):
            self.author = data['author']
        if data.has_key('email'):
            self.email = data['email']
        if data.has_key('model_name'):
            self.model_name = data['model_name']
        if data.has_key('model_dimension'):
            self.model_dimension = data['model_dimension']
        if data.has_key('debug'):
            self.debug = data['debug']

    def __getitem__(self, key):
        return eval('self.'+key)

    def __iter__(self):
        dict = {}
        for attribute in self.attributes:
            dict[attribute] = eval('self.'+attribute)
        return dict.__iter__()


    def set(self):
        if self.author != '' and self.email != '' and self.model_name != '' and self.model_dimension != 0 :
            return True
        else:
            return False

class Parameter(Attributes):
    attributes = ['name','type','value']
    def __init__(self, name='', type='', value=''):
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self):
        return '%s %s %s' % (self.name, self.value, self.type)

    def __cmp__(self, other):
        if self.name > other.name :
            return 1
        elif self.name == other.name :
            return 0
        else:
            return -1

class ParameterList(SimpleList):
    def __init__(self, callback, node_index):
        SimpleList.__init__(self, callback, node_index)
        self.parameters = self.data

    def on_get_value(self, rowref, column):
        return rowref.name


    def __repr__(self):
        outstr = ''
        for parameter in self.parameters:
            outstr +=  parameter.__repr__() + '\n'
        return outstr

class Process(Attributes):
    attributes = ['name','center_site', 'rate_constant','condition_list','action_list']
    def __init__(self, name='', center_site=(), rate_constant=0.):
        self.name = name
        self.center_site = center_site
        self.rate_constant = rate_constant
        self.condition_list = []
        self.action_list = []

    def __repr__(self):
        return '    %s %s' % (self.name, self.rate_constant)

    def add_action(self, action):
        self.action_list.append(action)

    def add_condition(self, condition):
        self.condition_list.append(condition)

class ProcessList(SimpleList):
    def __init__(self, callback, node_index):
        SimpleList.__init__(self, callback, node_index)
        self.processes = self.data

    def __repr__(self):
        out = ''
        for process in self.processes:
            out += process.__repr__() + '\n'
        return out

    def on_get_value(self, rowref, column):
        return rowref.name

class Species(Attributes):
    attributes = ['name','color','id']
    def __init__(self, name, color, id):
        self.name = name
        self.color = color
        self.id = id

    def __repr__(self):
        return "    %s %s %s" % (self.name, self.color, self.id)

    def __cmp__(self, other):
        if self.name > other.name :
            return 1
        elif self.name == other.name :
            return 0
        else:
            return -1

class SpeciesList(SimpleList):
    def __init__(self, callback, node_index):
        SimpleList.__init__(self, callback, node_index)
        self.species = self.data

    def on_get_value(self, rowref, column):
        return rowref.name

    def __repr__(self):
        out = ''
        for species in self.species:
            out += str(species) + '\n'
        return out

class ConditionAction(Attributes):
    attributes = ['coord','species']
    def __init__(self, coord, species):
        self.coord = coord
        self.species = species

class Site(Attributes):
    attributes = ['index','name','coord']
    def __init__(self, index, name, coord):
        self.index = index
        self.name = name
        self.coord = coord

    def __repr__(self):
        return '        %s %s %s' % (self.name, self.index, self.coord)




def prettify_xml(elem):
    rough_string = ET.tostring(elem,encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='    ')


class Notifier:
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def __call__(self, message):
        for listener in self.listeners:
            listener(message)



class SaveChangesView :
    def __init__(self ):
        self.unsaved_changes = False

    def __call__(self, message):
        if message == 'saved':
            self.unsaved_changes = False
        elif message == 'changed':
            self.unsaved_changes = True





def main():
    """Main function, called if scripts called directly
    """
    MainWindow()
    gtk.main()

if __name__ == "__main__":
    main()
