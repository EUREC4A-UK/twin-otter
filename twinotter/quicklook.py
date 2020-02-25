import matplotlib.pyplot as plt
import pandas as pd

import twinotter
from twinotter.plots import vertical_profile


def main(flight_data_path, legs_file):
    generate(flight_data_path, legs_file)

    return


def generate(flight_data_path, legs_file):
    ds = twinotter.load_flight(flight_data_path)
    legs = pd.read_csv(legs_file)

    plot_all(ds, legs, 'Leg', plot_leg)
    plot_all(ds, legs, 'Profile', plot_profile)

    print('Completed')

    return


def plot_all(ds, legs, leg_type, plot_func):
    n = 0
    while True:
        try:
            start, end = twinotter.flight_leg_times(legs, leg_type, n)

            idx_start = twinotter.index_from_time(start, ds.Time)
            idx_end = twinotter.index_from_time(end, ds.Time)

            # Match the times to an index
            idx = slice(idx_start, idx_end)
            print(n)

            prefix = 'flight{}/{}{}'.format(ds.attrs['flight_number'], leg_type, n)
            plot_func(ds, idx, prefix)
            n += 1
        except IndexError:
            break

    return


def plot_leg(ds, idx, prefix):
    xmin, xmax = ds.Time[idx.start], ds.Time[idx.stop]

    # Temperature and Dewpoint
    ds.TAT_ND_R[idx].plot(label=r'Temperature (K)')
    ds.TDEW_BUCK[idx].plot(label=r'Dewpoint Temperature (K)')
    set_axes_and_labels(xmin, xmax, prefix, 'temperature')

    # Shortwave radiation
    ds.SW_DN_C[idx].plot(label=r'SW Downwelling Irradiance (W m$^{-2}$)')
    ds.SW_UP_C[idx].plot(label=r'SW Upwelling Irradiance (W m$^{-2}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'sw_fluxes')

    # Longwave radiation
    ds.LW_DN_C[idx].plot(label=r'LW Downwelling Irradiance (W m$^{-2}$)')
    ds.LW_UP_C[idx].plot(label=r'LW Upwelling Irradiance (W m$^{-2}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'lw_fluxes')

    # CPC Concentration
    ds.CPC_CONC[idx].plot(label=r'CPC Concentration (m$^{-3}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'cpc')

    # Velocities
    ds.U_OXTS[idx].plot(label=r'Zonal Velocity (m s$^{-1}$)')
    ds.V_OXTS[idx].plot(label=r'Meridional Velocity (m s$^{-1}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'velocities')

    ds.W_OXTS[idx].plot(label=r'Vertical Velocity (m s$^{-1}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'vertical_wind')

    return


def plot_profile(dataset, idx, prefix):
    p = dataset.PS_AIR[idx]
    T = dataset.TAT_ND_R[idx] - 273.15
    Td = dataset.TDEW_BUCK[idx] - 273.15
    u = dataset.U_OXTS[idx]
    v = dataset.V_OXTS[idx]
    vertical_profile.skewt(p, T, Td, u, v)

    plt.savefig('{}_{}.png'.format(prefix, 'skewt'))

    plt.close()

    return


def set_axes_and_labels(xmin, xmax, prefix, figure_name):
    plt.xlim(xmin, xmax)
    plt.xlabel('')
    plt.ylabel('')
    plt.legend()

    plt.savefig('{}_{}.png'.format(prefix, figure_name))
    plt.close()

    return


if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')
    argparser.add_argument('legs_file')

    args = argparser.parse_args()

    main(flight_data_path=args.flight_data_path, legs_file=args.legs_file)
