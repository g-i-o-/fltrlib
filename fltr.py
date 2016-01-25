#! .env/bin/python

import sys
import os
import os.path
import csv
import lib.storage
import a2audio.segmentation
import a2audio.rec


USAGE = """Runs a ROI Pattern extraction and categorization job.
{prog} recs_folder outfolder
    recs_folder - folder with recordings to analyze
    outfolder - folder with output results
"""

def log_write(*args):
    print args[0]
    
def main(recs_folder, outfolder, *meh):
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    output_storage = lib.storage.LocalStorage(outfolder)
    input_storage = lib.storage.LocalStorage(recs_folder)
    
    if not input_storage.exists():
        log_write('fatal error: recordings storage does not exist.')
        quit()

    if output_storage.exists():
        log_write('storing in : ' + repr(output_storage))
    else:
        log_write(repr(output_storage) + ' does not exists and could not be created.')
        quit()

    log_write('fetching recording set..')

    def has_extensions(*extensions):
        return lambda file: file.split('.')[-1].lower() in extensions

    playlist = input_storage.get_file_list(filter=has_extensions('flac', 'wav'))


    stype = "flattened-trimmed-local-range"
    segmenter = a2audio.segmentation.AudioSegmenter.instantiate(stype)

    log_write('started fltr segmentation on data set')

    roi_stats_computer = a2audio.segmentation.stats.MultipleSCStatsCalculator([
        a2audio.segmentation.stats.FitEllipseRoiStatsCalculator(),
        a2audio.segmentation.stats.MaxPointRoiStatsCalculator(),
        a2audio.segmentation.stats.CoverageRoiStatsCalculator()
    ])

    roi_fieldnames = ['rec', 'idx', 'x', 'y', 'w', 'h', 't0', 'f0', 't1', 'f1'] + roi_stats_computer.names

    with output_storage.open_for_writing('rois.txt') as output_file:
        roi_writer = csv.DictWriter(output_file, fieldnames = roi_fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        roi_writer.writeheader()

        for i, rec in enumerate(playlist):
            roi_count = 0
            try:
                print "rec #{} : {}".format(i, rec)
                recording = a2audio.rec.Recording(rec, storage=input_storage)
                spectrum, freqs, times = recording.getSpectrogram()
                rec_output_storage = None

                duration = recording.sample_count * 1.0 / recording.sample_rate  # seconds
                max_freq = recording.sample_rate / 2.0
                specH, specW = spectrum.shape
                p2sec = duration / specW
                p2hz = max_freq / specH
                origin, scale = [0, 0], (p2sec, p2hz)

                for i, roi in enumerate(segmenter.segment(
                    spectrum, storage=rec_output_storage,
                    sample_rate=recording.sample_rate
                )):
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
                    origin[1] = y0
                    roidata.update(roi_stats_computer(roi, origin, scale))

                    roi_writer.writerow(roidata)

            except StandardError as e:
                if isinstance(e, KeyboardInterrupt):
                    raise
                import traceback
                print "--------\nError processing recording {}".format(rec)
                traceback.print_exc()
                print "--------"
            log_write("    ({} rois found)".format(roi_count))


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print USAGE.format(prog=sys.argv[0])
        sys.exit(-1)

    main(*[x.strip("'") for x in sys.argv[1:]])
