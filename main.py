#!/usr/bin/python
"""The main program of KMC Modeling On Steroid (kmos)
    a GUI program to generate kMC models
"""

import pdb
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
        elif signal == 'row-deleted':
            path = args[0]
            self.row_deleted(path)
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
            return 'Processes (%s)' % len(self.process_list.data)
        elif isinstance(rowref, Process):
            return self.process_list.on_get_value(rowref, column)
        elif isinstance(rowref, SpeciesList):
            return 'Species (%s)' % len(self.species_list.data) 
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


    #@verbose
    def export_source(self, dir=''):
        if not dir:
            dir = SRCDIR
        if not os.path.exists(dir):
            os.mkdir(dir)

        for filename in [ 'base.f90', 'kind_values_f2py.f90', 'units.f90', 'assert.ppc', 'compile_for_f2py', 'run_kmc.py']:
            # copy files
            shutil.copy(APP_ABS_PATH + '/%s' % filename, dir)

        lattice_source = open(APP_ABS_PATH + '/lattice_template.f90').read()
        lattice = self.lattice_list[0]
        # more processing steps ...
        # SPECIES DEFINITION
        if not self.species_list:
            print('No species defined, yet, cannot complete source')
            return
        species_definition = "integer(kind=iint), public, parameter :: &\n "
        for species in self.species_list.data[:-1]:
            species_definition += '    %(species)s =  %(id)s, &\n' % {'species':species.name, 'id':species.id}
        species_definition += '     %(species)s = %(id)s\n' % {'species':self.species_list.data[-1].name, 'id':self.species_list.data[-1].id}
        species_definition += 'character(len=800), dimension(%s) :: species_list\n' % len(self.species_list.data)
        species_definition += 'integer(kind=iint), parameter :: nr_of_species = %s\n' % len(self.species_list.data)
        species_definition += 'integer(kind=iint), parameter :: nr_of_lattices = %s\n' % len(self.lattice_list.data)
        species_definition += 'character(len=800), dimension(%s) :: lattice_list\n' % len(self.lattice_list.data)

        # UNIT VECTOR DEFINITION
        unit_vector_definition = 'integer(kind=iint), dimension(2,2) ::  lattice_matrix = reshape((/%(x)s,0,0,%(y)s/),(/2,2/))' % {'x':lattice.unit_cell_size[0], 'y':lattice.unit_cell_size[1],'name':lattice.name}
        # LOOKUP TABLE INITIALIZATION
        indexes = [ x.index for x in lattice.sites ]
        lookup_table_init = 'integer(kind=iint), dimension(0:%(x)s, 0:%(y)s) :: lookup_%(lattice)s2nr\n' % {'x':lattice.unit_cell_size[0]-1,'y':lattice.unit_cell_size[1]-1,'lattice':lattice.name}
        lookup_table_init += 'integer(kind=iint), dimension(%(min)s:%(max)s,2) :: lookup_nr2%(lattice)s\n' % {'min':min(indexes), 'max':max(indexes), 'lattice':lattice.name}

        # LOOKUP TABLE DEFINITION
        lookup_table_definition = ''
        lookup_table_definition += '! Fill lookup table nr2%(name)s\n' % {'name':lattice.name }
        for site in lattice.sites:
            lookup_table_definition += '    lookup_nr2%(name)s(%(index)s,:) = (/%(x)s,%(y)s/)\n' % {'name': lattice.name,
                                                                                                'x':site.coord[0],
                                                                                                'y':site.coord[1],
                                                                                                'index':site.index}
        lookup_table_definition += '\n\n    ! Fill lookup table %(name)s2nr\n' % {'name':lattice.name }
        for site in lattice.sites:
            lookup_table_definition += '    lookup_%(name)s2nr(%(x)s, %(y)s) = %(index)s\n'  % {'name': lattice.name,
                                                                                                'x':site.coord[0],
                                                                                                'y':site.coord[1],
                                                                                                'index':site.index}
        for i,species in enumerate(self.species_list.data):
            lookup_table_definition +=  '    species_list(%s) = "%s"\n' % (i+1, species.name)
        for i, lattice_name in enumerate(self.lattice_list.data):
            lookup_table_definition +=  '    lattice_list(%s) = "%s"\n' % (i+1, lattice_name.name)


        #LATTICE MAPPINGS


        lattice_source = lattice_source % {'lattice_name': lattice.name,
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
        lattice = self.lattice_list.data[0]
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
        for species in self.species_list.data:
            species_elem = ET.SubElement(species_list, 'species')
            species_elem.set('name',species.name)
            species_elem.set('id',species.id)

        # extract process list
        process_list = ET.SubElement(root, 'process_list')
        process_list.set('lattice',lattice.name)
        for process in self.process_list.data:
            process_elem = ET.SubElement(process_list,'process')
            process_elem.set('name',process.name)
            process_elem.set('rate',process.rate_constant)
            condition_list = ET.SubElement(process_elem, 'condition_list')
            center_coord = [None,None]
            center_coord[0] = process.center_site[0]*lattice.unit_cell_size[0] + process.center_site[2]
            center_coord[1] = process.center_site[1]*lattice.unit_cell_size[1] + process.center_site[3]
            for site_index, condition in enumerate(process.condition_list):
                coord = [None,None]
                coord[0] = condition.coord[0]*lattice.unit_cell_size[0] + condition.coord[2]
                coord[1] = condition.coord[1]*lattice.unit_cell_size[1] + condition.coord[3]
                local_coord = [ x % y for (x,y) in zip(coord, lattice.unit_cell_size) ]
                type = '_'.join([ str(x) for x in local_coord ])
                for i in range(2):
                    coord[i] = coord[i] - center_coord[i]
                coord = ' '.join([ str(x) for x in coord ])
                species = condition.species
                condition_elem = ET.SubElement(condition_list,'condition')
                condition_elem.set('site','site_' + str(site_index+1))
                condition_elem.set('type', type)
                condition_elem.set('species', species)
                condition_elem.set('coordinate', coord)
                # Also add to site type list if necessary
                if type not in recorded_types:
                    site_type_elem = ET.SubElement(site_type_list,'type')
                    site_type_elem.set('name',type)
                    recorded_types.append(type)
            action_elem = ET.SubElement(process_elem,'action')
            for action in process.action_list:
                action_coord = [None, None]
                action_coord[0] = action.coord[0]*lattice.unit_cell_size[0] + action.coord[2]
                action_coord[1] = action.coord[1]*lattice.unit_cell_size[1] + action.coord[3]
                for i in range(2):
                    action_coord[i] = action_coord[i] - center_coord[i]
                action_coord = ' '.join([ str(x) for x in action_coord ])
                corresp_condition = filter(lambda x:x.attrib['coordinate'] == action_coord, condition_list.getchildren())[0]
                site_index = corresp_condition.attrib['site']
                new_species = action.species
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
        self.window.set_title('New kMC Project')
        self.statbar = self.wtree.get_widget('stb_process_editor')
        self.keywords = ['exp','sin','cos','sqrt','log']
        self.kmc_model = KMC_Model()
        self.da_widget = self.wtree.get_widget('dwLattice')
        self.da_widget.props.has_tooltip = True
        self.process_editor = ProcessEditor(self.da_widget)
        dic = {
                'on_btnAddLattice_clicked' : self.new_lattice ,
                'on_btnMainQuit_clicked' : self.close,
                'destroy' : self.close,
                'on_dwLattice_configure_event' : self.process_editor.configure,
                'on_dwLattice_expose_event' : self.process_editor.expose,
                'on_dwLattice_button_press_event' : self.process_editor.dw_lattice_clicked,
                'on_dwLattice_query_tooltip' : self.process_editor.query_tooltip,
                'on_dwLattice_key_press_event' : self.on_da_key_pressed,
                'on_btnAddParameter_clicked': self.add_parameter,
                'on_btnAddSpecies_clicked' : self.add_species,
                'on_btnAddProcess_clicked' : self.create_process,
                'on_eventbox1_button_press_event' : self.statbar_clicked,
                'on_btnImportXML_clicked' : self.import_xml,
                'on_btnExportXML_clicked' : self.export_xml,
                'on_btnExportSource_clicked': self.export_source,
                'on_btnExportProgram_clicked' : self.export_program,
                'on_btnHelp_clicked' : self.display_help,
                'on_overviewtree_button_press_event' : self.overview_button_pressed,
                'on_overviewtree_key_press_event' : self.overview_key_pressed, 
                }

        self.wtree.signal_autoconnect(dic)
        self.statbar.push(1,'Add a new lattice first.')

        #setup overview tree
        self.treeview = self.wtree.get_widget('overviewtree')
        self.treeview.connect('row-activated', self.treeitem_clicked)
        self.treeview.set_enable_tree_lines(True)
        self.tvcolumn = gtk.TreeViewColumn('Project Data')
        self.cell = gtk.CellRendererText()
        self.cell.set_property('editable', True)
        self.cell.connect('edited',self.treeitem_edited)
        self.tvcolumn.pack_start(self.cell, expand=True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.append_column(self.tvcolumn)
        self.set_model(self.kmc_model)
        self.checked_out_process = (False,)



    def import_xml(self, *args):
        if self.kmc_model.save_changes_view.unsaved_changes:
            dialog_save_changes = DialogSaveChanges(self)
            response = dialog_save_changes.run()
            if response == gtk.RESPONSE_CANCEL:
                return
        self.kmc_model = KMC_Model()
        self.set_model(self.kmc_model)
        self.kmc_model.import_xml(XMLFILE)
        self.kmc_model.save_changes_view.unsaved_changes = False
        self.window.set_title(self.kmc_model.meta.model_name)
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
        print(self.kmc_model.export_source())
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
        print(widget, row, col)
        item = self.kmc_model.on_get_iter(row)

        if isinstance(item, Meta):
            dlg_meta = DialogMetaInformation()
            dlg_meta.author.set_text(self.kmc_model.meta.author)
            dlg_meta.email.set_text(self.kmc_model.meta.email)
            dlg_meta.model_name.set_text(self.kmc_model.meta.model_name)
            dlg_meta.model_dimension.set_value(float(self.kmc_model.meta.model_dimension))
            dlg_meta.debug_level.set_value(float(self.kmc_model.meta.debug))

            result, data = dlg_meta.run()
            if result == gtk.RESPONSE_OK:
                self.kmc_model.meta.add(data)
                self.statbar.push(1,'Meta information added')
                self.kmc_model.notifier('changed')
        elif isinstance(item, Parameter):
            parameter_editor = DialogAddParameter()
            parameter_editor.name_field.set_text(item.name)
            for i, row in enumerate(parameter_editor.type_field.get_model()):
                if row[0] == item.type:
                    active_type = i
            parameter_editor.type_field.set_active(active_type)
            parameter_editor.value_field.set_text(item.value)
            parameter_editor.name_field.set_sensitive(False)
            result, data = parameter_editor.run()
            if result == gtk.RESPONSE_OK:
                name = data['name']
                type = data['type']
                value = data['value']
                parameter = Parameter(name=name, type=type, value=value)
                for i, elem in enumerate(self.kmc_model.parameter_list.data):
                    if elem.name == name :
                        self.kmc_model.parameter_list[i] = parameter
        elif isinstance(item, Species):
            dlg_species = DialogNewSpecies(item.id)
            dlg_species.species_id.set_text(item.id)
            dlg_species.species_id.set_sensitive(False)
            dlg_species.species.set_text(item.name)
            dlg_species.species.set_sensitive(False)
            dlg_species.color = item.color
            result, data = dlg_species.run()
            if result == gtk.RESPONSE_OK:
                species = Species(name=data['name'],color=data['color'],id=data['id'])
                for i, elem in enumerate(self.kmc_model.species_list.data):
                    if elem.name == data['name']:
                        self.kmc_model.species_list[i] = species
        elif isinstance(item, Lattice):
            self.statbar.push(1,"Retroactive change of lattice is not supported, yet")
        elif isinstance(item, Process):
            new_process = item
            self.checked_out_process = True, self.kmc_model.process_list.data.index(item)
            self.process_editor.set_process(new_process, self.kmc_model.lattice_list.data[0])
            self.da_widget.grab_focus()
            self.statbar.push(1,'Left-click sites for condition, right-click site for actions, hit Return when finished.')

    def treeitem_edited(self, cell, path, new_text):
        path = tuple([int(x) for x in path.split(':')])
        item = self.kmc_model.on_get_iter(path)
        if isinstance(item, Process):
            item.name = new_text
            self.kmc_model.notifier('changed')

    def overview_button_pressed(self, widget, event):
        x, y = int(event.x), int(event.y)
        path, col, cellx, celly = self.treeview.get_path_at_pos(x, y)
        item = self.kmc_model.on_get_iter(path)
        if event.button == 3 :
            if isinstance(item, Process):
                context_menu = gtk.Menu()
                menu_item = gtk.MenuItem('Duplicate process')
                menu_item.connect('activate', self.duplicate_process, item)
                context_menu.append(menu_item)
                context_menu.show_all()
                context_menu.popup(None, None, None, event.button, event.time)
            
    def duplicate_process(self, event, process):
        duplicate = deepcopy(process)
        # first figure out the 'highest duplicate' made so far
        others = filter(lambda x: x.name.split('(')[0] == duplicate.name.split('(')[0], self.kmc_model.process_list.data)
        dupl_nrs = []
        for other in others:
            if other.name.endswith(')'):
                index = other.name.index('(')
                nr = int(other.name[index+1 : -1])
                dupl_nrs.append(nr)
        if dupl_nrs:
            duplicate.name = duplicate.name[:index] + "(%s)" % (max(dupl_nrs) + 1)
        else:
            duplicate.name += '(1)'
        self.kmc_model.process_list.append(duplicate)

    def overview_key_pressed(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        model, paths = (self.treeview.get_selection().get_selected_rows())
        for path in paths:
            item = self.kmc_model.on_get_iter(path)
            if key == 'Delete':
                if isinstance(item, Process):
                    self.kmc_model.process_list.data.remove(item)
                    self.kmc_model.callback('row-deleted', path)

    def create_process(self, widget):
        new_process = Process()

        self.process_editor.clear()
        self.checked_out_process = (False, )
        if len(self.kmc_model.lattice_list) < 1 :
            self.statbar.push(1,'No lattice defined!')
            return
        dlg_process_name = DialogProcessName()
        result, data = dlg_process_name.run()
        if result == gtk.RESPONSE_CANCEL or result == gtk.RESPONSE_DELETE_EVENT :
            self.process_editor.clear()
            return
        else:
            new_process.name = data['process_name']

        self.process_editor.set_process(new_process, self.kmc_model.lattice_list.data[0])
        self.da_widget.grab_focus()
        self.statbar.push(1,'Left-click sites for condition, right-click site for actions, hit Return when finished.')


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

    def set_model(self, kmc_model):
        self.treeview.set_model(kmc_model)
        self.process_editor.set_model(kmc_model)




    def on_da_key_pressed(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == 'Return':
            self.statbar_clicked(widget, event)
        elif key == 'Escape':
            self.process_editor.clear()
            if self.checked_out_process[0]:
                self.checked_out_process = (False, )
        elif key == 'Up':
            self.process_editor.change_zoom(2)
        elif key == 'Down':
            self.process_editor.change_zoom(-2)


    # Serves to finish process input
    def statbar_clicked(self, widget, event):
        self.window.grab_focus()
        new_process = self.process_editor.get_process()
        if new_process:
            if not new_process.rate_constant:
                preset = 'rate_' + new_process.name 
                dlg_rate_constant = DialogRateConstant(self.kmc_model.parameter_list.data, self.keywords, preset)
                result, data = dlg_rate_constant.run()
                if result == gtk.RESPONSE_OK:
                    new_process.rate_constant = data['rate_constant']
            #Check if process is sound
            if not new_process.name :
                self.statbar.push(1,'New process has no name')
                return
            elif not new_process.center_site:
                self.statbar.push(1,'No sites defined!')
                return
            elif not new_process.condition_list:
                self.statbar.push(1,'New process has no conditions')
                return
            elif not new_process.action_list:
                self.statbar.push(1,'New process has no actions')

            for elem in new_process.action_list + new_process.condition_list :
                print('%s %s' % (elem, new_process.center_site))
                for i in range(2):
                    elem.coord[i] = elem.coord[i] - new_process.center_site[i]
                print('%s %s' % (elem, new_process.center_site))

            new_process.center_site[0] = 0
            new_process.center_site[1] = 0
            print(new_process)
            if self.checked_out_process[0]:
                index = self.checked_out_process[1]
                self.kmc_model.process_list[index] = new_process
                self.checked_out_process = (False, )
                self.statbar.push(1,'Process "'+ new_process.name + '" edited')
            else:
                self.kmc_model.process_list.append(new_process)
                self.statbar.push(1,'New process "'+ new_process.name + '" added')
            self.process_editor.draw_lattices(blank=True)
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


class ProcessEditor():
    def __init__(self, da_widget):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.da_widget = da_widget
        self.lattice_ready = False
        self.zoom = 3

    def configure(self, widget, event):
        self.process_editor_width, self.process_editor_height = widget.get_allocation()[2], widget.get_allocation()[3]
        self.pixmap = gtk.gdk.Pixmap(widget.window, self.process_editor_width, self.process_editor_height)
        self.pixmap.draw_rectangle(widget.get_style().white_gc, True, 0, 0, self.process_editor_width, self.process_editor_height)
        return True

    def expose(self, widget, event):
        site_x, site_y, self.process_editor_width, self.process_editor_height = widget.get_allocation()
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL], self.pixmap, 0, site_y, 0, site_y, self.process_editor_width, self.process_editor_height)

    def query_tooltip(self, widget, xcoord, ycoord, foo, tooltip):
        if self.lattice_ready:
            width, height = self.process_editor_width, self.process_editor_height
            lattice = self.lattice
            unit_x = lattice.unit_cell_size[0]
            unit_y = lattice.unit_cell_size[1]
            for i in range(self.zoom+1):
                for j in range(self.zoom):
                    for x in range(unit_x):
                        for y in range(unit_y):
                            for site in lattice.sites:
                                if site.coord[0] == x and site.coord[1] == y:
                                    center = []
                                    coordx = int((i+ float(x)/unit_x)*width/self.zoom)
                                    coordy = int(height - (j+ float(y)/unit_y)*height/self.zoom)
                                    if (coordx - xcoord)**2 + (coordy - ycoord)**2 < 90 :
                                        for site in lattice.sites:
                                            if site.coord == list((x, y)):
                                                site_nick = site.name
                                                tooltip.set_text(site_nick)
                                                return True

    def set_model(self, kmc_model):
        self.kmc_model = kmc_model

    def set_process(self, process, lattice):
        self.new_process = process
        self.lattice = lattice
        self.draw_lattices()
        self.lattice_ready = True

    def get_process(self):
        return self.new_process


    def dw_lattice_clicked(self, widget, event):
        if self.lattice_ready:
            width, height = self.process_editor_width, self.process_editor_height
            lattice = self.lattice
            unit_x = lattice.unit_cell_size[0]
            unit_y = lattice.unit_cell_size[1]
            for i in range(self.zoom+1):
                for j in range(self.zoom):
                    for x in range(unit_x):
                        for y in range(unit_y):
                            for site in lattice.sites:
                                if site.coord[0] == x and site.coord[1] == y:
                                    center = []
                                    coordx = int((i+ float(x)/unit_x)*width/self.zoom)
                                    coordy = int(height - (j+ float(y)/unit_y)*height/self.zoom)
                                    if (coordx - event.x)**2 + (coordy - event.y)**2 < 30 :
                                        for site in lattice.sites:
                                            if site.coord == list((x, y)):
                                                site_nick = site.name
                                                self.species_menu = gtk.Menu()
                                                menu_header = gtk.MenuItem('Select condition (%s)' % site_nick)
                                                menu_header.set_sensitive(False)
                                                self.species_menu.append(menu_header)
                                                self.species_menu.append(gtk.SeparatorMenuItem())
                                                data = 'condition', i-self.zoom/2, j-self.zoom/2, x, y
                                                for species in self.kmc_model.species_list.data:
                                                    menu_item = gtk.MenuItem(4*' ' + species.name)
                                                    self.species_menu.append(menu_item)
                                                    menu_item.connect("activate", self.modify_condition, (species, list(data), True))

                                                if filter(lambda cond: cond.coord == [i-self.zoom/2, j-self.zoom/2, x, y], self.new_process.condition_list) :
                                                    # if already has a condition defined
                                                    self.species_menu.append(gtk.SeparatorMenuItem())
                                                    menu_header = gtk.MenuItem('Select action (%s)' % site_nick)
                                                    menu_header.set_sensitive(False)
                                                    self.species_menu.append(menu_header)
                                                    self.species_menu.append(gtk.SeparatorMenuItem())
                                                    data = 'action', i-self.zoom/2, j-self.zoom/2, x, y

                                                    for species in self.kmc_model.species_list.data:
                                                        menu_item = gtk.MenuItem(4*' ' + species.name)
                                                        self.species_menu.append(menu_item)
                                                        menu_item.connect("activate", self.modify_condition, (species, list(data), True))
                                                    if filter(lambda cond: cond.coord == [i-self.zoom/2, j-self.zoom/2, x, y], self.new_process.action_list) :
                                                        menu_item = gtk.MenuItem('Remove action')
                                                        self.species_menu.append(menu_item)
                                                        menu_item.connect('activate', self.modify_condition, (species, list(data), False))
                                                    else:
                                                        data = 'condition', i-self.zoom/2, j-self.zoom/2, x, y
                                                        menu_item = gtk.MenuItem('Remove condition')
                                                        self.species_menu.append(menu_item)
                                                        menu_item.connect('activate', self.modify_condition, (species, list(data), False))
                                                self.species_menu.show_all()
                                                self.species_menu.popup(None, None, None, event.button, event.time)
                                    else:
                                        #Catch events outside dots
                                        pass

    def change_zoom(self, change):
        if 2 <= self.zoom + change <=  10 :
            self.zoom += change
            self.draw_lattices()

    def modify_condition(self, event, data):
        #Test if point is condition or action
        is_condition = data[1][0] == 'condition'
        add = data[2]

        # weed out data
        data = [ data[0].name, data[1][1 :] ]
        # remove entry if requested
        if not add:
            if is_condition:
                for condition in self.new_process.condition_list:
                    if condition.coord == data[1]:
                        self.new_process.condition_list.remove(condition)
                    if not self.new_process.condition_list:
                        self.new_process.center_site = ()
            else:
                for action in self.new_process.action_list:
                    if action.coord == data[1]:
                        self.new_process.action_list.remove(action)
                        
            self.draw_lattices()
            print(self.new_process)
            return
        # new_ca stands for 'new condition/action'
        new_ca = ConditionAction(coord=data[1], species=data[0])
        # if this is the first condition, make it the center site
        # all other sites will be measure relative to this site
        if not self.new_process.condition_list:
            self.new_process.center_site = copy(data[1])

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
        print(self.new_process)


    def clear(self):
        self.new_process = Process()
        self.draw_lattices(blank=True)
        self.lattice_ready = False

    def draw_lattices(self,blank=False):
        gc = self.da_widget.get_style().black_gc
        gc = gtk.gdk.GC(self.pixmap)
        width, height = self.process_editor_width, self.process_editor_height
        gc.set_rgb_fg_color(gtk.gdk.color_parse('#fff'))
        self.pixmap.draw_rectangle(gc, True, 0, 0, width, height)
        gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
        gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
        gc.line_width = 1
        if blank:
            self.da_widget.queue_draw_area(0, 0, width, height)
            return
        lattice = self.lattice
        unit_x = lattice.unit_cell_size[0]
        unit_y = lattice.unit_cell_size[1]
        for sup_i in range(self.zoom+1):
            for i in range(-1,1):
                self.pixmap.draw_line(gc, 0, i+sup_i*height/self.zoom, width, i+(sup_i*height/self.zoom))
                self.pixmap.draw_line(gc, i+sup_i*width/self.zoom, 0, i+(sup_i*width/self.zoom), height)
        gc.line_style = gtk.gdk.LINE_SOLID
        for sup_i in range(self.zoom+1):
            for sup_j in range(self.zoom):
                for x in range(unit_x):
                    for y in range(unit_y):
                        for site in lattice.sites:
                            if site.coord[0] == x and site.coord[1] == y:
                                center = []
                                coordx = int((sup_i+ float(x)/unit_x)*width/self.zoom )
                                coordy = int(height - (sup_j+ float(y)/unit_y)*height/self.zoom )
                                center = [ coordx, coordy ]
                                self.pixmap.draw_arc(gc, True, center[0]-5, center[1]-5, 10, 10, 0, 64*360)
                                for entry in self.new_process.condition_list:
                                    if entry.coord == [sup_i-self.zoom/2, sup_j-self.zoom/2, x, y ]:
                                        color = filter((lambda x : x.name == entry.species), self.kmc_model.species_list.data)[0].color
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse(color))
                                        self.pixmap.draw_arc(gc, True, center[0]-15, center[1]-15, 30, 30, 64*90, 64*360)
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
                                        self.pixmap.draw_arc(gc, False, center[0]-15, center[1]-15, 30, 30, 64*90, 64*360)
                                for entry in self.new_process.action_list:
                                    if entry.coord == [sup_i-self.zoom/2, sup_j-self.zoom/2, x, y ]:
                                        color = filter((lambda x : x.name == entry.species), self.kmc_model.species_list.data)[0].color
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse(color))
                                        self.pixmap.draw_arc(gc, True, center[0]-10, center[1]-10, 20, 20, 64*270, 64*360)
                                        gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
                                        self.pixmap.draw_arc(gc, False, center[0]-10, center[1]-10, 20, 20, 64*270, 64*360)
                                gc.set_rgb_fg_color(gtk.gdk.color_parse('#000'))
        self.da_widget.queue_draw_area(0, 0, width, height)

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
        # define fields
        self.name_field = self.wtree.get_widget('parameterName')
        self.type_field = self.wtree.get_widget('parameterType')
        self.value_field = self.wtree.get_widget('parameterValue')

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog_add_parameter.show()
        # run
        result = self.dialog_add_parameter.run()
        # extract fields
        data = {}
        data['name'] = self.name_field.get_text()

        type_model = self.type_field.get_model()
        type_index = self.type_field.get_active()
        data['type'] = type_model[type_index][0]
        data['value'] = self.value_field.get_text()
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
        index_adjustment = gtk.Adjustment(value=len(self.lattice_dialog.lattice.sites) + 1, lower=0, upper=1000, step_incr=1, page_incr=4, page_size=0)
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
        # define fields
        self.process_name = self.wtree.get_widget('process_name')
        self.process_name.set_text('')

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog.show()
        #run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['process_name'] = self.process_name.get_text()
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
        # define fields
        self.species = self.wtree.get_widget('field_species')
        self.species_id = self.wtree.get_widget('species_id')
        self.species_id.set_text(str(self.nr_of_species))
        self.species_id.set_sensitive(False)
        self.color = ""


    def open_dlg_color_selection(self, widget):
        dlg_color_selection = DialogColorSelection(self.color)
        result, data = dlg_color_selection.run()
        if result == gtk.RESPONSE_OK:
            self.color = data['color']
        dlg_color_selection.close()

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog.show()
        #run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['name'] = self.species.get_text()
        data['id'] = self.species_id.get_text()
        data['color'] = self.color
        self.dialog.destroy()
        return result, data

