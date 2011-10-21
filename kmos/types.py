#!/usr/bin/env python
"""Holds all the data models used in kmos.
"""

# stdlib imports
from copy import deepcopy

# XML handling
from lxml import etree as ET
#Need to pretty print XML
from xml.dom import minidom

# kmos own modules
from kmos.utils import CorrectlyNamed
from kmos.config import *

KMCPROJECT_V0_1_DTD = '/kmc_project_v0.1.dtd'
KMCPROJECT_V0_2_DTD = '/kmc_project_v0.2.dtd'
XML_API_VERSION = (0, 2)

class FixedObject(object):
    """Handy class that easily allows to define data structures
    that can only hold a well-defined set of fields
    """
    attributes = []
    def __init__(self, **kwargs):
        self.__doc__ += '\nAllowed keywords: %s' % self.attributes
        for attribute in self.attributes:
            if attribute in kwargs:
                self.__dict__[attribute] = kwargs[attribute]
        for key in kwargs:
            if key not in self.attributes:
                raise AttributeError(
                    'Tried to initialize illegal attribute %s' % key)

    def __setattr__(self, attrname, value):
        if attrname in self.attributes + ['__doc__']:
            self.__dict__[attrname] = value
        else:
            raise AttributeError('Tried to set illegal attribute %s' \
                                                            % attrname)


class Site(FixedObject):
    """Represents one lattice site.
    """
    attributes = ['name', 'x', 'y', 'z', 'tags', 'default_species']
    # vector is now a list of floats for the graphical representation

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)
        self.tags = kwargs['tags'] if  'tags' in kwargs else []
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.default_species = kwargs['default_species'] \
            if 'default_species' in kwargs else 'default_species'

    def __repr__(self):
        return '[SITE] %s %s %s' % (self.name,
                                   (self.x, self.y, self.z), self.tags)


class ProcessFormSite(Site):
    """This is just a little varient of the site object,
    with the sole difference that it has a layer attribute
    and is meant to be used in the process form. This separation was chosen,
    since the Site object as in the ProjectTree should not have a layer
    attribute to avoid data duplication but in the ProcessForm we need this
    to define processes
    """
    attributes = Site.attributes
    attributes.append('layer')
    attributes.append('color')

    def __init__(self, **kwargs):
        Site.__init__(self, **kwargs)
        self.layer = kwargs['layer'] if 'layer' in kwargs else ''


class Layer(FixedObject, CorrectlyNamed):
    """Represents one layer in a possibly multi-layer geometry
    """
    attributes = ['name', 'sites', 'active', 'color']

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.active = kwargs['active'] if 'active' in kwargs else True
        self.color = kwargs['color'] if 'color' in kwargs else '#ffffff'
        self.sites = kwargs['sites'] if 'sites' in kwargs else []

    def __repr__(self):
        return "[LAYER] %s\n[\n%s\n]" % (self.name, self.sites)

    def add_site(self, site):
        """Adds a new site to a layer.
        """
        self.sites.append(site)

    def get_info(self):
        if self.active:
            return 'visible'
        else:
            return 'invisible'


class ConditionAction(FixedObject):
    """Represents either a condition or an action. Since both
    have the same attributes we use the same class here, and just
    store them in different lists, depending on its role.
    """
    attributes = ['species', 'coord']

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)

    def __repr__(self):
        return "[COND_ACT] Species: %s Coord:%s\n" % (self.species, self.coord)


