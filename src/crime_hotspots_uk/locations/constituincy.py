import generic
import geopandas as gpd

class constituincy(generic.Locations):
    """
    This class is used to hold a dataframe of constituincy boundaries and any relevant data. Any data pertaining to a perticular constituincy including demographics or political representation should be implemented here.
    """
    
    def __init__(self, name):
        super().__init__(name)
    
    def _import_(self, file_name = 'constituincies.geojson', update = True):
        """
        Import boundary data for the constituincy
        """
        
        # Checks if it is neccesary to download new constituincy boundaries by 
        # checking if either the file name for the boundaries doesn't exist or
        # if update has been set to True'
        if not self.load_constituincy_boundaries() or update == True:
            print('updating boundaries')
            # If it is needed to update the boundaries run the update function
            self.update_constituincy_boundaries()
            # Check that the boundaries correctly updated
            if not self.load_constituincy_boundaries():
                print("Failed to get constituincies")
        
        
        self.locations = gpd.read_file(file_name)
        for i in range(0, len(testing['geometry'])):
            if type(testing['geometry'][i]) == Polygon:
                multi = MultiPolygon([testing['geometry'][i]])
            else:
                multi = testing['geometry'][i]
            testing.iat[i, 9] = multi
        
    def update_constituincy_boundaries(self, file_name = 'DEADBEEF'):
        """ This downloads ne constituincy boundary data from the `ONS GeoPortal <https://geoportal.statistics.gov.uk/datasets/5ce27b980ffb43c39b012c2ebeab92c0_2>`_ This contains the 2018 westminster parkimentary boundaries for the UK.
        
        :param file_name: What to save the downloaded constituincy boundary data as. If nothing is passed it will default to DEADBEEF and take whatever file name is stored in the file_name member variable, defaults to self.file_name
        :type file_name: string, optional
        """
    
    def load_constituincy_boundaries(self, file_name = 'DEADBEEF'):
        """ Load in the constituincy boundaries from a specified file.
        
        :param file_name: Path to a cached copy of the constituincies.geojson file. If nothing is passed it will default to DEADBEEF and take whatever file name is stored in the file_name member variable, defaults to self.file_name
        :type update: string, optional
        
        :return: Will return true if it managed to successfully download and validate the constituincy boundaries. If it fails to it will return false.
        :rtype: bool
        """
