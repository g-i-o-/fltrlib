from __future__ import absolute_import

import numpy
from .roistats import RoiStatsCalculator


class MaxPointRoiStatsCalculator(RoiStatsCalculator):
    names = ('x_max','y_max')
    def compute_stats(self, data, mask, bounds, offset, scale):
        ym, xm = numpy.where(data == data.max())
        return (xm[0] + offset[0]) * scale[0], (ym[0] + offset[1]) * scale[1]
