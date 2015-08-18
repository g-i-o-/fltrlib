
class ROI:
    def __init__(self, data, mask, bounds, cmax):
        self.data = data
        self.mask = mask
        self.bounds = bounds
        self.channel_max = cmax
