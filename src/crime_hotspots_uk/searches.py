from crime_hotspots_uk.data import Root

from crime_hotspots_uk.locations.constituincy import Constituincy


class Data(Root):
    """
    This class is used to hold a dataframe of constituincy boundaries and any relevant
    data. Any data pertaining to a perticular constituincy including demographics or
    political representation should be implemented here.
    """

    def __init__(self, name, location_names, location_type=Constituincy):

        super().__init__(
            name, location_names, location_type=Constituincy, usage="search"
        )
