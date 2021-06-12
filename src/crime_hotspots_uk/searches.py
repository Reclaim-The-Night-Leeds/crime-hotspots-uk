from crime_hotspots_uk.data import Root, locations_not_fixed_yet

from crime_hotspots_uk.locations.constituincy import Constituincy

import pandas as pd

import os

import numpy as np

from pathlib import Path


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

    def get_data(self):
        super().get_data("All crime")

        self.all_crimes["month"] = pd.to_datetime(self.all_crimes["datetime"])
        self.all_crimes["month"] = self.all_crimes["month"].dt.to_period("M")

    def cache_data(self):

        try:
            self.global_locales.empty
        except AttributeError:
            raise locations_not_fixed_yet

        location_type = self.locations.__name__

        cache = os.path.expanduser("~/.crime_hotspots_cache/" + location_type)

        areas = np.unique(self.all_crimes["area name"])

        for area in areas:
            area_mask = self.all_crimes["area name"] == area

            months = np.unique(self.all_crimes["month"])

            directory = cache + "/" + area + "/" + self.usage
            Path(directory).mkdir(parents=True, exist_ok=True)

            for month in months:
                month_mask = self.all_crimes["month"] == month
                final_mask = area_mask & month_mask

                file_name = directory + "/" + str(month) + ".csv"

                self.all_crimes[final_mask].to_csv(file_name, index=False)

    def import_cache(self, location_type, area, month, category=None):
        file_name = os.path.expanduser(
            "~/.crime_hotspots_cache/"
            + location_type
            + "/"
            + area
            + "/"
            + "stops-street"
            + "/"
            + month
            + ".csv"
        )

        if Path(file_name).is_file():
            data = pd.read_csv(file_name)
            return data
        else:
            return None
