# -*- coding: utf-8 -*-
#
# t3sphinx.yamlsettings.py  alpha
#
# mb, 2012-08-14, 2014-03-24
#
#

"""Handle Yaml Settings Files."""

"""BTW: If you wonder what this 'if 1:' means: It's the shortest way
to group the following code as a chunk. Make it 'if 0:' and it's all
turned off. And more: The Python byte compiler will then leave out
the whole section as he is smart enough to understand that the
if-clause has constants only and will *never* be executed.
And it's easy to transform the whole code into a function by just
writing "def myFunc():" instead of "if 1:". Just to let you know :-)
"""

import codecs, os, yaml, time

ospj = os.path.join
ospe = os.path.exists
osps = os.path.split

safe_types = [
    #None,
    type(None),
    str,
    unicode,
    bool,
    int,
    float,
    long,
    list,
    dict,
    tuple,
    set,
    # type(datetime.date),
    # type(datetime.datetime),
    ]

class YamlSettings:

    def __init__(self, theDict, parameters):
        self.theDict = theDict
        self.parameters = parameters

    def applyYamlSettings(self, fname=None):
        result = 'Nothing done.'
        S = None
        if fname is None:
            return result, S
        try:
            import yaml
        except ImportError:
            result = "Could not import module 'yaml'. Try '(sudo) easy_install (--user) PyYAML'."
            return result, S
        if not ospe(fname):
            result = "Could not find '%s'." % fname
            return result, S
        f1 = codecs.open(fname, 'r', 'utf-8')
        try:
            # yaml.safe_load() will only load scalars and
            # throw an error otherwise. DO NOT USE yaml.load()!
            S = yaml.safe_load(f1)
        except:
            result = "Could not parse '%s'" % fname
            S = None
            f1.close()
            return result, S
        f1.close()

        if (not S) or (not S.has_key('conf.py')):
            result = "Did not find key 'conf.py' in yaml settings '%s'." % fname
            return result, S

        skippedKeys = []

        def integrate(pool, incoming, skippedKeys):
            assert type(pool) == dict
            assert type(incoming) == dict
            assert type(skippedKeys) == list
            keys = {}
            for k in incoming.keys():
                if k.startswith('__'):
                    skippedKeys.append(k)
                else:
                    keys[k] = k
            while keys:
                key = keys.keys()[0]
                for mode in ['_!UPDATE!', '_!REMOVE!']:
                    if key.endswith(mode):
                        key = key[:-len(mode)]
                        break
                else:
                    mode = '_!REPLACE!'

                if incoming.has_key(key + '_!REMOVE!'):
                    key_remove = key + '_!REMOVE!'
                    value_remove = incoming[key_remove]
                    del keys[key_remove]
                else:
                    key_remove = None
                    
                if incoming.has_key(key):
                    key_replace = key
                    value_replace = incoming[key_replace]
                    del keys[key_replace]
                else:
                    key_replace = None

                if incoming.has_key(key + '_!UPDATE!'):
                    key_update = key + '_!UPDATE!'
                    value_update = incoming[key_update]
                    del keys[key_update]
                else:
                    key_update = None

                if key_remove and pool.has_key(key):
                    if type(value_remove) is dict:
                        if type(pool[key]) is dict:
                            for kk in value_remove.keys():
                                if pool[key].has_key(kk):
                                    del pool[key][kk]
                    elif type(value_remove) is list:
                        if type(pool[key]) is list:
                            for vv in value_remove:
                                try:
                                    p = pool[key].index(vv)
                                except ValueError:
                                    p = None
                                if not p is None:
                                    del pool[key][p]
                    else:
                        del pool[key]

                if key_replace:
                    pool[key] = value_replace

                if key_update:
                    if type(value_update) is dict:
                        if not pool.has_key(key):
                            pool[key] = {}
                        if type(pool[key]) is dict:
                            for kk in value_update.keys():
                                pool[key][kk] = value_update[kk]
                    elif type(value_update) is list:
                        if not pool.has_key(key):
                            pool[key] = []
                        if type(pool[key]) is list:
                            for vv in value_update:
                                try:
                                    p = pool[key].index(vv)
                                except ValueError:
                                    p = None
                                if p is None:
                                    pool[key].append(vv)
                                else:
                                    pool[key][p] = vv
                    else:
                        pool[key] = value_update



        integrate(self.theDict, S['conf.py'], skippedKeys)
        result = "Result: Applied '%s' to 'conf.py'." % fname
        if skippedKeys:
            result += ' These were skipped: %r.' % skippedKeys + '.'
        return result, S

    def safeListOrTuple(self, listOrTuple):
        """..."""
        result = []
        for v in listOrTuple:
            if type(v) in [type(list), type(tuple)]:
                result.append(self.safeListOrTuple(v))
            elif type(v) == type(dict):
                result.append(self.safeDictionary(v))
            elif not (type(v) in safe_types):
                pass
            else:
                result.append(v)
        return result

    def safeDictionary(self, data):
        """..."""
        result = {}
        for k in data.keys():
            v = data[k]
            if k.startswith('__'):
                pass
            elif type(v) in [type(list), type(tuple)]:
                result[k] = self.safeListOrTuple(v)
            elif type(v) == dict:
                result[k] = self.safeDictionary(v)
            elif not (type(v) in safe_types):
                pass
            else:
                result[k] = v
        return result

    def fixIntersphinxMapping(self):
        """Convert lists to tuples in intersphinx_mapping.

        Currently the intersphinx extension in Sphinx v1.2pre only
        accepts tuples and not lists in the new mapping format.
        When we read mappings from Yaml they are given als lists
        though. So we fix it here. It would be really desirable
        that Sphinx in general would accept both list and tuple
        format in settings. See the `feature request
        <https://bitbucket.org/birkenfeld/sphinx/issue/978/please-allow-a-list-instead-of-a-tuple-in>`_
        for this in the Sphinx bug tracker.

        """
        intersphinx_mapping = self.theDict.get('intersphinx_mapping', {})
        if intersphinx_mapping:
            for k in intersphinx_mapping.keys():
                if type(intersphinx_mapping[k] == list):
                    intersphinx_mapping[k] = tuple(intersphinx_mapping[k])


    def dumpToFileAsYaml(self, data, fname, destdir=None, msg=None, frominfo=''):
        if destdir is None:
            destdir = self.parameters['path_to_logdir']
        f2name = os.path.join(destdir, fname)
        f2 = codecs.open(f2name, 'w', 'utf-8')
        f2.write('# %s\n' % os.path.basename(f2name))
        timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        f2.write('# %s\n' % timestr)
        f2.write('# read from : %s\n' % frominfo)
        f2.write('# written to: %s\n' % f2name)
        if msg:
            f2.write('# %s\n' % '\n# '.join(msg.split('\n')))
        f2.write('%s\n' % '')
        yaml.safe_dump(
            data,
            default_flow_style=False,
            explicit_start=True,
            explicit_end=True,
            stream=f2)
        f2.close()

    def safeDumpToFileAsYaml(self, data, fname, destdir=None, msg=None, frominfo=''):
        self.dumpToFileAsYaml(self.safeDictionary(data), fname, destdir, msg, frominfo)


