# -*- coding: utf-8 -*-
"""
    t3sphinx.writers.t3htmlwriter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Customize HTML writing for TYPO3

    :copyright: Copyright 2007-2099 by the TYPO3 Documentation Team
    :license: BSD, see LICENSE for details.
"""

from sphinx.writers.html import HTMLTranslator, _, Image, os, posixpath

class T3HTMLTranslator(HTMLTranslator):

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
                if 0:
                    print 'what:', repr(what)
                    print 'aname:', repr(aname)
                self.body.append(what)
            elif close_tag.startswith('</a></h'):
                what = u'</a><a class="headerlink" href="#%s" ' % aname + u'title="%s">%s' % (
                    _('Permalink to this headline') + ref_text, link_text)
                if 0:
                    print 'what:', repr(what)
                    print 'aname:', repr(aname)
                self.body.append(what)

        HTMLTranslator.depart_title(self, node)


