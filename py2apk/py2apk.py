#! /usr/bin/env python3

import os, toml, jdk, zipfile, requests, platform, shutil, subprocess, time
from string import Template
from PIL import Image
from tqdm import tqdm
from getpass import getpass

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))
XML_FILE = os.path.join(PACKAGE_DIR, 'resources/AndroidManifest.xml')
ACTIVITY_FILE = os.path.join(PACKAGE_DIR, 'resources/activity_main.xml')
STRING_FILE = os.path.join(PACKAGE_DIR, 'resources/strings.xml')
STYLE_FILE = os.path.join(PACKAGE_DIR, 'resources/styles.xml')
HTML_FILE = os.path.join(PACKAGE_DIR, 'resources/index.html')
JAVA_FILE = os.path.join(PACKAGE_DIR, 'resources/MainActivity.java')
CLIENT_FILE = os.path.join(PACKAGE_DIR, 'resources/MyWebViewClient.java')
GRADLE_FILE = os.path.join(PACKAGE_DIR, 'resources/build.gradle')
ICON_FILE = os.path.join(PACKAGE_DIR, 'resources/icon.png')
HOME = os.path.expanduser("~")
os.environ["JAVA_HOME"] = f'{HOME}/.py2apk/jdk'
os.environ["ANDROID_HOME"] = f'{HOME}/.py2apk/android-sdk'
pathlist = [
    f'{HOME}/.py2apk/jdk/bin',
    f'{HOME}/.py2apk/gradle/gradle-7.1.1/bin',
    f'{HOME}/.py2apk/android-sdk/cmdline-tools/latest/bin',
    f'{HOME}/.py2apk/android-sdk/emulator',
    f'{HOME}/.py2apk/android-sdk/platform-tools'
]
os.environ["PATH"] += os.pathsep + os.pathsep.join(pathlist)

