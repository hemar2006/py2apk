#! /usr/bin/env python3

import os, toml, jdk, zipfile, requests, platform, shutil, subprocess, time
from string import Template
from PIL import Image
from tqdm import tqdm
from getpass import getpass

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))
MANIFEST_FILE = os.path.join(PACKAGE_DIR, 'resources/AndroidManifest.xml')
ACTIVITY_FILE = os.path.join(PACKAGE_DIR, 'resources/activity_main.xml')
STRING_FILE = os.path.join(PACKAGE_DIR, 'resources/strings.xml')
STYLE_FILE = os.path.join(PACKAGE_DIR, 'resources/styles.xml')
BG_FILE = os.path.join(PACKAGE_DIR, 'resources/bg_splash.xml')
COLOR_FILE = os.path.join(PACKAGE_DIR, 'resources/colors.xml')
HTML_FILE = os.path.join(PACKAGE_DIR, 'resources/index.html')
JAVA_FILE = os.path.join(PACKAGE_DIR, 'resources/MainActivity.java')
GRADLE_FILE = os.path.join(PACKAGE_DIR, 'resources/build.gradle')
GP_FILE = os.path.join(PACKAGE_DIR, 'resources/gradle.properties')
ICON_FILE = os.path.join(PACKAGE_DIR, 'resources/icon.png')
LOGO_FILE = os.path.join(PACKAGE_DIR, 'resources/logo.png')
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

    def icons(self, data, logo):
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
        im2 = Image.open(logo)           
        im2.save('src/main/res/drawable/ic_logo.png') 
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
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024                   
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f'download {name}')
        with open(name, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            os.remove(name)
            return self.download_file(name, url)

    def download_data(self, name, url):
        response = requests.get(url)
        with open(name, 'wb') as file:
            file.write(response.content)        

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
        print('android-sdk installed!')                         

    def new(self):
        if os.path.exists(f'{PACKAGE_DIR}/resources'):
            shutil.rmtree(f'{PACKAGE_DIR}/resources')
        os.makedirs(f'{PACKAGE_DIR}/resources')
        self.download_data(MANIFEST_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/AndroidManifest.xml')
        self.download_data(ACTIVITY_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/activity_main.xml')
        self.download_data(STRING_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/strings.xml')
        self.download_data(STYLE_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/styles.xml')
        self.download_data(BG_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/bg_splash.xml')
        self.download_data(COLOR_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/colors.xml')
        self.download_data(HTML_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/index.html')
        self.download_data(JAVA_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/MainActivity.java')
        self.download_data(GRADLE_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/build.gradle')
        self.download_data(GP_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/gradle.properties')
        self.download_data(ICON_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/icon.png')
        self.download_data(LOGO_FILE, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/logo.png')
        data_toml = {'data': {
            'app_name': input('App name [py2apk]: ') or 'py2apk',
            'app_id': input('App name [APPLICATION_ID]: ') or 'APPLICATION_ID',
            'app_pub': input('App name [3940256099942544/6300978111]: ') or '3940256099942544/6300978111',
            'package_name': input('Package name [demo.py2apk.app]: ') or 'demo.py2apk.app',            
            'version_name': input('Version [1.0.0]: ') or '1.0.0',
            'status_color': input('Status bar color [#202225]: ') or '#202225',
            'icon_file': input('Icon [icon.png]: ') or ICON_FILE,
            'logo_file': input('Logo [logo.png]: ') or LOGO_FILE,
            'bg_color': input('Background color [#000000]: ') or '#000000',
            'url_path': input('URL [file:///android_asset/index.html]: ') or 'file:///android_asset/index.html',
        }}
        with open('app.toml', 'w') as f:
            toml.dump(data_toml, f)
        data = data_toml['data']        
        self.render(MANIFEST_FILE, 'src/main/', data)
        self.render(ACTIVITY_FILE, 'src/main/res/layout/', data)
        self.render(STRING_FILE, 'src/main/res/values/', data)
        self.render(STYLE_FILE, 'src/main/res/values/', data)
        self.render(COLOR_FILE, 'src/main/res/values/', data)
        self.render(BG_FILE, 'src/main/res/drawable/', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/', data)        
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, None, data)
        self.render(GP_FILE, None, data)
        self.render(HTML_FILE, 'src/main/assets/', data)
        self.icons(data['icon_file'], data['logo_file'])       

    def build(self):
        data_toml = toml.load('app.toml')
        data = data_toml['data']        
        self.render(MANIFEST_FILE, 'src/main/', data)
        self.render(ACTIVITY_FILE, 'src/main/res/layout/', data)
        self.render(STRING_FILE, 'src/main/res/values/', data)
        self.render(STYLE_FILE, 'src/main/res/values/', data)
        self.render(COLOR_FILE, 'src/main/res/values/', data)
        self.render(BG_FILE, 'src/main/res/drawable/', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/', data)        
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, None, data)
        self.render(GP_FILE, None, data)
        self.icons(data['icon_file'], data['logo_file'])
        os.system('gradle wrapper')
        if os.name == 'nt':
            os.system('gradlew assembleDebug')            
        else:
            os.system('chmod +x gradlew')
            os.system('./gradlew assembleDebug')            

    def run(self):              
        if os.name != 'nt':
            os.system(f'chmod +x {HOME}/.py2apk/android-sdk/emulator/emulator')
            os.system(f'chmod +x {HOME}/.py2apk/android-sdk/platform-tools/adb')
        subprocess.run(['adb', 'devices'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
        emu = subprocess.check_output(['emulator', '-list-avds']).decode().strip()
        if 'py2apk_emu' not in emu:
            os.system('avdmanager --verbose create avd --name "py2apk_emu" --abi "x86" --package "system-images;android-28;default;x86" --device "pixel"')
        subprocess.Popen(['emulator', '@py2apk_emu'], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)       
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
        app_name = os.path.basename(os.getcwd())
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
            gdl = './gradlew'
        os.system(f'{gdl} assembleRelease -PstoreFile="{key_name}.jks" -PstorePassword="{key_pass}" -PkeyAlias="{key_name}" -PkeyPassword="{key_pass}"')
        os.system(f'{gdl} bundleRelease -PstoreFile="{key_name}.jks" -PstorePassword="{key_pass}" -PkeyAlias="{key_name}" -PkeyPassword="{key_pass}"')

    def verify(self):
        app_name = os.path.basename(os.getcwd())
        os.system(f'jarsigner -verify -verbose -certs "{os.getcwd()}/build/outputs/apk/release/{app_name}-release.apk"')        
