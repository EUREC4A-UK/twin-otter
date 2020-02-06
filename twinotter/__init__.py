import pandas as pd
import xarray as xr


flight_info = pd.read_csv('obs/flight_information.csv')


def load_flight(flight_number, frequency=1):
    datestr = flight_info['Date'][flight_info['Flight Number'] == flight_number].values[0].replace('-', '')
    filename = 'obs/core_masin_{}_r002_flight{}_{}hz.nc'.format(datestr, flight_number, frequency)

    ds = xr.open_dataset(filename, decode_cf=False)

    # plot as function of time
    ds = ds.swap_dims(dict(data_point='Time'))

    return ds


def flight_leg_index(flight_number, leg_name, leg_number=0):
    """Get a slice representing a single section of the flight

    Args:
        flight_number (int):
        leg_name (str):
        leg_number (int): For multiple of the same type of leg within a flight,
            select which leg you want. Default is zero

    Returns:
        slice: 
    """
    legs = pd.read_csv('obs/legs_flight{}.csv'.format(flight_number))
    idx = legs[legs['Type'] == leg_name].index[leg_number]
    start = legs['Start'][idx]
    end = legs['End'][idx]

    return slice(start, end)
