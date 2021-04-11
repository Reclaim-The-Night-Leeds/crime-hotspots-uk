import generic
from crime_hotspots_uk.constants import baseURL, crime_categories_url, constituincies_url, ignore
from pathlib import Path
import requests
from tqdm.auto import trange, tqdm
import geopandas as gpd
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon

class Constituincy(generic.Locations):
    """
    This class is used to hold a dataframe of constituincy boundaries and any relevant data. Any data pertaining to a perticular constituincy including demographics or political representation should be implemented here.
    """
    
    def __init__(self, name, file_name = 'constituincies.geojson', update = False):
        super()
        
        # Set the name of the class to the name passed
        self.name = name
        
        # Run the import function
        self._import_(file_name = file_name, update = update)
        
    def _import_(self, file_name, update):
        """
        Import boundary data for the constituincy
        """
        
        # Checks if it is neccesary to download new constituincy boundaries by 
        # checking if either the file name for the boundaries doesn't exist or
        # if update has been set to True'
        file_exists = Path(file_name).is_file()
        file_exists = not file_exists
        if file_exists or update:
            print('updating boundaries')
            # If it is needed to update the boundaries run the update function
            self.update_constituincy_boundaries(file_name)
            # Check that the boundaries correctly updated
            if not Path(file_name).is_file():
                print("Failed to get constituincies")
        
        # Load the geojson into a file
        self.locations = gpd.read_file(file_name)
        
        # Loop through all locations found
        for i in range(0, len(self.locations['geometry'])):
            # Convert any single polygons into multipolygons
            if type(self.locations['geometry'][i]) == Polygon:
                multi = MultiPolygon([self.locations['geometry'][i].simplify(0.01)])
            else:
                multi = []
                for j in self.locations['geometry'][i]:
                    multi.append(j.simplify(0.01))
                multi = MultiPolygon(multi)
                
            # Replace the single polygons with the multi's
            self.locations.iat[i, 9] = multi
        
    def update_constituincy_boundaries(self, file_name):
        """ This downloads ne constituincy boundary data from the `ONS GeoPortal <https://geoportal.statistics.gov.uk/datasets/5ce27b980ffb43c39b012c2ebeab92c0_2>`_ This contains the 2018 westminster parkimentary boundaries for the UK.
        
        :param file_name: What to save the downloaded constituincy boundary data as. If nothing is passed it will default to DEADBEEF and take whatever file name is stored in the file_name member variable, defaults to self.file_name
        :type file_name: string, optional
        """
        
        # Set the url to get the constituincy data to the URL in constants.py
        link = constituincies_url
        
        # Start streaming the data using python requests
        resp = requests.get(link, stream=True)
        
        # Open the file to save the data to and create a TQDM progress bar to
        # track the progress (currently the total length is set by the known
        # size but it should be moved to calculating total file size using
        # the response headers)
        with open(file_name, 'wb') as file, tqdm(
            desc=file_name,
            total=200517386,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in resp.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        file.close() # Make sure to close the file after
        
