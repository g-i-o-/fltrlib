import numpy
import scipy
import skimage.filter
import scipy.ndimage
from AudioSegmenter import AudioSegmenter, ROI

def power2decibels(matrix):
    return 10. * numpy.log10(matrix.clip(min=0.0000000001))


@AudioSegmenter.declare_type("flattened-trimmed-local-range")
class FlattenedTrimmedLocalRangeAudioSegmenter(AudioSegmenter):
    def compute_mask(self, spectrum, storage, **params):
        S = spectrum
        p = params.get('percentile', 5)
        r = params.get('radius', 10)
        th = params.get('th', 'yen')
        # remove the band medians
        band_medians = numpy.percentile(S, 50, 1).tolist()
        divide_by_median = lambda r, m: r / m.pop(0)
        S_nomed = numpy.apply_along_axis(divide_by_median, 1, S, band_medians)
        # compute the range
        Smin = scipy.ndimage.percentile_filter(S_nomed, p, r)
        Smax = scipy.ndimage.percentile_filter(S_nomed, 100 - p, r)
        Srange = Smax-Smin
        Sdb = power2decibels(Srange)

        if storage:
            with storage.open_for_writing('.png') as output_file:
                matplotlib.image.imsave(output_file, power2decibels(S_nomed), cmap=pylab.cm.gray_r, vmax=None, origin='lower')
            with storage.open_for_writing('min.png') as output_file:
                matplotlib.image.imsave(output_file, Smin, cmap=pylab.cm.gray_r, vmax=None, origin='lower')
            with storage.open_for_writing('max.png') as output_file:
                matplotlib.image.imsave(output_file, Smax, cmap=pylab.cm.gray_r, vmax=None, origin='lower')
            with storage.open_for_writing('range.png') as output_file:
                matplotlib.image.imsave(output_file, Sdb, cmap=pylab.cm.gray_r, vmax=None, origin='lower')

        # threshold using yen or a given number
        if th == 'yen':
            th = skimage.filter.threshold_yen(Sdb)
            Smask = Srange > th
        else:
            Smask = Sdb > th
            
        return Smask
