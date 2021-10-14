import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='vax-status-listener',
    version='0.1',
    packages=['vs_listener'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'Django~=3.2',
        'UW-RestClients-SWS>=2.3.17',
        'UW-RestClients-PWS~=2.1',
        'psycopg2<2.9',
    ],
    license='Apache License, Version 2.0',
    description=('AXDD listener client for DocuSign Connect events'),
    url='https://github.com/uw-it-aca/vax-status-listener',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
