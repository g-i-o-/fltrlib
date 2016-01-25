from __future__ import absolute_import

from .roistats import RoiStatsCalculator

import numpy

class CoverageRoiStatsCalculator(RoiStatsCalculator):
    names = ('Cov','dur','bw')
    def compute_stats(self, data, mask, bounds, offset, scale):
        if data.size:
            n, m = data.shape
            c = numpy.count_nonzero(mask) * 1.0 / mask.size
        else:
            c, n, m = 0.0, 0.0, 0.0
        # return c, n, m
        return c, m * scale[0], n * scale[1]