class Py2Apk():

    def __init__(self) -> None:
        pass

    def render(self, source, destination, data):
        file_name = os.path.basename(source)
        with open(source, 'r') as template_file:
            t = Template(template_file.read()).substitute(data)
        if destination:
            if not os.path.exists(destination):
                os.makedirs(destination)       
            with open(os.path.join(destination, file_name), 'w') as destination_file:
                destination_file.write(t)
        else:
            with open(file_name, 'w') as destination_file:
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
        im.save(f'src/main/ic_launcher-web.png')
        for size in sizes:
            path = os.path.join('src', 'main', 'res', size['name'])
            if not os.path.exists(path):
                os.makedirs(path)
            im = Image.open(data)
            im.thumbnail((size['d'], size['d']))
            im.save(f'{path}/ic_launcher.png')

    def unzip(self, source, destination):
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(destination)

    def download_file(self, name, url):
        response = requests.get(url, stream=True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f'download {name}')
        with open(name, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            os.remove(name)
            return self.download_data()        

    def install(self):
        if os.path.exists(f'{HOME}/.py2apk'):
            print('delete old files...')
            shutil.rmtree(f'{HOME}/.py2apk')
        print('download jdk...')
        jdk_11 = jdk.install('11')
        shutil.move(jdk_11, f'{HOME}/.py2apk/jdk')
        shutil.rmtree(f'{HOME}/.jdk')
        print('jdk installed!')
        self.download_file('gradle.zip', 'https://services.gradle.org/distributions/gradle-7.1.1-bin.zip')
        self.unzip('gradle.zip', f'{HOME}/.py2apk/gradle')
        os.remove('gradle.zip')                    
        print('gradle installed!')
        if platform.system() == 'Windows':
            sdk = 'win'
        if platform.system() == 'Darwin':
            sdk = 'mac'
        if platform.system() == 'Linux':
            sdk = 'linux'
        self.download_file('cmdline-tools.zip', f'https://dl.google.com/android/repository/commandlinetools-{sdk}-7583922_latest.zip')
        self.unzip('cmdline-tools.zip', f'{HOME}/.py2apk/android-sdk/')
        os.remove('cmdline-tools.zip')
        shutil.move(f'{HOME}/.py2apk/android-sdk/cmdline-tools', f'{HOME}/.py2apk/android-sdk/latest')
        shutil.move(f'{HOME}/.py2apk/android-sdk/latest', f'{HOME}/.py2apk/android-sdk/cmdline-tools/latest')
        if os.name != 'nt':
            os.system(f'chmod +x {HOME}/.py2apk/gradle/gradle-7.1.1/bin/gradle')
            os.system(f'chmod +x {HOME}/.py2apk/android-sdk/cmdline-tools/latest/bin/sdkmanager')
            os.system(f'chmod +x {HOME}/.py2apk/android-sdk/cmdline-tools/latest/bin/avdmanager')
        os.system('sdkmanager --licenses')
        os.system('sdkmanager --install "system-images;android-28;default;x86"')
        os.system('avdmanager --verbose create avd --name "py2apk_emu" --abi "x86" --package "system-images;android-28;default;x86" --device "pixel"')        
        print('android-sdk installed!')
        if os.path.exists(f'{PACKAGE_DIR}/resources'):
            shutil.rmtree(f'{PACKAGE_DIR}/resources')
        self.download_file('resources.zip', 'https://github.com/anbuhckr/py2apk/releases/download/v1.2.0/resources.zip')
        self.unzip('resources.zip', PACKAGE_DIR)
        os.remove('resources.zip')
        print('resources installed!')                 

    def new(self):
        data_toml = {'data': {
            'app_name': input('App name: '),            
            'package_name': input('Package name: '),            
            'version_name': input('Version: '),
            'status_color': input('Status bar color: ') or '#202225',
            'icon_file': input('Icon: ') or ICON_FILE,         
            'url_path': input('URL: ') or 'file:///android_asset/index.html',         
        }}
        with open('app.toml', 'w') as f:
            toml.dump(data_toml, f)
        data = data_toml['data']        
        self.render(XML_FILE, 'src/main/', data)
        self.render(ACTIVITY_FILE, 'src/main/res/layout/', data)
        self.render(STRING_FILE, 'src/main/res/values/', data)
        self.render(STYLE_FILE, 'src/main/res/values/', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/', data)
        data['host_name'] = '.'.join(reversed(data['package_name'].split('.')))
        self.render(CLIENT_FILE, f'{targetPath}/', data)
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, None, data)        
        self.render(HTML_FILE, 'src/main/assets/', data)
        self.icons(data['icon_file'])

    def build(self):
        data_toml = toml.load('app.toml')
        data = data_toml['data']        
        self.render(XML_FILE, 'src/main/', data)
        self.render(ACTIVITY_FILE, 'src/main/res/layout/', data)
        self.render(STRING_FILE, 'src/main/res/values/', data)
        self.render(STYLE_FILE, 'src/main/res/values/', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/', data)
        data['host_name'] = '.'.join(reversed(data['package_name'].split('.')))
        self.render(CLIENT_FILE, f'{targetPath}/', data)
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, None, data)        
        self.icons(data['icon_file'])
        os.system('gradle wrapper')
        if os.name == 'nt:
            os.system('gradlew assembleDebug')
            os.system('gradlew bundleDebug')
        else:
            os.system('chmod +x gradlew')
            os.system('./gradlew assembleDebug')
            os.system('./gradlew bundleDebug')

    def run(self):
        if os.name == 'nt':
            os.system('start /MIN emulator @py2apk_emu')
        else:
            os.system(f'chmod +x {HOME}/.py2apk/android-sdk/emulator/emulator')
            os.system(f'chmod +x {HOME}/.py2apk/android-sdk/platform-tools/adb')
            os.system('emulator @py2apk_emu &')
        print('Waiting for emulator to start...', flush=True, end='')
        stats = None
        while not stats:
            adb = subprocess.check_output(['adb', 'devices']).decode().strip()
            if 'emulator' in adb and 'offline' not in adb:
                stats = True
            print('.', flush=True, end='')
            time.sleep(1)
        data_toml = toml.load('app.toml')
        data = data_toml['data']
        package = data['package_name']
        app_name = os.getcwd().split('\\')[-1]
        os.system(f'adb uninstall {package}')
        os.system(f'adb install "{os.getcwd()}/build/outputs/apk/debug/{app_name}-debug.apk"')
        os.system(f'adb shell am start -n {package}/{package}.MainActivity')

    def package(self):        
        data_toml = toml.load('app.toml')
        data = data_toml['data']
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, None, data)
        key_pass = getpass('Enter keystore password: ')
        key_name = data['package_name'].replace('.', '_')
        if not os.path.exists(f'{key_name}.jks'):
            os.system(f'keytool -genkey -v -keystore {key_name}.jks -keyalg RSA -keysize 2048 -validity 10000 -alias {key_name} -storepass {key_pass} -keypass {key_pass}')
        if os.name == 'nt':
            gdl = 'gradle'
        else:
            gdl = './gradlew')
        os.system(f'{gdl} assembleRelease -PstoreFile="{key_name}.jks" -PstorePassword="{key_pass}" -PkeyAlias="{key_name}" -PkeyPassword="{key_pass}"')
        os.system(f'{gdl} bundleRelease -PstoreFile="{key_name}.jks" -PstorePassword="{key_pass}" -PkeyAlias="{key_name}" -PkeyPassword="{key_pass}"')

    def verify(self):
        app_name = os.getcwd().split('\\')[-1]
        os.system(f'jarsigner -verify -verbose -certs "{os.getcwd()}/build/outputs/apk/release/{app_name}-release.apk"')
