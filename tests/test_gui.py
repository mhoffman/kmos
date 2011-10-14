#!/usr/bin/env python

def test_gui():
    import os, sys
    import os.path, shutil

    import kmos.gui

    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    editor = kmos.gui.Editor()
    editor.import_file('export_test/default.xml')
    os.chdir(cwd)
    assert len(editor.project_tree.get_processes()) == 36

if __name__ == '__main__':
    test_gui()
