import numpy
import matplotlib.pyplot
import scipy.stats

def normalize_data(X):
    return lt_data(X, numpy.mean(X, axis=0), numpy.std(X, axis=0))

def range_normalize_data(X):
    return lt_data(X, numpy.min(X, axis=0), numpy.max(X, axis=0) - numpy.min(X, axis=0))

def P_normalize_data(X, p=0.15865525393145707):
    xp, xq = numpy.percentile(X, p, axis=0), numpy.percentile(X, 1 - p, axis=0)
    return lt_data(X, xp, xq - xp)


def lt_data(X, offset, scale): 
    def _n(x):
        return (x - offset) / scale
    return numpy.apply_along_axis(_n, 1, X)

def sorting_permutation(X, reverse=False):
    return [x[0] for x in sorted(zip(range(len(X)), X), key=lambda x:x[1], reverse=reverse)]


def estimate_entropy(X, bins=10):
    return numpy.apply_along_axis(lambda x: scipy.stats.entropy(numpy.histogram(x, bins=bins)[0]), 0, X)

def density_plot(X, Y, **kwdargs):
    """Plot of density of (x, y) points."""
    histopts={}
    opts = {'origin':'bottom', 'aspect':'auto', 'bins': 150}
    opts.update(kwdargs)
    xmin, xmax, ymin, ymax = X.min(), X.max(), Y.min(), Y.max()
    if 'extent' not in opts:
        opts['extent'] = xmin, xmax, ymin, ymax
    if 'bins' in opts:
        histopts['bins'] = opts['bins']
        del opts['bins']
    if 'weights' in opts:
        histopts['weights'] = opts['weights']
        del opts['weights']
        

    H = numpy.histogram2d(Y, X, **histopts)[0]

    if 'log' in opts:
        if opts['log']:
            H = numpy.log(H + 1)
        del opts['log']

    matplotlib.pyplot.imshow(H, **opts)

def set_plot_axis(plot, axis, visible, tick_position=None, label=None, label_position=None):
    ax = getattr(plot, 'get_'+axis+'axis')()
    ax.set_visible(visible)
    if tick_position is not None:
        getattr(ax, 'tick_'+tick_position)()
    if label is not None:
        getattr(plot, 'set_'+axis+'label')(label)
    if label_position:
        ax.set_label_position(label_position)

def set_tick_labels(plot, axis, ticks, count=None):
    if not callable(ticks):
        tick_fmt = ticks
        ticks = lambda x: tick_fmt % x
    if count is not None:
        bmin, bmax = getattr(plot, 'get_'+axis+'bound')()
        getattr(plot, 'set_'+axis+'ticks')(numpy.linspace(bmin, bmax, count))
    getattr(plot, 'set_'+axis+'ticklabels')(
        map(ticks, getattr(plot, 'get_'+axis+'ticks')().tolist())
    )
    
def scatterplot_matrix(X, names=None, plotter=density_plot, hist_plotter=matplotlib.pyplot.hist, bins=None, hbins=None, tick_count=None, tick_fmt=None, rc=None, showfn=None, mtype=None, axshowfn=None, **kwargs):
    """Matrix of m x m plots, where m is X.shape[2]."""
    m, n = X.shape
    if not names:
        names = map(str, range(n))
        
    if not showfn and mtype:
        if mtype[0] == 'U':
            showfn = (lambda i,j: i<=j) if mtype == 'UD' else (lambda i,j: i<j)
        elif mtype[0] == 'D':
            showfn = (lambda i,j: i>=j) if mtype == 'DD' else (lambda i,j: i>j)
            
    if not axshowfn:
        axshowfn = lambda i, j: (i == 0 or i + 1 == n)
        
    if bins:
        try:
            len(bins)
        except:
            bins = [bins] * n
    
    if not hbins:
        hbins = bins
        
    if rc:
        rcOld = matplotlib.rcParams.copy()
        matplotlib.rcParams.update(rc)
        
    hist_kwargs = {}
    for k, v in kwargs.items():
        if k[:5] == 'hist_':
            hist_kwargs[k[5:]] = v
            del kwargs[k]
    
    for i in range(n):
        for j in range(n):
            if showfn and not showfn(i, j):
                continue
            ni, nj = names[i], names[j]
            if i == j:
                sp = matplotlib.pyplot.subplot(n, n, i*n + j + 1)
                hist_plotter(X[:,j], bins=hbins[i] if hbins else 150, **hist_kwargs)
                set_plot_axis(sp, 'y', visible=False)
            else:
                sp = matplotlib.pyplot.subplot(n, n, i*n + j + 1)
                if bins:
                    kwargs['bins'] = [bins[i], bins[j]]
                plotter(X[:,j], X[:,i], **kwargs)

                if j == 0 or j + 1 == n:
                    pos = "left" if j == 0 else "right"
                    set_plot_axis(sp, 'y', visible=True, tick_position=pos, label=ni, label_position=pos)
                    if tick_fmt:
                        set_tick_labels(sp, 'y', tick_fmt[i], tick_count)
                else:
                    set_plot_axis(sp, 'y', visible=False)

            if axshowfn(i, j):
                pos = "top" if i == 0 else "bottom"
                set_plot_axis(sp, 'x', visible=True, tick_position=pos, label=nj, label_position=pos)
                if tick_fmt:
                    set_tick_labels(sp, 'x', tick_fmt[j], tick_count)
            else:
                set_plot_axis(sp, 'x', visible=False)

    if rc:
        matplotlib.rcParams.update(rcOld)


