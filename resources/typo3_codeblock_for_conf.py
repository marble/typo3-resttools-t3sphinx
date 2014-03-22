# -*- coding: utf-8 -*-
#

# Example

project = 'Some project name'
version = '1.3'

# ============================================================
#
# TYPO3 codeblock BEGIN: (version 2014-03-23)
#
# Insert this codeblock at the end of your Sphinx builder
# configuration file 'conf.py'. This makes TYPO3 specific
# features like TYPO3 themes available. It makes Yaml settings
# files work.
#
# ------------------------------------------------------------

if 1 and "TYPO3 specific":

    html_translator_class = "t3sphinx.writers.t3htmlwriter.T3HTMLTranslator"

    try:
        t3DocTeam
    except NameError:
        t3DocTeam = {}

    try:
        import t3sphinx
        html_theme_path.insert(0, t3sphinx.themes_dir)
        html_theme = 'typo3sphinx'
    except:
        html_theme = 'default'
    try:
        t3DocTeam['locale_dir'] = t3sphinx.locale_dir
    except:
        t3DocTeam['locale_dir'] = None
    if t3DocTeam['locale_dir']:
        try:
            locale_dirs
        except NameError:
            locale_dirs = []
        locale_dirs.append(t3DocTeam['locale_dir'])
    t3DocTeam['conf_py_file'] = None
    try:
        t3DocTeam['conf_py_file'] = __file__
    except:
        import inspect
        t3DocTeam['conf_py_file'] = inspect.getfile(
            inspect.currentframe())

    t3DocTeam['conf_py_package_dir'] = os.path.abspath(os.path.dirname(
        t3DocTeam['conf_py_file']))
    t3DocTeam['relpath_to_master_doc'] = '..'
    t3DocTeam['relpath_to_logdir'] = '_not_versioned'
    t3DocTeam['path_to_logdir'] = os.path.join(
        t3DocTeam['conf_py_package_dir'],
        t3DocTeam['relpath_to_logdir'])
    t3DocTeam['pathToYamlSettings'] = os.path.join(
        t3DocTeam['conf_py_package_dir'],
        t3DocTeam['relpath_to_master_doc'], 'Settings.yml')
    try:
        t3DocTeam['pathToGlobalYamlSettings'] = \
            t3sphinx.pathToGlobalYamlSettings
    except:
        t3DocTeam['pathToGlobalYamlSettings'] = None
    if not t3DocTeam['pathToGlobalYamlSettings']:
        t3DocTeam['pathToGlobalYamlSettings'] = os.path.join(
            t3DocTeam['conf_py_package_dir'], 'GlobalSettings.yml')
    try:
        __function = t3sphinx.yamlsettings.processYamlSettings
    except:
        __function = None
    if not __function:
        try:
            import yamlsettings
            __function = yamlsettings.processYamlSettings
        except:
            __function = None
    if __function:
        __function(globals(), t3DocTeam)

#-------------------------------------------------
#
# TYPO3 codeblock END.
#
#=================================================
