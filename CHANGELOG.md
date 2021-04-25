# Changelog

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