class Coord(FixedObject):
    """Class that holds exactly one coordinate as used in the description
    of a process. The distinction between a Coord and a Site may seem
    superfluous but it is made to avoid data duplication.
    """
    attributes = ['offset', 'name', 'layer']

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)
        self.offset = kwargs['offset'] \
            if 'offset' in kwargs else (0, 0, 0)
        if len(self.offset) == 1:
            self.offset = (self.offset[0], 0, 0)
        if len(self.offset) == 2:
            self.offset = (self.offset[0], self.offset[1], 0)

    def __repr__(self):
        return '[COORD] %s.%s.%s' % (self.name, tuple(self.offset), self.layer)

    def __eq__(self, other):
        return (self.layer, self.name, self.offset) == \
               (other.layer, other.name, other.offset)

    def __add__(a, b):
        diff = [(x + y) for (x, y) in zip(a.offset, b.offset)]
        if a.layer and b.layer:
            name = "%s_%s + %s_%s" % (a.layer, a.name, b.layer, b.name)
        elif a.layer:
            name = '%s_%s + %s' % (a.layer, a.name, b.name)
        elif b.layer:
            name = "%s + %s_%s" % (a.name, b.layer, b.name)
        else:
            name = '%s + %s' % (a.name, b.name)
        layer = ''
        return Coord(name=name, layer=layer, offset=offset)

    def __sub__(a, b):
        """When subtracting to lattice coordinates from each other,
        i.e. a-b, we want to keep the name and layer from a, and just
        take the difference in supercells
        """
        offset = [(x - y) for (x, y) in zip(a.offset, b.offset)]
        if a.layer:
            a_name = '%s_%s' % (a.layer, a.name)
        else:
            a_name = a.name
        if b.layer:
            b_name = '%s_%s' % (b.layer, b.name)
        else:
            b_name = b.name

        if a_name == b_name:
            name = '0'
        else:
            name = '%s - %s' % (a_name, b_name)
        layer = ''
        return Coord(name=name, layer=layer, offset=offset)

    def rsub_ff(self):
        """Build term as if subtrating on the right, omit '-' if 0 anyway
        (in Fortran Form :-)
        """
        ff = self.ff()
        if ff == '(/0, 0, 0, 0/)':
            return ''
        else:
            return ' - %s' % ff

    def radd_ff(self):
        """Build term as if adding on the right, omit '+' if 0 anyway
        (in Fortran Form :-)
        """
        ff = self.ff()
        if ff == '(/0, 0, 0, 0/)':
            return ''
        else:
            return ' + %s' % ff

    def sort_key(self):
        return "%s_%s_%s_%s_%s" % (self.layer,
                                   self.name,
                                   self.offset[0],
                                   self.offset[1],
                                   self.offset[2])

    def ff(self):
        """ff like 'Fortran Form'"""
        if self.layer:
            return "(/%s, %s, %s, %s_%s/)" % (self.offset[0], self.offset[1],
                                              self.offset[2], self.layer,
                                              self.name,)
        else:
            return "(/%s, %s, %s, %s/)" % (self.offset[0], self.offset[1],
                                           self.offset[2], self.name, )


class Species(FixedObject):
    """Class that represent a species such as oxygen, empty, ... .
    Note: `empty` is treated just like a species.

    ..  testcode::

        s = Species; print(s.attributes)

    """
    attributes = ['name', 'color', 'representation']

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)
        self.name = kwargs['name'] \
            if 'name' in kwargs else ''
        self.representation = kwargs['representation'] \
            if 'representation' in kwargs else ''
    def __repr__(self):
        return '[SPECIES] Name: %s Color: %s\n' % (self.name, self.color)


class SpeciesList(FixedObject, list):
    """A list of species
    """
    attributes = ['default_species', 'name']

    def __init__(self, **kwargs):
        kwargs['name'] = 'Species'
        FixedObject.__init__(self, **kwargs)


class ProcessList(FixedObject, list):
    """A list of processes
    """
    attributes = ['name']
    def __init__(self, **kwargs):
        self.name = 'Processes'

    def __lt__(self, other):
        return self.name < other.name


class ParameterList(FixedObject, list):
    """A list of parameters
    """
    attributes = ['name']
    def __init__(self, **kwargs):
        self.name = 'Parameters'


