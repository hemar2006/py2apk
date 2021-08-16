#! /usr/bin/env python3

import os, toml, jdk, zipfile, requests, platform, shutil, subprocess, time
from string import Template
from PIL import Image
from tqdm import tqdm
from getpass import getpass

class Py2Apk():

    def __init__(self) -> None:
        self.package_dir = os.path.dirname(os.path.realpath(__file__))
        self.manifest_file = os.path.join(self.package_dir, 'resources', 'AndroidManifest.xml')
        self.activity_file = os.path.join(self.package_dir, 'resources', 'activity_main.xml')
        self.string_file = os.path.join(self.package_dir, 'resources', 'strings.xml')
        self.style_file = os.path.join(self.package_dir, 'resources', 'styles.xml')
        self.bg_file = os.path.join(self.package_dir, 'resources', 'bg_splash.xml')
        self.color_file = os.path.join(self.package_dir, 'resources', 'colors.xml')
        self.html_file = os.path.join(self.package_dir, 'resources', 'index.html')
        self.java_file = os.path.join(self.package_dir, 'resources', 'MainActivity.java')
        self.gradle_file = os.path.join(self.package_dir, 'resources', 'build.gradle')
        self.gp_file = os.path.join(self.package_dir, 'resources', 'gradle.properties')
        self.icon_file = os.path.join(self.package_dir, 'resources', 'icon.png')
        self.logo_file = os.path.join(self.package_dir, 'resources', 'logo.png')
        self.home = os.path.expanduser("~")
        self.gradlew = 'gradlew'
        if os.name != 'nt':
            self.gradlew = './gradlew'
        os.environ["JAVA_HOME"] = os.path.join(self.home, '.py2apk', 'jdk')
        os.environ["ANDROID_HOME"] = os.path.join(self.home, '.py2apk', 'android-sdk')
        pathlist = [
            os.path.join(self.home, '.py2apk', 'jdk', 'bin'),
            os.path.join(self.home, '.py2apk', 'gradle', 'gradle-7.1.1', 'bin'),
            os.path.join(self.home, '.py2apk', 'android-sdk', 'cmdline-tools', 'latest', 'bin'),
            os.path.join(self.home, '.py2apk', 'android-sdk', 'emulator'),
            os.path.join(self.home, '.py2apk', 'android-sdk', 'platform-tools')
        ]
        os.environ["PATH"] += os.pathsep + os.pathsep.join(pathlist)

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
        im.save(os.path.join('src', 'main', 'ic_launcher-web.png'))
        im2 = Image.open(logo)           
        im2.save(os.path.join('src', 'main', 'res', 'drawable', 'ic_logo.png'))
        for size in sizes:
            path = os.path.join('src', 'main', 'res', size['name'])
            if not os.path.exists(path):
                os.makedirs(path)
            im = Image.open(data)            
            im.thumbnail((size['d'], size['d']))
            im.save(os.path.join(path, 'ic_launcher.png'))                      

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

    def jdk_download(self):
        print('download jdk...')
        jdk_11 = jdk.install('11')
        shutil.move(jdk_11, os.path.join(self.home, '.py2apk', 'jdk'))
        shutil.rmtree(os.path.join(self.home, '.jdk'))
        print('jdk installed!')

    def gradle_download(self):
        self.download_file('gradle.zip', 'https://services.gradle.org/distributions/gradle-7.1.1-bin.zip')
        self.unzip('gradle.zip', os.path.join(self.home, '.py2apk', 'gradle'))
        os.remove('gradle.zip')
        if os.name != 'nt':
            os.system(f"chmod +x {os.path.join(self.home, '.py2apk', 'gradle', 'gradle-7.1.1', 'bin', 'gradle')}")                   
        print('gradle installed!')

    def sdk_download(self):
        if platform.system() == 'Windows':
            sdk = 'win'
        if platform.system() == 'Darwin':
            sdk = 'mac'
        if platform.system() == 'Linux':
            sdk = 'linux'
        self.download_file('cmdline-tools.zip', f'https://dl.google.com/android/repository/commandlinetools-{sdk}-7583922_latest.zip')
        self.unzip('cmdline-tools.zip', os.path.join(self.home, '.py2apk', 'android-sdk'))
        os.remove('cmdline-tools.zip')
        shutil.move(os.path.join(self.home, '.py2apk', 'android-sdk', 'cmdline-tools'), os.path.join(self.home, '.py2apk', 'android-sdk', 'latest'))
        shutil.move(os.path.join(self.home, '.py2apk', 'android-sdk', 'latest'), os.path.join(self.home, '.py2apk', 'android-sdk', 'cmdline-tools', 'latest'))
        if os.name != 'nt':            
            os.system(f"chmod +x {os.path.join(self.home, '.py2apk', 'android-sdk', 'cmdline-tools', 'latest', 'bin', 'sdkmanager')}")
            os.system(f"chmod +x {os.path.join(self.home, '.py2apk', 'android-sdk', 'cmdline-tools', 'latest', 'bin', 'avdmanager')}")
        os.system('sdkmanager --licenses')
        os.system('sdkmanager --install "system-images;android-28;default;x86"')
        print('android-sdk installed!')

    def resource_download(self):
        if os.path.exists(os.path.join(self.package_dir, 'resources')):
            shutil.rmtree(os.path.join(self.package_dir, 'resources'))
        os.makedirs(os.path.join(self.package_dir, 'resources'))
        self.download_data(self.manifest_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/AndroidManifest.xml')
        self.download_data(self.activity_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/activity_main.xml')
        self.download_data(self.string_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/strings.xml')
        self.download_data(self.style_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/styles.xml')
        self.download_data(self.bg_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/bg_splash.xml')
        self.download_data(self.color_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/colors.xml')
        self.download_data(self.html_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/index.html')
        self.download_data(self.java_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/MainActivity.java')
        self.download_data(self.gradle_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/build.gradle')
        self.download_data(self.gp_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/gradle.properties')
        self.download_data(self.icon_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/icon.png')
        self.download_data(self.logo_file, 'https://raw.githubusercontent.com/anbuhckr/py2apk/main/resources/logo.png')

    def save_setting(self):
        app_name = input('App name [py2apk]: ') or 'py2apk'              
        package_name = input('Package name [demo.py2apk.app]: ') or 'demo.py2apk.app'            
        version_name = input('Version [1.0.0]: ') or '1.0.0'
        status_color = input('Status bar color [#202225]: ') or '#202225'
        self.icon_file = input('Icon [icon.png]: ') or self.icon_file
        self.logo_file = input('Logo [logo.png]: ') or self.logo_file
        bg_color = input('Background color [#000000]: ') or '#000000'
        url_path = input('URL [file:///android_asset/index.html]: ') or 'file:///android_asset/index.html'
        app_id = input('Admob App-Id []: ') or ''  
        banner_pub = input('Admob Banner []: ') or ''          
        interstitial_pub = input('Admob Interstitial []: ') or ''
        interstitial_time = input('Interstitial Time Show [10]: ') or 10        
        data_toml = {'data': {
            'app_name': app_name,            
            'package_name': package_name,            
            'version_name': version_name,
            'status_color': status_color,
            'icon_file': self.icon_file,
            'logo_file': self.logo_file,
            'bg_color': bg_color,
            'url_path': url_path,
            'app_id': app_id,
            'banner_pub': banner_pub,
            'interstitial_pub': interstitial_pub,
            'interstitial_time': interstitial_time            
        }}
        with open('app.toml', 'w') as f:
            toml.dump(data_toml, f)
        print("Saved to app.toml")
        return data_toml

    def install(self):
        if os.path.exists(os.path.join(self.home, '.py2apk')):
            print('delete old files...')
            shutil.rmtree(os.path.join(self.home, '.py2apk'))
        self.jdk_download()
        self.gradle_download()
        self.sdk_download()                                 

    def new(self):
        self.resource_download()              
        data_toml = self.save_setting()
        data = data_toml['data']
        data['manifest_id'] = data['app_id'] or 'ca-app-pub-3940256099942544~3347511713'        
        self.render(self.manifest_file, os.path.join('src', 'main'), data)
        self.render(self.activity_file, os.path.join('src', 'main', 'res', 'layout'), data)
        self.render(self.string_file, os.path.join('src', 'main', 'res', 'values'), data)
        self.render(self.style_file, os.path.join('src', 'main', 'res', 'values'), data)
        self.render(self.color_file, os.path.join('src', 'main', 'res', 'values'), data)
        self.render(self.bg_file, os.path.join('src', 'main', 'res', 'drawable'), data)
        dirs = data['package_name'].split('.')       
        self.render(self.java_file, os.path.join('src', 'main', 'java', *dirs), data)     
        data['version_code'] = data['version_name'].split('.')[0]
        data['good_app_name'] = data['app_name'].replace(' ', '-')      
        self.render(self.gradle_file, None, data)
        self.render(self.gp_file, None, data)
        self.render(self.html_file, os.path.join('src', 'main', 'assets'), data)
        self.icons(data['icon_file'], data['logo_file'])  

    def build(self):
        data_toml = toml.load('app.toml')
        data = data_toml['data']
        data['manifest_id'] = data['app_id'] or 'ca-app-pub-3940256099942544~3347511713'      
        self.render(self.manifest_file, os.path.join('src', 'main'), data)
        self.render(self.activity_file, os.path.join('src', 'main', 'res', 'layout'), data)
        self.render(self.string_file, os.path.join('src', 'main', 'res', 'values'), data)
        self.render(self.style_file, os.path.join('src', 'main', 'res', 'values'), data)
        self.render(self.color_file, os.path.join('src', 'main', 'res', 'values'), data)
        self.render(self.bg_file, os.path.join('src', 'main', 'res', 'drawable'), data)
        shutil.rmtree(os.path.join('src', 'main', 'java'))
        dirs = data['package_name'].split('.')        
        self.render(self.java_file, os.path.join('src', 'main', 'java', *dirs), data)       
        data['version_code'] = data['version_name'].split('.')[0]
        data['good_app_name'] = data['app_name'].replace(' ', '-')    
        self.render(self.gradle_file, None, data)
        self.render(self.gp_file, None, data)
        self.icons(data['icon_file'], data['logo_file'])
        os.system('gradle wrapper')
        if os.name != 'nt':
            os.system(f'chmod +x {self.gradlew}')
        os.system(f'{self.gradlew} assembleDebug')            

    def run(self):              
        if os.name != 'nt':
            os.system(f"chmod +x {os.path.join(self.home, '.py2apk', 'android-sdk', 'emulator', 'emulator')}")
            os.system(f"chmod +x {os.path.join(self.home, '.py2apk', 'android-sdk', 'platform-tools', 'adb')}")
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
        app_name = data['app_name'].replace(' ', '-')
        os.system(f'adb uninstall {package}')
        debug_apk = os.path.join(os.getcwd(), 'build', 'outputs', 'apk', 'debug', f'{app_name}.apk')
        os.system(f"adb install {debug_apk}")
        os.system(f'adb shell am start -n {package}/{package}.MainActivity')

    def package(self):        
        data_toml = toml.load('app.toml')
        data = data_toml['data']
        data['version_code'] = data['version_name'].split('.')[0]
        data['good_app_name'] = data['app_name'].replace(' ', '-')       
        self.render(self.gradle_file, None, data)
        key_pass = getpass('Enter keystore password: ')
        key_name = data['package_name'].replace('.', '_')
        if not os.path.exists(f'{key_name}.jks'):
            os.system(f'keytool -genkey -v -keystore {key_name}.jks -keyalg RSA -keysize 2048 -validity 10000 -alias {key_name} -storepass {key_pass} -keypass {key_pass}')
        os.system(f'{self.gradlew} assembleRelease -PstoreFile="{key_name}.jks" -PstorePassword="{key_pass}" -PkeyAlias="{key_name}" -PkeyPassword="{key_pass}"')
        os.system(f'{self.gradlew} bundleRelease -PstoreFile="{key_name}.jks" -PstorePassword="{key_pass}" -PkeyAlias="{key_name}" -PkeyPassword="{key_pass}"')

    def verify(self):
        app_name = os.path.basename(os.getcwd())
        os.system(f'jarsigner -verify -verbose -certs "{os.getcwd()}/build/outputs/apk/release/{app_name}-release.apk"')
        
