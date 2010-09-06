#!/usr/bin/python
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
from kiwi.ui.delegates import Delegate, SlaveDelegate, ProxyDelegate, ProxySlaveDelegate, GladeDelegate
from kiwi.python import Settable
from kiwi.ui.objectlist import ObjectTree, Column


KMCPROJECT_DTD = '/kmc_project.dtd'
PROCESSLIST_DTD = '/process_list.dtd'
XMLFILE = './default.xml'
SRCDIR = './fortran_src'
GLADEFILE = os.path.join(APP_ABS_PATH, 'kmc_editor2.glade')



class Lattice(Settable):
    def __init__(self, **kwargs):
        Settable.__init__(self, **kwargs)
        self.sites = []

    def add_site(self, site):
        self.sites.append(site)


class Species(Settable):
    def __init__(self, **kwargs):
        Settable.__init__(self, **kwargs)

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


class Parameter(Settable):
    def __init__(self, **kwargs):
        Settable.__init__(self, **kwargs)


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
            self.__setattr__(key, attrib[key])



class Process(Settable):
    def __init__(self, **kwargs):
        Settable.__init__(self, **kwargs)
        self.condition_list=[]
        self.action_list=[]
    def add_condition(self, condition):
        self.condition_list.append(condition)

    def add_action(self, action):
        self.action_list.append(action)

        

class ProjectTree(SlaveDelegate):
    project_data = ObjectTree(Column('name', data_type=str))

    def __init__(self, parent):
        self.set_parent(parent)
        self.lattice_list_iter = self.project_data.append(None, LatticeList())
        self.meta = self.project_data.append(None,Meta())
        self.parameter_list_iter = self.project_data.append(None, ParameterList())
        self.process_list_iter = self.project_data.append(None, ProcessList())
        self.species_list_iter = self.project_data.append(None, SpeciesList())
        self.meta_form = MetaForm(self.meta)

        SlaveDelegate.__init__(self, toplevel=self.project_data)

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
        else:
            raise AttributeError, attr

    def on_project_data__selection_changed(self, item, elem):
        slave = self.get_parent().get_slave('workarea')
        if slave:
            self.get_parent().detach_slave('workarea')

        if isinstance(elem, Meta):
            self.get_parent().attach_slave('workarea', self.meta_form)
            self.meta_form.show()
        elif isinstance(elem, Species):
            species_form = SpeciesForm(elem, self.project_data)
            self.get_parent().attach_slave('workarea', species_form)
            species_form.show()
        else:
            inline_message = InlineMessage('Not implemented, yet.')
            self.get_parent().attach_slave('workarea', inline_message)
            inline_message.show()


class MetaForm(ProxySlaveDelegate):
    gladefile=GLADEFILE
    toplevel_name='meta_form'
    widgets = ['author','email','model_name','model_dimension','debug']
    def __init__(self, model):
        ProxySlaveDelegate.__init__(self, model)



class InlineMessage(SlaveView):
    gladefile=GLADEFILE
    toplevel_name = 'inline_message'
    widgets = ['message_label']
    def __init__(self, message):
        print(dir(self))
        SlaveView.__init__(self)


class SpeciesForm(ProxySlaveDelegate):
    gladefile=GLADEFILE
    toplevel_name='species_form'
    widgets = ['name', 'color', 'id']
    def __init__(self, model, project_data):
            self.project_data = project_data
            ProxySlaveDelegate.__init__(self, model)

    def on_name__content_changed(self, text):
        self.project_data.update(self.model)
    




