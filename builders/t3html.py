# -*- coding: utf-8 -*-
"""
    sphinx.builders.t3html
    ~~~~~~~~~~~~~~~~~~~~

    Several HTML builders.

    :copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sphinx
import os
import posixpath
import codecs
import sphinx.builders.html
import sphinx.writers.html
from sphinx.locale import _
from docutils.core import Publisher
from docutils.io import DocTreeInput, StringOutput
from docutils.readers.doctree import Reader as DoctreeReader
from docutils.utils import new_document
from sphinx.addnodes import nodes
try:
    from PIL import Image        # check for the Python Imaging Library
except ImportError:
    Image = None


# from sphinx.writers.html import HTMLWriter, HTMLTranslator, SmartyPantsHTMLTranslator
# from sphinx.writers.html import HTMLWriter, HTMLTranslator, SmartyPantsHTMLTranslator

#from docutils.writers.html4css1 import Writer, HTMLTranslator as BaseTranslator
from docutils.writers.html4css1 import HTMLTranslator as BaseTranslator

b = str
b = unicode

printing = False



import docutils.nodes

class span(docutils.nodes.Inline, docutils.nodes.TextElement): pass

# GLOBALS we need
LAST_CUR_NODE = None
LAST_TOC_DIV = None


class HTMLWriter(sphinx.writers.html.Writer):
    pass

class HTMLTranslator(sphinx.writers.html.HTMLTranslator):

    def visit_image(self, node):
        olduri = node['uri']
        s = olduri.lower()
        go = True
        go = go and not Image is None
        go = go and not (s.endswith('svg') or
                         s.endswith('svgz') or
                         s.endswith('swf'))
        go = go and not (node.has_key('width') or
                         node.has_key('height') or
                         node.has_key('scale'))
        if go and node.has_key('classes'):
            go = go and not 'screenshot-detail' in node['classes']
        if go:
            # Try to figure out image height and width.  Docutils does that too,
            # but it tries the final file name, which does not necessarily exist
            # yet at the time the HTML file is written.
            try:
                im = Image.open(os.path.join(self.builder.srcdir, olduri))
            except (IOError, # Source image can't be found or opened
                    UnicodeError):  # PIL doesn't like Unicode paths.
                go = False # better warn?
            else:
                im_width = str(im.size[0])
                im_height = str(im.size[1])
                del im
        if go:
            # rewrite the URI if the environment knows about it
            if olduri in self.builder.images:
                node['uri'] = posixpath.join(self.builder.imgpath,
                                             self.builder.images[olduri])
            atts = {}
            atts['src'] = node['uri']
            if not node.has_key('classes'):
                node['classes'] = ['img-scaling']
            elif not 'img-scaling' in node['classes']:
                node['classes'].append('img-scaling')
            else:
                pass
            atts['style'] = 'max-width: %spx;' % im_width
            if node.has_key('alt'):
                atts['alt'] = node['alt']
            else:
                atts['alt'] = node['uri']
            if node.has_key('align'):
                self.body.append('<div align="%s" class="align-%s">' %
                                 (node['align'], node['align']))
                self.context.append('</div>\n')
            else:
                self.context.append('')
            self.body.append(self.emptytag(node, 'img', '', **atts))
        else:
            del s, go
            sphinx.writers.html.HTMLTranslator.visit_image(self,node)
        return

    def visit_literal(self, node):
        self.body.append(self.starttag(node, 'span', '', CLASS='docutils literal tt'))
        self.protect_literal_text += 1

    def depart_literal(self, node):
        self.protect_literal_text -= 1
        self.body.append('</span>')

    def visit_span(self, node):
        # ToDo: handle class and id
        self.body.append(self.starttag(node, 'span'))

    def depart_span(self, node):
        self.body.append('</span>')

    def depart_title(self, node):
        close_tag = self.context[-1]
        if (self.permalink_text and self.builder.add_permalinks and node.parent.hasattr('ids') and node.parent['ids']):
            aname = ''
            for id in node.parent['ids']:
                if self.builder.env.domaindata['std']['labels'].has_key(id):
                    ref_text = '. Label :ref:`%s`' % id
                    aname = id
                    break
            if aname:
                link_text = ':ref:'
            else:
                ref_text = ''
                aname = node.parent['ids'][0]
                link_text = self.permalink_text


            # add permalink anchor
            if close_tag.startswith('</h'):
                what = u'<a class="headerlink" href="#%s" ' % aname + u'title="%s">%s</a>' % (
                    _('Permalink to this headline') + ref_text, link_text)
                if printing:
                    print 'what:', repr(what)
                    print 'aname:', repr(aname)
                self.body.append(what)
            elif close_tag.startswith('</a></h'):
                what = u'</a><a class="headerlink" href="#%s" ' % aname + u'title="%s">%s' % (
                    _('Permalink to this headline') + ref_text, link_text)
                if printing:
                    print 'what:', repr(what)
                    print 'aname:', repr(aname)
                self.body.append(what)

        BaseTranslator.depart_title(self, node)



class SmartyPantsHTMLTranslator(HTMLTranslator):
    pass


sphinx_builders_html_StandaloneHTMLBuilder = sphinx.builders.html.StandaloneHTMLBuilder
sphinx_writers_html_HTMLWriter = sphinx.writers.html.HTMLWriter

class StandaloneHTMLBuilder(sphinx.builders.html.StandaloneHTMLBuilder):
    """
    Builds standalone HTML docs.
    """

    mb_publisher = None
    mb_doccount = 0
    name = 't3html'

    def write_doc(self, docname, doctree):
        sphinx_builders_html_StandaloneHTMLBuilder.write_doc(self, docname, doctree)

        self.mb_doccount += 1
        if self.mb_doccount == 1:
            ##[Dbg]>>> self
            ##<sphinx.builders.t3html.SmartyPantsHTMLTranslator instance at 0x0699C800>
            ##[Dbg]>>> self.builder
            ##<sphinx.builders.t3html.StandaloneHTMLBuilder object at 0x0531D9B0>
            ##[Dbg]>>> self.builder.env
            ##<sphinx.environment.BuildEnvironment instance at 0x05984E68>
            ##[Dbg]>>> self.builder.env.intersphinx_cache
            ##[Dbg]>>> self.builder.env.intersphinx_inventory
            ##[Dbg]>>> self.builder.env.intersphinx_named_inventory
            from pprint import pprint
            #def pprint(object, stream=None, indent=1, width=80, depth=None):
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
        super(self.__class__, self).handle_page(pagename, addctx, templatename,
            outfilename, event_arg)


    def get_doc_context(self, docname, body, metatags):
        """Collect items for the template context of a page."""

        shorttitle = self.globalcontext.get('shorttitle', '')
        if shorttitle and shorttitle.endswith(' documentation'):
            shorttitle = shorttitle[0:-14].rstrip()
            self.globalcontext['shorttitle'] = shorttitle


        if 0 and "hacking for typo3 ...":
            master_doc = self.globalcontext['master_doc']
            docstitle_from_settings = self.globalcontext['docstitle']
            docstitle = self.env.titles[master_doc]
            self.globalcontext['docstitle'] = 'docstitle'
            """
            [Dbg]>>> pprint(self.globalcontext)
                {'builder': 'html',
                 'copyright': '2000-2012',
                 'css_files': [],
                 'docstitle': u'TypoScript Reference (TSref) 4.7.0 documentation',
                 'embedded': False,
                 'favicon': '',
                 'file_suffix': '.html',
                 'has_source': True,
                 'last_updated': None,
                 'logo': '',
                 'master_doc': 'Index',
                 'parents': [],
                 'project': 'TypoScript Reference (TSref)',
                 'release': '4.7.0',
                 'rellinks': [],
                 'script_files': ['_static/jquery.js',
                                  '_static/underscore.js',
                                  '_static/doctools.js'],
                 'shorttitle': u'TypoScript Reference (TSref) 4.7.0 documentation',
                 'show_copyright': True,
                 'show_source': True,
                 'show_sphinx': True,
                 'sphinx_version': '1.2pre',
                 'style': 'basic.css',
                 'theme_nosidebar': 'false',
                 'theme_sidebarwidth': '230',
                 'use_opensearch': '',
                 'version': '4.7.0'}
            """


        # find out relations
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
                rellinks.append((related[1], prev['title'], 'P', _('Previous')))
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
                rellinks.append((related[0], up['title'], 'U', _('Up')))
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
                rellinks.append((related[2], next['title'], 'N', _('Next')))
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

            self_toc = self_toc, # mb, 2012-12-15

            toc = toc,
            # only display a TOC if there's more than one item to show
            display_toc = (self.env.toc_num_entries[docname] > 1),
        )




    def _get_local_toctree(self, docname, collapse=True, **kwds):

        global LAST_CUR_NODE, LAST_TOC_DIV

        toctree_for = self.env.get_toctree_for(docname, self, collapse, **kwds)
        def dumpit(fname='U:\\htdocs\\LinuxData200\\py-dev\\LOG.txt'):
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

        def xx():
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
            result = xx()

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


        # def traverse(self, condition=None, include_self=1, descend=1, siblings=0, ascend=0)

        class visitor(docutils.nodes.GenericNodeVisitor):
            ul_level = 0
            last_nav_aside_lvl = ''
            cnt = 0

            def default_visit(self, node):
                """Override for generic, uniform traversals."""

                global LAST_TOC_DIV, LAST_CUR_NODE
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
                        LAST_CUR_NODE = node
                        try:
                            self_toc = self.t3addctx['self_toc']
                        except:
                            self_toc = None
                        if self_toc:
                            LAST_TOC_DIV = nodes.container(ids=["flyOutToc"], classes=['flyOutToc'])
                            LAST_TOC_DIV.append(nodes.paragraph(text='within this page:'))
                            LAST_TOC_DIV.append(self_toc)

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
            if not LAST_TOC_DIV is None:
                LAST_CUR_NODE.replace_self([LAST_CUR_NODE, LAST_TOC_DIV])
            LAST_CUR_NODE = None
            LAST_TOC_DIV = None
            result = self.render_partial(toctree_for)['fragment']

        else:
            result = ''
        return result


#sphinx.builders.html.HTMLWriter = HTMLWriter
sphinx.builders.html.HTMLTranslator = HTMLTranslator
sphinx.builders.html.SmartyPantsHTMLTranslator = SmartyPantsHTMLTranslator
sphinx.builders.html.StandaloneHTMLBuilder = StandaloneHTMLBuilder












##u'<?xml version="1.0" ?>\n
##<document source="&lt;partial node&gt;">
##<compact_paragraph classes="current" iscurrent="True" toctree="True">
##  <bullet_list classes="current" iscurrent="True">
##    <list_item classes="toctree-l1">
##      <compact_paragraph classes="toctree-l1">
##        <reference anchorname="" internal="True" refuri="../Introduction/Index.html">Introduction</reference>
##      </compact_paragraph>
##      <bullet_list/>
##    </list_item>
##    <list_item classes="toctree-l1 current" iscurrent="True">
##      <compact_paragraph classes="toctree-l1 current" iscurrent="True">
##        <reference anchorname="" classes="current" internal="True" iscurrent="True" refuri="">Chapter 1</reference>
##      </compact_paragraph>
##      <bullet_list/>
##    </list_item>
##    <list_item classes="toctree-l1">
##      <compact_paragraph classes="toctree-l1">
##        <reference anchorname="" internal="True" refuri="../NextSteps/Index.html">Next steps</reference>
##      </compact_paragraph>
##      <bullet_list/>
##    </list_item>
##  </bullet_list>
##</compact_paragraph>
##</document>'
