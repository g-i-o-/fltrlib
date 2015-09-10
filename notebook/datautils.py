import numpy
import scipy.signal


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5, passes=1):
    if passes == 0:
        return data
    if passes > 1:
        data = butter_bandpass_filter(data, lowcut, highcut, fs, order, passes-1)
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = scipy.signal.lfilter(b, a, data)
    return y
    
    
def clip_pad_and_draw_rgb_bounds(X, x0, x1, y0, y1, pad, color):
    h,w = X.shape
    m, M = X.flatten().min(), X.flatten().max()
    px0, px1, py0, py1 = max(x0-pad, 0), min(x1+pad, w-1), max(y0-pad, 0), min(y1+pad, h-1)
    roi = 255 * (1 - (X[py0:py1,px0:px1] - m ) / (M - m))**.5
    rH, rW = roi.shape
    roiRGB = numpy.zeros((rH,rW,3), dtype=numpy.uint8)
    x0, x1, y0, y1= x0-px0, x1-px0, y0-py0, y1-py0
    for ch in range(3):
        roiRGB[:,:,ch] = roi
        roiRGB[y0,x0:(x1+1),ch] *= color[ch]
        roiRGB[y1,x0:(x1+1),ch] *= color[ch]
        roiRGB[(y0+1):(y1),x0,ch] *= color[ch]
        roiRGB[(y0+1):(y1),x1,ch] *= color[ch]
    
    return roiRGB