#! /usr/bin/env python3

import re
import ast
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('py2apk/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


requirements = [    
    'toml>=0.10.2',
    'Pillow>=8.2.0',
    'install-jdk>=0.3.0',
    'requests>=2.25.1',
    'tqdm>=4.61.0',    
]


setup(
    name='py2apk',
    version=version,
    description="Python to apk",
    long_description=readme,
    author="anbuhckr",
    author_email='anbu.hckr@hotmail.com',
    url='https://github.com/anbuhckr/py2apk',
    packages=find_packages(),
    package_dir={},    
    include_package_data=True,    
    install_requires=requirements,
    license="GNU GENERAL PUBLIC LICENSE",
    zip_safe=False,
    keywords='py2apk',
    classifiers=[
        'Development Status :: 1 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: GNU GENERAL PUBLIC LICENSE',
        'Natural Language :: English',       
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