class KMC_Editor(GladeDelegate):
    widgets = ['workarea','statbar']
    gladefile=GLADEFILE
    toplevel_name='main_window'
    def __init__(self):
        self.project_tree = ProjectTree(parent=self)
        GladeDelegate.__init__(self, delete_handler=self.quit_if_last)
        self.attach_slave('overviewtree', self.project_tree)
        self.project_tree.show()

    
    def on_btn_quit__clicked(self, button):
        self.hide_and_quit()


    def on_btn_save_model__clicked(self, button):
        # build XML Tree
        root = ET.Element('kmc')
        meta = ET.SubElement(root,'meta')
        if hasattr(self.project_tree.meta, 'author'):
            meta.set('author', self.project_tree.meta.author)
        if hasattr(self.project_tree.meta, 'email'):
            meta.set('email', self.project_tree.meta.email)
        if hasattr(self.project_tree.meta, 'model_name'):
            meta.set('model_name', self.project_tree.meta.model_name)
        if hasattr(self.project_tree.meta, 'model_dimension'):
            meta.set('model_dimension', str(self.project_tree.meta.model_dimension))
        if hasattr(self.project_tree.meta, 'debug'):
            meta.set('debug', str(self.project_tree.meta.debug))
        species_list = ET.SubElement(root,'species_list')
        for species in self.project_tree.species_list:
            print(species)
        #for species in self.project_tree.project_data.species_list:
            species_elem = ET.SubElement(species_list,'species')
            species_elem.set('name',species.name)
            species_elem.set('color',species.color)
            species_elem.set('id',str(species.id))
        parameter_list = ET.SubElement(root,'parameter_list')
        for parameter in self.project_tree.parameter_list:
            parameter_elem = ET.SubElement(parameter_list, 'parameter')
            parameter_elem.set('name', parameter.name)
            parameter_elem.set('type', parameter.type)
            parameter_elem.set('value', str(parameter.value))
        lattice_list = ET.SubElement(root, 'lattice_list')
        for lattice in self.project_tree.lattice_list:
            lattice_elem = ET.SubElement(lattice_list,'lattice')
            lattice_elem.set('unit_cell_size', str(lattice.unit_cell_size)[1 :-1].replace(',',''))
            lattice_elem.set('name', lattice.name)
            for site in lattice.sites:
                site_elem = ET.SubElement(lattice_elem, 'site')
                site_elem.set('index',str(site.index))
                site_elem.set('type',site.name)
                site_elem.set('coord',str(site.coord)[1 :-1].replace(',',''))
        process_list = ET.SubElement(root, 'process_list')
        for process in self.project_tree.process_list:
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
        outfile = open(XMLFILE,'w')
        outfile.write(prettify_xml(root))
        outfile.write('<!-- This is an automatically generated XML file, representing a kMC model ' + \
                        'please do not change this unless you know what you are doing -->\n')
        outfile.close()
      
    def on_btn_open_model__clicked(self, button):
        """Import project from XML
        """
        xmlparser = ET.XMLParser(remove_comments=True)
        root = ET.parse(XMLFILE, parser=xmlparser).getroot()
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
                    self.project_tree.project_data.append(self.project_tree.lattice_list, lattice_elem)
            elif child.tag == 'meta':
                for attrib in ['author','email', 'debug','model_name','model_dimension']:
                    if child.attrib.has_key(attrib):
                        self.project_tree.meta.add({attrib:child.attrib[attrib]})
            elif child.tag == 'parameter_list':
                for parameter in child:
                    name = parameter.attrib['name']
                    type = parameter.attrib['type']
                    value = parameter.attrib['value']
                    parameter_elem = Settable(name=name,type=type,value=value)
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
                            condition_action = Settable(species=species, coord=coord)
                            if sub.tag == 'action':
                                process_elem.add_action(condition_action)
                            elif sub.tag == 'condition':
                                process_elem.add_condition(condition_action)
                    self.project_tree.project_data.append(self.project_tree.process_list, process_elem)
            elif child.tag == 'species_list':
                for species in child:
                    name = species.attrib['name']
                    id = species.attrib['id']
                    color = species.attrib['color']
                    species_elem = Species(name=name, color=color, id=id)
                    self.project_tree.project_data.append(self.project_tree.species_list, species_elem)
        

def prettify_xml(elem):
    rough_string = ET.tostring(elem,encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='    ')


if __name__ == '__main__':
    editor = KMC_Editor()
    editor.show_and_loop()