class DialogRateConstant():
    def __init__(self, parameters=[], keywords=[], preset = ''):
        self.parameters = parameters
        self.keywords = keywords
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('dlgRateConstant')
        # define fields
        self.rate_constant = self.wtree.get_widget('rate_constant')
        self.rate_constant.set_text(preset)

    def run(self):
        """Set initial values and send back entries if OK button clicked
        """
        self.dialog.show()
        completion = gtk.EntryCompletion()
        liststore = gtk.ListStore(str)
        self.rate_constant.set_completion(completion)
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
        data['rate_constant'] = self.rate_constant.get_text()
        self.dialog.destroy()
        return result, data

class DialogMetaInformation():
    def __init__(self):
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('meta_info')
        # define field
        self.author = self.wtree.get_widget('metaAuthor')
        self.email = self.wtree.get_widget('metaEmail')
        self.model_name = self.wtree.get_widget('metaModelName')
        self.model_dimension = self.wtree.get_widget('metaDimension')
        self.model_dimension.set_sensitive(False)
        self.debug_level = self.wtree.get_widget('metaDebug')

    def run(self):
        self.dialog.show()
        # run
        result = self.dialog.run()
        # extract fields
        data = {}
        data['author'] = self.author.get_text()
        data['email'] = self.email.get_text()
        data['model_name'] = self.model_name.get_text()
        data['model_dimension'] = str(self.model_dimension.get_value_as_int())
        data['debug'] = self.debug_level.get_value_as_int()
        self.dialog.destroy()
        return result, data


