#!/usr/bin/python
"""This module reads an XML file and create a kMC Fortran
code from it

 Copyright (C)  2009-2010 Max J. Hoffmann

 This file is part of kmos.

 kmos is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 kmos is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with kmos; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
 USA
"""

from lxml import etree as et
import os
import optparse
import re
import pprint
import numpy
from string import Template

DTD_FILENAME = '../scripts/process_list.dtd'


class OptionParser(optparse.OptionParser):
    """This class should assist in creating a kMC simulation
    by reading an XML file and creating the corresponding Fortran
    source code"""
    def check_required(self, opt):
        """Little extension of OptionParser: allows to efficiently check
         for presence of required options
         """
        option = self.get_option(opt)
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)


class ProcessList():
    """Constructor for process list object. Expects the
        filename of an xml file as input.
    """
    def __init__(self, options):
        """Constructor method"""
        if hasattr(options,'dtd_filename'):
            DTD_FILENAME = options.dtd_filename
        validate_xml(options.xml_filename, DTD_FILENAME)
        self.xmlparser = et.XMLParser(remove_comments=True)
        self.root = et.parse(options.xml_filename, parser=self.xmlparser).getroot()

        # Initialize fields
        self.meta = {}
        self.meta['emptys'] = []
        self.procs = {}
        self.site_types = []
        self.species = {}
        self.parameters = []
        self.options = options

        self.plists = self.flatten(self.root)
        self.pythonize_xml()
        for plist in self.plists:
            self.pythonize_plist(plist)
        self.check_consistency()
        self.write_source_code()
        #self._write_io_template()
        #self._write_lattice_template()
        #sketches not satisfying yet, deferred
        #self.write_tex_code()

    def _out(self, line):
        """Write source code to previously defined source file"""
        source_file = open(self.meta['source_file'],'a')
        source_file.write(str(line)+'\n')
        source_file.close()

    def _tout(self, line):
        """Write LaTeX code to previously defined TeX file"""
        source_file = open(self.meta['tex_file'],'a')
        source_file.write(str(line)+'\n')
        source_file.close()

    def pythonize_plist(self, proclist):
        """Put XML information for one process list in more accessible
        (pythonic) data format
        """

        lattice = proclist.attrib['lattice']
        for process in proclist:
            if self.multilattice :
                procname = lattice + '_' + process.attrib['name']
            else:
                procname =  process.attrib['name']
            if not self.procs.has_key(procname):
                self.procs[procname] = {}

                # Each process inherits the lattice from the (mandatory) process list attribute
                # which can then be viewed as a real list
                self.procs[procname]['lattice'] = lattice
                self.procs[procname]['condition_list'] = []
                self.procs[procname]['action'] = []
            if process.attrib.has_key('rate'):
                self.procs[procname]['rate'] = process.attrib['rate']
            for elem in process:
                if elem.tag == 'condition_list':
                    self.procs[procname]['condition_list'].append({})
                    self.procs[procname]['condition_list'][-1]\
                        ['conditions'] = []
                    if elem.attrib.has_key('suffix'):
                        suffix = elem.attrib['suffix']
                        self.procs[procname]['condition_list'][-1]\
                            ['suffix'] = suffix
                    if elem.attrib.has_key('rate'):
                        self.procs[procname]['condition_list'][-1]\
                            ['rate'] = elem.attrib['rate']
                    elif self.procs[procname].has_key('rate'):
                        self.procs[procname]['condition_list'][-1]\
                            ['rate'] = self.procs[procname]['rate']
                    elif self.rates_specified:
                        self.procs[procname]['condition_list'][-1]\
                            ['rate'] = 0.
                        if elem.attrib.has_key('suffix'):
                            print("Warning: you seem to have forgotten a rate for " + procname + '_' + suffix)
                        else:
                            print("Warning: you seem to have forgotten a rate for " + procname + '_... ')
                    for condition in elem:
                        self.procs[procname]['condition_list'][-1]\
                            ['conditions'].append({})
                        for key in condition.attrib:
                            if key == 'coordinate':
                                try:
                                    coordinate = numpy.\
                                        fromstring(condition.\
                                        attrib[key],sep=' ', dtype=int)
                                    self.procs[procname]\
                                        ['condition_list'][-1]\
                                        ['conditions'][-1][key] = \
                                        coordinate
                                except:
                                    raise ConsistencyError('Coordinates'
                                    ' need to be specified like e.g.'+
                                    '"x y", i.e. integer numbers'
                                    ' separated by a space: ' +
                                    str(condition.attrib[key]))
                            else:
                                self.procs[procname]['condition_list']\
                                    [-1]['conditions'][-1][key] = \
                                    condition.attrib[key]

                        if not filter((lambda x: x['name'] == condition.attrib['type']), self.site_types):
                            print("Error: site type '" + condition.attrib['type'] + "' has not been declared!")
                            exit()
                        # If the 0,0 site has a lattice attribute and it differs from the process list lattice, than this attribute
                        # overrides the process list attribute
                        if filter((lambda x: x['name'] == condition.attrib['type']), self.site_types)[0].has_key('lattice'):
                            self.procs[procname]['condition_list'][-1]['conditions'][-1]['lattice'] = filter((lambda x: x['name'] == condition.attrib['type']), self.site_types)[0]['lattice']
                        else:
                            self.procs[procname]['condition_list'][-1]['conditions'][-1]['lattice'] = self.procs[procname]['lattice']

                elif elem.tag == 'action':
                    action = []
                    for replacement in elem:
                        action.append({})
                        for key in replacement.attrib:
                            action[-1][key] = replacement.attrib[key]
                        # Fetch old_species from condition
                        site_label = action[-1]['site']
                        for condition in self.procs[procname]['condition_list'][0]['conditions']:
                            if condition['site'] == site_label:
                                action[-1]['old_species'] = condition['species']
                    if self.procs[procname]['action']:
                        if self.procs[procname]['action'] != action:
                            print("Error: I found two definitions for " + procname + ", but with")
                            print("different resulting actions.")
                            print("This means you either have a type in your action definition or")
                            print("we are talking about to different actions and they should accordingly")
                            print("get different names. If you change names, this need to be corrected accordingly")
                            print("in the set_rates subroutine")
                            raise ConsistencyError("Contradicting action definition encountered!")
                    else:
                        self.procs[procname]['action'] = action

    def pythonize_xml(self):
        """Run over XML tree except those part, that define details
        of the process list(s) and put string in more accessible
        local data format"""

        #Prescan if we are running multi-lattice or single lattice
        plist_elems = filter((lambda x: x.tag in ['process_list','include_list']),list(self.root))
        self.multilattice = (len(plist_elems) > 1)


        #Prescan if any rate has been specified
        self.rates_specified = False
        for plist in self.plists:
            for process in plist:
                if self.rates_specified:
                    break
                if process.attrib.has_key('rate'):
                    self.rates_specified = True
                    break
                for elem in process:
                    if elem.tag == 'condition_list':
                        if elem.attrib.has_key('rate'):
                            self.rates_specified = True
                            break

        for child in self.root:
            if child.tag == 'meta':
                try:
                    self.meta['dimension'] = int(child.attrib['dimension'])
                except:
                    raise ConsistencyError('Could not convert process list '
                    'dimension to integer: %s' % child.attrib['dimension'])

                self.meta['lattice_module'] = child.attrib['lattice_module']
                self.meta['lattice_template'] = 'TMPLT_lattice_' + self.meta['lattice_module'] + '.f90'
                self.meta['name'] = child.attrib['name']

                if child.attrib.has_key('author'):
                    self.meta['author'] = child.attrib['author']
                if child.attrib.has_key('debug'):
                    self.meta['debug'] = int(child.attrib['debug'])
                    if self.meta['debug'] not in range(5):
                        print("Warning: debug level must be 0-4.")
                else:
                    self.meta['debug'] = 0
                if child.attrib.has_key('root_lattice'):
                    self.meta['root_lattice'] = child.attrib['root_lattice']

            elif child.tag == 'site_type_list':
                for site_type in child:
                    self.site_types.append(dict(site_type.attrib))
                    if site_type.attrib.has_key('lattice'):
                        if not self.meta.has_key('lattices'):
                            self.meta['lattices'] = []
                        if site_type.attrib['lattice'] not in self.meta['lattices']:
                            self.meta['lattices'].append(site_type.attrib['lattice'])
            elif child.tag == 'species_list':
                if child.attrib.has_key('empty_species'):
                    for empty in child.attrib['empty_species'].split():
                        self.meta['emptys'].append(empty)
                else:
                    if 'empty' not in self.meta['emptys']:
                        self.meta['emptys'].append('empty')

                for species in child:
                    name = species.attrib['name']
                    try:
                        id_nr = int(species.attrib['id'])
                        self.species[name] = id_nr
                    except:
                        raise ConsistencyError('Could not convert species'
                        ' id to int: %s %s' % (name, species.attrib['id']))

            elif child.tag == 'process_list':
                if not self.meta.has_key('lattices'):
                    self.meta['lattices'] = []
                if child.attrib['lattice'] not in self.meta['lattices']:
                    self.meta['lattices'].append(child.attrib['lattice'])


                if hasattr(self.options,'proclist_filename'):
                    self.meta['source_file'] = self.options.proclist_filename
                else:
                    self.meta['source_file'] = 'proclist_' + self.meta['name'] + '.f90'
                self.meta['io_template'] = 'TMPLT_io_' + self.meta['name'] + '.f90'
                self.meta['tex_file'] = 'proclist_' + self.meta['name'] + '.tex'
                # Parse xtra args
                # Deprecated feature, use in XML file discouraged
                if child.attrib.has_key('xtra_args'):
                    try:
                        xtra_args = eval(child.attrib['xtra_args'])
                    except:
                        print(child.attrib['xtra_args'],'Can\'t parse')
                        exit()
                    if not type(xtra_args) == type({}):
                        print(xtra_args,' has to be a python dictionary { name : declaration}')
                        exit()
                else:
                    xtra_args = {}
                if xtra_args:
                    self.xtra_args = ', ' + ', '.join(xtra_args.keys())
                else:
                    self.xtra_args = ''
                self.xtra_args_def = ''
                for arg in xtra_args:
                    self.xtra_args_def += ('    ' + xtra_args[arg] + ', intent(in) :: ' + arg + '\n')


            elif child.tag == 'parameter_list':
                for parameter in child:
                    self.parameters.append(dict(parameter.attrib))



    def flatten(self,node):
        """Function that scans kMC XML document for process_list and
        include_list tags and merges them into a big one
        """
        plists = []
        for child in node:
            if child.tag == 'process_list':
                plists.append(child)
            elif child.tag == 'include_list':
                linked_xml = child.attrib['source']
                validate_xml(linked_xml, DTD_FILENAME)
                root = et.parse(linked_xml, parser=self.xmlparser).getroot()
                plists += self.flatten(root)
        return plists




    def check_consistency(self):
        """Performs several consistency checks of
            a given XML process list
        """

        # Check if process list name is valid
        if not is_name_string(self.meta['name']):
            raise ConsistencyError('Process list name is not well formed.')

        # Make sure every process name is a valid namestring
        for key in sorted(self.procs):
            if not is_name_string(key):
                raise ConsistencyError('%s is not a well-formed string for a '
                    'process name' % key)


        # Check if dimensionality is integer number
        # Already happens when pythonizing


        # Check if process names are valid
        for proc in sorted(self.procs):
            if not is_name_string(str(proc)):
                raise ConsistencyError('%s is not a well-formed name for a '
                    'process' % str(proc))
        # Check site_type list contains only unique values
        if not list_unique(self.site_types):
            raise ConsistencyError('List of site types needs to be unique: '
                '%s.' % str(self.site_types))

        # Check if species names and ids are valid
        for key in self.species:
            if not is_name_string(key):
                raise ConsistencyError('%s is not a well-formed species name'
                    % str(self.species))
        # Int checking already happens when pythonizing
        for procname in self.procs:
            proc = self.procs[procname]
            site_labels = []
            if len(proc['condition_list']) > 1 :
                suffix_list = []
            # Check if each subcondition has a suffix, if there is more than one
            for conditions in proc['condition_list']:
                # Check if there is at least one site with no relative offset
                if not filter((lambda x: not x['coordinate'].any()),conditions['conditions']):
                    print("Found no site, without relative offset but I need this!")
                    print(procname)
                    print(conditions); exit()

                if len(proc['condition_list']) > 1 :
                    if not conditions.has_key('suffix'):
                        raise ConsistencyError('Every set of conditions needs a'
                            ' suffix like left, up, ... if there is more than '
                            'one')
                    else:
                        suffix_list.append(conditions['suffix'])
                for condition in conditions['conditions']:
                    # Check if species name used in condition is defined
                    if not condition['species'] in self.species.keys():
                        raise ConsistencyError('Species "%s" is not defined in '
                            'species list.' % condition['species'])
                    # Check if coordinate has correct dimension
                    if not condition['coordinate'].size == \
                        self.meta['dimension']:
                        raise ConsistencyError('Coordinate %s does not have '
                            'the right dimension %d.' %
                            (str(condition['coordinate']),
                            self.meta['dimension']))
                    # Check if site label used in condition is valid name string
                    if not is_name_string(condition['site']):
                        raise ConsistencyError('Site label %s does not comply '
                            'to naming rules.' % condition['site'])
                    else:
                        site_labels.append(condition['site'])
                    if condition.has_key('site_type'):
                        # Check if site type name is valid name string
                        if not is_name_string(condition['site_type']):
                            raise ConsistencyError('Site type "%s" is not a '
                                'valid name string.' % condition['site_type'])
                        # Check if site type name is defined
                        if not condition['site_type'] in self.site_types:
                            raise ConsistencyError('Site type "%s" is not '
                                'defined.' % condition['site_type'])
            if len(proc['condition_list']) > 1 :
                if not list_unique(suffix_list):
                    raise ConsistencyError('Elements of suffix list have to be '
                        'unique: %s ' % str(suffix_list))

            for action in proc['action']:
                # Check if old species name used in replacement rule is defined
                if not action['old_species'] in self.species.keys():
                    raise ConsistencyError('Old species "%s" is not defined.' %
                        action['old_species'])

                # Check if new species name used in replacement rule is defined
                if not action['new_species'] in self.species.keys():
                    raise ConsistencyError('New species "%s" is not defined.' %
                        action['new_species'])

                # Check if site label used in replacement rule is defined
                if not action['site'] in site_labels:
                    raise ConsistencyError('Site label "%s" is not defined.' %
                        action['site'])

                #Check if parameters are defined only once
                doublettes = filter((lambda x: self.parameters.count(x) > 1),self.parameters)
                doublettes = list(set(doublettes))
                for doublette in doublettes:
                    raise ConsistencyError(doublette + ' is defined as a parameter more than once')


    def _write_lattice_template(self):
        """Write template file for lattice_module
        """

        if os.path.exists(self.meta['lattice_template']) and not self.options.force_overwrite:
            owrite = raw_input('File ' + self.meta['lattice_template'] + ' exists, overwrite [Y/n]:')
            if owrite in ['Y', 'y', '']:
                os.system('rm -rf ' + self.meta['lattice_template'])
            else:
                return
        template = open(self.meta['lattice_template'],'w')
        template.write('module lattice_' + self.meta['lattice_module'] + '\n\n')
        template.write('use kind_values\n')
        template.write("""use base, only: &
    assertion_fail, &
    deallocate_system, &
    get_kmc_step, &
    get_kmc_time, &
    get_kmc_time_step, &
    base_get_rate => get_rate, &
    base_increment_procstat => increment_procstat, &
    increment_procstat, &
    base_add_proc => add_proc, &
    base_allocate_system => allocate_system, &
    base_can_do => can_do, &
    base_del_proc => del_proc, &
    determine_procsite, &
    base_replace_species => replace_species, &
    base_get_species => get_species, &
    base_get_volume  => get_volume, &
    base_reload_system => reload_system, &
    null_species, &
    reload_system, &
    reset_site, &
    save_system, &
    base_set_rate => set_rate, &
    update_accum_rate, &
    update_clocks\n\n""")
        template.write('implicit none\n\n')

        if self.species:
            template.write('integer(kind=iint), parameter :: &\n')
        for species in self.species.keys()[:-1]:
            template.write(4*' ' + species + ' = ' + str(self.species[species]) + ', &\n')
        template.write(4*' ' + self.species.keys()[-1] + ' = ' + str(self.species[self.species.keys()[-1]]) + '\n\n')
        template.write('\n\ncontains\n\n')
        for lattice in self.meta['lattices']:
            # Write mapping function templates
            template.write('subroutine nr2' + lattice + '(nr, ' + lattice + ')\n')
            template.write(4*' ' + 'integer(kind=iint), intent(in) :: nr\n')
            template.write(4*' ' + 'integer(kind=iint), dimension(' + str(self.meta['dimension']) + '), intent(out) :: ')
            template.write(lattice + '\n\n')
            template.write(4*' ' + '! PLEASE FILL OUT CORRECTLY :-)\n')
            template.write('end subroutine nr2' + lattice + '\n\n\n')
            template.write('subroutine ' + lattice + '2nr(' + lattice + ', nr)\n')
            template.write(4*' ' + 'integer(kind=iint), dimension(' + str(self.meta['dimension']) + '), intent(in) :: ')
            template.write(lattice + '\n')
            template.write(4*' ' + 'integer(kind=iint), intent(out) :: nr\n\n')
            template.write(4*' ' + '! PLEASE FILL OUT CORRECTLY :-)\n')
            template.write('end subroutine ' + lattice + '2nr\n\n\n')

        # Automatically generatoe cross transformations
        template.write(self.write_cross_transformations())

        for lattice in self.meta['lattices']:
            # Add proc
            add_proc = """
subroutine %(latt)s_add_proc(proc, site)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(%(dim)s), intent(in) :: site
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    call %(latt)s2nr(site, nr)
    call base_add_proc(proc, nr)

end subroutine %(latt)s_add_proc
"""
        template.write(add_proc % {'latt' : lattice, 'dim': self.meta['dimension']})

        # del proc
        del_proc = """
subroutine %(latt)s_del_proc(proc, site)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(%(dim)s), intent(in) :: site
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    call %(latt)s2nr(site, nr)
    call base_del_proc(proc, nr)

end subroutine %(latt)s_del_proc
"""
        template.write(del_proc % {'latt' : lattice, 'dim': self.meta['dimension']})

        # replace species
        replace_species = """
subroutine %(latt)s_replace_species(site, old_species, new_species)
    !---------------I/O variables---------------
    integer(kind=iint), dimension(%(dim)s), intent(in) :: site
    integer(kind=iint), intent(in) :: old_species, new_species
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    call %(latt)s2nr(site, nr)
    call base_replace_species(nr, old_species, new_species)

end subroutine %(latt)s_replace_species
"""
        template.write(replace_species % {'latt' : lattice, 'dim': self.meta['dimension']})

        # get_species
        get_species = """
subroutine %(latt)s_get_species(site, return_species)
    !---------------I/O variables---------------
    integer(kind=iint), dimension(%(dim)s), intent(in) :: site
    integer(kind=iint), intent(out) :: return_species
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    call %(latt)s2nr(site, nr)
    call base_get_species(nr, return_species)

end subroutine %(latt)s_get_species
"""
        template.write(get_species % {'latt' : lattice, 'dim': self.meta['dimension']})

        # can do
        can_do = """
subroutine %(latt)s_can_do(proc, site, can)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(%(dim)s), intent(in) :: site
    logical, intent(out) :: can
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    call %(latt)s2nr(site, nr)
    call base_can_do(proc, nr, can)

end subroutine %(latt)s_can_do
"""
        template.write(can_do % {'latt' : lattice, 'dim': self.meta['dimension']})


        # reset_site
        reset_site = """
subroutine %(latt)s_reset_site(site, old_species)
    !---------------I/O variables---------------
    integer(kind=iint), dimension(%(dim)s), intent(in) :: site
    integer(kind=iint) :: old_species
    !---------------internal variables---------------
    integer(kind=iint) :: nr_site

    call %(latt)s2nr(site, nr_site)
    call reset_site(nr_site, old_species)

end subroutine %(latt)s_reset_site
"""
        template.write(reset_site % {'latt' : lattice, 'dim': self.meta['dimension']})


        template.write('\n\nend module lattice_' + self.meta['lattice_module'] + '\n')
        template.close()



    def _write_io_template(self):
        """Write template file for io_module
        """
        if os.path.exists(self.meta['io_template']) and not self.options.force_overwrite:
            owrite = raw_input('File ' + self.meta['io_template'] + ' exists, overwrite [Y/n]:')
            if owrite in ['Y', 'y', '']:
                os.system('rm -rf ' + self.meta['io_template'])
            else:
                return
        iotemplate = open(self.meta['io_template'],'w')
        iotemplate.write('module io_' + self.meta['name']+'\n\n')
        iotemplate.write('use units\n')
        iotemplate.write('use kind_values\n')
        iotemplate.write('use proclist_'+self.meta['name'] + '\n')
        iotemplate.write('use lattice_' + self.meta['lattice_module'] + '\n\n')
        iotemplate.write('\n! Physical parameters\n')
        for parameter in self.parameters:
            if parameter.has_key('type'):
                if parameter['type'] != 'none':
                    iotemplate.write(parameter['type'] + ', public :: ' + parameter['name'] + '\n')
            else:
                iotemplate.write('real(kind=rsingle), public :: ' + parameter['name'] + '\n')

        iotemplate.write('\ncontains\n\n')
        iotemplate.write("""subroutine parse_commandline()
    !---------------internal variables---------------
    integer(kind=iint), parameter :: needed_args = 1
    character(len=200), dimension(:), allocatable :: command_line
    integer :: nr_args, i
    character(len=200) :: control_file

    nr_args = command_argument_count()
    allocate(command_line(0:nr_args))
    call GET_COMMAND(command_line(0))

    if(nr_args.ne.needed_args) then
        write(*,'(40a)')'Usage:',trim(adjustl(command_line(0))),' (<control_file>|help)'
        stop
    endif

    do i =1, needed_args
        call GET_COMMAND_ARGUMENT(i,command_line(i))
    enddo

    read(command_line(1),*)control_file

    call parse_controlfile(control_file)

end subroutine parse_commandline\n""")
        iotemplate.write("""
subroutine parse_controlfile(control_file)
    character(len=*),intent(in) :: control_file
    !---------------internal variables---------------
    integer, parameter :: filehandler = 17
    integer :: io_state, line, pos
    logical :: file_exists
    character(len=100) :: label
    character(len=10**4) :: buffer
    character(len=10**4) :: empty_line  = ""

    if(trim(adjustl(control_file)).eq."help")then
        ! Print help message and exit
        print *,""
        print *,"     All parameters are supplied via a single ASCII file,"
        print *,"     whose name is read from the command line."
        print *,"     Inside the ASCII file values are specified in the format"
        print *,"     <label> value"
        print *,""
        print *,"     Upper/lower case is not ignored."
        print *,"     More labels will be added in the future, so check back"
        print *,"     frequently. Also for correct functioning specify all values"
        print *,"     since default values are not set. The labels can be speci-"
        print *,"     fied in arbitrary order and any line starting with 0 or"
        print *,"     more space character follow by a '#' are ignored as well"
        print *,"     as well as blank lines."
        print *,""\n""")
        iotemplate.write('        print *,"     Accepted fields are:"\n')
        iotemplate.write('        print *,""\n')
        for parameter in self.parameters:
            iotemplate.write('        print *,"        ' + parameter['name'] + '"\n')


        iotemplate.write("""        print *,""; print *,""

    else
        ! Check if control file exists
        inquire(file=trim(adjustl(control_file)),exist=file_exists)
        if(.not. file_exists)then
            print *,"Control file not found!"
            stop
        endif
    endif


    ! Open control file
    open(filehandler, file = control_file)

    ! Read control file
    io_state = 0
    line = 0
    do while(io_state == 0)
        read(filehandler, '(a)', iostat = io_state) buffer
        if(io_state == 0) then
            ! advance line number
            line = line + 1
            ! Shuffle all non-space characters to the left
            buffer = adjustl(buffer)


            ! Ignore comment lines
            if(buffer(1:1) == '#')then
                cycle
            endif
            ! Ignore empty lines
            if(buffer(:).eq.empty_line)then
                cycle
            endif

            ! Find position of first space
            pos = scan(buffer, ' ')
            ! Store everything before pos in label
            label = buffer(1:pos)
            ! Everythings else remains in the buffer
            buffer = buffer(pos+1:)

            select case(label)\n""")
        for parameter in self.parameters:
            iotemplate.write("            case('" + parameter['name'] + "')\n")
            iotemplate.write("                read(buffer,*,iostat = io_state) " + parameter['name'] + "\n")

        iotemplate.write("""            case default
                print *,"Warning: unrecognized keyword: "//trim(adjustl(label))
                stop
            endselect

        endif
    enddo

    close(filehandler)


    if(io_state>0)then
        print *,"Some read error occured in the read input loop, investigate!"
        stop
    endif




end subroutine parse_controlfile\n""")
        iotemplate.write('\n\nsubroutine set_rates()\n')
        iotemplate.write('    !---------------internal variables---------------\n')
        iotemplate.write('    real(kind=rsingle) :: rate\n\n')
        if self.rates_specified:
            for proc in sorted(self.procs):
                for conditions in self.procs[proc]['condition_list'] :
                    if conditions.has_key('rate'):
                        iotemplate.write('    rate = ' + str(conditions['rate']) + '\n')
                        if(conditions.has_key('suffix')):
                            suffix = '_' + conditions['suffix']
                        else:
                            suffix = ''
                        process_name = proc +  suffix
                        iotemplate.write('    call set_rate(' + process_name + ', rate)\n\n')
        else:
            iotemplate.write('     ! rate = ...')
            iotemplate.write('     ! call set_rate(process_name, rate)')
        iotemplate.write('\n\nend subroutine set_rates')
        iotemplate.write('\n\nsubroutine print_rates()\n')
        iotemplate.write('\n    real(kind=rsingle) :: rate\n\n')
        iotemplate.write('    print *,"' + self.meta['name'].capitalize() + ' rates"\n')
        iotemplate.write('    print *,"--------------------------------"\n')
        if self.rates_specified:
            for proc in sorted(self.procs):
                iotemplate.write('\n\n    ! ' + proc.upper() + '\n')
                for conditions in self.procs[proc]['condition_list'] :
                    if conditions.has_key('rate'):
                        if(conditions.has_key('suffix')):
                            suffix = '_' + conditions['suffix']
                        else:
                            suffix = ''
                        process_name = proc +  suffix
                        iotemplate.write('    call get_rate(' + process_name + ', rate)\n')
                        iotemplate.write('    print *,"' + process_name + '", rate\n\n')
        else:
            iotemplate.write('     print *, " NO RATES SPECIFIED IN XML INPUT"\n')
        iotemplate.write('    print *,"--------------------------------"\n')
        iotemplate.write('\n\nend subroutine print_rates\n')
        iotemplate.write('\n\nend module io_' + self.meta['name'] + '\n')
        iotemplate.close()
        print("Wrote template for I/O module to " + iotemplate.name)


    def write_tex_code(self):
        """Produce a nice TeX output with sketches to be read by
        human beings
        """
        s = Template(r"""\documentclass[english]{article}
\usepackage[T1]{fontenc}
\usepackage[latin9]{inputenc}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage[numbers]{natbib}

\makeatletter
\newif\iffinal % introduce a switch for draft vs. final document
%\finaltrue % use this to compile the final document

% [more preamble that in my case also uses \iffinal for other stuff]
\usepackage[top=1cm,bottom=1.5cm]{geometry}
\usepackage[hang,small,bf]{caption}
\setlength{\captionmargin}{20pt}

\usepackage{tikz}
\usetikzlibrary{fit}
\usetikzlibrary{decorations.pathmorphing}
\usetikzlibrary{calc}
\usetikzlibrary{shapes.geometric}
\usetikzlibrary{shapes.misc}
\pgfrealjobname{$name}

\iffinal
  \newcommand{\inputTikZ}[1]{%
    \input{#1.tikz}%
  }
\else
  \newcommand{\inputTikZ}[1]{%
    \beginpgfgraphicnamed{#1-external}%
    \input{#1.tikz}%
    \endpgfgraphicnamed%
  }
\fi

\@ifundefined{showcaptionsetup}{}{%
 \PassOptionsToPackage{caption=false}{subfig}}
\usepackage{subfig}
\makeatother

\usepackage{babel}

\begin{document}
{\noindent \sf \ \hfill \today}\\
        """)
        self._tout(s.substitute(name = 'proclist_' + self.meta['name']))
        self._tout("\subsection*{The " + self.meta['name'].replace('_', ' ').capitalize() + " Process List}")

        self._tout(r"""
\subsubsection*{Description Scheme}

The proposed kinetic Monte Carlo (kMC) process list  is explained here in a somewhat formalized way.
Each elementary process is stated as follows:\\


\emph{\{Diagrams\} }\{species\} can \{adsorb | desorb | diffuse |
react \} \{ \{on | from | to\} \{sites $\dots$\} \}

if \{condition 1 \} {[} and

\{condition 2\} 

... {]}
        """)

        self._tout(r'\subsubsection*{Process List}')
        for proc in sorted(self.procs):
            if len(self.procs[proc]['condition_list']) > 1 :
                subprocs = []
                for conditions in self.procs[proc]['condition_list']:
                    sites = []
                    for condition in conditions['conditions']:
                        sites.append(condition['site'])
                    sites.sort()
                    conditions['sites'] = sites
                    for subproc in subprocs:
                        if subproc[0]['sites'] == sites:
                            subproc.append(conditions)
                            break
                    else:
                        subprocs.append([])
                        subprocs[-1].append(conditions)
                for subproc in subprocs:
                    i = 0
                    if len(subprocs) > 1 :
                        self._tout(r'\subsubsection*{' + proc.replace('_',' ') + ' (' + str(i) + ')}')
                        i += 1
                    else:
                        self._tout(r'\subsubsection*{' + proc.replace('_',' ') + '}')

                    self._tout(r'\begin{figure}[h]\centering')
                    geom_nr = 0
                    for geom in subproc:
                        geom_nr += 1
                        self._tout('\subfloat[' + geom['suffix'].replace('_' , r'\_') + ']{ %')
                        self.generate_tikz_sketch(geom)
                        self._tout('}')
                        if geom_nr % 2 == 0 :
                            self._tout(r'\\')

                    i = 0
                    if len(subprocs) > 1 :
                        self._tout(r'\caption{Geometry for ' + proc.replace('_',' ') +  ' (' + str(i) + ')}')
                    else:
                        self._tout(r'\caption{Geometry for ' + proc.replace('_',' ') + '}')
                    self._tout(r'\end{figure}')

            else:
                self._tout(r'\subsubsection*{' + proc.replace('_',' ') + '}')
                self._tout(r'\begin{figure}[h]')
                self._tout('\centering ')
                self.generate_tikz_sketch(self.procs[proc]['condition_list'][0])
                self._tout(r'\caption{Geometry for ' + proc.replace('_',' ') + '}')
                self._tout(r'\end{figure}')


        self._tout(r'\end{document}')



    def generate_tikz_sketch(self, conditions):
        """Generates source code for a simple geometrical sketch,
        that can be turned into a real picture with sketch by Eugene Ressler
        """
        self._tout(r'\begin{tikzpicture}[ultra thick, rounded corners=2pt, line cap = round]')
        for condition in conditions['conditions']:
            self._tout(r'\node at' + str(tuple(condition['coordinate'].tolist())) + '[ circle, draw = black, fill=white]{$' + condition['site'] + '$};')
        self._tout(r'\end{tikzpicture}')

    def write_source_code(self):
        """Wrapping function that writes out one proclist_ module
        calling all other sub parts."""
        if os.path.exists(self.meta['source_file']) and not self.options.force_overwrite:
            owrite = raw_input('File ' + self.meta['source_file'] + ' exists, overwrite [Y/n]:')
            if owrite in ['Y', 'y', '']:
                os.system('rm -rf ' + self.meta['source_file'])
            else:
                return
        elif self.options.force_overwrite:
            os.system('rm -rf ' + self.meta['source_file'])
        if os.path.exists(self.meta['tex_file']) and not self.options.force_overwrite:
            owrite = raw_input('File ' + self.meta['tex_file'] + ' exists, overwrite [Y/n]:')
            if owrite in ['Y', 'y', '']:
                os.system('rm -rf ' + self.meta['tex_file'])
            else:
                return
        elif self.options.force_overwrite:
            os.system('rm -rf ' + self.meta['tex_file'])

        self._print_gpl_message()
        self._out('module proclist')
        self._out('')
        self._out('use kind_values')
        #self._out('use base, only: null_species')
        self._out('use lattice, only: &')
        for lattice in self.meta['lattices']:
            for lattice2 in self.meta['lattices'] :
                if lattice != lattice2:
                    self._out('    ' + lattice + '2' + lattice2 + ', &')
            self._out('    nr2' + lattice + ', &')
            self._out('    ' + lattice + '2nr, &')
            self._out('    ' + lattice + '_add_proc, &')
            self._out('    ' + lattice + '_can_do, &')
            self._out('    ' + lattice + '_replace_species, &')
            self._out('    ' + lattice + '_del_proc, &')
            self._out('    ' + lattice + '_get_species, &')
        self._out('    increment_procstat, &')

        for species in self.species.keys()[:-1]:
            self._out('    '+species+', &')
        self._out('    '+self.species.keys()[-1])
        self._out('\nimplicit none')
        #self.write_interface()
        #self.write_species_definitions()
        self.write_process_list_constants()
        self._out('\ncontains\n')
        self.write_run_proc_nr_function()
        self.write_atomic_update_functions()
        self.writeTouchupFunction()
        self.write_check_functions()
        self._out('end module proclist')
        print("Wrote module proclist_" + self.meta['name'] + ' to ' + self.meta['source_file'])



    def write_species_definitions(self):
        """Write out the list of species, where each one refers to one species in the system"""
        self._out('\n! Species constants')
        for species in self.species:
            self._out('integer(kind=iint), parameter, public :: ' + species + ' = ' + str(self.species[species]))

    def write_process_list_constants(self):
        """Writes out the list of constants, where each refers to one
        process in the process list."""
        i = 0
        self._out('\n! Process constants')
        for proc in sorted(self.procs):
            for conditions in self.procs[proc]['condition_list']:
                i += 1
                if conditions.has_key('suffix'):
                    self._out('integer(kind=iint), parameter, public :: ' + proc  + '_' + conditions['suffix'] + ' = ' + str(i))
                else:
                    self._out('integer(kind=iint), parameter, public :: ' + proc  + ' = ' + str(i))
        self._out('\ninteger(kind=iint), parameter, public :: nr_of_proc = ' + str(i))

    def write_interface(self):
        """Writes source code for which subroutines are public and which
        are private
        """
        self._out('\nprivate')
        self._out('public :: &')
        for typ in self.site_types:
            self._out('    touchup_' + typ + '_site, &')
        self._out('    nr_of_proc, &\n    run_proc_nr')


    def write_check_functions(self):
        """Simply iterates over process list and write check_function for reach."""
        for process in sorted(self.procs):
            for conditions in self.procs[process]['condition_list']:
                self.write_check_function(process, conditions)
                self._out('')
                self._out('')


    def write_check_function(self, process, conditions):
        """The check functions are building-blocks that check for one
        specific process if all conditions are met, so it can be executed
        at 'site'
        """
        if conditions.has_key('suffix') :
            function_name = 'subroutine check_' + process + '_' + conditions['suffix']
        else:
            function_name = 'subroutine check_' + process


        name = filter((lambda x: not x['coordinate'].any()),conditions['conditions'])[0]['site']
        root_lattice = filter((lambda x: x['site'] == name),conditions['conditions'])[0]['lattice']
        involved_lattices = []
        for condition in conditions['conditions']:
            lattice = condition['lattice']
            if lattice != root_lattice and not lattice in involved_lattices:
                involved_lattices.append(lattice)

        self._out(function_name + '(site, can)')
        self._out('    !-----------------I/O variables-------------------')
        self._out('    integer(kind=iint), intent(in), dimension(' + str(self.meta['dimension']) + ') :: site')
        self._out('    logical, intent(out) :: can')
        self._out('    !-----------------Internal variables-------------------')
        self._out('    integer(kind=iint) :: species')
        if involved_lattices:
            self._out('    integer(kind=iint) :: nr')
        for lattice in involved_lattices:
            if lattice != root_lattice:
                self._out('    integer(kind=iint), dimension(' + str(self.meta['dimension']) + ') :: ' + lattice + '_site')
        self._out('')
        self._out('    can = .true.')
        self._out('')
        if involved_lattices:
            self._out('    call '+root_lattice+'2nr(site, nr)')
        for lattice in involved_lattices:
            if lattice != root_lattice:
                self._out('    call nr2'+lattice+'(nr, ' +lattice + '_site)')
        self._out('')
        for condition in conditions['conditions']:
            if condition['coordinate'].any():
                if condition['lattice'] == root_lattice :
                    site = 'site+(/' + str(condition['coordinate'].tolist())[1 :-1] + '/)'
                else:
                    site = condition['lattice'] + '_site+(/' + str(condition['coordinate'].tolist())[1 :-1] + '/)'
            else:
                site = 'site'
            self._out('    call '+condition['lattice'] + '_get_species' + '(' + site + ', species)')
            if self.meta['debug'] > 3 :
                self._out('print \'(a,' + str(self.meta['dimension']) +'i4,a,i0,a,i0)\',"      Check if ' + site + ' (",' + site + ',") has ",' + condition['species'] + '," and found ",species')
            self._out('    if(species.ne.' + condition['species'] + ')then')
            if self.meta['debug'] > 3 :
                self._out('print \'(a)\',"      ...  negative!"')
            self._out('        can = .false.; return')
            self._out('    end if\n')
        if self.meta['debug'] > 3 :
            self._out('print \'(a)\',"      ...  positive!"')
        self._out('end ' + function_name)


    def write_cross_transformations(self):
        retstring = ''
        for l1 in self.meta['lattices']:
            for l2 in self.meta['lattices']:
                if l1 != l2:
                    retstring+='subroutine ' + l1 + '2' + l2 + '(' + l1 + '_site, ' + l2 + '_site)\n'
                    retstring+='    integer(kind=iint), dimension(' + str(self.meta['dimension']) + '), intent(in) :: ' + l1 + '_site\n'
                    retstring+='    integer(kind=iint), dimension(' +str(self.meta['dimension']) + '), intent(out) :: ' + l2 + '_site\n'
                    retstring+='    integer(kind=iint) :: nr\n\n'
                    retstring+='    call ' + l1 + '2nr(' + l1 + '_site, nr)\n'
                    retstring+='    call nr2' + l2 + '(nr, ' + l2 + '_site)\n'
                    retstring+='\nend subroutine ' + l1 + '2' + l2 + '\n\n'

        return retstring

    def _print_gpl_message(self):
        """Prints the GPL statement at the top of the source file"""
        self._out("!  This file was generated by kMOS (kMC modelling on steroids)")
        self._out("!  written by Max J. Hoffmann mjhoffmann@gmail.com (C) 2009-2010.")
        if self.meta.has_key('author') :
            self._out('!  The model was written by ' + self.meta['author'] + '.')
        self._out("""
!  This file is part of kmos.
!
!  kmos is free software; you can redistribute it and/or modify
!  it under the terms of the GNU General Public License as published by
!  the Free Software Foundation; either version 2 of the License, or
!  (at your option) any later version.
!
!  kmos is distributed in the hope that it will be useful,
!  but WITHOUT ANY WARRANTY; without even the implied warranty of
!  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
!  GNU General Public License for more details.
!
!  You should have received a copy of the GNU General Public License
!  along with kmos; if not, write to the Free Software
!  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
!  USA
""")
    def writeTouchupFunction(self):
        """This creates one subroutine per lattice type, and updates all capabilities.
        To do so, it checks the availability based on the current lattice configuration and
        based on the avail_sites database. It then makes the database entry consistent with
        the real world.
        """
        for typ in self.site_types:
            routine_name = 'subroutine '  + 'touchup_' + typ['name'] + '_site'
            self._out(routine_name + '(site' + self.xtra_args+ ')')
            self._out('    integer(kind=iint), dimension(' + str(self.meta['dimension']) + '), intent(in) :: site')
            self._out(self.xtra_args_def)
            self._out('\n    logical :: check, can\n\n')

            # Debugging statement
            if self.meta['debug'] > 1 :
                self._out('    print *,"Touching up ' + typ['name'] +' at ",site')
            # Iterate over processes
            for proc in sorted(self.procs):
                # Iterate over suffixes
                for conditions in self.procs[proc]['condition_list'] :
                    # Iterate over conditions
                    for condition in conditions['conditions']:
                        if (condition['coordinate']==numpy.zeros(self.meta['dimension'])).all() and typ['name'] == condition['type']:
                            if conditions.has_key('suffix'):
                                full_proc = proc + '_' + conditions['suffix']
                            else:
                                full_proc = proc
                            # Debugging statement
                            if self.meta['debug'] > 2 :
                                self._out('    print *," ... regarding ' + full_proc + '"')
                            # Checks if the avail_site db says, we can do it
                            self._out('    call ' + condition['lattice'] + '_can_do(' + full_proc + ', site' + self.xtra_args + ', can=can)')
                            # Checks if we can do it looking at the actual lattice
                            self._out('    call check_' + full_proc + '(site, check)')
                            self._out('    if(check .and. .not. can)then')
                            if self.meta['debug'] > 2 :
                                self._out('        print \'(a,' + str(self.meta['dimension']) + 'i3)\',"         Adding ' + full_proc + ' to", site')
                            self._out('        call ' + condition['lattice'] + '_add_proc(' + full_proc + ', site' + self.xtra_args + ')')
                            self._out('    else if(.not. check .and. can)then')
                            if self.meta['debug'] > 2 :
                                self._out('        print \'(a,' + str(self.meta['dimension']) + 'i3)\',"         Deleting ' + full_proc + ' from", site')
                            self._out('        call ' + condition['lattice'] + '_del_proc(' + full_proc + ', site' + self.xtra_args + ')')
                            self._out('    end if\n')

            self._out('end ' +routine_name + '\n\n')

    def write_atomic_update_functions(self):
        """Here we write the most complex part of the program:
        we write two functions per lattice and species: a take and a put function.
        From this we can put together all the more complex processes."""
        update_functions = []

        def bout(line):
            """Ugly hack function to get procedure body behind declaration statement
            however declaration statement could not be completed without writing the body
            """
            self.body += line + '\n'
        # Collect all update functions we need
        for proc in sorted(self.procs):
            for replacement in self.procs[proc]['action']:
                for conditions in self.procs[proc]['condition_list'] :
                    for condition in conditions['conditions']:
                        if replacement['site'] == condition['site']:
                            if condition.has_key('type'):
                                typ = condition['type']
                                root_lattice = condition['lattice']
                                break
                            else:
                                typ = ''
                                root_lattice = ''
                                break
                    if replacement['old_species'] in self.meta['emptys'] and replacement['new_species'] not in self.meta['emptys'] :
                        update_function = UpdateFunction('put', replacement['new_species'], typ, root_lattice, replacement['old_species'])
                        if update_function not in update_functions:
                            #print("appending put " + str(update_function) + ' to ' + str(sorted(update_functions)))
                            update_functions.append(update_function)
                    elif replacement['old_species'] not in self.meta['emptys'] and replacement['new_species'] in self.meta['emptys']  :
                        update_function = UpdateFunction('take', replacement['old_species'], typ, root_lattice, replacement['new_species'])
                        if update_function not in update_functions:
                            #print("appending take " + str(update_function) + ' to ' + str(sorted(update_functions)))
                            update_functions.append(update_function)
                    else:
                        print(replacement['old_species'],replacement['new_species'],self.meta['emptys'])
                        print(proc, replacement, "One species must be 'empty' and the other mustn't!")

        # Write the update functions
        for update_function in update_functions:
            self.body = ""
            need_dummy_site = False
            # Determine first, which lattice we start with
            root_lattice = update_function.lattice
            involved_lattices = []
            # Add needed update function to each update function
            self._out('subroutine ' + str(update_function) + '(site' + self.xtra_args + ')')
            self._out(self.xtra_args_def)
            self._out('    integer(kind=iint), dimension(' + str(self.meta['dimension']) + '), intent(in) :: site')
            if self.meta['debug'] > 1 :
                if update_function.action == 'put':
                    bout('    print \'(a,' +str(self.meta['dimension'])+ 'i5)\',"    Trying to put ' + update_function.species + ' on (' + root_lattice + ')",site')
                elif update_function.action == 'take':
                    bout('    print \'(a,' +str(self.meta['dimension'])+ 'i5)\',"    Trying to take ' + update_function.species + ' from (' + root_lattice + ')",site')

            # print lattice updates
            bout('    ! lattice updates')
            if update_function.action == 'put':
                bout('    call ' + update_function.lattice + '_replace_species(site' +  ', ' + update_function.other_species + ', ' + update_function.species + ')')
            elif update_function.action == 'take':
                bout('    call ' + update_function.lattice + '_replace_species(site' +  ', ' + update_function.species + ', ' + update_function.other_species + ')')
            else:
                print('Cannot get here')

            # print avail_sites updates
            bout('    ! book keeping updates')
            # Iterate over processes
            for proc in sorted(self.procs):
                # Iterate over suffixes
                for conditions in self.procs[proc]['condition_list']:
                    involved_lattice = filter((lambda x: not x['coordinate'].any()),conditions['conditions'])[0]['lattice']
                    if(conditions.has_key('suffix')):
                        suffix = '_' + conditions['suffix']
                    else:
                        suffix = ''
                    process_name = proc +  suffix
                    # Iterate over conditions
                    for condition in conditions['conditions']:
                        if condition['coordinate'].any():
                            if involved_lattice == root_lattice :
                                # if both sites are on the same lattice, no conversion neccessary
                                site = 'site-(/' + str(condition['coordinate'].tolist())[1 :-1] + '/)'
                            else:
                                # let figure out, which route we go in the conversion
                                if self.meta.has_key('root_lattice') and self.meta['root_lattice'] != involved_lattice:
                                    dummy_call = '    call ' + root_lattice + '2' + involved_lattice + '(site - (/' +str(condition['coordinate'].tolist())[1 :-1] + '/), dummy_site)'
                                    site = 'dummy_site'
                                    need_dummy_site = True
                                else:
                                    site = involved_lattice + '_site-(/' + str(condition['coordinate'].tolist())[1 :-1] + '/)'
                        else:
                            site = 'site'
                        if condition['type'] == update_function.type :
                            if involved_lattice not in involved_lattices :
                                involved_lattices.append(involved_lattice)
                            if update_function.action == 'put':
                                if condition['species'] in self.meta['emptys']:
                                # breaking, call can_do
                                    if site == 'dummy_site':
                                        bout(dummy_call)
                                    bout('    call ' + involved_lattice + '_can_do(' + process_name + ', ' + site + self.xtra_args + ', can=can)')

                                    # debug statement
                                    if self.meta['debug'] > 3 :
                                        bout('    print \'(a,' + str(self.meta['dimension']) + 'i3,a,l2)\',"      Checked if ",' + site + '," can do ' + process_name + '",can')
                                    bout('    if(can)then')
                                    # debug statement
                                    if self.meta['debug'] > 2 :
                                        bout('        print \'(a,' + str(self.meta['dimension']) + 'i3)\',"        Deleting ' + process_name + ' from", ' + site)
                                    bout('        call ' + involved_lattice + '_del_proc(' + process_name + ', ' + site + self.xtra_args + ')')
                                    bout('    end if')
                                elif condition['species'] == update_function.species:
                                # maybe fulfill condition, call check_... function
                                    if site == 'dummy_site':
                                        bout(dummy_call)
                                    bout('    call check_' + process_name + '(' + site + ', can=can)')
                                    # debug statement
                                    if self.meta['debug'] > 3 :
                                        bout('    print \'(a,' + str(self.meta['dimension']) + ' i3,a,l2)\',"      Checked if ",' + site + '," can do ' + process_name + '",can')
                                    bout('    if(can)then')
                                    # debug statement
                                    if self.meta['debug'] > 2 :
                                        bout('        print \'(a,' + str(self.meta['dimension']) + 'i3)\',"         Adding ' + process_name + ' to", ' + site)
                                    bout('        call ' + involved_lattice + '_add_proc(' + process_name + ', ' + site + self.xtra_args + ')')
                                    bout('    end if')
                            elif update_function.action == 'take':
                                if condition['species'] in self.meta['emptys']:
                                    # maybe fulfill condition, call check_... function
                                    if site == 'dummy_site':
                                        bout(dummy_call)
                                    bout('    call check_' + process_name + '(' + site + ', can=can)')
                                    # debug statement
                                    if self.meta['debug'] > 3 :
                                        bout('    print \'(a,' + str(self.meta['dimension']) + 'i3,a,l2)\',"      Checked if ",' + site + '," can do ' + process_name + '",can')
                                    bout('    if(can)then')
                                    # debug statement
                                    if self.meta['debug'] > 2 :
                                        bout('        print \'(a,' + str(self.meta['dimension']) + 'i3)\',"         Adding ' + process_name + ' to", ' + site)
                                    bout('        call ' + involved_lattice + '_add_proc(' + process_name + ', ' + site + self.xtra_args + ')')
                                    bout('    end if\n')
                                    pass
                                elif condition['species'] == update_function.species:
                                # breaking, call can_do
                                    if site == 'dummy_site':
                                        bout(dummy_call)
                                    bout('    call ' + involved_lattice + '_can_do(' + process_name + ', ' + site + self.xtra_args + ', can=can)')
                                    # debug statement
                                    if self.meta['debug'] > 3 :
                                        bout('    print \'(a,' + str(self.meta['dimension']) + 'i3,a,l2)\',"      Checked if ",' + site + '," can do ' + process_name + '",can')
                                    bout('    if(can)then')
                                    # debug statement
                                    if self.meta['debug'] > 2 :
                                        bout('        print \'(a,' + str(self.meta['dimension']) + 'i3)\',"        Deleting ' + process_name + ' from", ' + site)
                                    bout('        call ' + involved_lattice + '_del_proc(' + process_name + ', ' + site + self.xtra_args + ')')
                                    bout('    end if\n')
                            else:
                                print('Only functions allowed are put and take')
                                print(update_functions)
                                exit()
            self._out('    logical :: can\n')
            if involved_lattices:
                self._out('    integer(kind=iint) :: nr')
            for lattice in involved_lattices:
                if lattice != root_lattice:
                    self._out('    integer(kind=iint), dimension(' + str(self.meta['dimension']) + ') :: ' +lattice + '_site')
            if need_dummy_site:
                self._out('    integer(kind=iint), dimension(' + str(self.meta['dimension']) + ') :: ' + 'dummy_site')
            self._out('')
            if involved_lattices:
                self._out('    call '+root_lattice+'2nr(site, nr)')
            for lattice in involved_lattices:
                if lattice != root_lattice:
                    self._out('    call nr2'+lattice+'(nr, ' +lattice + '_site)')
            self._out('')
            # Now print the accumulated body
            self._out(self.body)

            self._out('end subroutine ' + str(update_function))
            self._out('')


    def write_run_proc_nr_function(self):
        self._out('\nsubroutine run_proc_nr(proc, site' + self.xtra_args + ')')
        self._out('    !-----------------I/O variables-------------------')
        self._out('    integer(kind=iint), intent(in) :: proc')
        self._out('    integer(kind=iint), intent(in) :: site')
        self._out(self.xtra_args_def)
        self._out('    !-----------------Internal variables-------------------\n\n')
        for lattice in self.meta['lattices']:
            self._out('    integer(kind=iint),  dimension(' + str(self.meta['dimension']) + ') :: '+ lattice +'_site')
        self._out('    ! Update process counter\n    call increment_procstat(proc' + self.xtra_args + ')\n')
        self._out('    select case(proc)')
        i = 0
        for proc in sorted(self.procs):
            for conditions in self.procs[proc]['condition_list']:
                i += 1
                if conditions.has_key('suffix'):
                    self._out('    case('+proc+'_'+conditions['suffix']+ ')! #'+str(i))
                else:
                    self._out('    case ('+proc+')! #'+str(i))
                root_lattice = filter((lambda x: not x['coordinate'].any()),conditions['conditions'])[0]['lattice']
                self._out(8*' '+'call nr2'+root_lattice+'(site, '+root_lattice+'_site)')

                #  Print debug message
                if self.meta['debug'] > 1 :
                    for i in xrange(3):
                        self._out('    print \'(a)\',""')
                if self.meta['debug'] > 0 :
                    if conditions.has_key('suffix'):
                        self._out('    print \'(a,' +str(self.meta['dimension'])+ 'i5)\',"---> Selected process ' +proc + '_'+conditions['suffix'] + ' on (' + root_lattice + ')",' + root_lattice + '_site')
                    else:
                        self._out('    print \'(a,' +str(self.meta['dimension'])+ 'i5)\',"---> Selected process ' +proc + ' on (' + root_lattice + ')",' + root_lattice + '_site')
                for action in self.procs[proc]['action']:
                    site_label = action['site']
                    for condition in conditions['conditions']:
                        if condition['site'] == site_label:
                            if condition['coordinate'].any():
                                if condition['lattice'] == root_lattice :
                                    site = root_lattice + '_site+(/' + str(condition['coordinate'].tolist())[1 :-1] + '/)'
                                else:
                                    self._out(8*' '+'call nr2'+condition['lattice']+'(site, ' + condition['lattice'] + '_site)')
                                    site = condition['lattice'] + '_site+(/' + str(condition['coordinate'].tolist())[1 :-1] + '/)'

                            else:
                                site = root_lattice + '_site'
                            site += self.xtra_args
                            if condition.has_key('type'):
                                typ = '_' + condition['type']
                            else:
                                typ = ''
                            break
                    else:
                        print('Site ' + site_label +' not found defined under conditions', proc)
                        exit()

                    if action['old_species'] in self.meta['emptys'] and action['new_species'] in self.meta['emptys']:
                        print('ERROR: Changing from empty to empty is not allowed')
                        print('Process: ' + proc)
                        exit()
                    elif action['old_species'] in self.meta['emptys']:
                        self._out('        call put_' + action['new_species'] + typ + '(' + site + ')')
                    elif action['new_species'] in self.meta['emptys']:
                        self._out('        call take_' + action['old_species'] + typ + '(' + site + ')')
                    else:
                        self._out('        call take_' + action['new_species'] + typ + '(' + site + ')')
                        self._out('        call put_' + action['new_species'] + typ + '(' + site + ')')

                self._out('')

        self._out('    case default')
        self._out('        print *,"' + self.meta['name'] + '/run_proc_nr: we should not get here!",proc')
        self._out('    endselect')

        self._out('\nend subroutine run_proc_nr\n\n')




