import sys, re

qt_re = re.compile("QT[4][_A-Z0-9]+")

def usage():
    print "extract_qt4_identifiers tool.py"

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)

    fin = open(sys.argv[1],'r')
    incontent = fin.read()
    fin.close()
    
    listin = []
    for m in qt_re.findall(incontent):
        if m not in listin:
            listin.append(m)

    for l in listpy:
        print l

if __name__ == "__main__":
    main()
