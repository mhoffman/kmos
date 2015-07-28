#!/usr/bin/env python
"""
Features front-end import/export functions for kMC Projects.
Currently import and export is supported to XML
and export is supported to Fortran 90 source code.
"""
#    Copyright 2009-2013 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.
#
#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.
import itertools
import operator
import shutil
import os
import sys
import copy
import numpy as np

from pprint import pformat


from kmos.types import ConditionAction, SingleLatIntProcess, Coord
from kmos.config import APP_ABS_PATH
from kmos.types import cmp_coords
from kmos.utils import evaluate_template


def _casetree_dict(dictionary, indent='', out=None):
    """ Recursively prints nested dictionaries."""
    # Fortran90 always expects the default branch
    # at the end of a 'select case' statement.
    # Thus we use reversed() to move the 'default'
    # branch from the beginning to the end.
    for key, value in reversed(list(dictionary.iteritems())):
        if isinstance(value, dict):
            if isinstance(key, Coord):
                out.write('%sselect case(get_species(cell%s))\n' % (indent, key.radd_ff()))
                _casetree_dict(value, indent + '  ', out)
                out.write('%send select\n' % indent)
            else:
                if key != 'default':
                    # allowing for or in species
                    keys = ', '.join(map(lambda x: x.strip(), key.split(' or ')))
                    out.write('%scase(%s)\n' % (indent, keys))
                    _casetree_dict(value, indent + '  ', out)
                else:
                    out.write('%scase %s\n' % (indent, key))
                    _casetree_dict(value, indent + '  ', out)
        else:
            out.write(indent+'%s = %s; return\n' % (key, value))

def _print_dict(dictionary, indent = ''):
    """ Recursively prints nested dictionaries."""

    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            print('%s%s:' % (indent, key) )
            _print_dict(value, indent+'    ')
        else:
            print(indent+'%s = %s' %(key, value))

def _flatten(L):
    return [item for sublist in L for item in sublist]


def _chop_line(outstr, line_length=100):
    if len(outstr) < line_length :
        return outstr
    outstr_list = []
    while outstr:
        try:
            NEXT_BREAK = outstr.index(',', line_length) + 1
        except ValueError:
            NEXT_BREAK = len(outstr)
        outstr_list.append(outstr[:NEXT_BREAK] + '&\n' )
        outstr = outstr[NEXT_BREAK:]
    return ''.join(outstr_list)


def compact_deladd_init(modified_process, out):
    n = len(modified_processes)
    out.write('integer :: n\n')
    out.write('integer, dimension(%s, 4) :: sites, cells\n\n' % n)

def compact_deladd_statements(modified_processes, out, action):
    n = len(modified_processes)
    processes = []
    sites = np.zeros((n, 4), int)
    cells = np.zeros((n, 4), int)

    for i, (process, offset) in enumerate(modified_procs):
        cells[i, :] = np.array(offset + [0])
        sites[i, :] = np.array(offset + [1])

    out.write('do n = 1, %s\n' % (n + 1))
    out.write('    call %s_proc(nli_%s(cell + %s), cell + %s)\n'
        % ())
    out.write('enddo\n')


def _most_common(L):
    # thanks go to Alex Martelli for this function
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item

    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        return count, - min_index
    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


