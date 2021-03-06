# -*- coding: utf-8 -*-
#
# Bounding Box Editor and Exporter (BBoxEE)
# Author: Peter Ersts (ersts@amnh.org)
#
# --------------------------------------------------------------------------
#
# This file is part of Animal Detection Network's (Andenet)
# Bounding Box Editor and Exporter (BBoxEE)
#
# BBoxEE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BBoxEE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# --------------------------------------------------------------------------
import os
import sys
import json
import glob
import pyodbc
import datetime
import numpy as np
from PIL import Image
from tqdm import tqdm
import tensorflow as tf


def build_label_map(file_name):
    # see if we can use this to eliminated the need for
    # label_map_util dependency
    a = open(file_name, 'r')
    string = a.read()
    a.close()
    lines = string.split("\n")
    parsed = ''
    comma = ''
    for line in lines:
        if line == '':
            pass
        elif line.find('item') != -1:
            parsed += '{'
        elif line.find('}') != -1:
            comma = ''
            parsed += '},'
        else:
            parts = line.replace('\\', '').replace('\'', '"').split(':')
            parsed += '{} "{}":{}'.format(comma, parts[0].lstrip(), parts[1])
            comma = ','

    string = "[{}]".format(parsed[0:-1])
    j = json.loads(string)
    label_map = {}
    for entry in j:
        if 'display_name' in entry:
            label_map[entry['id']] = entry['display_name']
        else:
            label_map[entry['id']] = entry['name']
    return label_map


if 'Microsoft Access Driver (*.mdb, *.accdb)' not in pyodbc.drivers():
    print('No Microsoft Access Driver found.')
    sys.exit(0)

print('----------------------------------------------------------------------------')
print('DO NOT RUN THIS SCRIPT ON YOUR MAIN DATABASE WITHOUT CREATING A BACKUP FIRST!')
print('----------------------------------------------------------------------------')
print()
print()
print('Example database path: c:\\database\\import-test.accdb')
print()
# Ask for database file and open
database = input("Enter the path and file name of your database: ")
try:
    conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + database)
    cur = conn.cursor()
except pyodbc.Error:
    print('Unable to open database.')
    sys.exit(0)

# Load species list
SPECIES = {}
results = cur.execute('Select SpeciesID, CommonName from Species').fetchall()
for rec in results:
    SPECIES[rec[1].lower()] = rec[0]
if "none" not in SPECIES:
    print('"None" label is missing from the species list')
    sys.exit(0)

# Ask for labelmap file
label_map_file = input('Enter the path and file name of your label map: ')
label_map_file = os.path.abspath(label_map_file)
LABEL_MAP = build_label_map(label_map_file)

# Check species labels match
print('Verifing species names...')
for label in LABEL_MAP:
    if LABEL_MAP[label].lower() not in SPECIES:
        print("Species list in the database does not contain [{}]".format(LABEL_MAP[label]))
        sys.exit(0)
print()

# Ask for the saved model
model_dir = input('Enter the path and file name of your saved model: ')
print('Loading model...')
MODEL = tf.saved_model.load(model_dir)
print()

# Get detection threshold
value = input('Enter the confidence threshold (0.1 to 1.0): ')
THRESHOLD = float(value)
if THRESHOLD == 0.0:
    print('Invalid threshold value.')
    sys.exit(0)

# Ask for image folder
IMAGE_PATH = input('Enter the path and folder name with your images: ')
IMAGE_PATH = os.path.abspath(IMAGE_PATH) + os.sep
print()

# Load observers and ask for ID number
observers = {}
results = cur.execute('Select ObserverID, LastName, FirstName from Observers').fetchall()
for rec in results:
    observers[str(rec[0])] = '{}, {}'.format(rec[1], rec[2])
    print('{}: {},{}'.format(rec[0], rec[1], rec[2]))
OBSID = input('Which ObserverID should the data be associated with? ')
if OBSID not in observers:
    print('That ObserverID is not recognized')
    sys.exit(0)
print()

