#! .env/bin/python

import os
import os.path
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import paths
import config
import db

dbconn = db.get_db()

def query_db(query, args=(), one=False, commit=False):
    cur = dbconn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if commit:
        conn.commit()
    return (rv[0] if rv else None) if one else rv

def get_recordings():
    "Fetches the recordings from the json file"
    with open(os.path.join(paths.input_data, 'recs.json')) as finp:
        return json.loads(finp.read())

def get_validations(recordings):
    with open(os.path.join(paths.input_data, 'roi-set.json')) as finp:
        return json.loads(finp.read())

def get_recording_output(recname, algorithm):
    info={'images':[]}
    for i in os.listdir(paths.output_data[algorithm]):
        if i.startswith(recname):
            itemname=i[len(recname) : ]
            if itemname[0] == '-':
                itemname = itemname[1:]
            tag = algorithm + '-' # 'flattened-trimmed-local-range-'
            if itemname.startswith(tag):
                itemname = itemname[len(tag):]
            if itemname[-4:] == '.png':
                info['images'].append(itemname[:-4])
            elif itemname[-9:] == 'rois.json':
                with open(os.path.join(paths.output_data[algorithm], i), 'r') as frois:
                    info['rois'] = json.load(frois)
    return info

def get_annotations(rec_id, algorithm):
    return query_db('SELECT x as t, y as f, annotation as text FROM annotations WHERE rec = ? AND algorithm = ?', [
        rec_id, algorithm
    ])

def find_closest_annotation(droi, annotations):
    min_dist, min_ann = 0, None
    t0, t1, f0, f1 = droi['t0'], droi['t1'], droi['f0'], droi['f1']
    mt, mf = (t1+t0)/2, (f1+f1)/2
    mw, mh = (t1-t0)/2, (f1-f0)/2
    for ann in annotations:
        dt, df = (ann['t'] - mt) / mw, (ann['f'] - mf) / mh
        dist = (dt*dt + df*df)**.5
        if not min_ann or dist < min_dist:
            min_dist = dist
            min_ann  = ann
    return min_ann

recs = get_recordings()
for vroi in get_validations(recs):
    rec_id = str(vroi['recording'])
    if rec_id in recs:
        rec = recs[rec_id]
        if 'vals' not in rec:
            rec['vals'] = []
        rec['vals'].append(vroi)



algorithm = config.algorithms[1]
for rec_id, rec in recs.items()[:1]:
    annotations = get_annotations(rec_id, algorithm)
    # print annotations
    
    output = get_recording_output(rec['file'], algorithm)
    for droi in output['rois']:
        ann = find_closest_annotation(droi, annotations)
        print droi, ann
