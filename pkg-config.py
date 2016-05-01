#!python

import sys

SYS_PATH = 'c:/fra/local'
SYS_INC_PATH = "%s/include" % SYS_PATH
SYS_LIB_PATH = "%s/lib" % SYS_PATH

libs = {
   'libpng': {
       'version': '1.2.8',
       'cflags': "-I%s" % SYS_INC_PATH,
       'libs': ' '.join(["-L%s" % SYS_LIB_PATH, "-lpng"])
    },
   'pixman-1': {
       'version': '0.30.0',
       'cflags': "-I%s/pixman" % SYS_INC_PATH,
       'libs': ' '.join(["-L%s" % SYS_LIB_PATH, "-lpixman-1"])
    }
}

what = None
libspec = None

def exit_error(msg):
    print(msg)
    sys.exit(1)

def print_usage():
    print("pkg-config [--cflags] [--libs] LIBRARY")
    sys.exit(1)

for opt in sys.argv[1:]:
    if opt == '--version':
        print("0.26")
	sys.exit(0)
    if opt == '--atleast-pkgconfig-version':
        sys.exit(0)
    if opt in ["--exists", "--cflags", "--libs"]:
        what = opt[2:]
    if opt[0] != '-':
        if libspec: exit_error("duplicate library name")
        libspec = opt

if not what or not libspec:
    print_usage()

# Return true is the relation "version1 op version2" is statisfied.
def compare_versions(op, version1, version2):
    vl1 = [int(s) for s in version1.split('.')]
    vl2 = [int(s) for s in version2.split('.')]
    sign = -1 if op == '<=' or op == '<' else 1
    c = 0
    for a, b in zip(vl1, vl2):
        if a != b:
            c = sign * cmp(a, b)
            break
    if op == '=':
        return (c == 0)
    elif op == '>' or op == '<':
        return (c > 0)
    else:
        return (c >= 0)

def compare_predicate(name, op, version):
    def compare(mylibs):
        if name not in mylibs: return false
        lib = mylibs[name]
        return compare_versions(op, lib['version'], version)
    return compare

def exists_predicate(name):
    def compare(mylibs):
        return (name in mylibs)
    return compare

def parse_libspec(mylibspec):
    args = mylibspec.split(' ')
    i = 0
    while i < len(args):
        name = args[i]
        op = args[i+1] if i+1 < len(args) else None
        if op and op in ['>=', '>', '=', '<=', '<']:
            version = args[i+2]
            i += 3
            yield (name, op, version)
        else:
            i += 1
            yield (name, None, None)

def parse_predicates(mylibspec):
    for name, op, version in parse_libspec(mylibspec):
        if op:
            yield compare_predicate(name, op, version)
        else:
            yield exists_predicate(name)

def parse_libnames(mylibspec):
    for name, op, ver in parse_libspec(mylibspec):
	yield name

if what == "exists":
    for predicate in parse_predicates(libspec):
        if not predicate(libs):
            print("FAIL")
            sys.exit(1)
    print("SUCCESS")
    sys.exit(0)

for libname in parse_libnames(libspec):
    if libname in libs:
        print(libs[libname][what])
    else:
        exit_error("unknown library: %s" % libname)
        sys.exit(1)
