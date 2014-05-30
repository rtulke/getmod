#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import argparse
import hashlib

parser = argparse.ArgumentParser(description='list files with file bits')
parser.add_argument('--format', '-f', default='%(bitmask)o %(filename)s',
    help="""Output format in sprintf syntax,
default: "%(default)s", usable: bitmask, filename, md5sum""")
parser.add_argument('--recursive', '-r', default=False, action="store_true",
    help='List sub-contents of given directories')
parser.add_argument('--exclude', '-e', default=[], action='append',
    help="""exclude every file that contains the given word.
can be given multiple times""")
parser.add_argument('filename', nargs='+', help='List of files to display')
args = parser.parse_args()


def get_md5_hash(filename):
    md5 = hashlib.md5()
    try:
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
    except IOError:
        return "-"
    return md5.hexdigest()


def print_rights(filename):
    exclude = False
    for pattern in args.exclude:
        if pattern in filename:
            exclude = True
    if not exclude:
        mode = 0
        md5sum = '-'
        try:
            mode = os.stat(filename).st_mode
            if stat.S_ISDIR(mode):
                filename = filename + '/'
            elif 'md5sum' in args.format:
                md5sum = get_md5_hash(filename)
        except Exception, e:
            sys.stderr.write(str(e) + '\n')
        print args.format % {
                'bitmask': mode & 0777,
                'filename': filename,
                'md5sum': md5sum,
                }

for filename in args.filename:
    if args.recursive and os.path.isdir(filename):
        for root, dirs, files in os.walk(filename):
            print_rights(root)
            for name in files:
                full_filename = os.path.join(root, name)
                print_rights(full_filename)
    else:
        print_rights(filename)