class LayerList(FixedObject, list):
    """A list of layers
    """
    attributes = ['name', 'cell_size_x', 'cell_size_y', 'cell_size_z',
                  'default_layer', 'representation']

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)
        self.name = 'Lattice(s)'
        self.cell_size_x = kwargs['cell_size_x'] \
            if 'cell_size_x' in kwargs else 1.
        self.cell_size_y = kwargs['cell_size_y'] \
            if 'cell_size_y' in kwargs else 1.
        self.cell_size_z = kwargs['cell_size_z'] \
            if 'cell_size_z' in kwargs else 1.
        self.default_layer = kwargs['default_layer'] \
            if 'default_layer' in kwargs else 'default'
        self.representation = kwargs['representation'] \
            if 'representation' in kwargs else ''

    def generate_coord(self, terms):
        """Expecting something of the form site_name.offset.layer
        and return a Coord object"""
        term = terms.split('.')
        if len(term) == 3 :
            return Coord(name=term[0],
                offset=tuple(term[1]),
                layer=term[2])
        elif len(term) == 2 :
            return Coord(name=term[0],
                offset=tuple(eval(term[1])),
                layer=self.default_layer)
        elif len(term) == 1 :
            return Coord(name=term[0],
                offset=(0, 0, 0),
                layer=self.default_layer)
        else:
            raise UserWarning("Cannot parse coord description")

    def get_abs_coord(self, coord):
        import numpy as np
        offset = np.array(coord.offset)
        layer = filter(lambda x: x.name == coord.layer, list(self))[0]
        site = filter(lambda x: x.name == coord.name, layer.sites)[0]
        pos = np.array([site.x, site.y, site.z])
        cell = np.diag([self.cell_size_x, self.cell_size_y, self.cell_size_z])

        return np.dot(offset + pos, cell)


class Parameter(FixedObject, CorrectlyNamed):
    """A parameter that can be used in a rate constant expression
    and defined via some init file
    """
    attributes = ['name', 'value', 'adjustable', 'min', 'max', 'scale']

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)
        self.name = kwargs['name'] \
            if 'name' in kwargs else ''
        self.adjustable = kwargs['adjustable'] \
            if 'adjustable' in kwargs else False
        self.value = kwargs['value'] \
            if 'value' in kwargs else 0.
        self.min = float(kwargs['min']) \
            if 'min' in kwargs else 0.0
        self.max = float(kwargs['max']) \
            if 'max' in kwargs else 0.0
        self.scale = str(kwargs['scale']) \
            if 'scale' in kwargs else 'linear'

    def __repr__(self):
        return '[PARAMETER] Name: %s Value: %s\n' % (self.name, self.value)

    def on_adjustable__do_toggled(self, value):
        print(value)

    def on_name__content_changed(self, _):
        self.project_tree.update(self.process)

    def get_info(self):
        return self.value


class Meta(object):
    """Class holding the meta-information about the kMC project
    """
    name = 'Meta'

    def __init__(self, *args, **kwargs):
        self.add(kwargs)

    def add(self, attrib):
        for key in attrib:
            if key in ['debug', 'model_dimension']:
                self.__setattr__(key, int(attrib[key]))
            else:
                self.__setattr__(key, attrib[key])

    def setattribute(self, attr, value):
        if attr in ['author', 'email', 'debug',
                    'model_name', 'model_dimension']:
            self.add({attr: value})

        else:
            print('%s is not a known meta information')
    def get_extra(self):
        return "%s(%s)" % (self.model_name, self.model_dimension)


