# -*- coding: iso-8859-1 -*-
#
# disapprove_changes.py --- A ListView utility, for bulk-deleting spam pages
#                           in the ApprovalQueue of the SCons wiki.

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

import sys
import xmlrpclib

# User name, password and Wiki URL
name = "your_name"
password = "your_password"
wikiurl = "http://scons.org/wiki"

#
# You shouldn't have to edit anything below here...
#
from Tkinter import *

entry_cnt = None
pagelist = None
root = None

def getToc(proxy):
    mc = xmlrpclib.MultiCall(proxy)
    auth_token = proxy.getAuthToken(name, password)
    mc.applyAuthToken(auth_token)
    mc.getAllPages()
    result = mc()

    return result[0], result[1]

def isSpamPage(path):
    return (path.find('_') >= 0)

def updatePages():
    global pagelist
    global entry_cnt

    homewiki = xmlrpclib.ServerProxy(wikiurl + "?action=xmlrpc2", allow_none=True)
    success, allpages = getToc(homewiki)

    pages = [x for x in allpages if x.endswith('ApprovalQueue')]
    
    pagelist.delete(0,'end')
    selcnt = 0
    if success and len(pages):
        for i,p in enumerate(pages):
            pagelist.insert(i, p)
        # Update selection
        pagelist.selection_clear(0)
        for i,p in enumerate(pages):
            if isSpamPage(p):
              pagelist.select_set(i)
              selcnt += 1
        entry_cnt.set("%d of %d pages selected" % (selcnt, len(pages)))
    else:
        entry_cnt.set("No pages found!")

def deleteSelected():
    # tuple of line index(es)
    sel = pagelist.curselection()
    # get the texts, might be multi-line
    dellist = [pagelist.get(x) for x in sel]

    if len(dellist):
        proxy = xmlrpclib.ServerProxy(wikiurl + "?action=xmlrpc2", allow_none=True)
        mc = xmlrpclib.MultiCall(proxy)
        auth_token = proxy.getAuthToken(name, password)
        mc.applyAuthToken(auth_token)
        for d in dellist:
            mc.deletePageWithAttributes(d, {'comment' : ''})
        result = mc()

        updatePages()

def makemenu(win):
    top = Menu(win)                                # win=top-level window
    win.config(menu=top)                           # set its menu option

    file = Menu(top)
    file.add_command(label='Delete selected', command=deleteSelected, underline=0)
    file.add_separator( )
    file.add_command(label='Quit', command=win.quit, underline=0)
    top.add_cascade(label='File', menu=file, underline=0)

def main():
    global root
    global entry_cnt
    global pagelist

    root = Tk() 
    root.title('DisapproveChanges')  # set window-mgr info
    makemenu(root) # associate a menu bar

    entry_cnt = StringVar()

    _widgets = {}
    _widgets['label'] = Label(root, name='label', text='%s (%s)' % (wikiurl, name))
    _widgets['label'].grid(column=1, columnspan=2, row=1, sticky='ew')
    
    pagelist = Listbox(root, selectmode='multiple', name='pagelist', height=50, width=0)
    pagelist.grid(column=1, row=2, sticky='nesw')
    sbar = Scrollbar(root, name='scrollbar#1')
    sbar.grid(column=2, row=2, sticky='ns')

    _widgets['pagecnt'] = Entry(root, name='pagecnt', textvariable=entry_cnt, state='readonly')
    _widgets['pagecnt'].grid(column=1, columnspan=2, row=3, sticky='ew')
    
    ## Scroll commands
    sbar.config(command=pagelist.yview)
    pagelist.config(yscrollcommand=sbar.set)
    
    ## Resize behavior(s)
    root.grid_rowconfigure(1, weight=0, minsize=30)
    root.grid_rowconfigure(2, weight=0, minsize=304)
    root.grid_rowconfigure(3, weight=0, minsize=30)
    root.grid_columnconfigure(1, weight=0, minsize=350)
    root.grid_columnconfigure(2, weight=0, minsize=30)
    
    updatePages()
    
    root.mainloop()

if __name__ == "__main__":
    main()

