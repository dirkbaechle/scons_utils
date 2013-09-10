import sys, re

qt_re = re.compile("QT[4][_A-Z0-9]+")

def usage():
    print "compare_in_tool doc.in tool.py"

def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(0)

    fin = open(sys.argv[1],'r')
    incontent = fin.read()
    fin.close()
    
    fpy = open(sys.argv[2],'r')
    pycontent = fpy.read()
    fpy.close()

    listin = []
    for m in qt_re.findall(incontent):
        if m not in listin:
            listin.append(m)

    listpy = []
    for m in qt_re.findall(pycontent):
        if m not in listpy:
            listpy.append(m)

    nodoc = []
    for l in listpy:
        if l not in listin:
            nodoc.append(l)

    superdoc = []
    for l in listin:
        if l not in listpy:
            superdoc.append(l)


    if len(nodoc) > 0:
        print "\n\nNot documented are:"
        for n in nodoc:
            print "  %s" % n

    if len(superdoc) > 0:
        print "\n\nSuperfluous are:"
        for s in superdoc:
            print "  %s" % s
    

if __name__ == "__main__":
    main()