class Process(FixedObject):
    """One process in a kMC process list
    """
    attributes = ['name',
                  'rate_constant',
                  'condition_list',
                  'action_list',
                  'enabled',
                  'chemical_expression',
                  'tof_count']

    def __init__(self, **kwargs):
        FixedObject.__init__(self, **kwargs)
        self.name = kwargs['name'] \
            if 'name' in kwargs else ''
        self.rate_constant = kwargs['rate_constant'] \
            if 'rate_constant' in kwargs else '0.'
        self.condition_list = kwargs['condition_list'] \
            if 'condition_list' in kwargs else []
        self.action_list = kwargs['action_list'] \
         if 'action_list' in kwargs else []
        self.tof_count = kwargs['tof_count'] \
            if 'tof_count' in kwargs else None
        self.enabled = kwargs['enabled'] if 'enabled' in kwargs else True

    def __repr__(self):
        return '[PROCESS] Name:%s Rate: %s\nConditions: %s\nActions: %s' \
            % (self.name, self.rate_constant,
               self.condition_list, self.action_list)

    def add_condition(self, condition):
        """Adds a conditions to a process"""
        self.condition_list.append(condition)

    def add_action(self, action):
        """Adds an action to a process"""
        self.action_list.append(action)

    def executing_coord(self):
        return sorted(self.action_list,
                      key=lambda action: action.coord.sort_key())[0].coord

    def get_info(self):
        return self.rate_constant

    def evaluate_rate_expression(self, parameters={}):
        import kmos.evaluate_rate_expression
        return kmos.evaluate_rate_expression(self.rate_constant, parameters)



class OutputList(FixedObject, list):
    """A dummy class, that will hold the values which are to be
    printed to logfile.
    """
    attributes = ['name']
    def __init__(self):
        self.name = 'Output'


class OutputItem(FixedObject):
    """Not implemented yet
    """
    attributes = ['name', 'output']

    def __init__(self, *args, **kwargs):
        FixedObject.__init__(self, **kwargs)


