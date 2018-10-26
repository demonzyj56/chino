#!/usr/bin/env python
from setuptools import setup


setup(
    name='chino',
    version='0.0.0',
    author='Yijie Zeng',
    author_email='demonzyj56@gmail.com',
    url='https://github.com/demonzyj56/chino',
    description="Utilities used for the author's research",
    license='MIT',
    packages=['chino'],
    install_requires=['pyyaml', 'addict', 'opencv-python', 'six', 'numpy'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
