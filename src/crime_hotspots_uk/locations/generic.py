

class Locations:
    """
    A template class that provide a generic structure for how location should be loaded in. The implementations of the functions should be overwritten or extended by each implementation but all implementations must follow this format.
    
    This class is handler to a python dataframe that contains rows of shapely geometries that define individual areas.
    """
    def __init__(self, name):
        """
        This function is called when the class is initialised. It will set variables that will describe the data and then call the import function.
        
        :param name: What the name of collection of locations is called. For instance Leeds constituincies. This should be human readable and provide a concise explanation of what the boundaries represent.
        :type name: string 
        """
        # Set the name of the class to the name passed
        self.name = name
        
        # Run the import function
        self._import_()
        
    def _import_(self):
        """
        Downloads and import any data needed. It will then save it to a cache
        
        .. warning:: This function should always be overwritten
        """
        
        
        
    def get_area(self, location_name):
        """
        Returns a list of lists containing lon/lat coordinate pairs defining the boundaries of an area (it is a list of lists as some areas have islands and as such have to be defined by multiple boundaries) that has the name passed to this function
        
        :param location_name: Name of the location to get the data for instance `Leeds Central` for the leed central constituincy.
        :type location_name: string
        """
        
        
        
    def export(self, filename):
        """
        Export the current dataframe of locations to a .csv file
        
        :param file_name: What to save the file as
        :type file_name: string
        """
        
        
