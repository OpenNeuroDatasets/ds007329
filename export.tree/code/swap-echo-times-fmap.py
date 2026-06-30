#!/usr/bin/env python
"""This script swaps EchoTime1 with EchoTime2 for recent BIDS specifications"""

from glob import glob
import simplejson as json

files = glob('/data/hyperface/inputs/data/*/*/fmap/*phasediff.json')

for phasediff in files:
    with open(phasediff, 'rb') as f:
        d = json.load(f)
    echo1 = d['EchoTime1']
    echo2 = d['EchoTime2']
    d['EchoTime1'], d['EchoTime2'] = echo2, echo1
    assert d['EchoTime2'] > d['EchoTime1']
    with open(phasediff, 'w') as f:
        json.dump(d, f, indent=2)