def setupHighlighting():
    from sphinx.highlighting import lexers
    if lexers:
        from pygments.lexers.web import PhpLexer
        lexers['php'] = PhpLexer(startinline=True)


def processYamlSettings(theDict, parameters={}):

    # This function is called from 'conf.py'.
    # The name is somewhat misleading as it does more initializing
    # than just process Yaml Settings. But since the 'conf.py's
    # calling this function are widespread we keep the name
    # and plugin more initialization stuff here.

    setupHighlighting()

    # There should be at least these keys in parameters.keys():
    dummy = [
        'conf_py_file',
        'conf_py_package_dir',
        'relpath_to_master_doc',
        'relpath_to_logdir',
        'path_to_logdir',
        'pathToYamlSettings',
        'relpath_to_master_doc',
        'pathToGlobalYamlSettings',
        ]
    ys = YamlSettings(theDict, parameters)
    ys.fixIntersphinxMapping()

        # unchanged conf.py:
    ys.safeDumpToFileAsYaml({'conf.py': ys.theDict}, '10_conf_py.yml', frominfo='conf.py')

        # conf.py plus GlobalSettings.yml
    p = ys.parameters['pathToGlobalYamlSettings']
    result, S = ys.applyYamlSettings(p)
    ys.dumpToFileAsYaml(S, '20_GlobalSettings.yml', msg=result, frominfo=p)
    ys.fixIntersphinxMapping()
    ys.safeDumpToFileAsYaml({'conf.py': ys.theDict}, '10+20_conf_py.yml', frominfo='conf.py')

        # conf.py plus Settings.yml
    p = ys.parameters['pathToYamlSettings']
    result, S = ys.applyYamlSettings(p)
    ys.dumpToFileAsYaml(S, '30_Settings.yml', msg=result, frominfo=p)
    ys.fixIntersphinxMapping()
    ys.safeDumpToFileAsYaml({'conf.py': ys.theDict}, '10+20+30_conf_py.yml', frominfo='conf.py')

        # conf.py plus FinalSettings.yml
    p = ospj(osps(ys.parameters['pathToGlobalYamlSettings'])[0], 'FinalSettings.yml')
    result, S = ys.applyYamlSettings(p)
    ys.dumpToFileAsYaml(S, '40_FinalSettings.yml', msg=result, frominfo=p)
    ys.fixIntersphinxMapping()
    ys.safeDumpToFileAsYaml({'conf.py': ys.theDict}, '10+20+30+40_EffectiveSettings.yml', frominfo='conf.py')


if 0 and __name__=="__main__":

    t3DocTeam = {}
    t3DocTeam['conf_py_file'] = None

    try:
        t3DocTeam['conf_py_file'] = __file__
    except:
        t3DocTeam['conf_py_file'] = None

    if not t3DocTeam['conf_py_file']:
        import inspect
        t3DocTeam['conf_py_file'] = inspect.getfile(
            inspect.currentframe())

    t3DocTeam['conf_py_package_dir'] = os.path.abspath(os.path.dirname(t3DocTeam['conf_py_file']))
    t3DocTeam['relpath_to_master_doc'] = '..'
    t3DocTeam['relpath_to_logdir'] = '_not_versioned'
    t3DocTeam['path_to_logdir'] = ospj(t3DocTeam['conf_py_package_dir'], t3DocTeam['relpath_to_logdir'])
    t3DocTeam['pathToYamlSettings'] = ospj(t3DocTeam['conf_py_package_dir'], t3DocTeam['relpath_to_master_doc'], 'Settings.yml')
    t3DocTeam['pathToGlobalYamlSettings'] = None

    processYamlSettings(globals(), t3DocTeam)

