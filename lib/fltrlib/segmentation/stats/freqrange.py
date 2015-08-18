from __future__ import absolute_import

from .roistats import RoiStatsCalculator

class FrequencyRangeStatsCalculator(RoiStatsCalculator):
    names = ('fmin','fmax')
    def compute_stats(self, data, mask, bounds, offset, scale):
        return (bounds[2] + offset[1]) * scale[0], (bounds[0] + offset[1]) * scale[1]
