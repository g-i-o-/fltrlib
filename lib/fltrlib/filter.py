import numpy
import scipy.ndimage


def band_flatten(X, percentile=50, divide=False):
    """
    Flattens the given data matrix by removing the medians in a row-wise manner.
    
    Parameters
    ----------
    X : array_like
        The input data matrix
    percentile : float in range [0,100], optional
        Adjusts the percentile that gets computed. The default (50) is 
        to compute the median.
    divide : bool, optional
        Wether to divide the medians instead of subtracting them. The
        default (False) is to do subtraction.
    """
    
    band_medians = numpy.percentile(X, percentile, axis=1).tolist()

    if divide:
        fn = lambda r, m: r / m.pop(0)
    else:
        fn = lambda r, m: r - m.pop(0)
        
    return numpy.apply_along_axis(fn, 1, X, band_medians)


def compute_local_trimmed_range(X, p=5, size=10, footprint=None, mode='reflect', cval=0.0, origin=0):
    """
    Computes the local trimmed range of a data matrix.
    
    The local trimmed range is just the trimmed range (percentile 
    difference) in the neighborhood of each cell in the data matrix.
    
    Parameters
    ----------
    X : array_like
        The input data matrix
    p : float in range [0, 100], or sequence of 2 floats.
        The percentile(s) to use in the trimmed range. If a 2 floats 
        are given, then they are used as the percentiles, if one float is
        given, then the p-th and (100-p)-th percentiles are used. Default
        (5) is 5-th and 95-th percentiles.
    size : int, optional
        Gives the shape that is taken from X, at every element position, to 
        compute the trimmed range. The defaul value (10) is a 10x10 shape.
    footprint : boolean array, optional
        Specifies a mask used to take from X, at every element position, to
        compute the trimmed range. If footprint is given, then size is 
        ignored. 
    mode : {'reflect', 'constant', 'nearest', 'mirror', 'wrap'}, optional
        The mode parameter determines how the array borders are handled, 
        where cval is the value when mode is equal to 'constant'. Default 
        is 'reflect'. 
    cval : scalar, optional
        Value to fill past edges of input if mode is 'constant'. Default 
        is 0.0.
    origin : scalar, optional
        The origin parameter controls the placement of the filter. Default 
        0.0.
    """
    
    try:
        p1, p2 = p[:2]
    except:
        p1 = p
        p2 = 100 - p
        
    if footprint:
        size = None
        
    Xmin = scipy.ndimage.percentile_filter(X, p1, size, footprint, mode, cval, origin)
    Xmax = scipy.ndimage.percentile_filter(X, p2, size, footprint, mode, cval, origin)
    
    return Xmax - Xmin
