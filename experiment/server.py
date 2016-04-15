#! .env/bin/python

import os.path
import json
import sqlite3
from flask import Flask, render_template, send_from_directory, send_file, Response, g, request
from paths import paths
from config import algorithms
import db

# configuration
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

def get_db():
    sqlite_db = getattr(g, '_sqlite_db', None)
    if sqlite_db is None:
        sqlite_db = g._sqlite_db = db.get_db()
    return sqlite_db

def query_db(query, args=(), one=False, commit=False):
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if commit:
        conn.commit()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_sqlite_db', None)
    if db is not None:
        db.close()

@app.route("/static/<path:path>")
def get_static(path):
    return send_from_directory('static', path)

@app.route("/bower_components/<path:path>")
def get_bower(path):
    return send_from_directory(paths.bower, path)


@app.route("/") # take note of this decorator syntax, it's a common pattern
def main_app():
    return render_template('index.html')


@app.route("/recording/list")
def get_recordings_list():
    return send_from_directory(paths.input_data, 'recs.json')

@app.route("/recording/<recname>/image/<algorithm>/<imagetype>.png")
def get_recording_image(recname, algorithm, imagetype):
    ending = imagetype + '.png'
    for i in os.listdir(paths.output_data[algorithm]):
        if i.startswith(recname):
            if i[-len(ending):] == ending:
                print i
                return send_from_directory(paths.output_data[algorithm], i)

@app.route("/recording/<recname>/output/<algorithm>")
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
    return json.dumps(info)


@app.route("/recording/<recid>/validation")
def get_recording_validation(recid):
    with open(os.path.join(paths.input_data, 'roi-set.json'), 'r') as froi:
        vdata = json.load(froi)
    return Response(json.dumps([
        {'idx':roi['id'], 'f0':roi['y1'], 'f1':roi['y2'], 't0':roi['x1'], 't1':roi['x2']}
        for roi in vdata
        if int(roi['recording']) == int(recid)
    ]), mimetype='application/json')

@app.route("/recording/<recid>/annotation/<algorithm>", methods=['POST'])
def post_recording_annotation(recid, algorithm):
    label = request.get_json().get('label')
    if label:
        print label
        query_db('INSERT INTO annotations (rec, x, y, annotation, algorithm) VALUES (?, ?, ?, ?, ?)', [
            recid, label.get('t'), label.get('f'), label.get('text'), algorithm
        ], commit=True)
    return Response('{"status":"ok"}', mimetype='application/json')

@app.route("/recording/<recid>/annotation/<algorithm>/list")
def get_recording_annotation(recid, algorithm):
    annots = query_db('SELECT x as t, y as f, annotation as text FROM annotations WHERE rec = ? AND algorithm = ?', [
        recid, algorithm
    ])
    return Response(json.dumps(annots), mimetype='application/json')


@app.route("/algorithms") # take note of this decorator syntax, it's a common pattern
def get_algorithms():
    return Response(json.dumps(algorithms), mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
