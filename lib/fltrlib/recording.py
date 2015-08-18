from __future__ import absolute_import

import matplotlib.mlab
import contextlib

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import scikits.audiolab

class LoadingError(StandardError):
    pass

class AudioRecording:
    def __init__(self, filename):
        if type(filename) is not str and type(filename) is not unicode:
            raise ValueError("filename must be a string")
        self.filename = filename

        with contextlib.closing(scikits.audiolab.Sndfile(self.localfilename)) as f:
            self.encoding = f.encoding
            self.channels = f.channels
            self.samples = f.nframes
            self.samplerate = f.samplerate
            self.frames = f.read_frames(f.nframes,dtype=np.dtype('int16'))

        if self.samples != len(self.frames):
            raise LoadingError('CorruptedFile')
        
        if float(self.samplerate) > 192000.0:
            raise LoadingError('SamplingRateNotSupported')
        
        if self.channs > 1:
            raise LoadingError('StereoNotSupported')

        if self.samples == 0:
            raise LoadingError('NoData')

    def getSpectrogram(self, NFFT=512, noverlap=256):
        "Returns the recording's spectrogram, given some parameters"
        return pylab.mlab.specgram(
            self.frames, NFFT=NFFT, Fs=self.samplerate, noverlap=noverlap)
