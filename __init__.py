# -*- coding: utf-8 -*-
"""
    t3sphinx
    ~~~~~~~~

    TYPO3 specific extensions for Sphinx

    :copyright: Copyright 2012-2012 by the TYPO3 Documentation Team
        and TYPO3 community, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# Keep this file executable as-is in Python 3!
# (Otherwise getting the version out of it from setup.py is impossible.)

import os
import yamlsettings

__version__  = '0.2.0'

package_dir = os.path.abspath(os.path.dirname(__file__))
themes_dir = os.path.join(package_dir, 'themes')
pathToGlobalYamlSettings = os.path.join(package_dir, 'settings', 'GlobalSettings.yml')
typo3_codeblock_for_conf_py = os.path.join(package_dir, 'resources', 'typo3_codeblock_for_conf.py')
