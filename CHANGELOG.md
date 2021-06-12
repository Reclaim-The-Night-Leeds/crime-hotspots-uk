# Changelog

## Version 0.1.2 Mary Wollstonecraft the Third
### Major Features
 * [devel~22] Implemented API method for acquiring stop and search data. This will be improved on in later versions with the ability to compute diversity statitistics for the data.
 * [devel~5] Added caching capability for all forms of data. This means you only hae to get the data for a reigion and crime type once and then can wor offline with it. Be warned with large requests this could take up a large ammount of space.
 * [devel~8] Added function to export data to csv (for general importing) or sav (for importing to SPSS)
 * [devel~12] Updated location fixing algorithim to only calculate snap points once. This vastly improves the speed at which the location points can be fixed especially with large datasets.


### Minor improvements and bug fixes
 * [devel~22] Added complete list of non descriptive place names
 * [devel~3] Updated demo document to use new features
 * [devel~4] Updated license document to include title block for RST compatibility
 * [devel~10] added exceptions for http error codes
 * [devel-11] changed date range to be calculated automatically as the past three years
 * [devel~13] Remove on or near part from all the place names


### Backend and API changes
 * [devel~6] Added child classes for different types of data
 * [devel~7] Renamed original Reclaim class to Root for easier understanding
 * [devel~23] Renamed columns in the constituincy class to follow standard format


## Version 0.1.1 Mary Wollstonecraft the seccond
### Features
* Can now filter to only show crimes that happened near a certain kind of area
* Added exporting of location data
* Now able to search for constituincies instead of passing their name

### Development workflow
* Added precommit hooks functionality, includeing Black and Flake8 code checkers

### Backend
* Refactored locations to be their own submodule, in future new location types can be added more easily
* Implemented constituincy location types to use the PyParliment module


## Version 0.1.0 Mary Wollstonecraft
* Added documentation for all existing classes
* Ported documentation to read the docs
* Removed fishnet algorithim so all data for each constituincy is got in one batch, paves the way to ensure program works for all constituincies
* Added a constants file to enable easier changing of widely used constant variables
* Minor speed improvements
* Assorted bug fixes
