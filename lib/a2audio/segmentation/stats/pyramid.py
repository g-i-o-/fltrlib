from __future__ import absolute_import

from .roistats import RoiStatsCalculator

class PyramidRoiStatsCalculator(object):
    def __init__(self, roi_stat_calculator, depth=1, split_location=None):
        self.roi_stat_calculator = roi_stat_calculator
        self.depth = 1
        self.names = self.compute_stat_names(self.depth)
        if split_location:
            self.split_location = split_location
        else:
            self.split_location = lambda stats, n, m, offset: (n/2, m/2)

    def compute_stats(self, data, mask, bounds, offset, depth, stats):
        tile_stats = self.roi_stat_calculator.compute_stats(data, mask, bounds, offset)
        stats.extend(tile_stats)
        if depth > 0:
            n, m = data.shape
            i, j = self.split_location(tile_stats, n, m, offset)
            bound_i, bound_j = bounds[0] + i, bounds[1] + j
            self.compute_stats(data[0:i, 0:j], mask[0:i, 0:j], (bounds[0], bounds[1], bound_i  , bound_j  ), (offset[0] + i, offset[1] + j), depth - 1, stats)
            self.compute_stats(data[i:n, 0:j], mask[i:n, 0:j], (bound_i  , bounds[1], bounds[2], bound_j  ), (offset[0]    , offset[1] + j), depth - 1, stats)
            self.compute_stats(data[0:i, j:m], mask[0:i, j:m], (bounds[0], bound_j  , bound_i  , bounds[3]), (offset[0] + i, offset[1]    ), depth - 1, stats)
            self.compute_stats(data[i:n, j:m], mask[i:n, j:m], (bound_i  , bound_j  , bounds[2], bounds[3]), (offset[0]    , offset[1]    ), depth - 1, stats)
        
        return stats

    def compute_stat_names(self, depth, deep=0, path='', names=None):
        if not names:
            names = []
        
        names.extend((path + '_' if path else '') + x for x in self.roi_stat_calculator.names)
        
        if depth > deep:
            deep += 1
            ds = str(deep)
            self.compute_stat_names(depth, deep, path + ds + 'a', names)
            self.compute_stat_names(depth, deep, path + ds + 'b', names)
            self.compute_stat_names(depth, deep, path + ds + 'c', names)
            self.compute_stat_names(depth, deep, path + ds + 'd', names)
        
        return names

    def __call__(self, roi):
        return dict(zip(self.names, self.compute_stats(roi.data, roi.mask, roi.bounds, (0,0), self.depth, [])))

