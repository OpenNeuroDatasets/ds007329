#!/usr/bin/env python
"""Add IntendedFor field

Usage: add_intededfor.py [--overwrite] JSON FILE ...

Arguments:
    JSON    json file in which to add the IntendedFor field
    FILE    list of files to add to the field

Options:
    --overwrite     whether to overwrite the field if already present
"""

import sys
import simplejson as json
from os.path import relpath, abspath, dirname
from glob import glob
from docopt import docopt

if __name__ == '__main__':
    args = docopt(__doc__)

    infile = args['JSON']
    overwrite = args['--overwrite']
    files2add = args['FILE']

    # try globbing
    if len(files2add) == 1:
        files2add = glob(files2add[0])

    if not infile.endswith('json'):
        raise ValueError("I need a json file as input")

    with open(infile) as f:
        values = json.load(f)

    if "IntendedFor" in values and not overwrite:
        print("IntendedFor field already present in json file")
        sys.exit(0)

    def fix_relative_name(filename):
        filename = abspath(filename)
        parts = filename.split('/')[::-1]
        while len(parts):
            p = parts.pop()
            if p.startswith('ses'):
                break
        return '/'.join([p] + parts[::-1])

    if files2add:
        values["IntendedFor"] = sorted(map(fix_relative_name, files2add))

    with open(infile, 'w') as f:
        json.dump(values, f, indent=2, sort_keys=True)