class RCSettings:
    def __init__(self, *args, **kwargs):
        self.settings={}
        for a in args:
            self.settings.update(a)
        self.settings.update(kwargs)
    
    def __enter__(self):
        self.oldParams =         rcOld = matplotlib.rcParams.copy()
        matplotlib.rcParams
        

def contour_plot(X, Y, **kwdargs):
    """Contour plot of (x, y) points density."""
    histopts={}
    opts = {'origin':'lower', 'aspect':'auto', 'bins': 150}
    opts.update(kwdargs)
    Xmin, Xmax, Ymin, Ymax = (X.min(), X.max(), Y.min(), Y.max())
    if 'bins' in opts:
        histopts['bins'] = opts['bins']
        del opts['bins']
    if 'weights' in opts:
        histopts['weights'] = opts['weights']
        del opts['weights']
    
    H = numpy.histogram2d(Y, X, **histopts)[0]
    Hx = numpy.arange(Xmin, Xmax, (Xmax - Xmin) / H.shape[1])
    Hy = numpy.arange(Ymin, Ymax, (Ymax - Ymin) / H.shape[0])

    if 'log' in opts:
        if opts['log']:
            H = numpy.log(H + 1)
        del opts['log']

    matplotlib.pyplot.contour(Hx, Hy, H, **opts)

def sparse_histogramdd(X, bins=10):
    if len(X.shape) == 1:
        X = X.reshape((X.shape[0], 1))
    m, n = X.shape
    try:
        len(bins)
    except:
        bins = [bins]*n
    bins = numpy.array(bins)
    H = {}
    mins, maxs = X.min(0), X.max(0)
    scale = (maxs - mins) * (1.0 / (bins-1))
    ranges = [numpy.linspace(dm, dM, bins[i]+1) for i, (dm, dM) in enumerate(zip(mins, maxs))]
    if hasattr(X, 'iloc'):
        X = ((X - mins) / scale).astype(int)
        for i in xrange(m):
            x = tuple(X.iloc[i])
            if x in H:
                H[x] += 1
            else:
                H[x] = 1
    else:
        for i in xrange(m):
            x = tuple(((X[i,:] - mins) / scale).astype(int))
            if x in H:
                H[x] += 1
            else:
                H[x] = 1
    return H, ranges


def bin_shift(X, bins, step):
    """Shifts X by an ammount proportional to a subdivision of its range"""
    return X + step * (X.max() - X.min()) / bins


def violin_density_plot(X, bins, vbins=100, cmap=matplotlib.cm.gray, log=True, **kwargs):
    """Violin plot of 1-d data, coupled with density information."""
    H = numpy.histogram(X, bins=bins)[0]
    if log:
        if log is True:
            H = numpy.log(H + 1)
        else:
            H = numpy.log(H + 1) / numpy.log(log)
    H2 =numpy.zeros((vbins, bins), dtype=H.dtype)
    maxh = H.max()
    b2 = vbins / 2
    for i, h in enumerate(H):
        y = min(vbins, int(h * vbins / maxh))/2
        for j in range(y):
            h2 = h - j * maxh / b2
            H2[b2-j,i] = h2
            H2[b2+j,i] = h2
        
    xmin, xmax = X.min(), X.max()
    extent = xmin, xmax, -vbins, vbins
    matplotlib.pyplot.imshow(H2, extent=extent,origin='bottom',aspect='auto', cmap=cmap, **kwargs)
    return H2

def density_contour_plot(X, Y, *args, **kwargs):
    bins = kwargs['bins']
    try:
        bins[0]
    except TypeError as te:
        bins=[bins,bins]
    density_plot(X, Y, *args, cmap=matplotlib.cm.gist_earth, **kwargs)
    X = bin_shift(X, bins[0], .5)
    Y = bin_shift(Y, bins[1], .5)
    contour_plot(X, Y, *args, cmap=matplotlib.cm.jet, **kwargs),

def violin_contour_plot(X, bins, **kwargs):
    if 'interpolation' not in kwargs:
        kwargs['interpolation'] = "nearest"
    if 'cmap' not in kwargs:
        kwargs['cmap'] = matplotlib.cm.gist_earth
    H2 = violin_density_plot(X, bins, **kwargs)
    Hx = numpy.linspace(X.min(), X.max(), bins)
    Hy = numpy.arange(-H2.shape[0]/2, H2.shape[0]/2)
    matplotlib.pyplot.contour(Hx, Hy, H2, origin='lower', aspect='auto')
