"""
    Setup file for crime-hotspots-uk.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.0.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import setuptools
from shutil import rmtree
import os


def create_directory_structure():
    replace = True

    home = os.path.expanduser("~")

    if replace:
        if os.path.exists(home + '/.crime_hotspots_cache'):
            rmtree(home + '/.crime_hotspots_cache')

        os.mkdir(home + '/.crime_hotspots_cache')
        os.mkdir(home + '/.crime_hotspots_cache/Constituincy')


if __name__ == "__main__":

    create_directory_structure()

    with open("README.md", "r") as fh:
        long_description = fh.read()
    print(f"Packages are: {setuptools.find_packages()}")
    setuptools.setup(
        # This is the name of the package
        name="RTNChuk",
        # The initial release version
        version="0.0.2",
        # Full name of the author
        author="Reclaim The Night Leeds",
        # Email of the author
        author_email="contact@reclaimleeds.org.uk",
        # Email of the author
        url="https://github.com/Reclaim-The-Night-Leeds/crime-hotspots-uk",
        description="API to get data from the UK Police API",
        # Long description read from the the readme file
        long_description=long_description,
        long_description_content_type="text/markdown",
        # List of all python modules to be installed
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],                                      # Information to filter the project on PyPi website
        python_requires='>=3.6',                # Minimum version requirement of the package
        # Name of the python package
        py_modules=["RTNChuk"],
        # Directory of the source code of the package
        # package_dir={'.'},
        install_requires=["pyreadstat", "shapely", "matplotlib",
                          "seaborn", "numpy", "tqdm", "pandas"],
        license="LICENSE.md"
    )
