#!python

# Pseudo pkg-config -- an alternative pkg-config implementation
#
# Copyright (C) 2016 Francesco Abbate. All rights reserved.
#
# Pseudo pkg-config is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pseudo pkg-config is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pseudo pkg-config.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import re
import sys
import glob

def interpolate_string(var_list, s):
    def subst(m):
        name = m.group(1)
        return var_list[name] if name in var_list else ""
    return re.sub(r'\$\{([a-zA-Z_]\w*)\}', subst, s)

def read_pc(filename):
    var_list = {}
    declarations = {}
    f = open(filename, "r")
    for line in f:
        m = re.match(r'([a-zA-Z_]\w*) *= *(.+)$', line)
        if m:
            var_list[m.group(1)] = interpolate_string(var_list, m.group(2).strip())
        else:
            m = re.match(r'([A-Z]\w*): (.+)$', line)
            if m:
                dec_name = m.group(1).lower()
                declarations[dec_name] = interpolate_string(var_list, m.group(2).strip())
    f.close()
    return declarations

PKG_CONFIG_VERSION = "0.29.1"
DEFAULT_PKG_CONFIG_PATH = "/usr/lib/pkgconfig"
PKG_CONFIG_PATH = os.environ['PKG_CONFIG_PATH'] if 'PKG_CONFIG_PATH' in os.environ else DEFAULT_PKG_CONFIG_PATH

libs = {}

for filename in glob.glob(os.path.join(PKG_CONFIG_PATH, "*.pc")):
    m = re.match(r'(.+)\.pc', os.path.basename(filename))
    if m:
        pc_name = m.group(1)
        pc = read_pc(filename)
        libs[pc_name] = pc

what = None
libspec = None

def exit_error(msg):
    print(msg)
    sys.exit(1)

def print_usage():
    print("pkg-config [--modversion] [--cflags] [--libs] [--exists] [--atleast-pkgconfig-version=VERSION] [LIBRARIES...]")
    sys.exit(1)

for opt in sys.argv[1:]:
    if opt == '--version':
        print(PKG_CONFIG_VERSION)
        sys.exit(0)
    if opt == '--atleast-pkgconfig-version':
        sys.exit(0)
    if opt in ["--exists", "--modversion", "--cflags", "--libs"]:
        what = opt[2:] if opt[2:] != "modversion" else "version"
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
            sys.exit(1)
    sys.exit(0)

for libname in parse_libnames(libspec):
    if libname in libs:
        print(libs[libname][what] if what in libs[libname] else "")
    else:
        msg = """Package libaggx was not found in the pkg-config search path.
Perhaps you should add the directory containing `%s.pc'
to the PKG_CONFIG_PATH environment variable
No package '%s' found"""
        exit_error(msg % (libname, libname))
        sys.exit(1)
