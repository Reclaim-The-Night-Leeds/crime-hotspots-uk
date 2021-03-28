import numpy as np
import pandas as pd

from pathlib import Path

from tqdm.auto import trange, tqdm

import requests
from pandas import json_normalize
import json

from datetime import date, timedelta

import seaborn as sns
from matplotlib import pyplot as plt

from math import sqrt

from scipy import stats

import sys

from shapely.geometry import shape, GeometryCollection, Polygon, box, LineString, Point
from shapely.ops import split
from scipy.spatial import Voronoi, voronoi_plot_2d

ignore = ['On or near Parking Area',
		  'On or near Shopping Area',
		  'On or near Sports/recreation Area',
		  'On or near Supermarket',
		  'On or near Petrol Station',
		  'On or near Nightclub',
		  'On or near Pedestrian Subway',
		  'On or near Further/higher Educational Building',
		  'On or near Bus/coach Station',
		  'On or near Hospital',
		  'On or near Conference/exhibition Centre',
		  'On or near Theatre/concert Hall',
		  'On or near Police Station']

class Reclaim:
	def __init__(self, update = False, file_name = 'constituincies.geojson'):
		self.file_name = file_name
		
		if not self.load_constituincy_boundaries() or update == True:
			print('updating boundaries')
			self.update_constituincy_boundaries()
			if not self.load_constituincy_boundaries():
				print("Failed to get constituincies")
		
		self.constituincies = []
		
		for i in range(0,len(self.gj)):
			self.constituincies.append(self.gj[i]['properties']['pcon18nm'])
			
		url = "https://data.police.uk/api/crime-categories?date=2011-08"
		payload={}
		files={}
		headers = {}
		response = requests.request("GET", url, headers=headers, data=payload, files=files)
		
		self.crime_types = {}
		for i in response.json():
			self.crime_types[i['name']] = i['url']
		
	def update_constituincy_boundaries(self, file_name = 'DEADBEEF'):
		if file_name == 'DEADBEEF':
			file_name = self.file_name
		
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
			f.close()
				
	def load_constituincy_boundaries(self, file_name = 'DEADBEEF'):
		if file_name == 'DEADBEEF':
			file_name = self.file_name
		if Path(file_name).is_file():
			with open(file_name) as f:
				try:
					self.gj = json.load(f)["features"]
				except json.JSONDecodeError:
					print('Corrupted .geojson file returning false')
					return False
			return True
		else:
			print('file does not exist')
			return False
		
	def get_data(self, constituincies, start_date, end_date, crime_type):
		boundaries = {}
		for i in constituincies:
			if i not in self.constituincies:
				print('Unknown constituincy')
				return False
			else:
				for j in range(0,len(self.gj)):
					if self.gj[j]['properties']['pcon18nm'] == i:
						boundaries[i] = self.gj[j]['geometry']['coordinates']
						
		
		self.areas = {}
		
		for i in boundaries:
			temp = []
			if len(boundaries[i]) == 1:
				temp.append(Polygon(boundaries[i][0]).simplify(0.01))
				
			else:
				for j in range(0, len(boundaries[i])):
					if len(boundaries[i][j]) == 1:
						temp.append(Polygon(boundaries[i][j][0]).simplify(0.01))
					else:
						temp.append(Polygon(boundaries[i][j]).simplify(0.01))
			temp_fishneted = []
			for j in range(0, len(temp)):
				temp_fishneted.append(GeometryCollection(self.fishnet(temp[j], 0.05)))
			
			self.areas[i] = temp_fishneted
		
		if crime_type not in self.crime_types.keys():
			print('Unkown crime type')
			return False
		
		crimes = []
		
		for i in tqdm(self.areas, desc = "Constituincy"):
			for j in tqdm(self.areas[i], leave=False, desc = "Area"):
				for self.k in tqdm(j, leave = False, desc = "Sub section"):
					temp = self.get_crimes(self.k.exterior.coords, self.crime_types[crime_type], i)
					if isinstance(temp, pd.DataFrame):
						crimes.append(temp)
		self.all_crimes = pd.concat(crimes)
	
	def get_crimes(self, coords, crimeType, constituincy):
	
		location = ''
		for i in range(0,len(coords)):
			temp = str(coords[i][1])[0:9] + "," + str(coords[i][0])[0:9] + ":"
			location = location + temp
		
		location = location[:-1]
	
	
		start_date = date(2018,2,1)   # start date
		end_date = date(2021,2,1)   # end date
	
		dates = pd.date_range(start_date,
							  end_date-timedelta(days=1),
							  freq='MS').strftime("%Y-%m").tolist()
	
		baseURL = "https://data.police.uk/api/crimes-street/"
	
		crime_jsons = []
	
		for i in tqdm(dates, leave = False, desc = "Months"):
			url = baseURL + crimeType + "?poly=" + location + "&date=" + str(i)
			payload={}
			headers = {}
		
			if(len(url) > 4096):
				print("url too long")
			response = requests.request("GET", url, headers=headers, data=payload)
			if(response.status_code == 429):
				print("-" * 10)
				print("ERROR: response code 429, too many requests")
				print("URL was:", url)
				print("Doccumentation at: https://data.police.uk/docs/api-call-limits/")
			elif(response.status_code == 503):
				print("-" * 10)
				print("ERROR: response code 503, more than 10,000 crimes in area")
				print("URL was:", url)
				print("Doccumentation at: https://data.police.uk/docs/method/crime-street/")
			elif(response.status_code == 200):
				crime_jsons.append(json_normalize(json.loads(response.text)))
			else:
				print("-" * 10)
				print("ERROR: unkown response code")
				print("URL was:", url)
				print("response code: ", response.status_code)
		crimes = pd.concat(crime_jsons)
		
		if crimes.shape[0] > 0:
		
			crimes['location.latitude'] = pd.to_numeric(crimes['location.latitude'])
			crimes['location.longitude'] = pd.to_numeric(crimes['location.longitude'])
			crimes['location.street.name'] = crimes['location.street.name'] + " - " +str(constituincy)
			
			crimes.reset_index(inplace = True)
			crimes.drop(['index', 'context', 'category'], axis = 1, inplace = True)
		
			return crimes
		else:
			return
		return
	
	def fix_locations(self):
		# Create a global list of all possible locations in the UK
		self.global_locales = self.all_crimes[['location.street.name',
									  'location.latitude',
									  'location.longitude',
									  'constituincy',
									  'pretty name']]
		self.global_locales = self.global_locales[~self.global_locales['location.street.name'].str.contains('|'.join(ignore))]
		self.global_locales.drop_duplicates(subset = ['pretty name'], inplace = True)
		self.global_locales.reset_index(inplace = True, drop = True)
		
		modified_crimes = self.all_crimes
		self.test = []
		for i in trange(0, modified_crimes.shape[0]):
			street = modified_crimes.iloc[i][7]
			
			for x in ignore:
				if x in street:
					#print(street)
					locales = self.global_locales.loc[self.global_locales['constituincy'] == modified_crimes.iloc[i][12]]
					local_lat = modified_crimes.iloc[i][5]
					local_lon = modified_crimes.iloc[i][8]
					min_distance = 1000000
					min_distance_index = -1
					for j in range(0, locales.shape[0]):
						point_lat = locales.iloc[j][1]
						point_lon = locales.iloc[j][2]
						distance = sqrt((local_lat - point_lat)**2 + (local_lon - point_lon)**2)
						if distance < min_distance:
							min_distance = distance
							min_distance_index = j
					new_street = locales.iloc[min_distance_index][0]
					#modified_crimes.iat[i, 11] = new_street + ' - ' + modified_crimes.iloc[i][12]
					self.all_crimes.iat[i, 11] = new_street + ' - ' + modified_crimes.iloc[i][12]
					self.all_crimes.iat[i, 7] = new_street
					#print(modified_crimes.iat[i, 11])
					self.test.append(i)
					
		#self.all_crimes = modified_crimes
		#print(modified_crimes.iat[self.test[0], 11])
		#print(self.all_crimes.iat[self.test[0], 11])
	
	
	
	### GET, SET AND CLEAR FUNCTIONS ###
	def get_file_name(self):
		return self.file_name
	
	def set_file_name(self, file_name):
		self.file_name = file_name
	
	def get_constituincies(self):
		return self.constituincies
	
	def get_crime_types(self):
		return self.crime_types
	
	
	### UTILITY FUNCTIONS ###
	def fishnet(self, geometry, threshold):
		bounds = geometry.bounds
		xmin = int(bounds[0] // threshold)
		xmax = int(bounds[2] // threshold)
		ymin = int(bounds[1] // threshold)
		ymax = int(bounds[3] // threshold)
		ncols = int(xmax - xmin + 1)
		nrows = int(ymax - ymin + 1)
		result = []
		for i in range(xmin, xmax+1):
			for j in range(ymin, ymax+1):
				b = box(i*threshold, j*threshold, (i+1)*threshold, (j+1)*threshold)
				g = geometry.intersection(b)
				if g.is_empty:
					continue
				result.append(g)
		return result
