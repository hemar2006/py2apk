#! /usr/bin/env python3

import py2apk, sys

HELP_TEXT = '''
optional arguments:
  help              show this help message and exit
  install           install all prerequisite
  new               create new app
  build             build debug app  
  run               run debug app in emulator
  package           package app for distribution 
'''

if __name__ == '__main__':
    if sys.argv[1] == 'install':
        app = py2apk.Py2Apk()
        app.install()
    elif sys.argv[1] == 'new':
        app = py2apk.Py2Apk()
        app.new()
    elif sys.argv[1] == 'build':
        app = py2apk.Py2Apk()
        app.build()
    elif sys.argv[1] == 'run':
        app = py2apk.Py2Apk()
        app.run()
    elif sys.argv[1] == 'package':
        app = py2apk.Py2Apk()
        app.package()
    elif sys.argv[1] == 'help':        
        print(HELP_TEXT)        
    else:
        print('usage: py2apk.py help')
    sys.exit()
