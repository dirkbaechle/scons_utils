import sys
import xmlrpclib

name = "DirkBaechle"
password = "1firefly1"
wikiurl = "http://scons.org/wiki"
homewiki = xmlrpclib.ServerProxy(wikiurl + "?action=xmlrpc2", allow_none=True)
mc = xmlrpclib.MultiCall(homewiki)
auth_token = homewiki.getAuthToken(name, password)
mc.applyAuthToken(auth_token)
attachname = sys.argv[1]
pagename = "Qt4Tool"
text = file(attachname, 'rb+').read()
data = xmlrpclib.Binary(text)
mc.putAttachment(pagename, attachname, data)
result = mc()