class ProjectTree(object):
    def __init__(self):
        self.meta = Meta()
        self.layer_list = LayerList()
        self.parameter_list = ParameterList()
        self.species_list = SpeciesList()
        self.process_list = ProcessList()
        self.output_list = OutputList()

        # Quick'n'dirty define access functions
        # needed in context with GTKProjectTree
        self.add_parameter = lambda parameter: \
            self.parameter_list.append(parameter)
        self.get_parameters = lambda : sorted(self.parameter_list,
                                              key=lambda x: x.name)
        
        self.add_layer = lambda layer: self.layer_list.append(layer)
        self.get_layers = lambda : sorted(self.layer_list,
                                          key=lambda x: x.name)

        self.add_process = lambda process: self.process_list.append(process)
        self.get_processes = lambda : sorted(self.process_list,
                                             key=lambda x: x.name)

        self.add_species = lambda species: self.species_list.append(species)
        self.get_speciess = lambda : sorted(self.species_list,
                                            key=lambda x: x.name)

        self.add_output = lambda output: self.output_list.append(output)
        self.get_outputs = lambda : sorted(self.output_list,
                                           key=lambda x: x.name)

    def __repr__(self):
        return self._get_xml_string()

    def _get_xml_string(self):
        """Produces an XML representation of the project data
        """
        # build XML Tree
        root = ET.Element('kmc')
        root.set('version', str(XML_API_VERSION))
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
        if hasattr(self.species_list, 'default_species'):
            species_list.set('default_species',
                             self.species_list.default_species)
        else:
            species_list.set('default_species', '')

        for species in self.get_speciess():
            species_elem = ET.SubElement(species_list, 'species')
            species_elem.set('name', species.name)
            species_elem.set('color', species.color)
            species_elem.set('representation', species.representation)
        parameter_list = ET.SubElement(root, 'parameter_list')
        for parameter in self.get_parameters():
            parameter_elem = ET.SubElement(parameter_list, 'parameter')
            parameter_elem.set('name', parameter.name)
            parameter_elem.set('value', str(parameter.value))
            parameter_elem.set('adjustable', str(parameter.adjustable))
            parameter_elem.set('min', str(parameter.min))
            parameter_elem.set('max', str(parameter.max))
            if hasattr(parameter, 'scale'):
                parameter_elem.set('scale', str(parameter.scale))
            else:
                parameter_elem.set('scale', 'linear')

        lattice_elem = ET.SubElement(root, 'lattice')
        if (hasattr(self.layer_list, 'cell_size_x') and \
            hasattr(self.layer_list, 'cell_size_y') and
            hasattr(self.layer_list, 'cell_size_z')):
            lattice_elem.set('cell_size', '%s %s %s' %
            (self.layer_list.cell_size_x,
            self.layer_list.cell_size_y,
            self.layer_list.cell_size_z))
            lattice_elem.set('default_layer',
                             self.layer_list.default_layer)
        if hasattr(self.layer_list, 'representation'):
            lattice_elem.set('representation', self.layer_list.representation)
        for layer in self.get_layers():
            layer_elem = ET.SubElement(lattice_elem, 'layer')
            layer_elem.set('name', layer.name)
            layer_elem.set('color', layer.color)

            for site in layer.sites:
                site_elem = ET.SubElement(layer_elem, 'site')
                site_elem.set('vector', '%s %s %s' % (site.x, site.y, site.z))
                site_elem.set('type', site.name)
                site_elem.set('tags', site.tags)
                site_elem.set('default_species', site.default_species)

        process_list = ET.SubElement(root, 'process_list')
        for process in self.get_processes():
            process_elem = ET.SubElement(process_list, 'process')
            process_elem.set('rate_constant', process.rate_constant)
            process_elem.set('name', process.name)
            process_elem.set('enabled', str(process.enabled))
            if process.tof_count:
                process_elem.set('tof_count', str(process.tof_count))
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
        for output in self.get_outputs():
            if output.output:
                output_elem = ET.SubElement(output_list, 'output')
                output_elem.set('item', output.name)
        return prettify_xml(root)

    def export_xml_file(self, filename):
        f = file(filename, 'w')
        f.write(str(self))
        f.close()


    def import_xml_file(self, filename):
        """Takes a filename, validates the content against kmc_project.dtd
        and import all fields into the current project tree
        """
        # TODO: catch XML version first and convert if necessary
        self.filename = filename
        #xmlparser = ET.XMLParser(remove_comments=True)
        #! FIXME : automatic removal of comment not supported in
        # stdlib version of ElementTree
        xmlparser = ET.XMLParser()
        try:
            root = ET.parse(filename, parser=xmlparser).getroot()
        except:
            print('\nCould not parse file. Are you sure this')
            print('a kmos project file?\n')
            raise

        if 'version' in root.attrib:
            self.version = eval(root.attrib['version'])
        else:
            self.version = (0, 1)

        if self.version == (0, 1):
            dtd = ET.DTD(APP_ABS_PATH + KMCPROJECT_V0_1_DTD)
            if not dtd.validate(root):
                print(dtd.error_log.filter_from_errors()[0])
                return
            nroot = ET.Element('kmc')
            nroot.set('version', '0.2')
            raise Exception('No legacy support!')
            # TODO: catch and warn when factored out
			# kiwi.ui.dialogs.info()
        elif self.version == (0, 2):
            dtd = ET.DTD(APP_ABS_PATH + KMCPROJECT_V0_2_DTD)
            if not dtd.validate(root):
                print(dtd.error_log.filter_from_errors()[0])
                return
            for child in root:
                if child.tag == 'lattice':
                    cell_size = [float(x)
                                 for x in child.attrib['cell_size'].split()]
                    self.layer_list.cell_size_x = cell_size[0]
                    self.layer_list.cell_size_y = cell_size[1]
                    self.layer_list.cell_size_z = cell_size[2]
                    self.layer_list.default_layer = child.attrib['default_layer']
                    if 'representation' in child.attrib:
                        self.layer_list.representation = child.attrib[
                                                             'representation']
                    else:
                        self.layer_list.representation = ''
                    for elem in child:
                        if elem.tag == 'layer':
                            name = elem.attrib['name']
                            if 'color' in elem.attrib:
                                color = elem.attrib['color']
                            else:
                                color = '#ffffff'
                            layer = Layer(name=name, color=color)
                            self.add_layer(layer)

                            for site in elem:
                                name = site.attrib['type']
                                x, y, z = [float(x)
                                    for x in site.attrib['vector'].split()]
                                if 'tags' in site.attrib:
                                    tags = site.attrib['tags']
                                else:
                                    tags = []
                                if 'default_species' in site.attrib:
                                    default_species = site.attrib[
                                                         'default_species']
                                else:
                                    default_species = 'default_species'
                                site_elem = Site(name=name,
                                    x=x, y=y, z=z,
                                    tags=tags,
                                    default_species=default_species)
                                layer.sites.append(site_elem)
                elif child.tag == 'meta':
                    for attrib in ['author',
                                    'debug',
                                    'email',
                                    'model_dimension',
                                    'model_name']:
                        if attrib in child.attrib:
                            self.meta.add({attrib: child.attrib[attrib]})
                elif child.tag == 'parameter_list':
                    for parameter in child:
                        name = parameter.attrib['name']
                        value = parameter.attrib['value']
                        if 'adjustable' in parameter.attrib:
                            adjustable = bool(eval(
                                            parameter.attrib['adjustable']))
                        else:
                            adjustable = False

                        min = parameter.attrib['min'] \
                            if 'min' in parameter.attrib else 0.0
                        max = parameter.attrib['max'] \
                            if 'max' in parameter.attrib else 0.0
                        scale = parameter.attrib['scale'] \
                            if 'scale' in parameter.attrib else 'linear'

                        parameter_elem = Parameter(name=name,
                                                   value=value,
                                                   adjustable=adjustable,
                                                   min=min,
                                                   max=max,
                                                   scale=scale)
                        self.add_parameter(parameter_elem)
                elif child.tag == 'process_list':
                    for process in child:
                        name = process.attrib['name']
                        rate_constant = process.attrib['rate_constant']
                        if 'tof_count' in process.attrib:
                            tof_count = process.attrib['tof_count']
                        else:
                            tof_count = None
                        if 'enabled' in process.attrib:
                            try:
                                proc_enabled = bool(
                                    eval(process.attrib['enabled']))
                            except:
                                proc_enabled = True
                        else:
                            proc_enabled = True
                        process_elem = Process(name=name,
                            rate_constant=rate_constant,
                            enabled=proc_enabled,
                            tof_count=tof_count)
                        for sub in process:
                            if sub.tag == 'action' or sub.tag == 'condition':
                                species = sub.attrib['species']
                                coord_layer = sub.attrib['coord_layer']
                                coord_name = sub.attrib['coord_name']
                                coord_offset = tuple(
                                    [int(i) for i in
                                    sub.attrib['coord_offset'].split()])
                                coord = Coord(layer=coord_layer,
                                              name=coord_name,
                                              offset=coord_offset)
                                condition_action = ConditionAction(
                                    species=species, coord=coord)
                                if sub.tag == 'action':
                                    process_elem.add_action(condition_action)
                                elif sub.tag == 'condition':
                                    process_elem.add_condition(
                                                            condition_action)
                        self.add_process(process_elem)
                elif child.tag == 'species_list':
                    self.species_list.default_species = child.attrib['default_species']
                    for species in child:
                        name = species.attrib['name']
                        color = species.attrib['color']
                        representation = species.attrib['representation'] \
                            if 'representation' in species.attrib else ''
                        species_elem = Species(name=name,
                                               color=color,
                                               representation=representation)
                        self.add_species(species_elem)
                if child.tag == 'output_list':
                    for item in child:
                        output_elem = OutputItem(name=item.attrib['item'],
                                                 output=True)
                        self.add_output(output_elem)



def prettify_xml(elem):
    """This function takes an XML document, which can have one or many lines
    and turns it into a well-breaked, nicely-indented string
    """
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='    ')
