import pandas as pd
import xarray as xr


flight_info = pd.read_csv('obs/flight_information.csv')


def load_flight(flight_number, frequency=1):
    datestr = flight_info['Date'][flight_info['Flight Number'] == flight_number].values[0].replace('-', '')
    filename = 'obs/core_masin_{}_r002_flight{}_{}hz.nc'.format(datestr, flight_number, frequency)

    # because of how the flags are stored (units is '1b') decoding cf times
    # fails
    ds = xr.open_dataset(filename, decode_times=False)

    # plot as function of time
    ds = ds.swap_dims(dict(data_point='Time'))

    return ds
