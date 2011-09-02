#!/usr/bin/python
"""Generic kMC steering script for binary modules created kmos"""

import kmc
import math
from ConfigParser import ConfigParser
from numpy import array
import StringIO
import tokenize


CONFIG_FILENAME = 'params.cfg'
DATAFILE = 'traj.dat'

class KMC_Run():
    def __init__(self):
        self.nr_of_proc = kmc.proclist.nr_of_proc

        # Read config file
        config = ConfigParser()
        # Prevent configparser from turning options to lowercase
        config.optionxform = str
        config.read(CONFIG_FILENAME)
        self.size = config.get('User Params', 'lattice_size')
        self.size = [ int(x) for x in self.size.split() ]
        name = config.get('Main', 'system_name')
        self.output_fields = config.get('Main', 'output_fields').split()
        kmc.proclist.init(self.size, name)
        self.params = {}
        for user_param in config.options('User Params'):
            self.params[user_param] = config.get('User Params', user_param)

        self.default_species = config.get('Main', 'default_species')

        # initialize name arrays
        self.process_names = []
        self.rate_expressions = []
        for i in range(kmc.proclist.nr_of_proc):
            self.rate_expressions.append(get_rate_expression(i+1))
            self.process_names.append(get_process_name(i+1))
        self.species_names = {}
        for i in range(kmc.lattice.nr_of_species):
            species_name = get_species_name(i+1)
            species_nr = int(eval('kmc.lattice.'+species_name))
            self.species_names[species_nr] = species_name
        self.lattice_names = []
        for i in range(kmc.lattice.nr_of_lattices):
            self.lattice_names.append(get_lattice_name(i+1))
        self.lattice_name = self.lattice_names[0]
        self.site_names = []
        for i in range(kmc.lattice.nr_of_sites):
            self.site_names.append(get_site_name(i+1))


        self.base = eval('kmc.lattice.lookup_nr2%s' % self.lattice_name)

        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.fill_unit_cell(x, y, self.default_species)

        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.touchup_unit_cell(x, y)





    def get_occupation(self):
        occupation = {}
        A = kmc.lattice.lattice_matrix
        for species_name in self.species_names.values():
            occupation[species_name] = {}
            for site_name in self.site_names:
                occupation[species_name][site_name] = 0.
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                for i, site in enumerate(self.base):
                    current_site = x*A[0] + y*A[1] + site
                    species = eval('kmc.lattice.%s_get_species' % self.lattice_name)(current_site)
                    species_name = self.species_names[species]
                    occupation[species_name][self.site_names[i]] += 1.
        total = float(self.size[0]*self.size[1])
        for species_name in self.species_names.values():
            for site_name in self.site_names:
                occupation[species_name][site_name] /= total
        return occupation

    def run(self):
        f = open(DATAFILE,'w')
        f.write('#\t%s\n' % ',\t'.join(self.output_fields))
        f.close()
        for i in xrange(int(self.params['total_steps'])/int(self.params['print_every'])):
            outstr = ''
            occupation = self.get_occupation()
            for field in self.output_fields:
                if field == 'kmc_step':
                    outstr += '\t%s ' % kmc.base.get_kmc_step()
                elif field == 'kmc_time':
                    outstr += '\t%s' % kmc.base.get_kmc_time()
                elif field == 'walltime':
                    outstr += '\t%s' % kmc.base.get_walltime()
                elif field in self.process_names:
                    outstr += '\t%s' % (kmc.base.get_procstat(eval('kmc.proclist.'+field))/float(self.size[0]*self.size[1]))
                elif field in self.species_names.values():
                    outstr += '\t%s ' % sum(occupation[field].values())
                elif field.count('@') == 1 :
                    field = field.split('@')
                    try:
                        outstr += '\t%s ' % occupation[field[0]][field[1]]
                    except:
                        raise UserWarning('Unknown site or species: %s' % field)
                else:
                    raise UserWarning('Could match your output request %s' % field)
                        

            f = open(DATAFILE,'a')
            f.write(outstr + '\n')
            f.close()

            for j in xrange(int(self.params['print_every'])):
                kmc.proclist.do_kmc_step()

    def set_rates(self):
        """For testing purpose we set all rates to a constant
        until formula and parameter support is implemented
        """
        for proc_nr in range(kmc.proclist.nr_of_proc):
            rate_expr = self.rate_expressions[proc_nr]
            if not rate_expr:
                kmc.base.set_rate(proc_nr+1, 0.0)
                continue
            replaced_tokens = []
            for i, token,_,_,_ in tokenize.generate_tokens(StringIO.StringIO(rate_expr).readline):
                # replace standard function by call to math module
                if token in ['sqrt','exp','sin','cos','pi','pow']:
                    replaced_tokens.append((i,'math.' + token))
                    
                # replace natural constants by call to unit module
                elif ('u_' + token) in dir(kmc.units):
                    replaced_tokens.append((i, str(eval('kmc.units.u_' + token))))
                # replace self-define params
                elif token in self.params:
                    replaced_tokens.append((i, str(self.params[token])))
                else:
                    replaced_tokens.append((i, token))
            rate_expr = tokenize.untokenize(replaced_tokens)
            try:
                kmc.base.set_rate(proc_nr+1, eval(rate_expr))
            except:
                raise UserWarning, "Could not evaluate %s, %s" % (rate_expr, proc_nr)



    def fill_unit_cell(self, x, y, species):
        species = eval('kmc.lattice.%s' % species)
        A = kmc.lattice.lattice_matrix
        for site in self.base:
            current_site = x*A[0] + y*A[1] + site
            old_species = eval('kmc.lattice.%s_get_species' % self.lattice_name)(current_site)
            eval('kmc.lattice.%s_replace_species' % self.lattice_name)(current_site, old_species, species)

    def touchup_unit_cell(self, x, y):
        A = kmc.lattice.lattice_matrix
        for i, site in enumerate(self.site_names):
            current_site = x*A[0] + y*A[1] + self.base[i]
            touchup = eval('kmc.proclist.touchup_%s_site' % site)
            touchup(current_site)



def get_rate_expression(process_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    rate_expr = ''
    i = 1
    while True:
        new_char = kmc.proclist.get_rate_char(process_nr, i)
        if new_char == ' ':
            break
        rate_expr += new_char
        i += 1
    return rate_expr

def get_process_name(process_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    process_name = ''
    i = 1
    while True:
        new_char = kmc.proclist.get_process_char(process_nr, i)
        if new_char == ' ':
            break
        process_name += new_char
        i += 1
    return process_name.lower()

def get_species_name(species_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    species_name = ''
    i = 1
    while True:
        new_char= kmc.lattice.get_species_char(species_nr, i)
        if new_char == ' ':
            break
        species_name += new_char
        i += 1
    return species_name.lower()

def get_lattice_name(lattice_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    lattice_name = ''
    i = 1
    while True:
        new_char= kmc.lattice.get_lattice_char(lattice_nr, i)
        if new_char == ' ':
            break
        lattice_name += new_char
        i += 1
    return lattice_name.lower()


def get_site_name(site_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    site_name = ''
    i = 1
    while True:
        new_char= kmc.lattice.get_site_char(site_nr, i)
        if new_char == ' ':
            break
        site_name += new_char
        i += 1
    return site_name.lower()

if __name__ == '__main__':
    kmc_run = KMC_Run()
    kmc_run.set_rates()
    kmc_run.run()
