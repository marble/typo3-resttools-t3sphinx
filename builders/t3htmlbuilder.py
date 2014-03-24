# -*- coding: utf-8 -*-
"""
    t3sphinx.builders.t3htmlbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Several HTML builders for TYPO3

    :copyright: Copyright 2007-2099 by the TYPO3 documentation team,
                see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from sphinx.builders.html import StandaloneHTMLBuilder, jsonimpl, _, \
    pickle, ENV_PICKLE_FILENAME, LAST_BUILD_FILENAME, OptionParser, \
    __version__, new_document, b, Publisher, DocTreeInput, \
    StringOutput, DoctreeReader, SEP, path, os_path, ensuredir, \
    codecs, copyfile, bold, darkgreen, brown, inline_all_toctrees, \
    nodes, os

import sphinx.util.osutil
import docutils.nodes

class span(docutils.nodes.Inline, docutils.nodes.TextElement):
    pass

class T3StandaloneHTMLBuilder(StandaloneHTMLBuilder):
    name = 't3html'

    mb_publisher = None
    mb_doccount = 0

    # too bad we need this class variables at the moment ...
    LAST_CUR_NODE = None
    LAST_TOC_DIV = None

    def write_doc(self, docname, doctree):
        StandaloneHTMLBuilder.write_doc(self, docname, doctree)

        if 0 and 'dump files for inspection':
            self.mb_doccount += 1
            if self.mb_doccount == 1:
                from pprint import pprint
                if 1:
                    outfilename = self.get_outfilename(docname) + '.intersphinx_cache.pprint.txt'
                    f2 = codecs.open(outfilename, 'w', 'utf-8')
                    pprint(self.env.intersphinx_cache, f2, width=160)
                    f2.close
                if 1:
                    outfilename = self.get_outfilename(docname) + '.intersphinx_inventory.pprint.txt'
                    f2 = codecs.open(outfilename, 'w', 'utf-8')
                    pprint(self.env.intersphinx_inventory, f2, width=160)
                    f2.close
                if 1:
                    outfilename = self.get_outfilename(docname) + '.intersphinx_named_inventory.pprint.txt'
                    f2 = codecs.open(outfilename, 'w', 'utf-8')
                    pprint(self.env.intersphinx_named_inventory, f2, width=160)
                    f2.close
            if 1:
                outfilename = self.get_outfilename(docname) + '.pformat.txt'
                # outfilename's path is in general different from self.outdir
                sphinx.util.osutil.ensuredir(os.path.dirname(outfilename))
                output = doctree.pformat()
                try:
                    f = codecs.open(outfilename, 'w', 'utf-8', 'xmlcharrefreplace')
                    try:
                        f.write(output)
                    finally:
                        f.close()
                except (IOError, OSError), err:
                    self.warn("error writing file %s: %s" % (outfilename, err))


    def handle_page(self, pagename, addctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        """addctx['toc'] is only here. To make that accessible
        we add it to self.
        """
        self.t3addctx = addctx
        StandaloneHTMLBuilder.handle_page(self, pagename, addctx,
            templatename, outfilename, event_arg)


    def get_doc_context(self, docname, body, metatags):
        """Collect items for the template context of a page."""

        # TYPO3: remove 'documentation' from end of 'shorttitle'
        shorttitle = self.globalcontext.get('shorttitle', '')
        if shorttitle and shorttitle.endswith(' documentation'):
            shorttitle = shorttitle[0:-14].rstrip()
            self.globalcontext['shorttitle'] = shorttitle
            

        # find out relations
        # TYPO3: always have order 'previous', 'up', 'next'
        prev = up = next = None
        parents = []
        rellinks = self.globalcontext['rellinks'][:]
        related = self.relations.get(docname)
        titles = self.env.titles
        if related and related[1]:
            try:
                prev = {
                    'link': self.get_relative_uri(docname, related[1]),
                    'title': self.render_partial(titles[related[1]])['title']
                }
                rellinks.append((related[1], prev['title'], 'P', _('previous')))
            except KeyError:
                # the relation is (somehow) not in the TOC tree, handle
                # that gracefully
                prev = None
        if related and related[0]:
            try:
                up = {
                    'link': self.get_relative_uri(docname, related[0]),
                    'title': self.render_partial(titles[related[0]])['title']
                }
                rellinks.append((related[0], up['title'], 'U', _('up')))
            except KeyError:
                # the relation is (somehow) not in the TOC tree, handle
                # that gracefully
                prev = None
        if related and related[2]:
            try:
                next = {
                    'link': self.get_relative_uri(docname, related[2]),
                    'title': self.render_partial(titles[related[2]])['title']
                }
                rellinks.append((related[2], next['title'], 'N', _('next')))
            except KeyError:
                next = None
        while related and related[0]:
            try:
                parents.append(
                    {'link': self.get_relative_uri(docname, related[0]),
                     'title': self.render_partial(titles[related[0]])['title']})
            except KeyError:
                pass
            related = self.relations.get(related[0])
        if parents:
            parents.pop() # remove link to the master file; we have a generic
                          # "back to index" link already
        parents.reverse()

        # title rendered as HTML
        title = self.env.longtitles.get(docname)
        title = title and self.render_partial(title)['title'] or ''
        # the name for the copied source
        sourcename = self.config.html_copy_source and docname + '.txt' or ''

        # metadata for the document
        meta = self.env.metadata.get(docname)

        # local TOC and global TOC tree
        self_toc = self.env.get_toc_for(docname, self)
        toc = self.render_partial(self_toc)['fragment']

        return dict(
            parents = parents,
            prev = prev,
            next = next,
            title = title,
            meta = meta,
            body = body,
            metatags = metatags,
            rellinks = rellinks,
            sourcename = sourcename,
            toc = toc,
            # only display a TOC if there's more than one item to show
            display_toc = (self.env.toc_num_entries[docname] > 1),
        )


    def _get_local_toctree(self, docname, collapse=True, **kwds):
        """Create menu in a form that suits the TYPO3 menu structure.
        
        """

        toctree_for = self.env.get_toctree_for(docname, self, collapse, **kwds)
        
        def dumpit(fname='/sphinx/tmp/t3htmlbuilder/LOG.txt'):
            import codecs
            f2 = codecs.open(fname,'a','utf-8','xmlrefreplace')
            f2.write('%s: %s\n' % ('self', self))
            f2.write('%s: %s\n' % ('docname', docname))
            f2.write('%s: %s\n' % ('collapse', collapse))
            f2.write('%s: %r\n' % ('kwds', kwds))
            f2.write('%s: %r\n' % ('toctree_for', toctree_for))
            f2.write('%s: %r\n' % ("self.render_partial(toctree_for)['fragment']", self.render_partial(toctree_for)['fragment']))
            # f2.write('%s: %s\n' % ('toctree_for.asdom().toxml()', toctree_for.asdom().toxml()))
            f2.write('%s: %s\n' % ('toctree_for.pformat()', toctree_for.pformat()))
            f2.write('#####' * 10)
            f2.close()

        if 0:
            dumpit()

        def debugpublish():
            import docutils
            # def publish_from_doctree(document, destination_path=None,
            #              writer=None, writer_name='pseudoxml',
            #              settings=None, settings_spec=None,
            #              settings_overrides=None, config_section=None,
            #              enable_exit_status=False)

            document = toctree_for
            destination_path = 'U:\\htdocs\\LinuxData200\\py-dev\\LOG.txt'
            writer=None
            writer_name='pseudoxml'
            settings=None
            settings_spec=None
            settings_overrides=None
            config_section=None
            enable_exit_status=False

            docutils.core.publish_from_doctree(document, destination_path=None,
                         writer=None, writer_name='pseudoxml',
                         settings=None, settings_spec=None,
                         settings_overrides=None, config_section=None,
                         enable_exit_status=False)
        if 0:
            result = debugpublish()

        def publishAsXml(doc):
            if self.mb_publisher is Non9e:
                self.mb_publisher = Publisher(
                    source_class = DocTreeInput,
                    destination_class=StringOutput)
                self.mb_publisher.set_components(
                    'standalone','restructuredtext', 'pseudoxml')
            pub = self.mb_publisher
            pub.reader = DoctreeReader()
            pub.writer = sphinx_writers_html_HTMLWriter(self)
            pub.process_programmatic_settings(
                None, {'output_encoding': 'unicode'}, None)
            pub.set_source(doc, None)
            pub.set_destination(None, None)
            pub.publish()
            result = pub.writer.parts

        if 0:
            # doesn't work yet!?!
            publishAsXml(toctree_for)


        # def traverse(self, condition=None, include_self=1, descend=1, 
        #    siblings=0, ascend=0)

        class visitor(docutils.nodes.GenericNodeVisitor):
            ul_level = 0
            last_nav_aside_lvl = ''
            cnt = 0

            def default_visit(self, node):
                """Override for generic, uniform traversals."""

                if hasattr(node, 'attributes'):
                    self.cnt += 1
                    classes = node.attributes.get('classes', [])
                    newlist = []
                    iscurrent = False
                    for cl in classes:
                        if not cl in newlist:
                            newlist.append(cl)
                            if cl.startswith('toctree-l'):
                                self.last_nav_aside_lvl = 'nav-aside-lvl%s' % (cl[9:],)
                                newlist.append(self.last_nav_aside_lvl)
                            if cl == 'current':
                                newlist.append('cur')
                                iscurrent = True
                    if node.attributes.get('iscurrent', False) and type(node.parent) == nodes.list_item:
                        # print node.pformat()
                        T3StandaloneHTMLBuilder.LAST_CUR_NODE = node
                        try:
                            self_toc = self.t3addctx['self_toc']
                        except:
                            self_toc = None
                        if self_toc:
                            T3StandaloneHTMLBuilder.LAST_TOC_DIV = nodes.container(ids=["flyOutToc"], classes=['flyOutToc'])
                            T3StandaloneHTMLBuilder.LAST_TOC_DIV.append(nodes.paragraph(text='within this page:'))
                            T3StandaloneHTMLBuilder.LAST_TOC_DIV.append(self_toc)

                    newlist.append('cnt-%s' % self.cnt)
                    if isinstance(node, docutils.nodes.reference) and self.last_nav_aside_lvl and not (self.last_nav_aside_lvl in newlist):
                        newlist.append(self.last_nav_aside_lvl)
                    if isinstance(node, docutils.nodes.bullet_list):
                        self.ul_level += 1
                        if self.ul_level == 1:
                            node['ids'].insert(0, 'nav-aside')
                        else:
                            newlist.append('nav-aside-lvl%s' % self.ul_level)
                    node['classes'] = newlist

                if isinstance(node, docutils.nodes.Text):
                    if self.ul_level > 1:
                        # n = docutils.nodes.inline(rawsource='', text='abc', *children, ** attributes)
                        newnode = span(rawsource='', text=b(node))
                        node.parent.children = [newnode]



                ## improve css classes here!
                if 0 and hasattr(node, 'attributes'):
                    n = node
                    mycount = 0
                    while 'cur' in n.attributes.get('classes', []):
                        print '%03d: %s' % (mycount, n)
                        mycount -= 1
                        n = n.parent
                    if mycount != 0:
                        print



            def default_departure(self, node):
                """Override for generic, uniform traversals."""

                if isinstance(node, docutils.nodes.bullet_list):
                    self.ul_level -= 1

            def unknown_visit(self, node):
                """
                Called when entering unknown `Node` types.

                Raise an exception unless overridden.
                """
                pass

            def unknown_departure(self, node):
                """
                Called before exiting unknown `Node` types.

                Raise exception unless overridden.
                """
                pass

        if toctree_for:
            doc = new_document(b('<partial node>'))
            doc.append(toctree_for)


            # make self.t3addctx['toc'] available
            # make it a visitor class variable
            visitor.t3addctx = self.t3addctx
            toctree_for.walkabout(visitor(doc))
            if not T3StandaloneHTMLBuilder.LAST_TOC_DIV is None:
                T3StandaloneHTMLBuilder.LAST_CUR_NODE.replace_self([T3StandaloneHTMLBuilder.LAST_CUR_NODE, T3StandaloneHTMLBuilder.LAST_TOC_DIV])
            T3StandaloneHTMLBuilder.LAST_CUR_NODE = None
            T3StandaloneHTMLBuilder.LAST_TOC_DIV = None
            result = self.render_partial(toctree_for)['fragment']

        else:
            result = ''
        return result





class T3DirectoryHTMLBuilder(T3StandaloneHTMLBuilder):
    """
    A StandaloneHTMLBuilder that creates all HTML pages as "index.html" in
    a directory given by their pagename, so that generated URLs don't have
    ``.html`` in them.
    """
    name = 't3dirhtml'

    def get_target_uri(self, docname, typ=None):
        if docname == 'index':
            return ''
        if docname.endswith(SEP + 'index'):
            return docname[:-5] # up to sep
        return docname + SEP

    def get_outfilename(self, pagename):
        if pagename == 'index' or pagename.endswith(SEP + 'index'):
            outfilename = path.join(self.outdir, os_path(pagename)
                                    + self.out_suffix)
        else:
            outfilename = path.join(self.outdir, os_path(pagename),
                                    'index' + self.out_suffix)

        return outfilename

    def prepare_writing(self, docnames):
        T3StandaloneHTMLBuilder.prepare_writing(self, docnames)
        self.globalcontext['no_search_suffix'] = True


class T3SingleFileHTMLBuilder(T3StandaloneHTMLBuilder):
    """
    A StandaloneHTMLBuilder subclass that puts the whole document tree on one
    HTML page.
    """
    name = 't3singlehtml'
    copysource = False

    def get_outdated_docs(self):
        return 'all documents'

    def get_target_uri(self, docname, typ=None):
        if docname in self.env.all_docs:
            # all references are on the same page...
            return self.config.master_doc + self.out_suffix + \
                   '#document-' + docname
        else:
            # chances are this is a html_additional_page
            return docname + self.out_suffix

    def get_relative_uri(self, from_, to, typ=None):
        # ignore source
        return self.get_target_uri(to, typ)

    def fix_refuris(self, tree):
        # fix refuris with double anchor
        fname = self.config.master_doc + self.out_suffix
        for refnode in tree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue
            refuri = refnode['refuri']
            hashindex = refuri.find('#')
            if hashindex < 0:
                continue
            hashindex = refuri.find('#', hashindex+1)
            if hashindex >= 0:
                refnode['refuri'] = fname + refuri[hashindex:]

    def assemble_doctree(self):
        master = self.config.master_doc
        tree = self.env.get_doctree(master)
        tree = inline_all_toctrees(self, set(), master, tree, darkgreen)
        tree['docname'] = master
        self.env.resolve_references(tree, master, self)
        self.fix_refuris(tree)
        return tree

    def get_doc_context(self, docname, body, metatags):
        # no relation links...
        toc = self.env.get_toctree_for(self.config.master_doc, self, False)
        # if there is no toctree, toc is None
        if toc:
            self.fix_refuris(toc)
            toc = self.render_partial(toc)['fragment']
            display_toc = True
        else:
            toc = ''
            display_toc = False
        return dict(
            parents = [],
            prev = None,
            next = None,
            docstitle = None,
            title = self.config.html_title,
            meta = None,
            body = body,
            metatags = metatags,
            rellinks = [],
            sourcename = '',
            toc = toc,
            display_toc = display_toc,
        )

    def write(self, *ignored):
        docnames = self.env.all_docs

        self.info(bold('preparing documents... '), nonl=True)
        self.prepare_writing(docnames)
        self.info('done')

        self.info(bold('assembling single document... '), nonl=True)
        doctree = self.assemble_doctree()
        self.info()
        self.info(bold('writing... '), nonl=True)
        self.write_doc_serialized(self.config.master_doc, doctree)
        self.write_doc(self.config.master_doc, doctree)
        self.info('done')

    def finish(self):
        # no indices or search pages are supported
        self.info(bold('writing additional files...'), nonl=1)

        # additional pages from conf.py
        for pagename, template in self.config.html_additional_pages.items():
            self.info(' '+pagename, nonl=1)
            self.handle_page(pagename, {}, template)

        if self.config.html_use_opensearch:
            self.info(' opensearch', nonl=1)
            fn = path.join(self.outdir, '_static', 'opensearch.xml')
            self.handle_page('opensearch', {}, 'opensearch.xml', outfilename=fn)

        self.info()

        self.copy_image_files()
        self.copy_download_files()
        self.copy_static_files()
        self.copy_extra_files()
        self.write_buildinfo()
        self.dump_inventory()


class T3SerializingHTMLBuilder(T3StandaloneHTMLBuilder):
    """
    An abstract builder that serializes the generated HTML.
    """
    #: the serializing implementation to use.  Set this to a module that
    #: implements a `dump`, `load`, `dumps` and `loads` functions
    #: (pickle, simplejson etc.)
    implementation = None
    implementation_dumps_unicode = False
    #: additional arguments for dump()
    additional_dump_args = ()

    #: the filename for the global context file
    globalcontext_filename = None

    supported_image_types = ['image/svg+xml', 'image/png',
                             'image/gif', 'image/jpeg']

    def init(self):
        self.config_hash = ''
        self.tags_hash = ''
        self.theme = None       # no theme necessary
        self.templates = None   # no template bridge necessary
        self.init_translator_class()
        self.init_highlighter()

    def get_target_uri(self, docname, typ=None):
        if docname == 'index':
            return ''
        if docname.endswith(SEP + 'index'):
            return docname[:-5] # up to sep
        return docname + SEP

    def dump_context(self, context, filename):
        if self.implementation_dumps_unicode:
            f = codecs.open(filename, 'w', encoding='utf-8')
        else:
            f = open(filename, 'wb')
        try:
            self.implementation.dump(context, f, *self.additional_dump_args)
        finally:
            f.close()

    def handle_page(self, pagename, ctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        ctx['current_page_name'] = pagename
        self.add_sidebars(pagename, ctx)

        if not outfilename:
            outfilename = path.join(self.outdir,
                                    os_path(pagename) + self.out_suffix)

        self.app.emit('html-page-context', pagename, templatename,
                      ctx, event_arg)

        ensuredir(path.dirname(outfilename))
        self.dump_context(ctx, outfilename)

        # if there is a source file, copy the source file for the
        # "show source" link
        if ctx.get('sourcename'):
            source_name = path.join(self.outdir, '_sources',
                                    os_path(ctx['sourcename']))
            ensuredir(path.dirname(source_name))
            copyfile(self.env.doc2path(pagename), source_name)

    def handle_finish(self):
        # dump the global context
        outfilename = path.join(self.outdir, self.globalcontext_filename)
        self.dump_context(self.globalcontext, outfilename)

        # super here to dump the search index
        T3StandaloneHTMLBuilder.handle_finish(self)

        # copy the environment file from the doctree dir to the output dir
        # as needed by the web app
        copyfile(path.join(self.doctreedir, ENV_PICKLE_FILENAME),
                 path.join(self.outdir, ENV_PICKLE_FILENAME))

        # touch 'last build' file, used by the web application to determine
        # when to reload its environment and clear the cache
        open(path.join(self.outdir, LAST_BUILD_FILENAME), 'w').close()


class T3PickleHTMLBuilder(T3SerializingHTMLBuilder):
    """
    A Builder that dumps the generated HTML into pickle files.
    """

    implementation = pickle
    implementation_dumps_unicode = False
    additional_dump_args = (pickle.HIGHEST_PROTOCOL,)
    indexer_format = pickle
    indexer_dumps_unicode = False
    name = 't3pickle'
    out_suffix = '.fpickle'
    globalcontext_filename = 'globalcontext.pickle'
    searchindex_filename = 'searchindex.pickle'

# compatibility alias
T3WebHTMLBuilder = T3PickleHTMLBuilder


class T3JSONHTMLBuilder(T3SerializingHTMLBuilder):
    """
    A builder that dumps the generated HTML into JSON files.
    """
    implementation = jsonimpl
    implementation_dumps_unicode = True
    indexer_format = jsonimpl
    indexer_dumps_unicode = True
    name = 't3json'
    out_suffix = '.fjson'
    globalcontext_filename = 'globalcontext.json'
    searchindex_filename = 'searchindex.json'

    def init(self):
        if jsonimpl.json is None:
            raise SphinxError(
                'The module simplejson (or json in Python >= 2.6) '
                'is not available. The JSONHTMLBuilder builder will not work.')
        T3SerializingHTMLBuilder.init(self)
