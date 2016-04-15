
class RoiStatsCalculator(object):
    names=()
    def compute_stats(self, data, mask, bounds, offset):
        return ()

    def __call__(self, roi, origin=None, scale=None):
        return dict(zip(self.names, self.compute_stats(roi.data, roi.mask, roi.bounds, origin or (0, 0), scale or (1.0,1.0))))
