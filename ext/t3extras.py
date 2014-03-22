# -*- coding: utf-8 -*-
"""
    t3sphinx.ext.t3sphinx
    ~~~~~~~~~~~~~~~~~~~

    Extending Sphinx ...

    :copyright: Copyright 2012-2099 by the TYPO3 team, see AUTHORS.
    :license: BSD, see LICENSE for details.
    :author: Martin Bless <martin@mbless.de>

"""

from t3sphinx.builders.t3html import StandaloneHTMLBuilder

##Sphinx core events (hooks)
##
##http://sphinx-doc.org/latest/ext/appapi.html#sphinx-core-events
##
##builder-inited(app)
##env-get-outdated(app, env, added, changed, removed)
##env-purge-doc(app, env, docname)
##source-read(app, docname, source)
##doctree-read(app, doctree)
##missing-reference(app, env, node, contnode)
##doctree-resolved(app, doctree, docname)
##env-updated(app, env)
##html-collect-pages(app)
##html-page-context(app, pagename, templatename, context, doctree)
##build-finished(app, exception)



# see: http://sphinx-doc.org/ext/appapi.html

def setup(app):
    app.add_builder(StandaloneHTMLBuilder)
