#! .env/bin/python

import sys
import os
import os.path
import csv
import time
import fltrlib.filter
import fltrlib.segment
import fltrlib.recording

VERSION = '1.0'
DESCRIPTION = 'Analyzes and extracts audio events in the given recordings.'
ARGS = (
    ('recordings', {'metavar':'rec', 'nargs':'+', 'help':'Recordings to analyze. Can also be folders holding the recordings.'}),
    ('--version', {'action':'version', 'version':'%(prog)s '+VERSION}),
    ('-o', {'dest':'outputfile', 'default':'-', 'help':"file in wich to output the audio event segments. '-' means standard output (default -)."}),
    ('-v', {'dest':'verbose', 'type':int, 'default':1, 'help':"Level of verbosity (default:1)."})
)

def segment_one_recording(recording):
    audio_recording = AudioRecording(recording)
    spectrum, freqs, times = audio_recording.getSpectrogram()
    duration = audio_recording.samples * 1.0 / audio_recording.sample_rate  # seconds
    max_freq = audio_recording.sample_rate / 2.0
    specH, specW = spectrum.shape
    p2sec = duration / specW
    p2hz = max_freq / specH
    origin, scale = [0, 0], (p2sec, p2hz)
    roi_count = 0
    for i, roi in enumerate(fltrlib.segment.segment(spectrum)):
        roi_count += 1
        y0, x0, y1, x1 = roi.bounds
        w, h = x1 - x0 + 1, y1 - y0 + 1
        t0, t1 = x0 * p2sec, x1 * p2sec
        f0, f1 = y0 * p2hz, y1 * p2hz
        roidata = {
            'rec':rec,
            'idx':i, 'x':x0, 'y':specH-y1, 'w':w, 'h':h,
            't0':t0, 'f0':f0, 't1':t1, 'f1':f1
        }
        yield roidata, roi


def segment_recordings(recordings, outputfile, log):
    start_time = tictoc()
    log(2, "Started at {}".format(start_time))
    log(1, "Writing audio events in {}".format('stdout' if outputfile == '-' else outputfile))
    
    log(1, 'Fetching classification playlist')
    playlist = list(all_recordings_in(recordings))

    roi_stats_computer = a2audio.segmentation.stats.MultipleSCStatsCalculator([
        a2audio.segmentation.stats.FitEllipseRoiStatsCalculator(),
        a2audio.segmentation.stats.MaxPointRoiStatsCalculator(),
        a2audio.segmentation.stats.CoverageRoiStatsCalculator()
    ])
    roi_fieldnames = ['rec', 'idx', 'x', 'y', 'w', 'h', 't0', 'f0', 't1', 'f1'] + roi_stats_computer.names

    segmentation_overall_start_time = tictoc()
    roi_writer = csv.DictWriter(outputfile, fieldnames = roi_fieldnames, quoting=csv.QUOTE_NONNUMERIC)
    roi_writer.writeheader()

    for i, rec in enumerate(playlist):
        try:
            log(1, "rec #{} : {}".format(i, rec))
            for roidata, roi in segment_one_recording(recording):
                stat_time = tictoc()
                origin[1] = y0
                roidata.update(roi_stats_computer(roi, origin, scale))
                stat_time = tictoc(log, 1, "computed stats", stat_time)

                roi_writer.writerow(roidata)

            rec_time = tictoc(log, 2, "segmented recording ({} rois)".format(roi_count), rec_time)
        except :
            import traceback
            log(-1, "Error processing recording {}. traceback:{}".format(rec, traceback.format_exc()))            

    tictoc(log, 2, "Segmentation Finished", segmentation_overall_start_time)
    tictoc(log, 1, "Execution Finished", start_time)

def make_log_fn(threshold):
    def log_fn(level, msg):
        print level, threshold, "# ", msg.replace('\n','\n# ')
        if level < threshold:
            print "# ", msg.replace('\n','\n# ')
    return log_fn

def tictoc(log=None, level=0, msg='', stime=None):
    now = time.time()
    if log and  msg and stime:
        log(level, "{} - {} seconds elapsed.".format(title, now - stime))
    return now

def all_recordings_in(filelist):
    for entry in filelist:
        if os.path.isdir(entry):
            dir_files = (os.path.join(entry, f) for f in os.listdir(entry))
            for subentry in all_recordings_in(dir_files):
                yield subentry
        elif entry[-5:] == '.flac' or entry[-4:] == '.wav':
            yield entry

print "A"
if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(description=DESCRIPTION)
    for arg in ARGS:
        argparser.add_argument(arg[0], **arg[1])
        
    args = vars(argparser.parse_args())
    
    args['log'] = make_log_fn(args['verbose'])
    del args['verbose']
    
    if args['outputfile'] == '-':
        args['outputfile'] = sys.stdout
    else:
        with open(args['outputfile'], 'w') as fout:
            args['outputfile'] = fout
            segment_recordings(**args)
