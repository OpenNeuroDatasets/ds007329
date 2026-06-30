#!/usr/bin/env python
"""This script will rename the column stim_file to video_file for 
the events.tsv associated with the localizer."""

from glob import glob
import pandas as pd

events = sorted(glob('/data/hyperface/inputs/data/sub-sid000*/*/func/*task-localizer*.tsv'))

for ev in events:
    df = pd.read_csv(ev, sep='\t')
    df.columns = [c.replace('stim_file', 'video_file') for c in df.columns]
    df.to_csv(ev, sep='\t', index=False)
