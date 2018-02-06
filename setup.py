#run as root
from codecs import open
import os
from os import path
from setuptools import setup, find_packages
import sys

options_ = sys.argv

if len(options_) > 1:
    if options_[1] == 'install':
        print("\nstarting dependency installing process....")
        #dependecy libraries
        print("\ninstalling  python 3 dependences...\n")
        test_ = os.popen('apt-get install libssl-dev build-essential automake pkg-config libtool libffi-dev libgmp-dev libyaml-cpp-dev').read()
        print(test_)
        #install pip for python 3
        print("\ninstalling pip for python 3...\n")
        test_ = os.popen('apt-get install -y python3-pip').read()
        print(test_)
        #install setuptools
        print("\ninstalling setuptools for python 3...\n")
        test_ = os.popen('pip3 install setuptools').read()
        print(test_)
        #install selenium library for python 3
        print("\ninstalling selenium for python3....\n")
        test_ = os.popen('pip3 install selenium').read()
        print(test_)
        #
        print("\ninstalling future for python3....\n")
        test_ = os.popen('pip3 install future').read()
        print(test_)
        #
        print("\ninstalling cryptocompy for python3....\n")
        test_ = os.popen('pip3 install cryptocompy').read()
        print(test_)
        #
        print("\ninstalling rlp for python3....\n")
        test_ = os.popen('pip3 install rlp').read()
        print(test_)
        #
        print("\ninstalling web3 python3....\n")
        test_ = os.popen('pip3 install web3').read()
        print(test_)
        #
        print("\ninstalling ethereum python3....\n")
        test_ = os.popen('pip3 install ethereum').read()
        print(test_)
        #install zip
        print("\ninstalling zip....\n")
        test_ = os.popen('apt-get install -y zip').read()
        print(test_)
        #install openvpn
        print("\ninstalling openvpn....\n")
        test_ = os.popen('apt-get install -y openvpn').read()
        print(test_)
        #install chromedriver
        print("\ninstalling chromedriver....\n")
        test_ = os.popen('apt-get install -y chromium-chromedriver').read()
        print(test_)
        pass

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cloudomate',

    version='1.0.0',

    description='Automate buying VPS instances with Bitcoin',
    long_description=long_description,

    url='https://github.com/Jaapp-/Cloudomate',

    author='PlebNet',
    author_email='plebnet@heijligers.me',

    license='LGPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Installation/Setup',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],

    keywords='vps bitcoin',

    packages=find_packages(exclude=['docs', 'test']),

    install_requires=['appdirs', 'lxml', 'MechanicalSoup', 'bs4', 'mock', 'forex-python', 'parameterized'],

    extras_require={
        'dev': [],
        'test': ['mock', 'parameterized'],
        'ethereum' : ['cryptocompy','rlp','web3','ethereum'],
    },

    package_data={
        'cloudomate': [],
    },

    entry_points={
        'console_scripts': [
            'cloudomate=cloudomate.cmdline:execute',
        ],
    },
)
