#! /usr/bin/env python3

import py2apk, sys

if __name__ == '__main__':
    if sys.argv[1] == 'new':
        app = py2apk.Py2Apk()
        app.new()
    elif sys.argv[1] == 'build':
        app = py2apk.Py2Apk()
        app.buid()
    elif sys.argv[1] == 'run':
        app = py2apk.Py2Apk()
        app.run()
    elif sys.argv[1] == 'package':
        app = py2apk.Py2Apk()
        app.package()
    else:
        print('usage: py2apk.py [-h]')
    sys.exit()
    
