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
        self._out('use base, only: &')
        self._out('    update_accum_rate, &')
        self._out('    determine_procsite, &')
        self._out('    update_clocks, &')
        self._out('    increment_procstat')
        self._out('use lattice, only: &')
        self._out('    lattice_allocate_system => allocate_system ,&')
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

        for species in self.species.keys()[:-1]:
            self._out('    '+species+', &')
        self._out('    '+self.species.keys()[-1])
        self._out('\nimplicit none')
        #self.write_interface()
        #self.write_species_definitions()
        self.variable_definitions()
        self._out('\ncontains\n')
        self.write_init_function()
        self.write_run_proc_nr_function()
        self.write_atomic_update_functions()
        self.writeTouchupFunction()
        self.write_check_functions()
        self._out('end module proclist')

    def write_init_function(self):
        """This write a convenience function that wraps around lattice.allocate_system
        and initialize some array, which are useful in the f2py scripts
        """
        self._out('subroutine init(input_system_size, system_name)')
        self._out('    integer(kind=iint), dimension(2), intent(in) :: input_system_size')
        self._out('    character(len=400), intent(in) :: system_name\n\n')
        self._out('    print *,"This kMC Model \'%s\' was written by %s"' % (self.meta['name'], self.meta['author']))
        self._out('    print *,"and implemented with the help of kmos, which is distributed under "')
        self._out('    print *,"GNU/GPL Version 3 (C) Max J. Hoffmann mjhoffmann@gmail.com."')
        self._out('    print *,"Currently kmos is a very alphaish stage and there is"')
        self._out('    print *,"ABSOLUTELY NO WARRANTY for correctness."')
        self._out('    print *,"Please check back with the author prior to using results in publication."')
        self._out('    call lattice_allocate_system(nr_of_proc, input_system_size, system_name)\n')
        for i, proc in enumerate(sorted(self.procs)):
            self._out('    processes(' + str(i+1) + ') = \'' + proc + '\'')
            self._out('    rates(' + str(i+1) + ') = \'' + self.procs[proc]['rate'] + '\'')
        self._out('end subroutine init\n\n')

        self._out('subroutine get_rate_char(process_nr, char_slot, process_name)')
        self._out('    integer(kind=iint), intent(in) :: process_nr, char_slot')
        self._out('    character,  intent(out) :: process_name\n')
        self._out('    process_name = rates(process_nr)(char_slot:char_slot)')
        self._out('\nend subroutine get_rate_char\n\n')
        self._out('subroutine get_process_char(process_nr, char_slot, process_name)')
        self._out('    integer(kind=iint), intent(in) :: process_nr, char_slot')
        self._out('    character,  intent(out) :: process_name\n')
        self._out('    process_name = processes(process_nr)(char_slot:char_slot)')
        self._out('\nend subroutine get_process_char\n\n')
        self._out('subroutine do_kmc_step()')
        self._out('    !---------------internal variables---------------')
        self._out('    integer(kind=iint), dimension(2)  :: pdo_site, pd100_site')
        self._out('    real(kind=rsingle) :: ran_proc, ran_time, ran_site')
        self._out('    integer(kind=iint) :: nr_site, proc_nr\n')
        self._out('    ! Draw 3 random numbers')
        self._out('    call random_number(ran_time)')
        self._out('        call random_number(ran_proc)')
        self._out('    call random_number(ran_site)')
        #self._out('    print *, ran_time')
        #self._out('    print *, ran_proc')
        #self._out('    print *, ran_site')
        self._out('    ! Update the accumulated process rates')
        self._out('    call update_accum_rate ! @libkmc')
        self._out('    ! Determine the process and site')
        self._out('    call determine_procsite(ran_proc, ran_time, proc_nr, nr_site) ! @libkmc\n')
        self._out('    call run_proc_nr(proc_nr, nr_site)')
        self._out('    call update_clocks(ran_time)\n')
        self._out('end subroutine do_kmc_step\n\n')

    def variable_definitions(self):
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
        self._out('character(len=2000), dimension(%s)  :: processes, rates' % i)

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
            self._out('\n    logical :: check\n    logical :: can\n\n')

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
	# iterate over processes
        for proc in sorted(self.procs):
	    # iterate over actions
            for replacement in self.procs[proc]['action']:
		# iterate over conditions list (deprecated concept)
                for conditions in self.procs[proc]['condition_list'] :
		    # iterate over conditions in condition list
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
    if re.match(r'^[A-Za-z][A-Za-z_0-9]{0,62}$', string):
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
    PARSER = optparse.OptionParser(usage="%prog")
    PARSER.add_option("-x", "--xml", dest="xml_filename", \
            help="Set XML file where the process list is specified.", \
            type = "string")
    PARSER.add_option('-f', '--force', dest='force_overwrite', \
            action = 'store_true', default = False, \
            help = 'Force source files to be overwritten')
    (OPTIONS, ARGS) = PARSER.parse_args()

    PLIST = ProcessList(OPTIONS)

    PRINTER = pprint.PrettyPrinter(indent=4)
    print("META")
    PRINTER.pprint(PLIST.meta)
    print("SPECIES")
    PRINTER.pprint(PLIST.species)
