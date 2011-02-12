#!/usr/bin/env python
"""A modules holding all the data models used in kmos.
"""

from kiwi.python import Settable
from utils import CorrectlyNamed

from copy import deepcopy


class Attributes:
    """Handy class that easily allows to define data structures
    that can only hold a well-defined set of fields
    """
    attributes = []
    def __init__(self, **kwargs):
        for attribute in self.attributes:
            if kwargs.has_key(attribute):
                self.__dict__[attribute] = kwargs[attribute]
        for key in kwargs:
            if key not in self.attributes:
                raise AttributeError, 'Tried to initialize illegal attribute %s' % key
    def __setattr__(self, attrname, value):
        if attrname in self.attributes:
            self.__dict__[attrname] = value
        else:
            raise AttributeError, 'Tried to set illegal attribute %s' % attrname



class Site(Attributes):
    """A class holding exactly one lattice site
    """
    attributes = ['index', 'name', 'x', 'y', 'z', 'site_class', 'layer']
    # vector is now a list of floats for the graphical representation
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.site_class = kwargs['site_class'] if  'site_class' in kwargs else ''
        self.layer = kwargs['layer'] if 'layer' in kwargs else ''
        self.name = kwargs['name'] if 'name' in kwargs else ''

    def __repr__(self):
        return '%s(%s) %s %s %s' % (self.name, self.layer, self.index, (self.x, self.y, self.z), self.site_class)

class Grid(Attributes):
    attributes = ['x','y','z','offset_x','offset_y','offset_z',]
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.x = kwargs['x'] if 'x' in kwargs else 1
        self.y = kwargs['y'] if 'y' in kwargs else 1
        self.z = kwargs['z'] if 'z' in kwargs else 1
        self.offset_x = kwargs['offset_x'] if 'offset_x' in kwargs else 0.0
        self.offset_y = kwargs['offset_y'] if 'offset_y' in kwargs else 0.0
        self.offset_z = kwargs['offset_z'] if 'offset_z' in kwargs else 0.0

    def __repr__(self):
        return ('grid: %s %s %s\noffset: %s %s %s' %
            (self.x, self.y, self.z,
            self.offset_x,
            self.offset_y,
            self.offset_z))
        
class Layer(Attributes, CorrectlyNamed):
    """A class that defines exactly one layer
    """
    attributes = ['name', 'grid','sites', 'site_classes']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.grid = kwargs['grid'] if 'grid' in kwargs else Grid()
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.sites = []

    def __repr__(self):
        return "%s\n[%s]\n" % (self.name, self.grid)

    def add_site(self, site):
        """Add a new site to a layer
        """
        self.sites.append(site)

    #def get_coords(self, site):
        #"""Return simple numerical representation of coordinates
        #"""
        #local_site = filter(lambda x: x.name == site.coord.name, self.sites)[0]
        #local_coords = local_site.site_x, local_site.site_y
        #global_coords = site.coord.offset[0]*self.unit_cell_size_x, site.coord.offset[1]*self.unit_cell_size_y
        #coords = [ x + y for (x, y) in zip(global_coords, local_coords) ]
        #return coords


class ConditionAction(Attributes):
    """Class that holds either a condition or an action
    """
    attributes = ['species', 'coord']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return "Species: %s Coord:%s\n" % (self.species, self.coord)

class Coord(Attributes):
    """Class that hold exactly one coordinate as used in the description
    of a process
    """
    attributes = ['offset', 'name']
    def __init__(self, **kwargs):
        if kwargs.has_key('string'):
            raw = kwargs['string'].split('.')
            if len(raw) == 1 :
                self.name = raw[0]
                self.offset = [0, 0]
            elif len(raw) == 2 :
                self.name = raw[0]
                self.offset = eval(raw[1])
            else:
                raise TypeError, "Coordinate specification %s does not match the expected format" % raw

        else:
            Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return '%s.%s.%s' % (self.name, tuple(self.offset), self.layer)

    def __eq__(self, other):
        return str(self) == str(other)


class Species(Attributes):
    """Class that represent a species such as oxygen, empty, ... . Not empty
    is treated just like a species.
    """
    attributes = ['name', 'color', 'id']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return 'Name: %s Color: %s ID: %s\n' % (self.name, self.color, self.id)


class SpeciesList(Attributes):
    """A list of species
    """
    attributes = ['default_species', 'name']
    def __init__(self, **kwargs):
        kwargs['name'] = 'Species'
        Attributes.__init__(self, **kwargs)


class ProcessList(Settable):
    """A list of processes
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Processes'
        Settable.__init__(self, **kwargs)

    def __lt__(self, other):
        return self.name < other.name
        

class ParameterList(Settable):
    """A list of parameters
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Parameters'
        Settable.__init__(self, **kwargs)


class LayerList(Attributes):
    """A list of layers
    """
    attributes = ['name','cell_size_x', 'cell_size_y', 'cell_size_z']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.name = 'Lattice(s)'
        self.cell_size_x = 1.
        self.cell_size_y = 1.
        self.cell_size_z = 1.


class Parameter(Attributes, CorrectlyNamed):
    """A parameter that can be used in a rate constant expression
    and defined via some init file
    """
    attributes = ['name', 'value']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return 'Name: %s Value: %s\n' % (self.name, self.value)

    def on_name__content_changed(self, _):
        self.project_tree.update(self.process)

    def get_extra(self):
        return self.value


class Meta(Settable, object):
    """Class holding the meta-information about the kMC project
    """
    name = 'Meta'
    def __init__(self):
        Settable.__init__(self, email='', author='', debug=0, model_name='', model_dimension=0, )

    def add(self, attrib):
        for key in attrib:
            if key in ['debug', 'model_dimension']:
                self.__setattr__(key, int(attrib[key]))
            else:
                self.__setattr__(key, attrib[key])

    def get_extra(self):
        return "%s(%s)" % (self.model_name, self.model_dimension)



class Process(Attributes):
    """One process in a kMC process list
    """
    attributes = ['name', 'rate_constant', 'condition_list', 'action_list']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.condition_list = []
        self.action_list = []
            
    def __repr__(self):
        return 'Name:%s Rate: %s\nConditions: %s\nActions: %s' % (self.name, self.rate_constant, self.condition_list, self.action_list)

    def add_condition(self, condition):
        self.condition_list.append(condition)

    def add_action(self, action):
        self.action_list.append(action)

    def get_extra(self):
        return self.rate_constant



class OutputList():
    """A dummy class, that will hold the values which are to be printed to logfile.
    """
    def __init__(self):
        self.name = 'Output'

class OutputItem(Attributes):
    """Not implemented yet
    """
    attributes = ['name', 'output']
    def __init__(self, *args, **kwargs):
        Attributes.__init__(self, **kwargs)
