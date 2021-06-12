from crime_hotspots_uk.locations import generic

from pyparliment.members.location import find

import pandas as pd


class Constituincy(generic.Locations):
    """
    This class is used to hold a dataframe of constituincy boundaries and any relevant
    data. Any data pertaining to a perticular constituincy including demographics or
    political representation should be implemented here.
    """

    def __init__(self, names, title):
        """
        Initialise the class and import data

        :param names: A list of strings containing names of constituincies to search for
        :type name: list
        :param title: A string representing what area the constiuincies represent. For
            instance `London Mayoral Constituincies`
        :type title: string

        The init function will get all constituincies with names starting with any of
        the items in names.
        """

        super()

        # Set the name of the class to the name passed
        self.title = title

        # Create a template list to contain the areas
        self.locations = []

        # Loop over all the names passed and import each of them
        for name in names:
            self.locations.append(find.search(name))

        # Concatanate the dataframes into one big dataframe of all the areas
        self.locations = pd.concat(self.locations)
        
        self.locations.columns = ['ID',
                                  'Name',
                                  'Representative ID',
                                  'Representative Name',
                                  'Affiliation',
                                  'Gender',
                                  'Status',
                                  'Start Date',
                                  'shapes']
        
        self.__name__ = 'Constituincy'
        
