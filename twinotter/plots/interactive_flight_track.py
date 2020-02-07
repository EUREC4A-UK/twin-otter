"""Interactive flight track plot

Plot a variable of interest and the flight track then click on either figure
to mark the corresponding points on both figures.
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr

from .. import load_flight
from . import plot_flight_path


def main(flight_data_path):
    # because of how the flags are stored (units is '1b') decoding cf times fails
    ds = load_flight(flight_data_path)

    # Plot the main variable of interest
    # Change this to whatever variable you want or add additional figures here
    fig1 = plt.figure()
    ds.ROLL_OXTS.plot(linestyle='--', alpha=0.5)
    plt.twinx()
    plt.plot(ds.Time, ds.ALT_OXTS/1000)
    plt.ylabel('Altitude (km)')
    ymin, ymax = plt.gca().get_ylim()


    # Plot flight path with colours for altitude
    fig2, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()),)
    ax.gridlines(draw_labels=True)
    ax.coastlines()
    plot_flight_path(ax=ax, ds=ds)


    # Functions to select points along the flightpath to mark
    # Keep a counter so each point is marked differently
    counter = 1

    # Select an interesting point on the main plot as mark the corresponding
    # point on the flight path
    def select_interesting_point(event):
        nonlocal counter
        idx = find_nearest_point(event.xdata, 0, ds.Time, np.zeros_like(ds.Time))
        print(idx)
        add_selected_points(idx, ds, counter, ymax)
        counter += 1

    # Select a position on the flight path and mark the corresponding point on
    # the main plot
    def select_flight_position(event):
        nonlocal counter
        idx = find_nearest_point(event.xdata, event.ydata, ds.LON_OXTS, ds.LAT_OXTS)
        print(idx)
        add_selected_points(idx, ds, counter, ymax)
        counter += 1

    fig1.canvas.mpl_connect('button_press_event', select_interesting_point)
    fig2.canvas.mpl_connect('button_press_event', select_flight_position)

    plt.show()
    return



def find_nearest_point(x, y, xpoints, ypoints):
    return int(np.argmin((x-xpoints)**2 + (y-ypoints)**2))


def add_selected_points(idx, ds, counter, ymax):
    # Plot a vertical line at the specified flight time with a number at the top
    fig = plt.figure(1)
    plt.axvline(ds.Time[idx], color='k')
    plt.text(ds.Time[idx], ymax, str(counter))
    fig.canvas.draw()

    # Mark the corresponding position on the flight path
    fig = plt.figure(2)
    plt.text(ds.LON_OXTS[idx], ds.LAT_OXTS[idx], str(counter))
    fig.canvas.draw()

    return


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')

    args = argparser.parse_args()

    main(flight_data_path=args.flight_data_path)