class DialogColorSelection():
    def __init__(self, color=''):
            
        self.gladefile = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.dialog = self.wtree.get_widget('dlgcolorselection')
        self.color = color



    def run(self):
        self.dialog.show()
        color_dlg = self.wtree.get_widget('colorsel-color_selection1')
        if self.color:
            color_dlg.set_current_color(gtk.gdk.color_parse(self.color))
        result = self.dialog.run()
        data = {}
        data['color'] = color_dlg.get_current_color().to_string()
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
    def __setitem__(self, key, item):
        self.data[key] = item
        self.data.sort()
        self.callback('changed')
    #@verbose
    def __getitem__(self, key):
        return self.data[key]

    def sort(self):
        self.data.sort()

    #@verbose
    def append(self, elem):
        if elem not in self.data:
            self.data.append(elem)
            full_path = (self.node_index, self.data.index(elem))
            self.callback('row-inserted', full_path)
        self.data.sort()
        self.callback('changed')

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
        ret = ''
        ret += 'Process: %s %s\n' % (self.name, self.rate_constant)
        if self.center_site:
            ret += 'Center Site: %s\n' % self.center_site
        else:
            ret + 'No center site defined.\n'
        ret += 'Conditions:\n'
        for elem in self.condition_list:
            ret += elem.__repr__()
        ret += 'Actions:\n'
        for elem in self.action_list:
            ret += elem.__repr__()
        return ret

    def __cmp__(self, other):
        if self.name > other.name :
            return 1
        elif self.name == other.name :
            return 0
        else:
            return -1

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
    def __repr__(self):
        return '    %s %s\n' % (self.coord, self.species)

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
    def __init__(self):
        self.unsaved_changes = False

    def __call__(self, message):
        if message == 'saved':
            self.unsaved_changes = False
        elif message == 'changed':
            self.unsaved_changes = True





def main():
    """Main function, called if scripts called directly
    """
    parser = OptionParser()
    parser.add_option('-n','--no-gui', dest='nogui', action='store_true', default=False, help='Runs without opening a GUI')
    parser.add_option('-i','--import', dest='xml_import', type='string', help='Defines the  kMC project file to import')
    parser.add_option('-s','--export-source', dest='export_source', action='store_true', default=False)
    (options, args) = parser.parse_args()
    if options.nogui:
        kmc_model = KMC_Model()
        if hasattr(options,'xml_import'):
            kmc_model.import_xml(options.xml_import)
            if options.export_source:
                kmc_model.export_source()
    else:
        main = MainWindow()
        main.window.show()
        gtk.main()

if __name__ == "__main__":
    main()
