#!/usr/bin/env python
"""Script to copy Budapest data for participants who took part in both experiments"""
import os.path as op
from glob import glob
from shutil import copy, copytree, move

HERE = op.abspath(op.dirname(__file__))

# unfortunately this is specific to hydra
BUDAPEST_DIR = '/data/budapest/data'
FAMFACE_DIR = op.dirname(HERE)

subj_budapest = map(op.basename, glob(op.join(BUDAPEST_DIR, 'sub-*')))
subj_famface = map(op.basename, glob(op.join(FAMFACE_DIR, 'sub-*')))

subj_common = sorted(list(set(subj_budapest).intersection(subj_famface)))

print("Found {0} subjects in common".format(len(subj_common)))

# Copy data recursively
for subj in subj_common:
    print("Copying data for {}".format(subj))
    indir = op.join(BUDAPEST_DIR, subj)
    outdir = op.join(FAMFACE_DIR, subj, 'ses-budapest')
    if op.exists(outdir):
        print("Skipping {}: exists".format(outdir))
        continue
    # print("{0}, {1}".format(indir, outdir))
    copytree(indir, outdir)
    # add ses-budapest to all files
    print("  renaming files")
    fns = glob(op.join(outdir, '*.*')) + glob(op.join(outdir, '*/*'))
    for fn in fns:
        fndir = op.dirname(fn)
        fnbase = op.basename(fn)
        fnbase = fnbase.replace(subj, subj + '_ses-budapest')
        fn_ = op.join(fndir, fnbase)
        move(fn, fn_)
    print("  Done.")

# Copy the json file
copy(op.join(BUDAPEST_DIR, 'task-movie_bold.json'), FAMFACE_DIR)
