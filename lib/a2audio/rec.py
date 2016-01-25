import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from scikits.audiolab import Sndfile
import contextlib
import numpy
from pylab import *
import matplotlib.mlab
import pylab
import numpy

class Recording:
    storage = None
    filename = None
    samples = None
    sample_count = 0
    sample_rate = 0
    channels = 0

    def __init__(self, filename, storage):
        if type(filename) not in (str, unicode):
            raise ValueError("filename must be a string")

        self.storage = storage
        self.filename = storage.get_file_uri(filename)
        self.samples = []
            
        self.process()
        
    def process(self):
        if not self.readAudioFromFile():
            raise IOError('CorruptedFile')
        
        if self.sample_count == 0:
            raise IOError('NoData')
        
        if self.sample_count != len(self.samples):
            raise IOError('CorruptedFile')
          
    def readAudioFromFile(self):
        with contextlib.closing(Sndfile(self.filename)) as f:
            self.channels = f.channels
            self.sample_count = f.nframes
            self.sample_rate = f.samplerate
            self.samples = f.read_frames(f.nframes,dtype=numpy.dtype('int16'))
        return True

    def getSpectrogram(self, NFFT=512, noverlap=256, channel=0):
        "Returns the recording's spectrogram, given some parameters"
        data = self.samples if self.channels == 1 else self.samples[:,channel]
        return matplotlib.mlab.specgram(
            data, NFFT=NFFT, Fs=self.sample_rate, noverlap=noverlap)
