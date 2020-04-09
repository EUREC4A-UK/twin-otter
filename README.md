# Tools for working with Twin-Otter data

![twinotter](https://github.com/EUREC4A-UK/twin-otter/workflows/twinotter/badge.svg)

## Useful Scripts

    $> python -m twinotter.generate_summary <data_directory>

To plot a flight track with altitude:

    $> python -m twinotter.plots.basic_flight_track <flight_data_path>

Interactive flight track with leg labelling:

    $> python -m twinotter.plots.interactive_flight_track <flight_data_path>

## Install

    $> git clone https://github.com/EUREC4A-UK/twin-otter.git
    $> cd twin-otter
    $> pip install .

If you are going to modify the code, replace the last line with

    $> pip install -e .


**Note that installing this package may initially fail due to some issues with cartopy.**

You can:

install cartopy first via conda

    $> conda install -c conda-forge cartopy

or manually install the cartopy dependencies (Following [this stack overflow answer](https://stackoverflow.com/a/56956172))

    $> apt-get install libproj-dev proj-data proj-bin
    $> apt-get install libgeos-dev
    $> pip install cython
    $> pip install cartopy



## Testing

To run tests (which reside in `tests/`) use `pytest`:

    $> pytest
        
Tests are automatically run on all commits pushed to github
