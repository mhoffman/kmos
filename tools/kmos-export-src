#!/usr/bin/env python
import sys
sys.path.append('..')
import main
import optparse
import os
import shutil


usage = 'usage: %prog [xml file] [export dir]\n'\
    + '    export directory will be deleted first!'

parser = optparse.OptionParser(usage=usage)
parser.add_option('-s','--source-only', action='store_true', dest='source_only', default=False, help='Export source code only, don\'t compile.')
(options, args) = parser.parse_args()

if len(args) != 2 :
    parser.print_help()
    exit()

xml_file = args[0]
export_dir = args[1]

shutil.rmtree(export_dir,ignore_errors=True)
kmc = main.KMC_Editor()
kmc.project_tree.import_xml_file(xml_file)

kmc.on_btn_export_src__clicked('',export_dir)

if os.uname()[0] == 'Linux' and not options.source_only:
    os.chdir(export_dir)
    os.system("./compile_for_f2py" )
exit()
