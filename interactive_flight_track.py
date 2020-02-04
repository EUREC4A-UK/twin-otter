"""Interactive flight track plot

Plot a variable of interest and the flight track then click on either figure
to mark the corresponding points on both figures.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.collections import LineCollection
import cartopy.crs as ccrs

import util


def main():
    # because of how the flags are stored (units is '1b') decoding cf times fails
    ds = util.load_flight(330)

    # Plot the main variable of interest
    # Change this to whatever variable you want or add additional figures here
    fig1 = plt.figure()
    ds.ROLL_OXTS.plot(linestyle='--', alpha=0.5)
    plt.twinx()
    plt.plot(ds.Time, ds.ALT_OXTS/1000)
    plt.ylabel('Altitude (km)')
    ymin, ymax = plt.gca().get_ylim()

    # Plot flight path with colours for altitude
    fig2 = plt.figure()
    plot_flight_path(ds, plt.gca().transData)

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


def plot_flight_path(ds, transform):
    lc = colored_line_plot(ds.LON_OXTS, ds.LAT_OXTS, ds.ALT_OXTS/1000,
                           vmin=0, vmax=3, cmap_steps=12, cmap='viridis',
                           transform=transform)
    plt.xlim(ds.LON_OXTS.min(), ds.LON_OXTS.max())
    plt.ylim(ds.LAT_OXTS.min(), ds.LAT_OXTS.max())
    cbar = plt.colorbar(lc)
    cbar.set_label('Altitude (km)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Add marker for start and end positions
    valid_times = np.where(ds.ALT_OXTS_FLAG == 0)[0]
    idx_s = valid_times[0]
    idx_f = valid_times[-1]

    print(idx_s, idx_f)

    plt.text(ds.LON_OXTS[idx_s], ds.LAT_OXTS[idx_s], 'S', transform=transform)
    plt.text(ds.LON_OXTS[idx_f], ds.LAT_OXTS[idx_f], 'F', transform=transform)

    return


def colored_line_plot(x, y, color, vmin=None, vmax=None, cmap='gray',
                      cmap_steps=0, **kwargs):
    """Add a multicolored line to an existing plot

    Args:
        x (np.array): The x points of the plot

        y (np.array): The y points of the plot

        color (np.array): The color of the line at the xy points

        vmin (scalar, optional): The minimum of the colorscale. Defaults to the
            minimum of the color array.

        vmax (scalar, optional): The maximum of the colorscale. Defaults to the
            maximum of the color array.

        cmap (str, optional): Colormap to plot. Default is grey.

        cmap_steps (int, optional): Number of discrete steps in the colorscale.
            Defaults is zero for a continuous colorscale.

        kwargs: Other keyword arguments to pass to LineCollection
    returns:
        matplotlib.collections.LineCollection:
            The plotted LineCollection. Required as argument to
            :py:func:`matplotlib.pyplot.colorbar`
    """
    # Set the color scalings
    if vmin is None:
        vmin = color.min()
    if vmax is None:
        vmax = color.max()

    # Break the xy points up in to line segments
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create discretised colourmap
    cmap = plt.get_cmap(cmap)
    if cmap_steps != 0:
        cmap = mpl.colors.ListedColormap(
            [cmap(n/(cmap_steps-1)) for n in range(cmap_steps)])

    # Collect the line segments
    lc = LineCollection(segments, cmap=cmap, norm=plt.Normalize(vmin, vmax),
                        **kwargs)

    # Set the line color to the specified array
    lc.set_array(color)

    # Add the colored line to the existing plot
    plt.gca().add_collection(lc)

    return lc


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
    main()