class ProcListWriter():
    """Write the different parts of Fortran 90 code needed
    to run a kMC model.
    """

    def __init__(self, data, dir):
        self.data = data
        self.dir = dir

    def write_lattice(self,code_generator='lat_int'):
        from kmos.utils import evaluate_template

        with open(os.path.join(os.path.dirname(__file__),
                               'fortran_src',
                               'lattice.mpy')) as infile:
            template = infile.read()

        with open(os.path.join(self.dir, 'lattice.f90'), 'w') as out:
            out.write(evaluate_template(template,  self=self, data=self.data,code_generator=code_generator))

    def write_proclist(self, smart=True, code_generator='local_smart'):
        """Write the proclist.f90 module, i.e. the rules which make up
        the kMC process list.
        """
        # make long lines a little shorter
        data = self.data

        # write header section and module imports
        out = open('%s/proclist.f90' % self.dir, 'w')

        if code_generator == 'local_smart':
            self.write_proclist_generic_part(data, out, code_generator=code_generator)
            self.write_proclist_run_proc_nr_smart(data, out)
            self.write_proclist_put_take(data, out)
            self.write_proclist_touchup(data, out)
            self.write_proclist_multilattice(data, out)
            self.write_proclist_end(out)

        elif code_generator == 'lat_int':
            constants_out = open('%s/proclist_constants.f90' % self.dir, 'w')
            self.write_proclist_constants(data,
                                          constants_out,
                                          close_module=True,
                                          code_generator=code_generator,
                                          module_name='proclist_constants',
                                          )
            constants_out.close()
            self.write_proclist_lat_int(data, out)
            self.write_proclist_end(out)

        elif code_generator == 'otf':
            # write the proclist_constant module from the template
            with open(os.path.join(os.path.dirname(__file__),
                                   'fortran_src',
                                   'proclist_constants_otf.mpy')) as infile:
                template = infile.read()
            constants_out = open('%s/proclist_constants.f90' % self.dir, 'w')
            constants_out.write(evaluate_template(template,
                                                  self=self,
                                                  data=data,
                                                  module_name='proclist_constants'))
            constants_out.close()
            parameters_out = open('%s/proclist_parameters.f90' % self.dir, 'w')
            self.write_proclist_parameters_otf(data,parameters_out)
            parameters_out.close()

            self.write_proclist_otf(data,out)
            self.write_proclist_end(out)

        else:
            raise Exception("Don't know this code generator '%s'" % code_generator)

        out.close()

    def write_proclist_touchup_otf(self, data, out):
        """
        The touchup function

        Updates the elementary steps that a cell can do
        given the current lattice configuration. This has
        to be run once for every cell to initialize
        the simulation book-keeping.

        """
        indent = 4
        out.write('subroutine touchup_cell(cell)\n')
        out.write('    integer(kind=iint), intent(in), dimension(4) :: cell\n\n')
        out.write('    integer(kind=iint), dimension(4) :: site\n\n')
        out.write('    integer(kind=iint) :: proc_nr\n\n')
        # First kill all processes from this site that are allowed
        out.write('    site = cell + (/0, 0, 0, 1/)\n')
        out.write('    do proc_nr = 1, nr_of_proc\n')
        out.write('        if(avail_sites(proc_nr, lattice2nr(site(1), site(2), site(3), site(4)) , 2).ne.0)then\n')
        out.write('            call del_proc(proc_nr, site)\n')
        out.write('        endif\n')
        out.write('    end do\n\n')

        # Then we need to build the iftree that will update all processes
        # from this site

        enabling_items = []
        for process in data.process_list:
            rel_pos = (0,0,0) # during touchup we only activate procs from current site
            #rel_pos_string = 'cell + (/ %s, %s, %s, 1 /)' % (rel_pos[0],rel_pos[1], rel_pos[2]) # CHECK!!
            item2 = (process.name,rel_pos,True)
            # coded like this to be parallel to write_proclist_run_proc_name_otf
            enabling_items.append((copy.deepcopy(process.condition_list),copy.deepcopy(item2)))

        self._write_optimal_iftree_otf(enabling_items, indent, out)

        out.write('\nend subroutine touchup_cell\n')

    def _otf_get_auxilirary_params(self,data):
        import StringIO
        import tokenize
        from kmos import units, rate_aliases
        units_list = []
        masses_list = []
        chempot_list = []
        for process in data.process_list:
            exprs = [process.rate_constant,]
            if process.otf_rate:
                exprs.append(process.otf_rate)
            for expr in exprs:
                for old, new in rate_aliases.iteritems():
                    expr=expr.replace(old, new)
                try:
                    tokenize_input = StringIO.StringIO(expr).readline
                    tokens = list(tokenize.generate_tokens(tokenize_input))
                except:
                    raise Exception('Could not tokenize expression: %s' % expr)
                for i, token, _, _, _ in tokens:
                    if token in dir(units):
                        if token not in units_list:
                            units_list.append(token)
                    if token.startswith('m_'):
                        if token not in masses_list:
                            masses_list.append(token)
                    elif token.startswith('mu_'):
                        if token not in chempot_list:
                            chempot_list.append(token)
        return sorted(units_list), sorted(masses_list), sorted(chempot_list)

    def write_proclist_parameters_otf(self,data,out):
        '''Writes the proclist_parameters.f90 files
        which implements the module in charge of doing i/o
        from python evaluated parameters, to fortran and also
        handles rate constants update at fortran level'''

        import tokenize
        import StringIO
        import itertools
        from kmos import evaluate_rate_expression
        from kmos import rate_aliases

        indent = 4
        # First the GPL message
        out.write(self._gpl_message())

        out.write('module proclist_parameters\n')
        out.write('use kind_values\n')
        out.write('use base, only: &\n')
        out.write('%srates\n' % (' '*indent))
        out.write('use proclist_constants\n')
        out.write('use lattice, only: &\n')
        site_params = []
        for layer in data.layer_list:
            out.write('%s%s, &\n' % (' '*indent,layer.name))
            for site in layer.sites:
                site_params.append((site.name,layer.name))
        for site,layer in site_params:
            out.write('%s%s_%s, &\n' % (' '*indent,layer,site))
        out.write('%sget_species\n' % (' '*indent))
        out.write('\nimplicit none\n\n')


        units_list, masses_list, chempot_list = self._otf_get_auxilirary_params(data)

        # Define variables for the user defined parameteres
        out.write('! User parameters\n')
        for ip,parameter in enumerate(sorted(data.parameter_list, key=lambda x: x.name)):
            out.write('integer(kind=iint), public :: %s = %s\n' % (parameter.name,(ip+1)))
        out.write('real(kind=rdouble), public, dimension(%s) :: user_params\n' % len(data.parameter_list))

        # Next, we need to put into the fortran module a placeholder for each of the
        # parameters that kmos.evaluate_rate_expression can replace, namely
        # mu_* and m_*.

        # For the chemical potentials  and masses we need to explore all rate expressions
        # this code will repeat a lot of the logic on evaluate_rate_expression
        # Can we compress this??

        out.write('\n! Constants\n')
        for const in units_list:
            out.write('real(kind=rdouble), parameter :: %s = %.10e\n'
                      % (const, evaluate_rate_expression(const)))
        out.write('\n! Species masses\n')
        for mass in masses_list:
            out.write('real(kind=rdouble), parameter :: %s = %.10e\n'
                      % (mass,evaluate_rate_expression(mass)))

        # Chemical potentials are different because we need to be able to update them
        if chempot_list:
            out.write('\n! Species chemical potentials\n')
            for iu,mu in enumerate(chempot_list):
                out.write('integer(kind=iint), public :: %s = %s\n' % (mu,(iu+1)))
            out.write('real(kind=rdouble), public, dimension(%s) :: chempots\n' % len(chempot_list))

        # This module contains functions
        out.write('\ncontains\n')

        # Once this is done, we need to build routines that update user parameters and chempots

        out.write('subroutine update_user_parameter(param,val)\n')
        out.write('    integer(kind=iint), intent(in) :: param\n')
        out.write('    real(kind=rdouble), intent(in) :: val\n')
        out.write('    user_params(param) = val\n')
        out.write('end subroutine update_user_parameter\n\n')

        if chempot_list:
            out.write('subroutine update_chempot(index,val)\n')
            out.write('    integer(kind=iint), intent(in) :: index\n')
            out.write('    real(kind=rdouble), intent(in) :: val\n')
            out.write('    chempots(index) = val\n')
            out.write('end subroutine update_chempot\n\n')

        # And finally, we need to write the subroutines to return each of the rate constants
        out.write('\n! On-the-fly calculators for rate constants\n\n')
        for process in data.process_list:
            out.write('function get_rate_%s(cell)\n' % process.name)
            out.write('%sinteger(kind=iint), dimension(4), intent(in) :: cell\n'
                      % (' '*indent))

            # get all of flags
            flags = list(set([byst.flag for byst in process.bystander_list]))
            # and all species
            specs_dict = {}
            for byst in process.bystander_list:
                if hasattr(specs_dict,byst.flag):
                    if not (sorted(byst.allowed_species) ==
                            sorted(specs_dict[byst.flag])):
                        raise RuntimeError('All bystanders sharing a flag must allow same species. proc: %s' % process.name)
                else:
                    specs_dict[byst.flag] = byst.allowed_species


            # parse the otf_rate expression to get auxiliary variables
            new_expr, aux_vars, nr_vars = self._parse_otf_rate(process.otf_rate,
                                                      process.name,
                                                      data,
                                                      indent=indent)

            nr2zero = ''
            for flag in flags:
                for spec in specs_dict[flag]:
                    out.write('%sinteger(kind=iint) :: nr_%s_%s\n' %
                              (' '*indent,spec,flag))
                    nr2zero += '%snr_%s_%s = 0\n' % (' '*indent,spec,flag)
            for nr_var in nr_vars:
                if not nr_var in nr2zero:
                    out.write('{}integer(kind=iint) :: {}\n'.format(' '*indent,nr_var))
                    nr2zero += '{}{} = 0\n'.format(' '*indent,nr_var)

            out.write('\n')
            out.write('! Local auxiliary variables\n')
            for aux_var in aux_vars:
                out.write('%sreal(kind=rdouble) :: %s\n' %
                          (' '*indent,aux_var))
            out.write('\n')


            out.write('%sreal(kind=rdouble) :: get_rate_%s\n' % (' '*indent,process.name))

            out.write('\n')
            out.write(nr2zero)
            out.write('\n')

            for byst in process.bystander_list:
                out.write('%sselect case(get_species(cell%s))\n' % (' '*indent,
                                                                 byst.coord.radd_ff()))
                for spec in byst.allowed_species:
                    out.write('%scase(%s)\n' % (' '*2*indent,spec))
                    out.write('%snr_%s_%s = nr_%s_%s + 1\n' %
                              (' '*3*indent,spec,byst.flag,spec,byst.flag))
                out.write('%send select\n' % (' '*indent))


            out.write('{}\n'.format(new_expr))
            out.write('%sreturn\n' % (' '*indent))
            out.write('\nend function get_rate_%s\n\n' % process.name)

        out.write('\nend module proclist_parameters\n')


    def _parse_otf_rate(self,expr,procname,data,indent=4):
        """
        Parses the otf_rate expression and returns the expression to be inserted
        into the associated ``get_rate'' subroutine.
        Additionally collects locally defined variables and the full set of used
        nr_<species>_<flag> variables in order to include them in the variable
        declarations in those functions
        """

        aux_vars = []
        nr_vars = []

        if expr:
            if not 'base_rate' in expr:
                raise UserWarning('Not base_rate in otf_rate for process %s' % procname)

            # rate_lines = expr.splitlines()
            rate_lines = expr.split('\\n') # FIXME still bound by explicit '\n' due to xml parser
            if len(rate_lines) == 1:
                if not ('=' in rate_lines[0]):
                    rate_lines[0] = 'otf_rate =' + rate_lines[0]
                elif 'otf_rate' not in rate_lines[0]:
                    raise ValueError('Bad expression for single line otf rate\n' +
                                     '{}\n'.format(rate_lines[0]) +
                                     " must assign value to 'otf_rate'")
            elif not 'otf_rate' in expr:
                raise ValueError('Found a multiline otf_rate expression'
                                 " without 'otf_rate' on it")
            final_expr = ''
            for rate_line in rate_lines:
                if '=' in rate_line:
                    # We found a line that assigns a new variable
                    aux_var = rate_line.split('=')[0].strip()
                    if (not aux_var == 'otf_rate' and
                        not aux_var.startswith('nr_')):
                        aux_vars.append(aux_var)

                parsed_line, nr_vars_line = self._parse_otf_rate_line(
                    rate_line,procname,data,indent=indent)
                final_expr += '{}{}\n'.format(
                    ' '*indent,parsed_line)
                nr_vars.extend(nr_vars_line)
        else:
            final_expr = '{0}get_rate_{1} = rates({1})'.format(' '*indent, procname)

        return final_expr, aux_vars[:-1], list(set(nr_vars))

    def _parse_otf_rate_line(self,expr,procname,data,indent=4):
        """
        Parses an individual line of the otf_rate
        returning the processed line and a list of the
        nr_<species>_<flag> encountered
        """
        import StringIO, tokenize
        from kmos import units, rate_aliases

        param_names = [param.name for param in data.parameter_list]

        MAXLEN = 65 # Maximun line length

        nr_vars = []

        # 'base_rate' has special meaning in otf_rate
        expr = expr.replace('base_rate','rates(%s)' % procname)
        # so does 'otf_rate'
        expr = expr.replace('otf_rate','get_rate_{}'.format(procname))

        # And all aliases need to be replaced
        for old, new in rate_aliases.iteritems():
            expr = expr.replace(old,new)

        # Then time to tokenize:
        try:
            tokenize_input = StringIO.StringIO(expr).readline
            tokens = list(tokenize.generate_tokens(tokenize_input))
        except:
            raise Exception('kmos.io: Could not tokenize expression: %s' % expr)
        replaced_tokens = []
        split_expression = ''
        currl=0
        for i, token, _, _, _ in tokens:
            if token.startswith('nr_'):
                nr_vars.append(token)
            if token.startswith('mu_'):
                replaced_tokens.append((i,'chempots(%s)' % token))
            elif token in param_names:
                replaced_tokens.append((i,'user_params(%s)' % token))
            else:
                replaced_tokens.append((i,token))
            if currl+len(replaced_tokens[-1][1])<MAXLEN:
                split_expression+=replaced_tokens[-1][1]
                currl += len(replaced_tokens[-1][1])
            else:
                split_expression+='&\n{0}&{1}'.format(
                    ' '*indent,replaced_tokens[-1][1])
                currl=len(replaced_tokens[-1][1])
        return split_expression, list(set(nr_vars))

    def write_proclist_constants(self, data, out,
                                 code_generator='local_smart',
                                 close_module=False,
                                 module_name='proclist'):

        with open(os.path.join(os.path.dirname(__file__),
                               'fortran_src',
                               'proclist_constants.mpy')) as infile:
            template = infile.read()

        out.write(evaluate_template(template,
                                    self=self,
                                    data=data,
                                    code_generator=code_generator,
                                    close_module=close_module,
                                    module_name=module_name))


    def write_proclist_generic_part(self, data, out, code_generator='local_smart'):
        self.write_proclist_constants(data, out, close_module=False)
        out.write('\n\ncontains\n\n')
        self.write_proclist_generic_subroutines(data, out, code_generator=code_generator)

    def write_proclist_generic_subroutines(self, data, out, code_generator='local_smart'):
        from kmos.utils import evaluate_template

        with open(os.path.join(os.path.dirname(__file__),
                               'fortran_src',
                               'proclist_generic_subroutines.mpy')) as infile:
            template = infile.read()

        out.write(evaluate_template(template,
                                    self=self,
                                    data=data,
                                    code_generator=code_generator,
                                    ))

    def write_proclist_run_proc_nr_smart(self, data, out):
        # run_proc_nr runs the process selected by determine_procsite
        # for sake of simplicity each process is formulated in terms
        # of take and put operations. This is due to the fact that
        # in surface science type of models the default species,
        # i.e. 'empty' has a special meaning. So instead of just
        # 'setting' new species, which would be more general
        # we say we 'take' and 'put' atoms. So a take is equivalent
        # to a set_empty.
        # While this looks more readable on paper, I am not sure
        # if this make code maintainability a lot worse. So this
        # should probably change.

        out.write('subroutine run_proc_nr(proc, nr_site)\n\n'
                  '!****f* proclist/run_proc_nr\n'
                  '! FUNCTION\n'
                  '!    Runs process ``proc`` on site ``nr_site``.\n'
                  '!\n'
                  '! ARGUMENTS\n'
                  '!\n'
                  '!    * ``proc`` integer representing the process number\n'
                  '!    * ``nr_site``  integer representing the site\n'
                  '!******\n'
                  '    integer(kind=iint), intent(in) :: proc\n'
                  '    integer(kind=iint), intent(in) :: nr_site\n\n'
                  '    integer(kind=iint), dimension(4) :: lsite\n\n'
                  '    call increment_procstat(proc)\n\n'
                  '    ! lsite = lattice_site, (vs. scalar site)\n'
                  '    lsite = nr2lattice(nr_site, :)\n\n'
                  '    select case(proc)\n')
        for process in data.process_list:
            out.write('    case(%s)\n' % process.name)
            if data.meta.debug > 0:
                out.write(('print *,"PROCLIST/RUN_PROC_NR/NAME","%s"\n'
                           'print *,"PROCLIST/RUN_PROC_NR/LSITE","lsite"\n'
                           'print *,"PROCLIST/RUN_PROC_NR/SITE","site"\n')
                           % process.name)
            for action in process.action_list:
                if action.coord == process.executing_coord():
                    relative_coord = 'lsite'
                else:
                    relative_coord = 'lsite%s' % (action.coord - process.executing_coord()).radd_ff()

                try:
                    previous_species = filter(lambda x: x.coord.ff() == action.coord.ff(), process.condition_list)[0].species
                except:
                    UserWarning("""Process %s seems to be ill-defined.
                                   Every action needs a corresponding condition
                                   for the same site.""" % process.name)

                if action.species[0] == '^':
                    if data.meta.debug > 0:
                        out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","create %s_%s"\n'
                                   % (action.coord.layer,
                                      action.coord.name))
                    out.write('        call create_%s_%s(%s, %s)\n'
                               % (action.coord.layer,
                                  action.coord.name,
                                  relative_coord,
                                  action.species[1:]))
                elif action.species[0] == '$':
                    if data.meta.debug > 0:
                        out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","annihilate %s_%s"\n'
                                   % (action.coord.layer,
                                      action.coord.name))
                    out.write('        call annihilate_%s_%s(%s, %s)\n'
                               % (action.coord.layer,
                                  action.coord.name,
                                  relative_coord,
                                  action.species[1:]))
                elif action.species == data.species_list.default_species \
                and not action.species == previous_species:
                    if data.meta.debug > 0:
                        out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                                   % (action.coord.layer,
                                      action.coord.name,
                                      previous_species))
                    out.write('        call take_%s_%s_%s(%s)\n'
                               % (previous_species,
                                  action.coord.layer,
                                  action.coord.name,
                                  relative_coord))
                else:
                    if not previous_species == action.species:
                        if not previous_species == data.species_list.default_species:
                            if data.meta.debug > 0:
                                out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n'
                                           % (action.coord.layer,
                                              action.coord.name,
                                              previous_species))
                            out.write('        call take_%s_%s_%s(%s)\n'
                                       % (previous_species,
                                          action.coord.layer,
                                          action.coord.name,
                                          relative_coord))
                        if data.meta.debug > 0:
                            out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n'
                                      % (action.coord.layer,
                                         action.coord.name,
                                         action.species))
                        out.write('        call put_%s_%s_%s(%s)\n'
                                   % (action.species,
                                      action.coord.layer,
                                      action.coord.name,
                                      relative_coord))

            out.write('\n')
        out.write('    end select\n\n')
        out.write('end subroutine run_proc_nr\n\n')


    def write_proclist_run_proc_nr_otf(self, data, out):
        # run_proc_nr runs the process selected by determine_procsite
        # this routine only selects the correct routine from all
        # of the run_proc_<procname> routines

        out.write('subroutine run_proc_nr(proc, nr_cell)\n\n'
                  '!****f* proclist/run_proc_nr\n'
                  '! FUNCTION\n'
                  '!    Runs process ``proc`` on site ``nr_site``.\n'
                  '!\n'
                  '! ARGUMENTS\n'
                  '!\n'
                  '!    * ``proc`` integer representing the process number\n'
                  '!    * ``nr_site``  integer representing the site\n'
                  '!******\n'
                  '    integer(kind=iint), intent(in) :: proc\n'
                  '    integer(kind=iint), intent(in) :: nr_cell\n\n'
                  '    integer(kind=iint), dimension(4) :: cell\n\n'
                  '    call increment_procstat(proc)\n\n'
                  '    ! lsite = lattice_site, (vs. scalar site)\n'
                  '    cell = nr2lattice(nr_cell, :) + (/0, 0, 0, -1/)\n\n'
                  '    select case(proc)\n')
        for process in data.process_list:
            out.write('    case(%s)\n' % process.name)

            if data.meta.debug > 0:
                out.write(('print *,"PROCLIST/RUN_PROC_NR/NAME","%s"\n'
                           'print *,"PROCLIST/RUN_PROC_NR/LSITE",lsite\n'
                           'print *,"PROCLIST/RUN_PROC_NR/SITE",nr_site\n')
                           % process.name)
            out.write('        call run_proc_%s(cell)\n' % process.name)

            out.write('\n')
        out.write('    end select\n\n')
        out.write('end subroutine run_proc_nr\n\n')

    def _db_print(self, line, debug=False):
        """Write out debugging statement if requested."""
        if debug:
            dbg_file = open('dbg_file.txt', 'a')
            dbg_file.write(line)
            dbg_file.close()

    def _get_lat_int_groups(self):
        data = self.data
        #TODO: now only for old style definition of processes (w/o bystanders)
        #FUTURE: insert switch and support new style definition of processes

        # FIRST: group processes by lateral interaction groups
        ################################################################
        process_list = []
        for process in data.process_list:
            actions = process.action_list

            # identify, which conditions
            # are truly changing and which are just bystanders
            true_conditions = []
            true_actions = []
            bystanders = []
            #for condition in [x for x in process.condition_list if not x.implicit]:
            for condition in process.condition_list :
                corresponding_actions = [action for action in actions if condition.coord == action.coord]


                self._db_print('%s: %s <-> %s' % (process.name, condition, corresponding_actions))

                if corresponding_actions:
                    action = corresponding_actions[0]
                    if condition.species != action.species:
                        true_conditions.append(condition)
                        true_actions.append(action)
                    else:
                        bystanders.append(condition)
                else:
                    bystanders.append(condition)
            if hasattr(process, 'bystanders'):
                bystanders.extend(process.bystanders)
            # extra block for multi-lattice actions
            for action in actions:
                if action not in true_actions:
                    if not(action.species.startswith('^')
                           or action.species.startswith('$')):
                        #raise UserWarning('Found unmatched action that is not a multi-lattice action: %s' % action)
                        print(('UserWarning: Found unmatched action (%s) that is not a multi-lattice action: %s'
                               % (process.name, action)))
                        # turn exceptions into warning for now
                    else:
                        true_actions.append(action)

            process_list.append(SingleLatIntProcess(
                                name=process.name,
                                rate_constant=process.rate_constant,
                                condition_list=true_conditions,
                                action_list=true_actions,
                                bystanders=bystanders,
                                enabled=process.enabled,
                                tof_count=process.tof_count,))
        # SECOND: Group lateral interaction groups into dictionary
        ################################################################
        lat_int_groups = {}
        for process in process_list:
            for lat_int_group, processes in lat_int_groups.iteritems():
                p0 = processes[0]
                same = True
                # check if conditions are identical
                if sorted(p0.condition_list, key=lambda x: x.coord, cmp=cmp_coords) \
                   != sorted(process.condition_list, key=lambda x: x.coord, cmp=cmp_coords):
                    same = False
                # check if actions are identical
                if sorted(p0.action_list, key=lambda x: x.coord, cmp=cmp_coords) \
                   != sorted(process.action_list, key=lambda x: x.coord, cmp=cmp_coords):
                    same = False

                # check if coords of bystanders are identical
                if [x.coord for x in sorted(p0.bystanders, key=lambda x: x.coord, cmp=cmp_coords)] \
                   != [x.coord for x in sorted(process.bystanders, key=lambda x: x.coord, cmp=cmp_coords)]:
                    same = False

                if same:
                    self._db_print('    %s <- %s\n' % (lat_int_group, process.name))
                    processes.append(process)
                    break
            else:
                lat_int_groups[process.name] = [process]
                self._db_print('* %s\n' % (process.name))

        # correctly determined lat. int. groups, yay.

        #TODO: check if lat_int group is correct
        # i.e.
        # - each bystander list is unique
        # - all bystanders cover the same set of sites
        # let's assume it for now

        return lat_int_groups

    def write_proclist_lat_int(self, data, out, debug=False):
        """
        This a dumber version f the run_proc_nr routine. Though
        the source code it generates might be quite a bit smaller.
        On the downside, it might be a little less optimized though
        it is local in a very strict sense. [EXPERIMENTAL/UNFINISHED!!!]
        """
        # initialize progress bar
        if os.name == 'posix':
            from kmos.utils.progressbar import ProgressBar
            progress_bar = ProgressBar('blue', width=80)
            progress_bar.render(10, 'generic part')

        # categorize elementary steps into
        # lateral interaction groups
        lat_int_groups = self._get_lat_int_groups()

        out.write(('module proclist\n'
                  'use kind_values\n'
                  'use base, only: &\n'
                  '    update_accum_rate, &\n'
                  '    update_integ_rate, &\n'
                  '    determine_procsite, &\n'
                  '    update_clocks, &\n'
                  '    avail_sites, &\n'))
        if len(data.layer_list) == 1 : # multi-lattice mode
            out.write('    null_species, &\n')
        else:
            out.write('    set_null_species, &\n')
        out.write('    increment_procstat\n\n'
                  'use lattice, only: &\n')
        site_params = []
        for layer in data.layer_list:
            out.write('    %s, &\n' % layer.name)
            for site in layer.sites:
                site_params.append((site.name, layer.name))
        for i, (site, layer) in enumerate(site_params):
            out.write(('    %s_%s, &\n') % (layer, site))
        out.write('    allocate_system, &\n'
              '    nr2lattice, &\n'
              '    lattice2nr, &\n'
              '    add_proc, &\n'
              '    can_do, &\n'
              '    set_rate_const, &\n'
              '    replace_species, &\n'
              '    del_proc, &\n'
              '    reset_site, &\n'
              '    system_size, &\n'
              '    spuck, &\n')

        out.write('    get_species\n')
        for i in range(len(lat_int_groups)):
            out.write('use run_proc_%04d; use nli_%04d\n' % (i, i))

        out.write('\nimplicit none\n')

        representation_length = max([len(species.representation) for species in data.species_list])
        out.write('integer(kind=iint), parameter, public :: representation_length = %s\n' % representation_length)
        if os.name == 'posix':
            out.write('integer(kind=iint), public :: seed_size = 12\n')
        elif os.name == 'nt':
            out.write('integer(kind=iint), public :: seed_size = 12\n')
        else:
            out.write('integer(kind=iint), public :: seed_size = 8\n')
        out.write('integer(kind=iint), public :: seed ! random seed\n')
        out.write('integer(kind=iint), public, dimension(:), allocatable :: seed_arr ! random seed\n')
        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_proc = %s\n'\
            % (len(data.process_list)))

        code_generator = 'lat_int'
        if code_generator == 'lat_int':
            out.write('\ncharacter(len=%s), parameter, public :: backend = "%s"\n'
                      % (len(code_generator), code_generator))
        elif code_generator == 'local_smart':
            pass # change nothing here, to not alter old code


        out.write('\ncontains\n\n')

        # write out the process list
        self.write_proclist_lat_int_run_proc_nr(data, lat_int_groups, progress_bar, out)
        self.write_proclist_lat_int_touchup(lat_int_groups, out)
        self.write_proclist_generic_subroutines(data, out, code_generator='lat_int')
        self.write_proclist_lat_int_run_proc(data, lat_int_groups, progress_bar)
        self.write_proclist_lat_int_nli_casetree(data, lat_int_groups, progress_bar)

        # and we are done!
        if os.name == 'posix':
            progress_bar.render(100, 'finished proclist.f90')

    def write_proclist_lat_int_run_proc_nr(self, data, lat_int_groups, progress_bar, out):
        """
        subroutine run_proc_nr(proc, cell)

        Central function at the beginning of each executed elementary step.
        Dispatches from the determined process number to the corresponding
        subroutine.

        """
        out.write('subroutine run_proc_nr(proc, nr_cell)\n')
        out.write('    integer(kind=iint), intent(in) :: nr_cell\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n\n')
        out.write('    integer(kind=iint), dimension(4) :: cell\n\n')
        out.write('    cell = nr2lattice(nr_cell, :) + (/0, 0, 0, -1/)\n')
        out.write('    call increment_procstat(proc)\n\n')
        if data.meta.debug > 1:
            out.write('    print *, "PROCLIST/RUN_PROC_NR"\n')
            out.write('    print *, "  PROCLIST/RUN_PROC_NR/PROC", proc\n')
            out.write('    print *, "  PROCLIST/RUN_PROC_NR/NR_CELL", nr_cell\n')
            out.write('    print *, "  PROCLIST/RUN_PROC_NR/CELL", cell\n')
        out.write('    select case(proc)\n')
        for lat_int_group, processes in lat_int_groups.iteritems():
            proc_names = ', '.join([proc.name for proc in processes])
            out.write('    case(%s)\n' % _chop_line(proc_names, line_length=60))
            out.write('        call run_proc_%s(cell)\n' % lat_int_group)
        out.write('    case default\n')
        out.write('        print *, "Whoops, should not get here!"\n')
        out.write('        print *, "PROC_NR", proc\n')
        out.write('        stop\n')
        out.write('    end select\n\n')
        out.write('end subroutine run_proc_nr\n\n')

    def write_proclist_lat_int_touchup(self, lat_int_groups, out):
        """
        The touchup function

        Updates the elementary steps that a cell can do
        given the current lattice configuration. This has
        to be run once for every cell to initialize
        the simulation book-keeping.

        """
        out.write('subroutine touchup_cell(cell)\n')
        out.write('    integer(kind=iint), intent(in), dimension(4) :: cell\n\n')
        out.write('    integer(kind=iint), dimension(4) :: site\n\n')
        out.write('    integer(kind=iint) :: proc_nr\n\n')
        out.write('    site = cell + (/0, 0, 0, 1/)\n')
        out.write('    do proc_nr = 1, nr_of_proc\n')
        out.write('        if(avail_sites(proc_nr, lattice2nr(site(1), site(2), site(3), site(4)) , 2).ne.0)then\n')
        out.write('            call del_proc(proc_nr, site)\n')
        out.write('        endif\n')
        out.write('    end do\n\n')

        for lat_int_group, process in lat_int_groups.iteritems():
            out.write('    call add_proc(nli_%s(cell), site)\n' % (lat_int_group))
        out.write('end subroutine touchup_cell\n\n')


    def write_proclist_lat_int_run_proc(self, data, lat_int_groups, progress_bar):
        """
        subroutine run_proc_<processname>(cell)

        Performs the lattice and avail_sites updates
        for a given process.
        """

        for lat_int_loop, (lat_int_group, processes) in enumerate(lat_int_groups.iteritems()):
            out = open('%s/run_proc_%04d.f90' % (self.dir, lat_int_loop), 'w')
            self._db_print('PROCESS: %s' % lat_int_group)
            # initialize needed data structure
            process0 = processes[0]
            modified_procs = set()

            out.write('module run_proc_%04d\n' % lat_int_loop)
            out.write('use kind_values\n')
            for i in range(len(lat_int_groups)):
                out.write('use nli_%04d\n' % i)
            out.write('use proclist_constants\n')
            out.write('implicit none\n')
            out.write('contains\n')
            # write F90 subroutine definition
            out.write('subroutine run_proc_%s(cell)\n\n' % lat_int_group)
            out.write('    integer(kind=iint), dimension(4), intent(in) :: cell\n')
            out.write('\n    ! disable processes that have to be disabled\n')

            # collect processes that could be modified by current process:
            # if current process modifies a site, that "another process" depends on,
            # add "another process" to the processes to be modified/updated.
            for action in process0.action_list:
                self._db_print('    ACTION: %s' % action)
                for _, other_processes in lat_int_groups.iteritems():
                    other_process = other_processes[0]
                    self._db_print('      OTHER PROCESS %s' % (pformat(other_process, indent=12)))
                    other_conditions = other_process.condition_list + other_process.bystanders
                    self._db_print('            OTHER CONDITIONS\n%s' % pformat(other_conditions, indent=12))

                    for condition in other_conditions:
                        if action.coord.eq_mod_offset(condition.coord):
                            modified_procs.add((other_process, tuple(action.coord.offset-condition.coord.offset)))

            # sort to one well-defined orded
            modified_procs = sorted(modified_procs,
                                    key=lambda x: '%s %s' % (x[0].name, str(x[1]))
                                    )

            # write out necessary DELETION statements
            for i, (process, offset) in enumerate(modified_procs):
                offset_cell = '(/%+i, %+i, %+i, 0/)' % tuple(offset)
                offset_site = '(/%+i, %+i, %+i, 1/)' % tuple(offset)
                out.write('    call del_proc(nli_%s(cell + %s), cell + %s)\n'
                    % (process.name, offset_cell, offset_site))


            # write out necessary LATTICE UPDATES
            out.write('\n    ! update lattice\n')
            matched_actions = []
            for condition in process0.condition_list:
                try:
                    action = [action for action in process0.action_list
                                            if condition.coord == action.coord][0]
                except Exception, e:
                    print(e)
                    print('Trouble with process %s' % process.name)
                    print('And condition %s' % condition)
                    raise
                matched_actions.append(action)

                # catch "multi-lattice" species
                if action.species.startswith('$'):
                    condition_species = condition.species
                    action_species = 'null_species'
                elif action.species.startswith('^') :
                    condition_species = 'null_species'
                    action_species = action.species
                else:
                    condition_species = condition.species
                    action_species = action.species

                if len(condition_species.split(' or ') ) > 1 :
                    out.write('    select case(get_species((cell%s)))\n'
                              % (action.coord.radd_ff(),))
                    for condition_species in map(lambda x: x.strip(), condition_species.split(' or ')):
                        out.write('    case(%s)\n' % condition_species)
                        out.write('    call replace_species(cell%s, %s, %s)\n'
                                  % (action.coord.radd_ff(),
                                     condition_species,
                                     action_species))
                    out.write('    case default\n        print *, "ILLEGAL SPECIES ENCOUNTERED"\n        stop\n    end select\n')

                else:
                    out.write('    call replace_species(cell%s, %s, %s)\n'
                              % (action.coord.radd_ff(),
                                 condition_species,
                                 action_species))

            # extra part for multi-lattice action
            # without explicit condition
            for action in process0.action_list:
                if action not in matched_actions:
                    #print(process0.name, action, not action in matched_actions)
                    # catch "multi-lattice" species
                    if action.species.startswith('$'):
                        condition_species = action.species[1:]
                        action_species = 'null_species'
                    elif action.species.startswith('^') :
                        condition_species = 'null_species'
                        action_species = action.species[1:]
                    else:
                        raise UserWarning('Unmatched action that is not a multi-lattice action: %s' % (action))
                    print(condition_species)
                    if len(condition_species.split(' or ') ) > 1 :
                        out.write('    select case(get_species((cell%s)))\n'
                                  % (action.coord.radd_ff(),))
                        for condition_species in map(lambda x: x.strip(), condition_species.split(' or ')):
                            out.write('    case(%s)\n' % condition_species)
                            out.write('            call replace_species(cell%s, %s, %s)\n'
                                      % (action.coord.radd_ff(),
                                         condition_species,
                                         action_species))
                        out.write('    case default\n        print *, "ILLEGAL SPECIES ENCOUNTERED"\n        stop    \nend select\n')

                    else:
                        out.write('    call replace_species(cell%s, %s, %s)\n'
                                  % (action.coord.radd_ff(),
                                     condition_species,
                                     action_species))


            # write out necessary ADDITION statements
            out.write('\n    ! enable processes that have to be enabled\n')
            for i, (process, offset) in enumerate(modified_procs):
                offset_cell = '(/%+i, %+i, %+i, 0/)' % tuple(offset)
                offset_site = '(/%+i, %+i, %+i, 1/)' % tuple(offset)
                out.write('    call add_proc(nli_%s(cell + %s), cell + %s)\n'
                    % (process.name, offset_cell, offset_site))
            out.write('\nend subroutine run_proc_%s\n\n' % lat_int_group)
            out.write('end module\n')

            if os.name == 'posix':
                progress_bar.render(int(10+40*float(lat_int_loop)/len(lat_int_groups)),
                                    'run_proc_%s' % lat_int_group)

    def write_proclist_lat_int_nli_casetree(self, data, lat_int_groups, progress_bar):
        """
        Write out subroutines that do the following:
        Take a given cell and determine from a group a processes
        that only differ by lateral interaction which one is possible.
        This version writes out explicit 'select case'-tree which is
        somewhat slower than the module version but can theoretically
        accomodate for infinitely many conditions for one elementary step.

        If no process is applicable an integer "0"
        is returned.

        """

        for lat_int_loop, (lat_int_group, processes) in enumerate(lat_int_groups.iteritems()):
            out = open('%s/nli_%04d.f90' % (self.dir, lat_int_loop), 'w')
            out.write('module nli_%04d\n' % lat_int_loop)
            out.write('use kind_values\n')
            out.write('use lattice\n'
                    )
            out.write('use proclist_constants\n')
            out.write('implicit none\n')
            out.write('contains\n')
            fname = 'nli_%s' % lat_int_group
            if data.meta.debug > 0:
                out.write('function %(cell)\n'
                          % (fname))
            else:
                # DEBUGGING
                #out.write('function nli_%s(cell)\n'
                          #% (lat_int_group))
                out.write('pure function nli_%s(cell)\n'
                          % (lat_int_group))
            out.write('    integer(kind=iint), dimension(4), intent(in) :: cell\n')
            out.write('    integer(kind=iint) :: %s\n\n' % fname)



            #######################################################
            # sort processes into a nested list (dictionary)
            # ordered by coords
            #######################################################

            # first build up a tree where each result has all
            # the needed conditions as parent nodes
            case_tree = {}
            for process in processes:
                conditions = [y for y in sorted(process.condition_list + process.bystanders,
                                                 key=lambda x: x.coord, cmp=cmp_coords)
                                                 if not y.implicit]
                node = case_tree
                for condition in conditions:
                    species_node = node.setdefault(condition.coord, {})
                    node = species_node.setdefault(condition.species, {})
                    species_node.setdefault('default', {fname: 0})
                node[fname] = process.name

            # second write out the generated tree by traversing it
            _casetree_dict(case_tree, '    ', out)

            out.write('\nend function %s\n\n' % (fname))
            out.write('end module\n')

            # update the progress bar
            if os.name == 'posix':
                progress_bar.render(int(50+50*float(lat_int_loop)/len(lat_int_groups)),
                                    'nli_%s' % lat_int_group)

    def write_proclist_lat_int_nli_caselist(self, data, lat_int_groups, progress_bar, out):
        """
        subroutine nli_<processname>

        nli = number of lateral interaction
        inspect a local enviroment for a set
        of processes that only differ by lateral
        interaction and return the process number
        corrresponding to the present configuration.
        If no process is applicable an integer "0"
        is returned.

        This version is the fastest found so far but has the problem
        that nr_of_species**nr_of_sites quickly runs over sys.max_int
        or whatever is the largest available integer for your Fortran
        compiler.

        """

        for lat_int_loop, (lat_int_group, processes) in enumerate(lat_int_groups.iteritems()):
            process0 = processes[0]

            # put together the bystander conditions and true conditions,
            # sort them in a unique way and throw out those that are
            # implicit
            conditions0 = [y for y in sorted(process0.condition_list + process0.bystanders,
                                             key=lambda x: x.coord, cmp=cmp_coords)
                                             if not y.implicit]
            # DEBUGGING
            self._db_print(process0.name, conditions0)

            if data.meta.debug > 0:
                out.write('function nli_%s(cell)\n'
                          % (lat_int_group))
            else:
                # DEBUGGING
                #out.write('function nli_%s(cell)\n'
                          #% (lat_int_group))
                out.write('pure function nli_%s(cell)\n'
                          % (lat_int_group))
            out.write('    integer(kind=iint), dimension(4), intent(in) :: cell\n')
            out.write('    integer(kind=iint) :: nli_%s\n\n' % lat_int_group)

            # create mapping to map the sparse
            # representation for lateral interaction
            # into a contiguous one
            compression_map = {}
            #print("# proc %s" % len(processes))
            for i, process in enumerate(sorted(processes)):
                # calculate lat. int. nr
                lat_int_nr = 0
                if len(data.layer_list) > 1:
                    nr_of_species = len(data.species_list) + 1
                else:
                    nr_of_species = len(data.species_list)
                conditions = [y for y in sorted(process.condition_list + process.bystanders,
                                                key=lambda x: x.coord, cmp=cmp_coords)
                                                if not y.implicit]

                for j, bystander in enumerate(conditions):
                    species_nr = [x for (x, species) in
                                  enumerate(sorted(data.species_list))
                                  if species.name == bystander.species][0]
                    lat_int_nr += species_nr*(nr_of_species**j)
                    #print(lat_int_nr, species.name, nr_of_species, j)
                compression_map[lat_int_nr] = process.name
                if lat_int_nr > sys.maxint :
                    print(("Warning: Lateral interaction index is too large to compile.\n"
                          "          Try to reduce the number of (non-implicit conditions\n"
                          "          or the total number of species.\n\n%s") % process)


            # use a threshold of 1./3 for very sparse maps
            if float(len(compression_map))/(nr_of_species**len(conditions)) > 1./3 :
                USE_ARRAY = True
            else:
                USE_ARRAY = False

            # use generator object to save memory
            if USE_ARRAY:
                compression_index = (compression_map.get(i, 0) for
                                     i in xrange(nr_of_species**len(conditions0)))
                out.write('    integer, dimension(%s), parameter :: lat_int_index_%s = (/ &\n'
                          % (len(compression_index), lat_int_group))
                outstr = ', '.join(map(str, compression_index))

                outstr = _chop_line(outstr)
                out.write(outstr)
                out.write('/)\n')
            out.write('    integer(kind=ilong) :: n\n\n')
            out.write('    n = 0\n\n')

            if data.meta.debug > 2:
                out.write('print *,"PROCLIST/NLI_%s"\n' % lat_int_group.upper())
                out.write('print *,"    PROCLIST/NLI_%s/CELL", cell\n' % lat_int_group.upper())

            for i, bystander in enumerate(conditions0):
                out.write('    n = n + get_species(cell%s)*nr_of_species**%s\n'
                % (bystander.coord.radd_ff(), i))

            if USE_ARRAY :
                out.write('\n    nli_%s = lat_int_index_%s(n)\n'
                          % (lat_int_group, lat_int_group))
            else:
                out.write('\n    select case(n)\n')
                for i, proc_name in sorted(compression_map.iteritems()):
                    if proc_name:
                        out.write('    case(%s)\n' % i)
                        out.write('        nli_%s = %s\n' %
                                   (lat_int_group, proc_name))
                out.write('    case default\n')
                out.write('        nli_%s = 0\n' % lat_int_group)
                out.write('    end select\n\n')
            if data.meta.debug > 2:
                out.write('print *,"    PROCLIST/NLI_%s/N", n\n'
                          % lat_int_group.upper())
                out.write('print *,"    PROCLIST/NLI_%s/PROC_NR", nli_%s\n'
                          % (lat_int_group.upper(), lat_int_group))
            out.write('\nend function nli_%s\n\n' % (lat_int_group))
            if os.name == 'posix':
                progress_bar.render(int(50+50*float(lat_int_loop)/len(lat_int_groups)),
                                    'nli_%s' % lat_int_group)

    def write_proclist_otf(self, data, out, debug=False):
        """
        Writes the proclist.f90 file for the otf backend
        """
        # initialize progress bar
        if os.name == 'posix':
            from kmos.utils.progressbar import ProgressBar
            progress_bar = ProgressBar('blue', width=80)
            progress_bar.render(10, 'generic part')

        out.write(('module proclist\n'
                  'use kind_values\n'
                  'use base, only: &\n'
                  '    update_accum_rate, &\n'
                  '    update_integ_rate, &\n'
                  '    reaccumulate_rates_matrix, &\n'
                  '    determine_procsite, &\n'
                  '    update_clocks, &\n'
                  '    avail_sites, &\n'))
        if len(data.layer_list) == 1 : # multi-lattice mode
            out.write('    null_species, &\n')
        else:
            out.write('    set_null_species, &\n')
        out.write('    increment_procstat\n\n'
                  'use lattice, only: &\n')
        site_params = []
        for layer in data.layer_list:
            out.write('    %s, &\n' % layer.name)
            for site in layer.sites:
                site_params.append((site.name, layer.name))
        for i, (site, layer) in enumerate(site_params):
            out.write(('    %s_%s, &\n') % (layer, site))
        out.write('    allocate_system, &\n'
              '    nr2lattice, &\n'
              '    lattice2nr, &\n'
              '    add_proc, &\n'
              '    can_do, &\n'
              '    set_rate_const, &\n'
              '    replace_species, &\n'
              '    del_proc, &\n'
              '    reset_site, &\n'
              '    system_size, &\n'
              '    update_rates_matrix, &\n'
              '    spuck, &\n')

        out.write('    get_species\n')
        out.write('use proclist_constants\n')
        out.write('use proclist_parameters\n')

        out.write('\nimplicit none\n')

        representation_length = max([len(species.representation) for species in data.species_list])
        out.write('integer(kind=iint), parameter, public :: representation_length = %s\n' % representation_length)
        if os.name == 'posix':
            out.write('integer(kind=iint), public :: seed_size = 12\n')
        elif os.name == 'nt':
            out.write('integer(kind=iint), public :: seed_size = 12\n')
        else:
            out.write('integer(kind=iint), public :: seed_size = 8\n')
        out.write('integer(kind=iint), public :: seed ! random seed\n')
        out.write('integer(kind=iint), public, dimension(:), allocatable :: seed_arr ! random seed\n')
        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_proc = %s\n'\
            % (len(data.process_list)))

        code_generator='otf'
        out.write('\ncharacter(len=%s), parameter, public :: backend = "%s"\n'
                      % (len(code_generator), code_generator))
        out.write('\ncontains\n\n')

        self.write_proclist_generic_subroutines(data, out, code_generator='otf')
        self.write_proclist_touchup_otf(data,out)
        self.write_proclist_run_proc_nr_otf(data,out)
        self.write_proclist_run_proc_name_otf(data,out)

        # and we are done!
        if os.name == 'posix':
            progress_bar.render(100, 'finished proclist.f90')


    def write_proclist_run_proc_name_otf(self,data,out=None,separate_files = False, indent=4):
        """ This routine implements the routines that execute
        an specific process.
        As with the local_smart backend, turning processes off
        is easy. For turning processes on, we reuse the same logic
        as in local_smart, but now working on whole processes,
        rather that with put/take single site routines.
        Aditionally, this routines must call the get_rate_<procname>
        routines, which are defined in the proclist_parameters module
        """
        nprocs = len(data.process_list)

        debug = 0

        for exec_proc in data.process_list:
            if separate_files:
                out = os.open('%s/run_proc_%s.f90' % (self.dir,exec_proc.name),'w')
                out.write('! INSERT HEADERS HERE ### TODO\n\n')
                ## TODO
            routine_name = 'run_proc_%s' % exec_proc.name
            out.write('\nsubroutine %s(cell)\n\n' %routine_name)
            out.write('%sinteger(kind=iint), dimension(4), intent(in) :: cell\n\n' % (' '*indent))

            # We will sort out all processes that are (potentially) influenced
            # (inhibited, activated or changed rate)
            # by the executing process
            inh_procs = [copy.copy([]) for i in xrange(nprocs)]
            enh_procs = copy.deepcopy(inh_procs)
            aff_procs = copy.deepcopy(enh_procs)
            # And look into how each of its actions...
            for exec_action in exec_proc.action_list:
                # ... affect each other processes' conditions
                for ip,proc in enumerate(data.process_list):
                    for condition in proc.condition_list:
                        if condition.coord.name == exec_action.coord.name and\
                          condition.coord.layer == exec_action.coord.layer:
                            # If any of the target process condition is compatible with
                            # this action, we need to store the relative position of this
                            # process with respect to the current process' location
                            rel_pos = tuple((exec_action.coord - condition.coord).offset)
                            if not condition.species == exec_action.species:
                                inh_procs[ip].append(copy.deepcopy(rel_pos))
                            else:
                                enh_procs[ip].append(copy.deepcopy(rel_pos))
                    # and similarly for the bystanders
                    for byst in proc.bystander_list:
                        if byst.coord.name == exec_action.coord.name and\
                          byst.coord.layer == exec_action.coord.layer:
                            rel_pos = tuple((exec_action.coord - byst.coord).offset)
                            aff_procs[ip].append(copy.deepcopy(rel_pos))


            if debug > 0:
                print('For process: %s' % exec_proc.name)
                print('No inh procs: %s' % [len(sublist) for sublist in inh_procs])
                print(inh_procs)
                print('No enh procs: %s' % [len(sublist) for sublist in enh_procs])
                print(enh_procs)
                print('No aff procs; %s' % [len(sublist) for sublist in aff_procs])
                print(aff_procs)
                print('  ')

            ## Get rid of repetition
            for ip in xrange(nprocs):
                inh_procs[ip] = [rel_pos for rel_pos in set(inh_procs[ip])]
            for ip in xrange(nprocs):
                enh_procs[ip] = [rel_pos for rel_pos in set(enh_procs[ip]) if not
                                 (rel_pos in inh_procs[ip])]
                aff_procs[ip] = [rel_pos for rel_pos in set(aff_procs[ip]) if not
                                  (rel_pos in inh_procs[ip])]


            if debug > 0:
                print('AFTER REDUCTION')

                print('For process: %s' % exec_proc.name)
                print('No inh procs: %s' % [len(sublist) for sublist in inh_procs])
                print(inh_procs)
                print('No enh procs: %s' % [len(sublist) for sublist in enh_procs])
                print(enh_procs)
                print('No aff procs; %s' % [len(sublist) for sublist in aff_procs])
                print(aff_procs)
                print('  ')


            ## Write the del_proc calls for all inh_procs
            out.write('\n! Disable processes\n\n')
            for ip,sublist in enumerate(inh_procs):
                for rel_pos in sublist:
                    out.write('%sif(can_do(%s,cell + (/ %s, %s, %s, 1/))) then\n'
                              % (' '*indent,data.process_list[ip].name,
                                    rel_pos[0],rel_pos[1],rel_pos[2]))
                    out.write('%scall del_proc(%s,cell + (/ %s, %s, %s, 1/))\n'
                              % (' '*2*indent,data.process_list[ip].name,
                                    rel_pos[0],rel_pos[1],rel_pos[2]))
                    out.write('%send if\n' % (' '*indent))


            ## Update the lattice!
            out.write('\n! Update the lattice\n')
            for exec_action in exec_proc.action_list:
                # find the corresponding condition
                matching_conds = [cond for cond in exec_proc.condition_list
                                  if cond.coord == exec_action.coord]
                if len(matching_conds)==1:
                    prev_spec = matching_conds[0].species
                else:
                    raise RuntimeError('Found wrong number of matching conditions: %s'
                                       % len(matching_conds))
                out.write('%scall replace_species(cell%s,%s,%s)\n' % (
                                                             ' '*indent,
                                                             exec_action.coord.radd_ff(),
                                                             prev_spec,
                                                             exec_action.species))

            ## Write the modification routines for already active processes
            out.write('\n! Update rate constants\n\n')
            for ip,sublist in enumerate(aff_procs):
                for rel_pos in sublist:
                    out.write('%sif(can_do(%s,cell + (/ %s, %s, %s, 1/))) then\n'
                              % (' '*indent,data.process_list[ip].name,
                                rel_pos[0], rel_pos[1], rel_pos[2]))
                    rel_site = 'cell + (/ %s, %s, %s, 1/)' % rel_pos
                    rel_cell = 'cell + (/ %s, %s, %s, 0/)' % rel_pos
                    out.write('%scall update_rates_matrix(%s,%s,get_rate_%s(%s))\n'
                              % (' '*2*indent,
                                 data.process_list[ip].name,
                                 rel_site,
                                 data.process_list[ip].name,
                                 rel_cell,
                                 ))
                    out.write('%send if\n' % (' '*indent))

            ## Write the update_rate calls for all processes if allowed
            ## Prepare a flatlist of all processes name, the relative
            ## coordinate in which to be executed and the list of
            ## need-to-be-checked conditions in the order
            ## [ other_conditions, (proc_name, relative_site, True) ]
            ## to mantain compatibility with older routine
            enabling_items = []
            out.write('\n! Enable processes\n\n')
            for ip,sublist in enumerate(enh_procs):
                for rel_pos in sublist:
                    # rel_pos_string = 'cell + (/ %s, %s, %s, 1 /)' % (rel_pos[0],rel_pos[1],rel_pos[2]) # FIXME
                    item2 = (data.process_list[ip].name,copy.deepcopy(rel_pos),True)
                    ## filter out conditions already met
                    other_conditions = []
                    for cond in data.process_list[ip].condition_list:
                        # this probably be incorporated in the part in which we
                        # eliminated duplicates... must think exactly how
                        for exec_action in exec_proc.action_list:
                            if (exec_action.coord.name == cond.coord.name and
                                exec_action.coord.layer == cond.coord.layer and
                                rel_pos == tuple((exec_action.coord-cond.coord).offset)):
                                if not exec_action.species == cond.species:
                                    raise RuntimeError('Found discrepancy in process selected for enabling!')
                                else:
                                    break
                        else:
                            relative_coord = Coord(name=cond.coord.name,
                                                   layer=cond.coord.layer,
                                                   offset=cond.coord.offset+np.array(rel_pos),
                                                   )
                            other_conditions.append(ConditionAction(coord=relative_coord,
                                                                   species=cond.species))
                    enabling_items.append((copy.deepcopy(other_conditions),copy.deepcopy(item2)))

            self._write_optimal_iftree_otf(enabling_items, indent, out)
            out.write('\nend subroutine %s\n' % routine_name)
            if separate_files:
                out.close()

    def _write_optimal_iftree_otf(self, items, indent, out):
        # this function is called recursively
        # so first we define the ANCHORS or SPECIAL CASES
        # if no conditions are left, enable process immediately
        # I actually don't know if this tree is optimal
        # So consider this a heuristic solution which should give
        # on average better results than the brute force way

        # TODO Must correct site/coord once understood

        # print(' ')
        # print('ROUTINE GOT CALLED')
        # print(' ')

        for item in filter(lambda x: not x[0], items):
            # [1][2] field of the item determine if this search is intended for enabling (=True) or
            # disabling (=False) a process
            if item[1][2]:
                rel_cell = 'cell + (/ %s, %s, %s, 0/)' % (item[1][1][0],
                                                          item[1][1][1],
                                                          item[1][1][2],)
                rel_site = 'cell + (/ %s, %s, %s, 1/)' % (item[1][1][0],
                                                          item[1][1][1],
                                                          item[1][1][2],)
                out.write('%scall add_proc(%s, %s, get_rate_%s(%s))\n' % (' ' * indent,
                                                                           item[1][0], rel_site,
                                                                           item[1][0], rel_cell))
            else:
                out.write('%scall del_proc(%s, %s)\n' % (' ' * indent, item[1][0], rel_site))

        # and only keep those that have conditions
        items = filter(lambda x: x[0], items)
        if not items:
            return

        # now the GENERAL CASE
        # first find site, that is most sought after
        most_common_coord = _most_common([y.coord for y in _flatten([x[0] for x in items])])

        # filter out list of uniq answers for this site
        answers = [y.species for y in filter(lambda x: x.coord == most_common_coord, _flatten([x[0] for x in items]))]
        uniq_answers = list(set(answers))

        if self.data.meta.debug > 1:
            out.write('print *,"    IFTREE/GET_SPECIES/VSITE","%s"\n' % most_common_coord)
            out.write('print *,"    IFTREE/GET_SPECIES/SITE","%s"\n' % most_common_coord.radd_ff())
            # out.write('print *,"    IFFTREE/GET_SPECIES/SPECIES",get_species(cell%s)\n' % most_common_coord.radd_ff())

        # rel_coord = 'cell + (/ %s, %s, %s, %s /)' % (most_common_coord.offset[0],
        #                                              most_common_coord.offset[1],
        #                                              most_common_coord.offset[2],
        #                                              most_common_coord.name)
        # out.write('%sselect case(get_species(%s))\n' % ((indent) * ' ', rel_coord))
        out.write('%sselect case(get_species(cell%s))\n' % ((indent) * ' ', most_common_coord.radd_ff() ))
        for answer in uniq_answers:

            # print(' ')
            # print('NEW answer = %s' % answer)
            # print(' ')

            out.write('%scase(%s)\n' % ((indent) * ' ', answer))
            # this very crazy expression matches at items that contain
            # a question for the same coordinate and have the same answer here

            # print('Calling nested items with:')
            # print(items)
            # print('for most_common_coord: %s' % most_common_coord)
            # print(' ')

            nested_items = filter(
                lambda x:
                (most_common_coord in [y.coord for y in x[0]]
                and answer == filter(lambda y: y.coord == most_common_coord, x[0])[0].species),
                items)

            # print('nested items resulted in:')
            # print(nested_items)
            # print(' ')

            # pruned items are almost identical to nested items, except the have
            # the one condition removed, that we just met
            pruned_items = []
            for nested_item in nested_items:

                conditions = filter(lambda x: most_common_coord != x.coord, nested_item[0])
                pruned_items.append((conditions, nested_item[1]))

            items = filter(lambda x: x not in nested_items, items)
            self._write_optimal_iftree_otf(pruned_items, indent + 4, out)
        out.write('%send select\n\n' % (indent * ' ',))

        if items:
            # if items are left
            # the RECURSION II
            self._write_optimal_iftree_otf(items, indent, out)

    def write_proclist_put_take(self, data, out):
        """
        HERE comes the bulk part of this code generator:
        the put/take/create/annihilation functions
        encode what all the processes we defined mean in terms
        updates for the geometry and the list of available processes

        The updates that disable available process are pretty easy
        and flat so they cannot be optimized much.
        The updates enabling processes are more sophisticasted: most
        processes have more than one condition. So enabling one condition
        of a processes is not enough. We need to check if all the other
        conditions are met after this update as well. All these checks
        typically involve many repetitive questions, i.e. we will
        inquire the lattice many times about the same site.
        To mend this we first collect all processes that could be enabled
        and then use a heuristic algorithm (any theoretical computer scientist
        knows how to improve on this?) to construct an improved if-tree
        """
        for species in data.species_list:
            if species.name == data.species_list.default_species:
                continue  # don't put/take 'empty'
            # iterate over all layers, sites, operations, process, and conditions ...
            for layer in data.layer_list:
                for site in layer.sites:
                    for op in ['put', 'take']:
                        enabled_procs = []
                        disabled_procs = []
                        # op = operation
                        routine_name = '%s_%s_%s_%s' % (op, species.name, layer.name, site.name)
                        out.write('subroutine %s(site)\n\n' % routine_name)
                        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                        if data.meta.debug > 0:
                            out.write('print *,"PROCLIST/%s/SITE",site\n' % (routine_name.upper(), ))
                        out.write('    ! update lattice\n')
                        if op == 'put':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES","%s"\n'
                                          % data.species_list.default_species)
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES","%s"\n'
                                            % species.name)
                            out.write('    call replace_species(site, %s, %s)\n\n'
                                       % (data.species_list.default_species, species.name))
                        elif op == 'take':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES","%s"\n'
                                          % species.name)
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES","%s"\n'
                                          % data.species_list.default_species)
                            out.write('    call replace_species(site, %s, %s)\n\n' %
                                      (species.name, data.species_list.default_species))
                        for process in data.process_list:
                            for condition in process.condition_list:
                                if site.name == condition.coord.name and \
                                   layer.name == condition.coord.layer:
                                    # first let's check if we could be enabling any site
                                    # this can be the case if we put down a particle, and
                                    # it is the right one, or if we lift one up and the process
                                    # needs an empty site
                                    if op == 'put' \
                                        and  species.name == condition.species \
                                        or op == 'take' \
                                        and condition.species == data.species_list.default_species:

                                        # filter out the current condition, because we know we set it to true
                                        # right now
                                        other_conditions = filter(lambda x: x.coord != condition.coord, process.condition_list)
                                        # note how '-' operation is defined for Coord class !
                                        # we change the coordinate part to already point at
                                        # the right relative site
                                        other_conditions = [ConditionAction(
                                                species=other_condition.species,
                                                coord=('site%s' % (other_condition.coord - condition.coord).radd_ff())) for
                                                other_condition in other_conditions]
                                        enabled_procs.append((other_conditions, (process.name, 'site%s' % (process.executing_coord() - condition.coord).radd_ff(), True)))
                                    # and we disable something whenever we put something down, and the process
                                    # needs an empty site here or if we take something and the process needs
                                    # something else
                                    elif op == 'put' \
                                        and condition.species == data.species_list.default_species \
                                        or op == 'take' \
                                        and species.name == condition.species:
                                            coord = process.executing_coord() - condition.coord
                                            disabled_procs.append((process, coord))
                        # updating disabled procs is easy to do efficiently
                        # because we don't ask any questions twice, so we do it immediately
                        if disabled_procs:
                            out.write('    ! disable affected processes\n')
                            for process, coord in disabled_procs:
                                if data.meta.debug > 1:
                                    out.write('print *,"    LATTICE/CAN_DO/PROC",%s\n' % process.name)
                                    out.write('print *,"    LATTICE/CAN_DO/VSITE","site%s"\n' % (coord).radd_ff())
                                    out.write('print *,"    LATTICE/CAN_DO/SITE",site%s\n' % (coord).radd_ff())
                                #out.write(('    if(can_do(%(proc)s, site%(coord)s))then\n'
                                out.write(('    if(avail_sites(%(proc)s, lattice2nr(%(unpacked)s), 2).ne.0)then\n'
                                + '        call del_proc(%(proc)s, site%(coord)s)\n'
                                + '    endif\n\n') % {'coord': (coord).radd_ff(),
                                                      'proc': process.name,
                                                      'unpacked': coord.site_offset_unpacked()})

                        # updating enabled procs is not so simply, because meeting one condition
                        # is not enough. We need to know if all other conditions are met as well
                        # so we collect  all questions first and build a tree, where the most
                        # frequent questions are closer to the top
                        if enabled_procs:
                            out.write('    ! enable affected processes\n')

                            self._write_optimal_iftree(items=enabled_procs, indent=4, out=out)
                        out.write('\nend subroutine %s\n\n' % routine_name)

    def write_proclist_touchup(self, data, out):
        for layer in data.layer_list:
            for site in layer.sites:
                routine_name = 'touchup_%s_%s' % (layer.name, site.name)
                out.write('subroutine %s(site)\n\n' % routine_name)
                out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                # First remove all process from this site
                for process in data.process_list:
                    out.write('    if (can_do(%s, site)) then\n' % process.name)
                    out.write('        call del_proc(%s, site)\n' % process.name)
                    out.write('    endif\n')
                # Then add all available one
                items = []
                for process in data.process_list:
                    executing_coord = process.executing_coord()
                    if executing_coord.layer == layer.name \
                        and executing_coord.name == site.name:
                        condition_list = [ConditionAction(
                            species=condition.species,
                            coord='site%s' % (condition.coord - executing_coord).radd_ff(),
                            ) for condition in process.condition_list]
                        items.append((condition_list, (process.name, 'site', True)))

                self._write_optimal_iftree(items=items, indent=4, out=out)
                out.write('end subroutine %s\n\n' % routine_name)

    def write_proclist_multilattice(self, data, out):
        if len(data.layer_list) > 1:
            # where are in multi-lattice mode
            for layer in data.layer_list:
                for site in layer.sites:
                    for special_op in ['create', 'annihilate']:
                        enabled_procs = []
                        disabled_procs = []
                        routine_name = '%s_%s_%s' % (special_op, layer.name, site.name)
                        out.write('subroutine %s(site, species)\n\n' % routine_name)
                        out.write('    integer(kind=iint), intent(in) :: species\n')
                        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                        out.write('    ! update lattice\n')
                        if data.meta.debug > 0:
                            out.write('print *,"PROCLIST/%s/SITE",site\n' % (routine_name.upper(), ))
                        if special_op == 'create':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES","null_species"\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES",species\n')
                            out.write('    call replace_species(site, null_species, species)\n\n')
                        elif special_op == 'annihilate':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES",species\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES","null_species"\n')
                            out.write('    call replace_species(site, species, null_species)\n\n')

                        for process in data.process_list:
                            for condition in filter(lambda condition: condition.coord.name == site.name and
                                                                      condition.coord.layer == layer.name,
                                                                      process.condition_list):
                                if special_op == 'create':
                                    other_conditions = [ConditionAction(
                                            species=other_condition.species,
                                            coord=('site%s' % (other_condition.coord - condition.coord).radd_ff()))
                                            for other_condition in process.condition_list]
                                    enabled_procs.append((other_conditions, (process.name,
                                        'site%s' % (process.executing_coord()
                                        - condition.coord).radd_ff(), True)))
                                elif special_op == 'annihilate':
                                    coord = process.executing_coord() - condition.coord
                                    disabled_procs.append((process, coord))
                        if disabled_procs:
                            out.write('    ! disable affected processes\n')
                            for process, coord in disabled_procs:
                                if data.meta.debug > 1:
                                    out.write('print *,"    LATTICE/CAN_DO/PROC",%s\n' % process.name)
                                    out.write('print *,"    LATTICE/CAN_DO/VSITE","site%s"\n' % (coord).radd_ff())
                                    out.write('print *,"    LATTICE/CAN_DO/SITE",site%s\n' % (coord).radd_ff())
                                out.write(('    if(can_do(%(proc)s, site%(coord)s))then\n'
                                + '        call del_proc(%(proc)s, site%(coord)s)\n'
                                + '    endif\n\n') % {'coord': (coord).radd_ff(), 'proc': process.name})
                        if enabled_procs:
                            out.write('    ! enable affected processes\n')
                            self._write_optimal_iftree(items=enabled_procs, indent=4, out=out)
                        out.write('\nend subroutine %s\n\n' % routine_name)

    def write_proclist_end(self, out):
        out.write('end module proclist\n')

    def _write_optimal_iftree(self, items, indent, out):
        # this function is called recursively
        # so first we define the ANCHORS or SPECIAL CASES
        # if no conditions are left, enable process immediately
        # I actually don't know if this tree is optimal
        # So consider this a heuristic solution which should give
        # on average better results than the brute force way

        for item in filter(lambda x: not x[0], items):
            # [1][2] field of the item determine if this search is intended for enabling (=True) or
            # disabling (=False) a process
            if item[1][2]:
                out.write('%scall add_proc(%s, %s)\n' % (' ' * indent, item[1][0], item[1][1]))
            else:
                out.write('%scall del_proc(%s, %s)\n' % (' ' * indent, item[1][0], item[1][1]))

        # and only keep those that have conditions
        items = filter(lambda x: x[0], items)
        if not items:
            return

        # now the GENERAL CASE
        # first find site, that is most sought after
        most_common_coord = _most_common([y.coord for y in _flatten([x[0] for x in items])])

        # filter out list of uniq answers for this site
        answers = [y.species for y in filter(lambda x: x.coord == most_common_coord, _flatten([x[0] for x in items]))]
        uniq_answers = list(set(answers))

        if self.data.meta.debug > 1:
            out.write('print *,"    LATTICE/GET_SPECIES/VSITE","%s"\n' % most_common_coord)
            out.write('print *,"    LATTICE/GET_SPECIES/SITE",%s\n' % most_common_coord)
            out.write('print *,"    LATTICE/GET_SPECIES/SPECIES",get_species(%s)\n' % most_common_coord)

        out.write('%sselect case(get_species(%s))\n' % ((indent) * ' ', most_common_coord))
        for answer in uniq_answers:
            out.write('%scase(%s)\n' % ((indent) * ' ', answer))
            # this very crazy expression matches at items that contain
            # a question for the same coordinate and have the same answer here
            nested_items = filter(
                lambda x: (most_common_coord in [y.coord for y in x[0]]
                and answer == filter(lambda y: y.coord == most_common_coord, x[0])[0].species),
                items)
            # pruned items are almost identical to nested items, except the have
            # the one condition removed, that we just met
            pruned_items = []
            for nested_item in nested_items:
                conditions = filter(lambda x: most_common_coord != x.coord, nested_item[0])
                pruned_items.append((conditions, nested_item[1]))

            items = filter(lambda x: x not in nested_items, items)
            self._write_optimal_iftree(pruned_items, indent + 4, out)
        out.write('%send select\n\n' % (indent * ' ',))

        if items:
            # if items are left
            # the RECURSION II
            self._write_optimal_iftree(items, indent, out)

    def write_settings(self, code_generator='lat_int'):
        """Write the kmc_settings.py. This contains all parameters, which
        can be changed on the fly and without recompilation of the Fortran 90
        modules.
        """

        from kmos import evaluate_rate_expression

        data = self.data
        out = open(os.path.join(self.dir, 'kmc_settings.py'), 'w')
        out.write('model_name = \'%s\'\n' % self.data.meta.model_name)
        out.write('simulation_size = 20\n')
        out.write('random_seed = 1\n\n')

        # stub for setup function
        out.write('def setup_model(model):\n')
        out.write('    """Write initialization steps here.\n')
        out.write('       e.g. ::\n')
        out.write('    model.put([0,0,0,model.lattice.default_a], model.proclist.species_a)\n')
        out.write('    """\n')
        out.write('    #from setup_model import setup_model\n')
        out.write('    #setup_model(model)\n')
        out.write('    pass\n\n')

        out.write('# Default history length in graph\n')
        out.write('hist_length = 30\n\n')
        # Parameters
        out.write('parameters = {\n')
        for parameter in data.parameter_list:
            out.write(('    "%s":{"value":"%s", "adjustable":%s,'
            + ' "min":"%s", "max":"%s","scale":"%s"},\n') % (parameter.name,
                                          parameter.value,
                                          parameter.adjustable,
                                          parameter.min,
                                          parameter.max,
                                          parameter.scale))
        out.write('    }\n\n')

        # Rate constants
        out.write('rate_constants = {\n')
        for process in data.process_list:
            out.write('    "%s":("%s", %s),\n' % (process.name,
                                                  process.rate_constant,
                                                  process.enabled))
            try:
                parameters = {}
                for param in data.parameter_list:
                    parameters[param.name] = {'value': param.value}
            except Exception, e:
                raise UserWarning('Parameter ill-defined(%s)\n%s\nProcess: %s'
                                  % (param, e, process.name))

            try:
                evaluate_rate_expression(process.rate_constant, parameters)
            except Exception, e:
                raise UserWarning('Could not evaluate (%s)\n%s\nProcess: %s'
                                  % (process.rate_constant, e, process.name))
        out.write('    }\n\n')


        if code_generator == 'otf':
            # additional auxiliary variables to be used in the calculation of rate constants
            # Must explore all rate expressions and otf_rate expressions
            _ , _, chempot_list = self._otf_get_auxilirary_params(data)
            if chempot_list:
                out.write('chemical_potentials = [\n')
                for param in chempot_list:
                    out.write('    "%s",\n' % param)
                out.write('    ]\n\n')

        # Site Names
        site_params = self._get_site_params()
        out.write('site_names = %s\n' % ['%s_%s' % (x[1], x[0]) for x in site_params])

        # Graphical Representations
        # rename to species
        # and include tags
        out.write('representations = {\n')
        for species in sorted(data.get_speciess(), key=lambda x: x.name):
            out.write('    "%s":"""%s""",\n'
                % (species.name,
                species.representation.strip()))
        out.write('    }\n\n')
        out.write('lattice_representation = """%s"""\n\n' % data.layer_list.representation)

        # Species Tags
        out.write('species_tags = {\n')
        for species in sorted(data.get_speciess(), key=lambda x: x.name):
            out.write('    "%s":"""%s""",\n'
                % (species.name,
                species.tags.strip()))
        out.write('    }\n\n')

        # TOF counting
        out.write('tof_count = {\n')
        for process in data.get_processes():
            if process.tof_count is not None:
                out.write('    "%s":%s,\n' % (process.name, process.tof_count))
        out.write('    }\n\n')

        # XML
        out.write('xml = """%s"""\n' % data)

        out.close()

    def _get_site_params(self):
        data = self.data
        site_params = []
        for layer in data.layer_list:
            for site in layer.sites:
                site_params.append((site.name, layer.name, tuple(site.pos)))
        return site_params

    def _gpl_message(self):
        """Prints the GPL statement at the top of the source file"""
        data = self.data
        out = ''
        out += "!  This file was generated by kMOS (kMC modelling on steroids)\n"
        out += "!  written by Max J. Hoffmann mjhoffmann@gmail.com (C) 2009-2013.\n"
        if hasattr(data.meta, 'author'):
            out += '!  The model was written by ' + data.meta.author + '.\n'
        out += """
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
"""
        return out


