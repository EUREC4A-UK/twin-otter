"""
Projection of the HALO circle adapted from AJDawson's answer on stackoverflow
https://stackoverflow.com/questions/52105543/drawing-circles-with-cartopy-in-orthographic-projection
"""

import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from datetime import datetime

from .. import load_flight
from . import plot_flight_path


# HALO circle attributes
lat = 13 + (18/60)
lon = -(57 + (43/60))
r = 1

def _compute_radius(ortho, radius_degrees):
    phi1 = lat + radius_degrees if lat <= 0 else lat - radius_degrees
    _, y1 = ortho.transform_point(lon, phi1, ccrs.PlateCarree())
    return abs(y1)


def main(flight_data_path):
    ax = draw_features()
    ds = load_flight(flight_data_path, debug=True)
    plot_flight_path(ax=ax, ds=ds)

    fig = ax.figure
    caption = "created {} from {}".format(datetime.now(), ds.source_file)
    ax.text(0.0, 0.0, caption, transform=fig.transFigure)

    path_fig = Path(flight_data_path)/'figures'/'flight{}_track_altitude.png'.format(ds.flight_number)
    path_fig.parent.mkdir(exist_ok=True, parents=True)

    plt.savefig(path_fig, bbox_inches='tight')
    print("Saved flight track to `{}`".format(str(path_fig)))


def draw_features():
    # create figure
    bbox = [-60, -56.4, 12, 14.4]
    domain_aspect = (bbox[3]-bbox[2])/(bbox[1]-bbox[0])
    fig = plt.figure(figsize=(11., domain_aspect*10), dpi=96)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Shade land and sea
    ax.imshow(np.tile(
        np.array([[cfeature.COLORS['water'] * 255]], dtype=np.uint8),[2, 2, 1]),
        origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -180, 180])
    ax.add_feature(
        cfeature.NaturalEarthFeature('physical', 'land', '10m',
                                     edgecolor='black',
                                     facecolor=cfeature.COLORS['land']))
    ax.gridlines(linestyle='--', color='black', draw_labels=True)


    # Add HALO circle
    # Define the projection used to display the circle:
    proj = ccrs.Orthographic(central_longitude=lon, central_latitude=lat)
    # Compute the required radius in projection native coordinates:
    r_ortho = _compute_radius(proj, r)
    # We can now compute the correct plot extents to have padding in degrees:
    pad_north = _compute_radius(proj, r + 0.1)
    pad_east = _compute_radius(proj, r + 0.1)
    pad_south = _compute_radius(proj, r + 0.1)
    pad_west = _compute_radius(proj, r + 1)
    ax.add_patch(mpatches.Circle(xy=[lon, lat], radius=r_ortho, color='red',
                                 alpha=0.3, transform=proj, zorder=30, fill=False))

    ax.set_extent(bbox, crs=ccrs.PlateCarree())
    fig.tight_layout()

    return ax


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path', nargs="+")

    args = argparser.parse_args()

    for flight_data_path in args.flight_data_path:
        main(flight_data_path=flight_data_path)
