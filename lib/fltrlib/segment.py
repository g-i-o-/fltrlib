from __future__ import absolute_import

import numpy
import skimage.filter
import scipy.ndimage

from .filter import band_flatten, compute_local_trimmed_range
from .convert import power2decibels


def compute_mask(X, percentile=5, radius=10, th='yen', **params):
    p = percentile
    r = radius
    th = th
    
    X = band_flatten(X, percentile=50, divide=False)
    Srange = compute_local_trimmed_range(X, p, r, **params)

    # threshold using yen or a given number (in db)
    if th == 'yen':
        th = skimage.filter.threshold_yen(Sdb)
        Smask = Srange > th
    else:
        Sdb = power2decibels(Srange)
        Smask = Sdb > th
        
    return Smask

def default_filter(self, obj, r):
    h = r[2] - r[0]
    w = r[3] - r[1]
    s = w * h
    passed = 25 < s and 4 < w < 500 and 4 < h < 200
    # if passed:
    #     print "%10s, %10s, %10s" % (w, h, s)
    # else:
    #     print "ignored : %10s, %10s, %10s" % (w, h, s)
    return passed

def segment(X, filter=default_filter, **params):
    mask = compute_mask(X, **params)

    vmax = numpy.max(X)

    labels, num_labels = scipy.ndimage.measurements.label(mask)
    objs = scipy.ndimage.measurements.find_objects(labels)

    for obj in objs:
        r = (obj[0].start, obj[1].start, obj[0].stop, obj[1].stop)
        if filter(obj, r):
            yield ROI(X[obj], mask[obj], r, vmax)