def export_source(project_tree, export_dir=None, code_generator='local_smart'):
    """Export a kmos project into Fortran 90 code that can be readily
    compiled using f2py.  The model contained in project_tree
    will be stored under the directory export_dir. export_dir will
    be created if it does not exist. The XML representation of the
    model will be included in the kmc_settings.py module.

    `export_source` is *the* central feature of the `kmos` approach.
    In order to generate different *backend* solvers, additional candidates
    of this methods could be implemented.
    """
    if export_dir is None:
        export_dir = project_tree.meta.model_name

    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # FIRST
    # copy static files
    # each file is tuple (source, target)
    if code_generator == 'local_smart':
        cp_files = [(os.path.join('fortran_src', 'assert.ppc'), 'assert.ppc'),
                    (os.path.join('fortran_src', 'base.f90'), 'base.f90'),
                    (os.path.join('fortran_src', 'kind_values.f90'), 'kind_values.f90'),
                    (os.path.join('fortran_src', 'main.f90'), 'main.f90'),
                    ]
    elif code_generator == 'lat_int':
        cp_files = [(os.path.join('fortran_src', 'assert.ppc'), 'assert.ppc'),
                    (os.path.join('fortran_src', 'base_lat_int.f90'), 'base.f90'),
                    (os.path.join('fortran_src', 'kind_values.f90'), 'kind_values.f90'),
                    (os.path.join('fortran_src', 'main.f90'), 'main.f90'),
                    ]
    elif code_generator == 'otf':
        cp_files = [(os.path.join('fortran_src', 'assert.ppc'), 'assert.ppc'),
                    (os.path.join('fortran_src', 'base_otf.f90'), 'base.f90'),
                    (os.path.join('fortran_src', 'kind_values.f90'), 'kind_values.f90'),
                    (os.path.join('fortran_src', 'main.f90'), 'main.f90'),
                    ]
    else:
        raise UserWarning("Don't know this backend")

    exec_files = []
    print(APP_ABS_PATH)

    for filename, target in cp_files:
        shutil.copy(os.path.join(APP_ABS_PATH, filename),
                    os.path.join(export_dir, target))

    for filename in exec_files:
        shutil.copy(os.path.join(APP_ABS_PATH, filename), export_dir)
        os.chmod(os.path.join(export_dir, filename), 0755)

    # SECOND
    # produce those source files that are written on the fly
    writer = ProcListWriter(project_tree, export_dir)
    writer.write_lattice(code_generator=code_generator)
    writer.write_proclist(code_generator=code_generator)
    writer.write_settings(code_generator=code_generator)
    project_tree.validate_model()
    return True


def import_xml(xml):
    from tempfile import mktemp
    from os import remove

    xml_filename = mktemp()
    xml_file = file(xml_filename, 'w')
    xml_file.write(xml)
    xml_file.close()
    project = import_xml_file(xml_filename)
    remove(xml_filename)
    return project


def import_xml_file(filename):
    """Imports and returns project from an XML file."""
    import kmos.types
    project_tree = kmos.types.Project()
    project_tree.import_file(filename)
    return project_tree


def export_xml(project_tree, filename=None):
    """Writes a project to an XML file."""
    if filename is None:
        filename = '%s.xml' % project_tree.meta.model_name
    f = open(filename, 'w')
    for line in str(project_tree):
        f.write(line)
    f.close()
