from __future__ import absolute_import

from .roistats import RoiStatsCalculator

import cv2

class FitEllipseRoiStatsCalculator(RoiStatsCalculator):
    names = ('mux','muy','Sxx','Syy','Sxy')
    def compute_stats(self, data, mask, bounds, offset, scale):
        if data.size:
            M = cv2.moments(data * 1.0 / data.sum())
            return (
                (M['m10'] + offset[0]) * scale[0], (M['m01'] + offset[1]) * scale[1],
                M['mu20'] * scale[0] * scale[0], M['mu02'] * scale[1] * scale[1], 
                M['mu11'] * scale[0] * scale[1]
            )
        else:
            return 0.0, 0.0, 0.0, 0.0, 0.0
