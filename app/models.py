#!/usr/bin/env python
"""A modules holding all the data models used in kmos.
"""

from kiwi.python import Settable
from utils import CorrectlyNamed


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
    attributes = ['index', 'name', 'site_x', 'site_y']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return '%s %s %s %s' % (self.name, self.index, self.site_x, self.site_y)

class Lattice(Attributes, CorrectlyNamed):
    """A class that defines exactly one lattice
    """
    attributes = ['name', 'unit_cell_size_x', 'unit_cell_size_y', 'sites']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.sites = []
        self.name = kwargs['name'] if 'name' in kwargs else ''

    def __repr__(self):
        return "%s %s %s\n\n%s" % (self.name, self.unit_cell_size_x, self.unit_cell_size_y, self.sites)

    def add_site(self, site):
        """Add a new site to a lattice
        """
        self.sites.append(site)

    def get_coords(self, site):
        """Return simple numerical representation of coordinates
        """
        local_site = filter(lambda x: x.name == site.coord.name, self.sites)[0]
        local_coords = local_site.site_x, local_site.site_y
        global_coords = site.coord.offset[0]*self.unit_cell_size_x, site.coord.offset[1]*self.unit_cell_size_y
        coords = [ x + y for (x, y) in zip(global_coords, local_coords) ]
        return coords


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
    attributes = ['offset', 'name', 'lattice']
    def __init__(self, **kwargs):
        if kwargs.has_key('string'):
            raw = kwargs['string'].split('.')
            if len(raw) == 2 :
                self.name = raw[0]
                self.offset = eval(raw[1])
                self.lattice = ''
            elif len(raw) == 1 :
                self.name = raw[0]
                self.offset = [0, 0]
                self.lattice = ''
            elif len(raw) == 3 :
                self.name = raw[0]
                self.lattice = raw[2]
                if raw[1]:
                    self.offset = eval(raw[1])
                else:
                    self.offset = [0, 0]
            else:
                raise TypeError, "Coordinate specification %s does not match the expected format" % raw

        else:
            Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return '%s.%s.%s' % (self.name, tuple(self.offset), self.lattice)

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


class LatticeList(Settable):
    """A list of lattices
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Lattices'
        Settable.__init__(self, **kwargs)


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
        Settable.__init__(self, email='', author='', debug=0, model_name='', model_dimension=0)

    def add(self, attrib):
        for key in attrib:
            if key in ['debug', 'model_dimension']:
                self.__setattr__(key, int(attrib[key]))
            else:
                self.__setattr__(key, attrib[key])


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
