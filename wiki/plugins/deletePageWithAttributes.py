# -*- coding: iso-8859-1 -*-

# deletePageWithAttributes.py --- Plugin XML-RPC command for MoinMoin deleting a page

# Copyright 2013 Dirk Baechle <dl9obn@darc.de>

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import xmlrpclib

from MoinMoin.PageEditor import PageEditor
import MoinMoin.wikiutil

###############################################################################
###############################################################################

def execute(xmlRpc, pagename, attributes):
    """
    Callback to execute the functionality of this plugin.

    Deletes a page using the basic security mechanisms described for C{putPage}.

    @param xmlRpc: Describes the local execution environment. While all other
                   parameters come from the remote caller this one is added by
                   the local execution environment.
    @type xmlRpc: XmlRpcBase

    @param pagename: The name of the page to delete.
    @type pagename: unicode | str

    @param attributes: Attributes describing the action further. Currently supported
                       is only the comment field.
    @type attributes: { 'comment': str | unicode, ..., }

    @return: Flag whether operation was successful or fault.
    @rtype: xmlrpclib.Boolean | xmlrpclib.Fault
    """
    # This is taken from `xmlrpc.XmlRpcBase.xmlrpc_putPage()` and modified.
    pagename = xmlRpc._instr(pagename)
    pagename = MoinMoin.wikiutil.normalize_pagename(pagename, xmlRpc.cfg)

    permissionDenied = xmlrpclib.Fault(1, "You are not allowed to delete this page")
    if not xmlRpc.request.user.may.delete(pagename):
        return permissionDenied

    comment = xmlRpc._instr(attributes.get('comment', u''))
    page = PageEditor(xmlRpc.request, pagename)
    try:
        page.deletePage(comment)
    except OSError, error:
        return xmlrpclib.Fault(1, "Deletion failed: %s" % ( error, ))

    return xmlrpclib.Boolean(1)

