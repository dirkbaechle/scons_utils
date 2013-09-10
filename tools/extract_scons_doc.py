import sys, re

re_cvlink = re.compile("&cv-link-([^;]+);")
re_tool = re.compile("&t-([^;]+);")
re_builder = re.compile("&b-([^;]+);")

def usage():
    print "extract in.xml"

PS_VOID = 0
PS_VAR = 1
PS_VARSUM = 2
PS_TOOL = 3

def processLine(l):
    cvmatch = re_cvlink.search(l)
    while cvmatch:
        l = l[:cvmatch.start()]+"<literal>"+cvmatch.group(1)+"</literal>"+l[cvmatch.end():]
        cvmatch = re_cvlink.search(l)
        
    tmatch = re_tool.search(l)
    while tmatch:
        l = l[:tmatch.start()]+"<literal>"+tmatch.group(1)+"</literal>"+l[tmatch.end():]
        tmatch = re_tool.search(l)
        
    bmatch = re_builder.search(l)
    while bmatch:
        l = l[:bmatch.start()]+"<literal>"+bmatch.group(1)+"</literal>"+l[bmatch.end():]
        bmatch = re_builder.search(l)

    return l

def extractVars(fpath):
    f = open(fpath,'r')
    state = PS_VOID
    for l in f.readlines():
        l = l.rstrip('\n')
        if l.find('</summary>') == 0:
            if state != PS_TOOL:
                if state == PS_VARSUM:
                    print "</para>"
                state = PS_VAR
        elif (state == PS_VOID) and (l.find('<cvar name="') == 0):
            state = PS_VAR
            varname = l[12:l.find('"',12)]
            print "<varlistentry><term>%s</term><listitem>" % varname
        elif (state == PS_VAR) and (l.find('<summary>') == 0):
            print "<para>"
            state = PS_VARSUM
        elif (state == PS_VAR) and (l.find('</cvar>') == 0):
            print "</listitem></varlistentry>"
            state = PS_VOID
        elif (state == PS_VOID) and (l.find('<tool name="') == 0):
            state = PS_TOOL
        elif (state == PS_TOOL) and (l.find('</tool>') == 0):
            state = PS_VOID
        else:
            print processLine(l)
            

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)
    
    extractVars(sys.argv[1])

if __name__ == "__main__":
    main()

