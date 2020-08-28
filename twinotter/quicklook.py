"""Quicklook plots for each leg over a single flight.

Use the flight-segments .yaml produced from
:mod:`twinotter.plots.interactive_flight_track`


Usage::

    $ python -m twinotter.quicklook <flight_data_path> <flight_segments>

"""

from pathlib import Path

import matplotlib.pyplot as plt
from tqdm import tqdm

from . import load_flight, load_segments
from .plots import vertical_profile


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')
    argparser.add_argument('flight_segments_file')

    args = argparser.parse_args()

    generate(
        flight_data_path=args.flight_data_path,
        flight_segments_file=args.legs_file
    )

    return


def generate(flight_data_path, flight_segments_file):
    ds = load_flight(flight_data_path)
    flight_segments = load_segments(flight_segments_file)

    path_figures = Path(flight_data_path)/"figures"
    path_figures.mkdir(exist_ok=True)

    counters = dict(level=0, profile=0)

    for segments in tqdm(flight_segments["segments"]):
        label = segments["kinds"][0]

        n = counters[label]
        if label == 'level':
            fn = '{}{}_{}.png'.format(label, n, 'quicklook')
            plot_func = plot_leg
        elif label == 'profile':
            fn = '{}{}_{}.png'.format(label, n, 'skewt')
            plot_func = plot_profile
        else:
            raise NotImplementedError(label)
        counters[label] += 1

        ds_section = ds.sel(Time=slice(segments["start"], segments["end"]))
        fig = plot_func(ds_section)
        fig.savefig(str(path_figures/fn))
        plt.close(fig)


def plot_leg(ds):
    fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=[16, 15])

    # Temperature and Dewpoint
    ds.TAT_ND_R.plot(ax=axes[0], label=r'True')
    ds.TDEW_BUCK.plot(ax=axes[0], label=r'Dewpoint')
    add_labels(axes[0], 'Temperature (K)')
    axes[0].legend()

    # Velocities
    ds.U_OXTS.plot(ax=axes[1], label=r'Zonal')
    ds.V_OXTS.plot(ax=axes[1], label=r'Meridional')
    add_labels(axes[1], 'Velocity (m s$^{-1}$)')
    axes[1].legend()

    ds.W_OXTS.plot(ax=axes[2])
    add_labels(axes[2], 'Vertical Velocity (m s$^{-1}$)')

    # Shortwave radiation
    ds.SW_DN_C.plot(ax=axes[3], label=r'SW Downwelling')
    ds.SW_UP_C.plot(ax=axes[3], label=r'SW Upwelling')
    axes[3].legend()

    # Longwave radiation
    ds.LW_DN_C.plot(ax=axes[3], label=r'LW Downwelling')
    ds.LW_UP_C.plot(ax=axes[3], label=r'LW Upwelling')
    add_labels(axes[3], 'Irradiance (W m$^{-2}$)')
    axes[3].legend()

    # CPC Concentration
    ds.CPC_CONC.plot(ax=axes[4])
    add_labels(axes[4], 'CPC Concentration (m$^{-3}$)')

    return fig


def plot_profile(dataset):
    p = dataset.PS_AIR
    T = dataset.TAT_ND_R - 273.15
    Td = dataset.TDEW_BUCK - 273.15
    u = dataset.U_OXTS
    v = dataset.V_OXTS
    fig = vertical_profile.skewt(p, T, Td, u, v)

    return fig


def add_labels(ax, ylabel):
    ax.set_xlabel('')
    ax.set_ylabel(ylabel)

    return


if __name__ == '__main__':
    main()
