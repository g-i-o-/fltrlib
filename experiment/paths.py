import os.path
import os
import config

class paths:
    pass
paths.root = os.path.abspath(os.path.dirname(__file__))
paths.input_data = os.path.abspath(os.path.join(paths.root, 'dataset'))
paths.output_data = dict([
    (algorithm, os.path.abspath(os.path.join(paths.root, 'output_'+algorithm)))
    for algorithm in config.algorithms
])
paths.bower = os.path.abspath(os.path.join(paths.root, 'bower_components'))
paths.DATABASE = os.path.abspath(os.path.join(paths.root, 'annotations.sqlite3'))
