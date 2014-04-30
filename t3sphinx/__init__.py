# -*- coding: utf-8 -*-
"""
    t3sphinx
    ~~~~~~~~

    TYPO3 specific extensions for Sphinx

    :copyright: Copyright 2012-2099 by the TYPO3 Documentation Team
        and TYPO3 community, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# Keep this file executable as-is in Python 3!
# (Otherwise getting the version out of it from setup.py is impossible.)

import os
import yamlsettings

__version__  = '0.3.0'

# absolute path to the 't3sphinx' package
package_dir = os.path.abspath(os.path.dirname(__file__))

# absolute path to the ./locale folder
locale_dir = os.path.join(package_dir, 'locale')

# absolute path to the ./themes folder
themes_dir = os.path.join(package_dir, 'themes')

# absolute path to /.../t3sphinx/settings/GlobalSettings.yml
pathToGlobalYamlSettings = os.path.join(package_dir, 'settings', 'GlobalSettings.yml')

# absolute path to /.../t3sphinx/resources/typo3_codeblock_for_conf.py
typo3_codeblock_for_conf_py = os.path.join(package_dir, 'resources', 'typo3_codeblock_for_conf.py')

# register the FieldListTable directive in docutils as 't3-field-list-table'
from docutils.parsers.rst import directives
from t3sphinx.t3docutils.directives import fieldlisttable
directives.register_directive('t3-field-list-table', fieldlisttable.FieldListTable)
