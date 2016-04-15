import numpy
import scipy
import pylab
import matplotlib.image


class AudioSegmenter:
    types = {}

    @classmethod
    def instantiate(cls, typename, **params):
        C = cls.types.get(typename, cls)
        return C(**params)

    @classmethod
    def declare_type(cls, typename):
        def declare_type_fn(C):
            cls.types[typename] = C
            C.typename = typename
            return C
        return declare_type_fn

    def __init__(self, **params):
        self.params = params

    def segment(self, spectrum, storage, **params):

        mask = self.compute_mask(spectrum, storage)
        if storage:
            with storage.open_for_writing('mask.png') as output_file:
                matplotlib.image.imsave(output_file, mask, cmap=pylab.cm.gray_r, vmax=None, origin='lower')

        vmax = numpy.max(spectrum)

        labels, num_labels = scipy.ndimage.measurements.label(mask)
        objs = scipy.ndimage.measurements.find_objects(labels)

        if storage:
            with storage.open_for_writing('labels.png') as output_file:
                matplotlib.image.imsave(output_file, labels, cmap=pylab.cm.Paired, vmax=None, origin='lower')

        for obj in objs:
            r = (obj[0].start, obj[1].start, obj[0].stop, obj[1].stop)
            if self.filter(obj, r):
                yield ROI(spectrum[obj], mask[obj], r, vmax)

    def compute_mask(self, spectrum, storage, **params):
        return numpy.zeros(spectrum.shape)

    def filter(self, obj, r):
        h = r[2] - r[0]
        w = r[3] - r[1]
        s = w * h
        passed = 25 < s and 4 < w < 500 and 4 < h < 200
        # if passed:
        #     print "%10s, %10s, %10s" % (w, h, s)
        # else:
        #     print "ignored : %10s, %10s, %10s" % (w, h, s)
        return passed


class ROI:
    def __init__(self, data, mask, bounds, cmax):
        self.data = data
        self.mask = mask
        self.bounds = bounds
        self.channel_max = cmax