class UpdateFunction():
    """Data type of an 'update function' on the kMC lattice
    """
    def __init__(self, action, species, type='', lattice = '', other_species = ''):
        self.action = str(action)
        self.species = str(species)
        self.type = str(type)
        self.lattice = str(lattice)
        self.other_species = str(other_species)

    def __cmp__(self, other):
        return(cmp(self.__repr__(), other.__repr__()))
    def __repr__(self):
        return(self.action + '_' + self.species + '_' + self.type)



def validate_xml(xml_filename, dtd_filename):
    """Validate a given XML file with a given external DTD.
       If the XML file is not valid, an exception will be 
         printed with an error message.
    """
    dtd = et.DTD(dtd_filename)
    root = et.parse(xml_filename)
    dtd.assertValid(root)

def list_unique(liste):
    """Returns True if all elements in liste are unique
    and false otherwise. Python needs to know how to compare elements
    """
    liste.sort()
    if len(liste) == 1 :
        return True
    for i in range(len(liste)):
        if liste[i] == liste[i-1]:
            return False
    return True

def is_name_string(string):
    """Checks if string complies with the following variable
    naming convention:
    First letter may be a lower or upper case letter,
    the following letters may be a letter, number or underscore
    """
    if re.match(r'^[A-Za-z][A-Za-z_0-9]{0,30}$', string):
        return True
    else:
        return False

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ConsistencyError(Error):
    """Errors raised for errors in process list consistency."""
    def __init__(self, msg):
        """Print a customized error message"""
        Error.__init__(self)
        print("Raised error, when trying to understand your XML file")
        print(msg + "\n")

if __name__ == "__main__":
    PARSER = OptionParser(usage="%prog")
    PARSER.add_option("-x", "--xml", dest="xml_filename", \
            help="Set XML file where the process list is specified.", \
            type = "string")
    PARSER.add_option('-f', '--force', dest='force_overwrite', \
            action = 'store_true', default = False, \
            help = 'Force source files to be overwritten')
    (OPTIONS, ARGS) = PARSER.parse_args()

    PARSER.check_required("-x")
    PLIST = ProcessList(OPTIONS)
    #exit()

    PRINTER = pprint.PrettyPrinter(indent=4)
    #print("PROCESSES")
    #PRINTER.pprint(PLIST.procs)
    print("META")
    PRINTER.pprint(PLIST.meta)
    print("SPECIES")
    PRINTER.pprint(PLIST.species)
    #print("SITE TYPES")
    #PRINTER.pprint(PLIST.site_types)
