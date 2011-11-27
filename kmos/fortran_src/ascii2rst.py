#!/usr/bin/env python


import os

os.system('robodoc --src base.f90 --doc base --singlefile --ascii')

asci = file('base.txt', 'r').readlines()


new_asci = []
jump = 0
for i, line in enumerate(asci):
    if jump:
        jump += -1
        continue
    if not i :
    # make first line header
        new_asci.append(line)
        new_asci.append('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
    elif i == len(asci) - 1:
    # ignore last line
        continue
    elif 'FUNCTION' in line:
    # ignore the function string
        continue
    elif 'ARGUMENTS' in line:
    # ignore the arguments string
        new_asci.append('\n')
    elif '------' in line:
        new_asci.append(asci[i+1])
        new_asci.append('"""""""""""""""""""""""""""""""""""""""""""""""""""')
        jump = 1
    else:
        new_asci.append(line)
    



rst = file('base.rst', 'w')
for line in new_asci:
    rst.write(line)
rst.close()


os.system('rm base.txt')
os.system('rst2html base.rst > base.html')
