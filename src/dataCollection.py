import numpy as np
import pandas as pd

from pathlib import Path

import gmaps

from tqdm.notebook import tnrange, tqdm

import requests
from pandas import json_normalize
import json

from datetime import date, timedelta

import seaborn as sns
from matplotlib import pyplot as plt

from math import isclose, sqrt

from scipy import stats

import sys

from shapely.geometry import shape, GeometryCollection, Polygon, box, LineString, Point
from shapely.ops import split
from scipy.spatial import Voronoi, voronoi_plot_2d

class reclaim:
    def __init__(self, update = True, file_name = 'constituincies.geojson'):
        self.file_name = file_name
    
    def update_constituincy_boundaries(self, file_name = self.file_name):
        link = 'https://opendata.arcgis.com/datasets/b64677a2afc3466f80d3d683b71c3468_0.geojson'
    
        with open(file_name, "wb") as f:
            print("Downloading %s" % file_name)
            response = requests.get(link, stream=True)
            print("Request sent")
            total_length = response.headers.get('content-length')
    
            if total_length is None: # no content length header
                Print("Done")
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                    sys.stdout.flush()
                
    def load_constituincy_boundaries(self, file_name = self.file_name):
        if Path(file_name).is_file():
            with open(file_name) as f:
                self.gj = json.load(f)["features"]
        else:
            print('file does not exist')
    
   






### GET, SET AND CLEAR FUNCTIONS ###
    def get_file_name(self):
        return self.file_name

### UTILITY FUNCTIONS ###
    