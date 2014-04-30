#!/usr/bin/env python

from setuptools import setup

setup(
    name='t3sphinx',
    version='0.3.0',
    author='Martin Bless',
    author_email='martin@mbless.de',
    description=('This adds TYPO3 specific stuff to the Sphinx Documentation Tools.'),
    license = "BSD",
    url='https://github.com/julianwachholz/typo3-resttools-t3sphinx',
    packages=['t3sphinx'],
    keywords=['typo3', 'documentation', 'sphinx'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 3',
    ],
)
