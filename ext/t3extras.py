# -*- coding: utf-8 -*-
"""
    t3sphinx.ext.t3extras
    ~~~~~~~~~~~~~~~~~~~~~

    Extending Sphinx ...

    :copyright: Copyright 2012-2099 by the TYPO3 documentation team, \
                see AUTHORS.
    :license: BSD, see LICENSE for details.
    :author: Martin Bless <martin@mbless.de>

"""

from t3sphinx.builders.t3htmlbuilder import T3StandaloneHTMLBuilder,\
    T3DirectoryHTMLBuilder, T3SingleFileHTMLBuilder, \
    T3PickleHTMLBuilder, T3JSONHTMLBuilder

def setup(app):
    app.add_builder(T3StandaloneHTMLBuilder)
    app.add_builder(T3DirectoryHTMLBuilder)
    app.add_builder(T3SingleFileHTMLBuilder)
    app.add_builder(T3PickleHTMLBuilder)
    app.add_builder(T3JSONHTMLBuilder)