# Load VisitIDs
# TODO: Make just one SQL statement(?)
# Pull StudyAreas data, StudyAreaID, StudyAreaName
study_area = {}
results = cur.execute('select StudyAreaID, StudyAreaName from StudyAreas').fetchall()
for rec in results:
    study_area[rec[0]] = rec[1]
# Pull CameraLocations data, LocationID, StudyAreaID, LocationName
locations = {}
results = cur.execute('select LocationID, StudyAreaID, LocationName from CameraLocations').fetchall()
for rec in results:
    locations[rec[0]] = (rec[1], rec[2])
# Pull Visits data, VisitID, LocationID, VisitTypeID=2 (Pull) order by VisitDate
visit_type = {1: 'Check', 2: 'Pull'}
visit_id_list = []
results = cur.execute('select VisitID, LocationID, VisitDate, VisitTypeID from Visits where VisitTypeID = 2 or VisitTypeID = 1 order by VisitDate asc').fetchall()
for rec in results:
    visit_id_list.append(str(rec[0]))
    print('{}: {} - {} [{}] ({})'.format(rec[0], study_area[locations[rec[1]][0]], locations[rec[1]][1], rec[2], visit_type[rec[3]]))
VISITID = input('Which VisitID should the data be associated with? ')
if VISITID not in visit_id_list:
    print('That VisitID is not recognized')
    sys.exit(0)

# Get all image files
files = glob.glob(os.path.join(IMAGE_PATH, '*'))
image_format = [".jpg", ".jpeg", ".png"]
f = (lambda x: os.path.splitext(x)[1].lower() in image_format)
image_list = list(filter(f, files))
image_list = [os.path.basename(x) for x in image_list]
image_list = sorted(image_list)

# Import data
counter = 1
for name in tqdm(image_list):
    file_name = os.path.join(IMAGE_PATH, name)
    img = Image.open(file_name)
    image_np = np.array(img)
    exif = img.getexif()
    img.close()
    created = exif.get(36867)
    if created is None:
        timestamp = None
    else:
        timestamp = datetime.datetime.fromisoformat(created.replace(':', '-', 2))
    cur.execute('INSERT INTO Photos (ImageNum, FileName, ImageDate, FilePath, VisitID) VALUES (?, ?, ?, ?, ?)', (counter, name, timestamp, IMAGE_PATH, VISITID))
    conn.commit()
    image_rec_id = float(cur.execute('SELECT @@Identity').fetchone()[0])
    counter += 1

    # Expand dimensions since the model expects images
    # to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    dets = MODEL(image_np_expanded)
    scores = dets['detection_scores'][0].numpy()
    boxes = dets['detection_boxes'][0].numpy()
    classes = dets['detection_classes'][0].numpy()
    detection = False
    detections = {}
    for index, score in enumerate(scores):
        if score >= THRESHOLD:
            detection = True
            bbox = boxes[index]
            xmin = float(bbox[1])
            xmax = float(bbox[3])
            ymin = float(bbox[0])
            ymax = float(bbox[2])
            class_number = int(classes[index])
            label = LABEL_MAP[class_number]
            XLen = xmax - xmin
            YLen = ymax - ymin
            TagX = xmin + (XLen / 2.0)
            TagY = ymin + (YLen / 2.0)
            cur.execute('INSERT INTO PhotoTags (TagX, TagY, XLen, YLen, ImageID, ObsID) values (?, ?, ?, ?, ?, ?)', (TagX, TagY, XLen, YLen, image_rec_id, OBSID))
            if label not in detections:
                detections[label] = 1.0
            else:
                detections[label] += 1.0

    if detection:
        for d in detections.keys():
            cur.execute('INSERT INTO Detections (SpeciesID, Individuals, ObsID, ImageID) values (?, ?, ?, ?)', (SPECIES[d.lower()], detections[d], OBSID, image_rec_id))
    else:
        cur.execute('INSERT INTO Detections (SpeciesID, Individuals, ObsID, ImageID) values (?, ?, ?, ?)', (SPECIES['none'], 0.0, OBSID, image_rec_id))
    conn.commit()
