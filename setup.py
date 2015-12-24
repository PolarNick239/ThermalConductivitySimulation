#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

from setuptools import setup, find_packages

setup(
    name='ThermalConductivitySimulation',
    version='0.0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    setup_requires=[
        'setuptools >= 18.0'
    ],
    install_requires=[
        'numpy>=1.9.1',
        'PyOpenGL>=3.1.0',
        'pyopencl>=2015.2.3',
        'cyglfw3>=3.1.0.2',
        'Pillow>=3.0.0',
        'scipy>=0.16.0',
    ],
    scripts=[
        "main.py",
    ],
)
