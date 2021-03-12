import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr


def flight_path(
    ax,
    ds,
    vmin=0,
    vmax=3,
    cmap_steps=12,
    cmap="jet",
    transform=ccrs.PlateCarree(),
    add_cmap=True,
    mark_end_points=True,
    **kwargs
):

    lc = colored_line_plot(
        ax,
        ds.LON_OXTS,
        ds.LAT_OXTS,
        ds.ALT_OXTS / 1000,
        vmin=vmin,
        vmax=vmax,
        cmap_steps=cmap_steps,
        cmap=cmap,
        transform=transform,
        **kwargs
    )

    if add_cmap:
        cbar = plt.colorbar(lc, ax=ax)
        cbar.set_label("Altitude (km)")

    ax.set_xlabel(xr.plot.utils.label_from_attrs(ds.LON_OXTS))
    ax.set_ylabel(xr.plot.utils.label_from_attrs(ds.LAT_OXTS))

    # Add marker for start and end positions
    if mark_end_points:
        ax.text(ds.LON_OXTS[0], ds.LAT_OXTS[0], "S", transform=ccrs.PlateCarree())
        ax.text(ds.LON_OXTS[-1], ds.LAT_OXTS[-1], "F", transform=ccrs.PlateCarree())

    return


def flight_path_3d(ds, ax=None):
    if ax == None:
        ax = plt.gca(projection="3d")

    ax.plot(ds.LON_OXTS, ds.LAT_OXTS, zs=0, zdir="z", color="grey")

    ax.plot(
        ds.LON_OXTS, ds.ALT_OXTS, zs=ds.LAT_OXTS.max() + 0.1, zdir="y", color="grey"
    )

    ax.plot(
        ds.LAT_OXTS, ds.ALT_OXTS, zs=ds.LON_OXTS.max() + 0.1, zdir="x", color="grey"
    )

    ax.plot(ds.LON_OXTS, ds.LAT_OXTS, ds.ALT_OXTS, color="k", lw=3, zorder=10)


def colored_line_plot(
    ax, x, y, color, vmin=None, vmax=None, cmap="gray", cmap_steps=0, **kwargs
):
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
    segments = np.array([(x[:-1].values, x[1:].values), (y[:-1].values, y[1:].values)])
    segments = np.transpose(segments, axes=(2, 1, 0))

    # Create discretised colourmap
    cmap = plt.get_cmap(cmap)
    if cmap_steps != 0:
        cmap = mpl.colors.ListedColormap(
            [cmap(n / (cmap_steps - 1)) for n in range(cmap_steps)]
        )

    # Collect the line segments
    lc = LineCollection(segments, cmap=cmap, norm=plt.Normalize(vmin, vmax), **kwargs)

    # Set the line color to the specified array
    lc.set_array(color)

    # Add the colored line to the existing plot
    ax.add_collection(lc)

    # autoscale if limits haven't already been set so that the linecollection
    # is visible
    if ax.get_xlim() == (0, 1) and ax.get_ylim() == (0, 1):
        ax.autoscale()

    return lc


def add_land_and_sea(ax):
    # Shade land and sea
    ax.imshow(
        np.tile(
            np.array([[cfeature.COLORS["water"] * 255]], dtype=np.uint8), [2, 2, 1]
        ),
        origin="upper",
        transform=ccrs.PlateCarree(),
        extent=[-180, 180, -180, 180],
    )

    ax.add_feature(
        cfeature.NaturalEarthFeature(
            "physical",
            "land",
            "10m",
            edgecolor="black",
            facecolor=cfeature.COLORS["land"],
        )
    )

    ax.gridlines(linestyle="--", color="black", draw_labels=True)

    return


def add_flight_position(ax, dataset):
    ax.plot(
        dataset.LON_OXTS,
        dataset.LAT_OXTS,
        marker=(2, 0, -float(dataset.HDG_OXTS)),
        color="red",
    )
    ax.plot(
        dataset.LON_OXTS,
        dataset.LAT_OXTS,
        marker=(3, 0, -float(dataset.HDG_OXTS)),
        color="red",
    )
    return
