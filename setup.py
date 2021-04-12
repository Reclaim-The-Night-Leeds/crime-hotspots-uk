"""
    Setup file for crime-hotspots-uk.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.0.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup
from shutil import rmtree
import os


def create_directory_structure():
    replace = True
    
    home = os.path.expanduser("~")
    
    if os.path.exists(home + '/.crime_hotspots_cache'):
        print('Installer detected existing cache directory')
        print('Do you want to replace the existing cache [y]/n: ')
        cache_test = input()
        if cache_test == 'n' or cache_test == 'N':
            replace = False
        else:
            replace = True
    
    if replace:
        if os.path.exists(home + '/.crime_hotspots_cache'):
            rmtree(home + '/.crime_hotspots_cache')
        
        os.mkdir(home + '/.crime_hotspots_cache')
        os.mkdir(home + '/.crime_hotspots_cache/constituincies')


if __name__ == "__main__":
    
    create_directory_structure()
    
    try:
        setup(use_scm_version={"version_scheme": "no-guess-dev"})
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
        
