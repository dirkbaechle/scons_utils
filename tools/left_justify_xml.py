# Reads all given XML files and left justifies the text in the following
# environments:
#
# programlisting, sconstruct, scons_example, screen, example_commands, literallayout
#

import sys

def usage():
    print "left_justify_xml.py file1 [file2 ...]"
    print "Reads all given XML files and left-justifies text in verbatim environments"

# The environments that get left-justified
verb_list = ['programlisting',
             'sconstruct',
             'scons_example',
             'screen',
             'example_commands',
             'literallayout']

PM_VOID = 0
PM_JUSTIFY = 1

def leftJustify(fpath):
    content = ""
    with open(fpath, 'r') as f:
        content = f.readlines()

    newcontent = []
    parse_mode = PM_VOID
    parsed_block = ""
    block = []
    for l in content:
        l = l.rstrip('\n')
        if parse_mode == PM_VOID:
            for v in verb_list:
                if l.find("<%s" % v) >= 0 and l.find("</%s" % v) < 0:
                    parsed_block = v
                    parse_mode = PM_JUSTIFY
                    block = []
                    break
            newcontent.append(l)
        else:
            if l.find("</%s" % parsed_block) >= 0:
                # End parsing of the block
                parse_mode = PM_VOID

                if len(block):
                    # Find num of spaces to remove
                    spaces = -1
                    for b in block:
                        if b.strip() == '':
                            continue
                        if not b.lstrip(' ').startswith('<'):
                            slen = len(b) - len(b.lstrip(' '))
                            if spaces < 0 or slen < spaces:
                                spaces = slen

                    if spaces < 0:
                        spaces = 0

                    # Output left-justified block
                    for b in block:
                        if b.strip() == '':
                            newcontent.append('')
                        else:
                            if not b.lstrip(' ').startswith('<'):
                                newcontent.append(b[spaces:])
                            else:
                                newcontent.append(b)

                newcontent.append(l)
            else:
                block.append(l)

    if parse_mode != PM_VOID:
        print "Error: Encountered EOF in %s with an open justify block!" % fpath
        print "       File is not written..."
        return

    fout = open(fpath, 'w')
    fout.write('\n'.join(newcontent))
    fout.write('\n')
    fout.close()

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)

    for f in sys.argv[1:]:
        leftJustify(f)

if __name__ == "__main__":
    main()

