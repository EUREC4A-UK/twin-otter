"""Interactive flight track plot

Plot a variable of interest and the flight track then click on either figure
to mark the corresponding points on both figures.
"""
import datetime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import cartopy.crs as ccrs

from twinotter import load_flight
from twinotter.plots import plot_flight_path


def main(flight_data_path):
    ds = load_flight(flight_data_path)

    # Plot the main variable of interest
    # Change this to whatever variable you want or add additional figures here
    fig1, ax1a = plt.subplots()
    ds.ROLL_OXTS.plot(linestyle='--', alpha=0.5)
    ax1b = ax1a.twinx()
    ax1b.plot(ds.Time, ds.ALT_OXTS/1000)
    ax1b.set_ylabel('Altitude (km)')

    # Plot flight path with colours for altitude
    fig2, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()),)
    ax.gridlines(draw_labels=True)
    ax.coastlines()
    plot_flight_path(ax=ax, ds=ds)

    # Save flight leg start and end points
    leg_times = []

    # Drag mouse from the start to the end of a leg and save the corresponding
    # times
    def highlight_leg(start, end):
        idx_start = find_nearest_point(start, ds.Time)
        idx_end = find_nearest_point(end, ds.Time)

        leg_times.append([format_timedelta(ds, idx_start),
                          format_timedelta(ds, idx_end)])

        print(leg_times)

        return

    selector = SpanSelector(
        ax1b, highlight_leg, direction='horizontal')

    plt.show()
    return


def find_nearest_point(value, points):
    return int(np.argmin(np.abs(value-points)))


def format_timedelta(ds, idx):
    return str(datetime.timedelta(seconds=float(ds.Time[idx])))


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')

    args = argparser.parse_args()

    main(flight_data_path=args.flight_data_path)
