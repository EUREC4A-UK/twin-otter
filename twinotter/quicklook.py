import matplotlib.pyplot as plt
import pandas as pd

import twinotter
from twinotter.plots import vertical_profile


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')
    argparser.add_argument('legs_file')

    args = argparser.parse_args()

    generate(flight_data_path=args.flight_data_path, legs_file=args.legs_file)

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

    fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=[16, 15])

    # Temperature and Dewpoint
    ds.TAT_ND_R[idx].plot(ax=axes[0], label=r'True')
    ds.TDEW_BUCK[idx].plot(ax=axes[0], label=r'Dewpoint')
    add_labels(axes[0], 'Temperature (K)')

    # Velocities
    ds.U_OXTS[idx].plot(ax=axes[1], label=r'Zonal')
    ds.V_OXTS[idx].plot(ax=axes[1], label=r'Meridional')
    add_labels(axes[1], 'Velocity (m s$^{-1}$)')

    ds.W_OXTS[idx].plot(ax=axes[2])
    add_labels(axes[2], 'Vertical Velocity (m s$^{-1}$)')

    # Shortwave radiation
    ds.SW_DN_C[idx].plot(ax=axes[3], label=r'SW Downwelling')
    ds.SW_UP_C[idx].plot(ax=axes[3], label=r'SW Upwelling')

    # Longwave radiation
    ds.LW_DN_C[idx].plot(ax=axes[3], label=r'LW Downwelling')
    ds.LW_UP_C[idx].plot(ax=axes[3], label=r'LW Upwelling')
    add_labels(axes[3], 'Irradiance (W m$^{-2}$)')

    # CPC Concentration
    ds.CPC_CONC[idx].plot(ax=axes[4])
    add_labels(axes[4], 'CPC Concentration (m$^{-3}$)')

    plt.xlim(xmin, xmax)
    plt.savefig('{}_{}.png'.format(prefix, 'quicklook'))
    plt.close()

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


def add_labels(ax, ylabel):
    ax.set_xlabel('')
    ax.set_ylabel(ylabel)
    ax.legend()

    return


if __name__ == '__main__':
    main()
