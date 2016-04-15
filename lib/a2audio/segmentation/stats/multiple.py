from __future__ import absolute_import

from .roistats import RoiStatsCalculator

class MultipleSCStatsCalculator(RoiStatsCalculator):
    def __init__(self, stat_calculators):
        self.stat_calculators = stat_calculators
        self.names = [X for rsc in self.stat_calculators for X in rsc.names]

    def compute_stats(self, data, mask, bounds, offset, scale):
        return [X for rsc in self.stat_calculators for X in rsc.compute_stats(data, mask, bounds, offset, scale)]
