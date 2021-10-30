"""
This module is used to download and analyse data from the data.police.uk API.
"""

import pandas as pd
from pandas import json_normalize

from tqdm.auto import trange, tqdm

import requests
import json

import os
import numpy as np
from pathlib import Path

from datetime import date, timedelta
import dateutil

import seaborn as sns
from matplotlib import pyplot as plt
from textwrap import wrap

from math import sqrt

from shapely.geometry import Polygon, box, MultiPolygon

from .constants import (
    baseURL,
    crime_categories_url,
    ignore,
)
from .locations.constituincy import Constituincy

from pyreadstat import write_sav


class Root:
    """This class handles all downloading and processing of the data."""

    def __init__(
        self,
        name,
        location_names,
        location_type=Constituincy,
        usage="crime",
    ):
        """This function initiates the class

         It does this by downloading the location boundaries and crime type
         options from the `UK Police API <https://data.police.uk/docs/>`_.

        :param usage: Wether to get crime data or stop and search data from the
            police API. If 'crime' is passed the class will use the `Street
            level crimes <https://data.police.uk/docs/method/crime-street/>`_
            method, if search is passed it will use the `Stop and searches by
            area <https://data.police.uk/docs/method/stops-street/>`_ method.
        :type usage: string, optional

        :raise AssertionError: This error is raised if the string passed to
            usage is not 'crime' or 'search'.
        """

        # Set the file_name member variable to the passed file name
        self.name = name

        # Set the usage member variable depending on the passed usage, this
        # variable is directly used to set the URL and should not be changed
        # If the passed usage is not either 'crime' or 'search' an assertation
        # error is raised
        if usage == "crime":
            self.usage = "crimes-street"
        elif usage == "search":
            self.usage = "stops-street"
        else:
            assert False, 'usage argument should be either "crime" or "search"'

        self.locations = location_type(location_names, name)
        temp = self.locations.locations["shapes"].apply(self.fix_polygons)
        self.locations.locations["shapes"] = temp
        self.locations.locations.reset_index(drop=True, inplace=True)

        # Update the local list of potential crime types by pulling from
        # https://data.police.uk/docs/method/crime-categories/
        url = crime_categories_url
        payload = {}
        files = {}
        headers = {}
        response = requests.request(
            "GET", url, headers=headers, data=payload, files=files
        )

        # Create a dictionary of the possible crime types and their names
        self.crime_types = {}
        for i in response.json():
            self.crime_types[i["name"]] = i["url"]

    def get_data(self, crime_type):
        """Download data for a specified crime type.

        This is also used to download stop and search data. To do so make sure
        self.usage has been set previously.

        :param crime_type: The crime type to download the data for. It must be
            one of the types listed in self.crime_types, it should be the
            readable name (without any -/_) The full explanation of what each
            category is can be infered from the `Police website <https://www.police.uk/pu/contact-the-police/what-and-how-to-report/what-report/>_` # noqa e501
        :type crime_type: string, required

        :return: Will return true if it managed to successfully download and
            validate the data. If it fails to it will return false.
        :rtype: bool
        """

        # Check if the crime type is valide then set the crime type to a member
        # variable so it can later be used to anotate graphs
        assert crime_type in self.crime_types.keys()
        self.crime_type = crime_type

        # Create a list to hold all the crime data once its downloaded
        crimes = []

        # Loop through all the areas
        for area in tqdm(self.locations.locations.index, desc="Areas"):
            for polygon in tqdm(
                self.locations.locations["shapes"].iloc[area],
                desc="Polygons",
                leave=False,
            ):
                # Get the crimes for the current Area
                temp = self.get_crimes(
                    polygon.exterior.coords,
                    self.locations.locations["Name"][area],
                )

                # If the data that is retrieved is a dataframe then append it
                # to the list of crime dataframes
                if isinstance(temp, pd.DataFrame):
                    crimes.append(temp)
                else:
                    print("No incidents found")

        # Convert the list of crime dataframes to one big dataframe
        self.all_crimes = pd.concat(crimes)

        # If you have reached here the function was executed successfully
        return True

    def get_crimes(self, coords, name):
        """Download all crimes of a specific type within a boundary

        :param coords: A two deep list containing latitude and longitude
            coordinate pairs
        :type coords: list
        :param name: The name of the area the data is for, this
            name will be appended as a column to the output dataframe to ensure
            that each area can be selected individualy
        :type coords: string

        :return: Returns either a pandas dataframe if the data retireval was
            successfull or NONE if it wasn't
        :rtype: pandas.dataframe
        """

        # Create an empty string that will be used to send the coordinates in
        # the API request
        location = ""

        # Loop through all the coordinate pairs
        for i in range(0, len(coords)):
            # Add each coordinate pair to the API request string
            temp = str(coords[i][1])[0:9] + "," + str(coords[i][0])[0:9] + ":"
            location = location + temp

        # Remove the traling `:` from the request
        location = location[:-1]

        # Set the start and end date fo the request
        end_date = date.today() - dateutil.relativedelta.relativedelta(months=1)
        start_date = end_date - dateutil.relativedelta.relativedelta(months=37)

        # Create a list of dates that can be added to the API request
        dates = (
            pd.date_range(start_date, end_date - timedelta(days=1), freq="MS")
            .strftime("%Y-%m")
            .tolist()
        )

        # Create an empty list to hold the returned JSONS of the crime data
        crime_jsons = []
        imports = []
        fail_count = 0

        # Loop through the list of dates
        for current_date in tqdm(dates, leave=False, desc="Months"):

            imported = self.import_cache(
                self.locations.__name__,
                name,
                current_date,
                self.crime_types[self.crime_type],
            )

            if imported is None:
                # Generate the URL to be sent by using the URL gen function
                url = self.url_gen(location, current_date)

                # No payload or headers are required for the request
                payload = {}
                headers = {}

                # The police API only accepts requests shorter than 4096 characters
                if len(url) > 4094:
                    print("url too long")
                    return

                # Send the request and save the response
                response = requests.request(
                    "GET", url, headers=headers, data=payload)

                # Check to see if the response code was correct (200), if it wasn't
                # print out a warning message and return NONE
                if response.status_code == 404:
                    fail_count += 1
                elif response.status_code != 200:
                    raise http_error_code(response.status_code, url)
                else:
                    # If the response code was 200 add the JSON ro the list of data
                    crime_jsons.append(json_normalize(
                        json.loads(response.text)))
            else:
                imports.append(imported)

        print(f"Failed to import {fail_count} months")

        # Convert the list of data to a dataframe
        if len(crime_jsons) > 0:
            crimes_downloaded = pd.concat(crime_jsons)
        else:
            crimes_downloaded = None

        if len(imports) > 0:
            crimes_imported = pd.concat(imports)
        else:
            crimes_imported = None

        if crimes_downloaded is None and crimes_imported is None:
            return
        elif crimes_downloaded is None and crimes_imported is not None:
            crimes = crimes_imported
        elif crimes_downloaded is not None and crimes_imported is None:
            crimes = crimes_downloaded
        else:
            crimes = pd.concat([crimes_downloaded, crimes_imported])

        # If data was found ensure the dataframe is formatted correctly, if not
        # return NONE
        if crimes.shape[0] > 0:
            # Set the latitude and longitude to numeric values
            crimes["location.latitude"] = pd.to_numeric(
                crimes["location.latitude"])
            crimes["location.longitude"] = pd.to_numeric(
                crimes["location.longitude"])

            # Create a pretty name that is easily readable
            # Example: `On or near Hyde Park Place - Leeds North West`
            crimes["pretty name"] = crimes["location.street.name"] + \
                " - " + str(name)

            # Add a column with the name of the area that the data is from
            crimes["area name"] = str(name)
            crimes["Type"] = "Street"

            # Reset the index to number all entries from 0 to length of the data
            crimes.reset_index(inplace=True, drop=True)

            crimes["location.street.name"] = crimes["location.street.name"].str.replace(
                "On or near ", ""
            )

            # Return the dataframe of crimes
            return crimes

        # Return NONE if no data was found
        return

    def fix_locations(self):
        """Fix locations in the self.all_crimes dataframe

        This is needed because some of the location names used by the police are
        used for multiple locations. For instance `On or near bus stop` doesn't
        tell us which bus stop it was near. This function takes the provided
        latitude and longitude coordinates and identifies which locale with a
        definitive name in the local area is closest.

        :raise AssertionError: This error is raised if a location name can't be
             correctly mapped to a street because there was no points close
             enough.

        """

        self.create_mappings()

        # Create a global list of all possible locations in the UK, this
        # contains the street name, latitude, longitude, area name and a
        # pretty name made up of the street name and area. Note that
        # one street can appear in two areas
        self.global_locales = self.all_crimes[
            [
                "location.street.name",
                "location.latitude",
                "location.longitude",
                "area name",
                "pretty name",
            ]
        ]

        # Create a search term to compare each entry agains, the search term
        # is formed from the known non desriptive values in the ignore constant
        search = "|".join(ignore)

        # Create a truth table mask of which locations names are descriptive
        mask = ~self.global_locales["location.street.name"].str.contains(
            search)

        # Apply the mask to the locales table and reset the index
        # We now have a list of all the descriptive street names which can
        # be filtered by constituincy
        self.global_locales = self.global_locales[mask]
        self.global_locales.reset_index(inplace=True, drop=True)

        # Duplicate the data dataframe
        modified_crimes = self.all_crimes

        # Get the indexes of the columns of interest
        street_id_loc = modified_crimes.columns.get_loc("location.street.name")
        latitude_id_loc = modified_crimes.columns.get_loc("location.latitude")
        longitude_id_loc = modified_crimes.columns.get_loc(
            "location.longitude")
        area_name_id_loc = modified_crimes.columns.get_loc("area name")
        pretty_id_loc = modified_crimes.columns.get_loc("pretty name")
        type_id_loc = modified_crimes.columns.get_loc("Type")

        # Loop through all the crimes in the dataset
        for i in trange(0, modified_crimes.shape[0]):
            # Copy the current street name into a local variable
            street = modified_crimes.iloc[i][street_id_loc]

            # Loop through all the non descriptive street names
            for x in ignore:
                # If the current street contains a non descriptive name then
                if x in street:

                    # Get the name of the area of the current street
                    area_name = modified_crimes.iloc[i][area_name_id_loc]

                    # Create a truth mask of which of the global locales
                    # areas match the current area
                    area_mask = self.mappings["area name"] == area_name

                    # Get the local latitude and logntitude values from the data
                    street_lat = modified_crimes.iloc[i][latitude_id_loc]
                    street_lon = modified_crimes.iloc[i][longitude_id_loc]

                    lat_mask = self.mappings["location.latitude"] == street_lat
                    lon_mask = self.mappings["location.longitude"] == street_lon

                    mask = area_mask & lat_mask & lon_mask

                    # Get the name of the new street and create the new pretty
                    # name
                    new_street = self.mappings[mask]["new name"].reset_index(drop=True)[
                        0
                    ]
                    pretty_name = street + " - " + new_street + " - " + area_name

                    # Set the names in the crimes dataframe to the new names
                    self.all_crimes.iat[i, pretty_id_loc] = pretty_name
                    self.all_crimes.iat[i, street_id_loc] = new_street
                    self.all_crimes.iat[i, type_id_loc] = street

    def hotspots_graph(self, top, location, location_type=["All"]):
        """Draw a bargraph of the rates of assult at the top hotspots

        :param top: how many hotspots to plot, for instance 10 would show the
            top 10 hotspots. IF this is set to none all hotspots will be
            graphed.
        :type top: int
        :param location: Where the title of the graph should
            say the data is from
        :type location: string
        :param location_type: Type of location to make the graph for, must be a
            list of location types, each entry must be either `Street` or
            value in the ignore list in constants.py. You can also pass `All`
            to select all crimes. The default value is `All`
        :type location_type: list (optional)

        """

        # Check if fix locations has been run yet, this graph only produces
        # valid data if the locations have been fixed
        if self.global_locales.empty:
            self.fix_locations()

        # If the value passed to top is none then it means graph all locations
        if top is None:
            top = len(self.all_crimes)

        # Check if the location type input is valid
        for x in location_type:
            assert x == "Street" or x == "All" or (x in ignore)

        # If the location_type was ['All'] set
        if location_type == ["All"]:
            location_type = ignore
            location_type.append("Street")

        search = "|".join(location_type)
        print("List of locations: ", location_type)
        print("Search term: ", search)
        # Create a mask of all the crimes that happened at the
        # given location type
        mask = self.all_crimes["Type"].str.contains(search)

        self.crime_list = self.all_crimes.loc[mask]

        # Create a pandas datafram containing the frequency counts of the top
        # locations
        self.hotspots = self.crime_list["pretty name"].value_counts()[:top]
        self.hotspots = self.hotspots.to_frame()

        # Reset the index and rename the columns
        self.hotspots.reset_index(inplace=True)
        self.hotspots.columns = ["locations", "frequency"]

        # Set the seaborn font scale
        sns.set(font_scale=4)

        # Set it so the number listed in the title is the same as the number of
        # bars on the graph
        top = len(self.hotspots["frequency"])

        # Create a barplot of the hotspots
        fig, ax = plt.subplots(figsize=(40, 40))
        sns.barplot(
            y=self.hotspots["locations"],
            x="frequency",
            ax=ax,
            data=self.hotspots,
            orient="h",
        )

        # Create the title of the chart depending on if it is crime or stop and
        # search data
        if self.usage == "crimes-street":
            title = (
                "Number of reported "
                + str(self.crime_type)
                + " crimes in locations within "
                + str(location)
                + " since 2018, top "
                + str(top)
                + " locations"
            )
        else:
            title = (
                "Number of stop and searches at locations within "
                + str(self.location.title)
                + " since 2018, top "
                + str(top)
                + " locations"
            )

        # Set the graph title to wrap
        title = "\n".join(wrap(title, 60))
        ax.set_title(title)

        # Add data labels to the bats
        for p in ax.patches:
            height = p.get_height()  # height of each horizontal bar is the same
            width = p.get_width()  # width (average number of passengers)
            # adding text to each bar
            ax.text(
                x=width + 1,  # x-coordinate position of data label
                y=p.get_y() + (height / 2),  # y-coordinate position of data label
                # data label, formatted to ignore decimals
                s="{:.0f}".format(width),
                va="center",
            )  # sets vertical alignment (va) to center

        # Set a tight layout
        fig.tight_layout()

        # Save the graph
        fig.savefig("locationFrequency.jpeg")

    # UTILITY FUNCTIONS
    def fishnet(self, geometry, threshold):
        """Divide a shapely geometry into small sections

        .. note:: This function is not currently used and is not doccumented

        """
        bounds = geometry.bounds
        xmin = int(bounds[0] // threshold)
        xmax = int(bounds[2] // threshold)
        ymin = int(bounds[1] // threshold)
        ymax = int(bounds[3] // threshold)
        result = []
        for i in range(xmin, xmax + 1):
            for j in range(ymin, ymax + 1):
                b = box(
                    i * threshold,
                    j * threshold,
                    (i + 1) * threshold,
                    (j + 1) * threshold,
                )
                g = geometry.intersection(b)
                if g.is_empty:
                    continue
                result.append(g)
        return result

    def url_gen(self, location, date):
        """Generate the url for API requests

        :param location: String of Lat/Lon coordinates marking out a boundary
        :type location: String
        :param date: The month to get the data for in format yyyy-mm
        :type: date String
        """

        # Check if the API request if for crimes or stop and search data then
        # assemble the URL
        if self.usage == "crimes-street":
            url = (
                baseURL
                + self.usage
                + "/"
                + self.crime_types[self.crime_type]
                + "?poly="
                + location
                + "&date="
                + str(date)
            )
        else:
            url = baseURL + self.usage + "?poly=" + \
                location + "&date=" + str(date)

        return url

    def fix_polygons(self, polygon):
        if type(polygon) == Polygon:
            polygon = MultiPolygon([polygon])
        return polygon

    def cache_data(self):

        try:
            self.global_locales.empty
        except AttributeError:
            raise locations_not_fixed_yet

        location_type = self.locations.__name__

        cache = os.path.expanduser("~/.crime_hotspots_cache/" + location_type)

        areas = np.unique(self.all_crimes["area name"])

        crime_types = np.unique(self.all_crimes["category"].astype(str))

        for area in areas:
            area_mask = self.all_crimes["area name"] == area

            for crime_type in crime_types:
                type_mask = self.all_crimes["category"].astype(
                    str) == crime_type

                months = np.unique(self.all_crimes["month"])

                directory = cache + "/" + area + "/" + self.usage + "/" + crime_type
                Path(directory).mkdir(parents=True, exist_ok=True)

                for month in months:
                    month_mask = self.all_crimes["month"] == month

                    final_mask = area_mask & type_mask & month_mask

                    file_name = directory + "/" + str(month) + ".csv"

                    self.all_crimes[final_mask].to_csv(file_name, index=False)

    def import_cache(self, location_type, area, month, category=None):
        file_name = os.path.expanduser(
            "~/.crime_hotspots_cache/"
            + location_type
            + "/"
            + area
            + "/"
            + "crimes-street"
            + "/"
            + category
            + "/"
            + month
            + ".csv"
        )

        if Path(file_name).is_file():
            data = pd.read_csv(file_name)
            return data
        else:
            return None

    def create_mappings(self):
        self.mappings = (
            self.all_crimes.groupby(
                [
                    "location.latitude",
                    "location.longitude",
                    "location.street.name",
                    "area name",
                ]
            )
            .size()
            .reset_index()
        )

        street_id_loc = self.mappings.columns.get_loc("location.street.name")
        latitude_id_loc = self.mappings.columns.get_loc("location.latitude")
        longitude_id_loc = self.mappings.columns.get_loc("location.longitude")

        mask = self.mappings["location.street.name"].str.match(
            "|".join(ignore))
        locales = self.mappings[~mask].reset_index(drop=True)

        new_cols = []

        for row in trange(0, self.mappings.shape[0]):

            if self.mappings.iloc[row, street_id_loc] in ignore:
                # create a new mapping
                # Get the local latitude and logntitude values from the data
                street_lat = self.mappings.iloc[row, latitude_id_loc]
                street_lon = self.mappings.iloc[row, longitude_id_loc]

                if row == 145:
                    print("Here")

                # Set a really high value for the minimum distance between
                # points, as the program calculates distances betwen the
                # street and the possilbe locales this will be updated to
                # represent what the smallest distance is
                min_distance = 1000000

                # Set the index to -1 so we know if no nearby locale was
                # found
                min_distance_index = -1

                for temp_row in range(0, locales.shape[0]):
                    # Get the latitude and longitude of the current
                    # candidate locale
                    locale_lat = locales.iloc[temp_row, latitude_id_loc]
                    locale_lon = locales.iloc[temp_row, longitude_id_loc]

                    # Calculate the difference between the current street
                    # and the candidate locale

                    lat_diff = street_lat - locale_lat
                    lon_diff = street_lon - locale_lon

                    # Calculate the difference between the two points
                    # TODO: Change this to the haversine formula
                    distance = sqrt((lat_diff) ** 2 + (lon_diff) ** 2)

                    # If the distance is the smalles so far
                    if distance < min_distance:
                        # Update the minimum distance and the index
                        min_distance = distance
                        min_distance_index = temp_row

                if min_distance_index > -1:
                    temp = [locales.iloc[min_distance_index, street_id_loc]]
                else:
                    print("No match found within bounds")
                    temp = ["DEADBEEF"]
                new_cols.append(temp)

            else:
                # copy across the name so its on the new name column as well
                temp = [self.mappings.iloc[row, street_id_loc]]
                new_cols.append(temp)

        new_cols = pd.DataFrame(new_cols, columns=["new name"])

        self.mappings = pd.concat([self.mappings, new_cols], axis=1)
        return self.mappings

    def export(self, name, file_type):
        file_path = os.path.expanduser("~/")
        file_path = file_path + "/" + name

        if file_type == "csv":
            self.all_crimes.to_csv(file_path)
        elif file_type == "sav":
            temp = self.all_crimes
            temp.columns = [col.replace(" ", "_") for col in temp.columns]
            write_sav(temp, file_path)


class locations_not_fixed_yet(Exception):
    """Exception raised when a function that should only be run after the crime data
    location data has been fixed to ensure readable place names are used instead of
    generic identifiers.
    """

    def __init__(self, message="Locations have not been fixed yet"):
        self.message = message
        super().__init__(self.message)


class http_error_code(Exception):
    """Exception raised when a function that should only be run after the crime data
    location data has been fixed to ensure readable place names are used instead of
    generic identifiers.
    """

    def __init__(self, code, url):
        if code == 404:
            message = (
                "ERROR: response code 404, page not found\n"
                + "URL was:"
                + url
                + "\n"
                + "This error probably means a cosntant variable has been spelt incorrectly"  # noqa: E501
            )
            self.message = message
        elif code == 429:
            message = (
                "ERROR: response code 429, too many requests\n"
                + "URL was:"
                + url
                + "\n"
                + "Doccumentation at: https://data.police.uk/docs/api-call-limits/"
            )
            self.message = message
        elif code == 503:
            message = (
                "ERROR: response code 503, more than 10,000 crimes in area\n"
                + "URL was:"
                + url
                + "\n"
                + "Doccumentation at: https://data.police.uk/docs/api-call-limits/"
            )
        else:
            message = (
                "ERROR: unkown response code\n"
                + "URL was:"
                + url
                + "\n"
                + "response code: "
                + str(code)
            )

        super().__init__(self.message)
