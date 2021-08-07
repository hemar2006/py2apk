#! /usr/bin/env python3

import toml, os
from string import Template
from PIL import Image

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))
XML_FILE = os.path.join(PACKAGE_DIR, 'resources/AndroidManifest.xml')
HTML_FILE = os.path.join(PACKAGE_DIR, 'resources/index.html')
JAVA_FILE = os.path.join(PACKAGE_DIR, 'resources/MainActivity.java')
GRADLE_FILE = os.path.join(PACKAGE_DIR, 'resources/build.gradle')
ICON_FILE = os.path.join(PACKAGE_DIR, 'resources/icon.png')

class Py2Apk():

    def __init__(self) -> None:
        pass
        
    def new(self):
        data_toml = {'data': {
            'app_name': input('App name: '),            
            'package_name': input('Package name: '),
            'version_name': input('Version: '), 
            'icon_file': input('Icon: ') or ICON_FILE,         
            'url_path': input('URL: ') or 'file:///assets/index.html',            
        }}
        with open('app.toml', 'w') as f:
            toml.dump(data_toml, f)
        data = data_toml['data']
        self.render(XML_FILE, 'src/main/AndroidManifest.xml', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/MainActivity.java', data)
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, 'build.gradle', data)
        self.render(HTML_FILE, 'src/main/assets/index.html', data)
        self.icons(data['icon_file'])

    def build(self):
        data_toml = toml.load('app.toml')
        data = data_toml['data']
        self.render(XML_FILE, 'src/main/AndroidManifest.xml', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/MainActivity.java', data)
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, 'build.gradle', data)
        self.render(HTML_FILE, 'src/main/assets/index.html', data)
        self.icons(data['icon'])

    def render(self, source, destination, data):
        file_name = os.path.basename(source)
        with open(source, 'r') as template_file:
            t = Template(template_file.read()).substitute(data)
        if not os.path.exists(destination):
            try:
                os.makedirs('/'.join(destination.split('/')[:-1]))
            except:
                pass
        with open(destination, 'w') as destination_file:
            destination_file.write(t) 

    def icons(self, data):        
        sizes = [{
            'name': 'mipmap-mdpi',
            'd': 48,
        }, {
            'name': 'mipmap-hdpi',
            'd': 72,
        }, {
            'name': 'mipmap-xhdpi',
            'd': 96,
        }, {
            'name': 'mipmap-xxhdpi',
            'd': 144,
        }, {
            'name': 'mipmap-xxxhdpi',
            'd': 192,
        }]
        im = Image.open(data)
        ext = data.split('.')[1]        
        im.save(f'src/main/ic_launcher-web.{ext}')
        for size in sizes:
            path = os.path.join('src', 'main', 'res', size['name'])
            if not os.path.exists(path):
                os.makedirs(path)
            im = Image.open(data)
            im.thumbnail((size['d'], size['d']))
            im.save(f'{path}/ic_launcher.{ext}')        
