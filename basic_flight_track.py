"""
Projection of the HALO circle adapted from AJDawson's answer on stackoverflow
https://stackoverflow.com/questions/52105543/drawing-circles-with-cartopy-in-orthographic-projection
"""

import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import util
from interactive_flight_track import plot_flight_path


# HALO circle attributes
lat = 13 + (18/60)
lon = -(57 + (43/60))
r = 1

# Define the projection used to display the circle:
proj = ccrs.Orthographic(central_longitude=lon, central_latitude=lat)

def compute_radius(ortho, radius_degrees):
    phi1 = lat + radius_degrees if lat <= 0 else lat - radius_degrees
    _, y1 = ortho.transform_point(lon, phi1, ccrs.PlateCarree())
    return abs(y1)

# Compute the required radius in projection native coordinates:
r_ortho = compute_radius(proj, r)

# We can now compute the correct plot extents to have padding in degrees:
pad_north = compute_radius(proj, r + 0.1)
pad_east = compute_radius(proj, r + 0.1)
pad_south = compute_radius(proj, r + 0.1)
pad_west = compute_radius(proj, r + 1)

# define image properties
resolution = '10m'


def main():
    flight_number = 330

    ax = draw_features()
    ds = util.load_flight(flight_number)
    plot_flight_path(ds, transform=ccrs.PlateCarree())

    # Deliberately avoiding set_extent because it has some odd behaviour that causes
    # errors for this case. However, since we already know our extents in native
    # coordinates we can just use the lower-level set_xlim/set_ylim safely.
    ax.set_xlim([-pad_west, pad_east])
    ax.set_ylim([-pad_south, pad_north])

    plt.savefig('figures/flight{}_track.png'.format(flight_number))
    return


def draw_features():
    # create figure
    fig = plt.figure(figsize=(16, 10), dpi=96)
    ax = plt.axes(projection=proj)

    # Shade land and sea
    ax.imshow(np.tile(
        np.array([[cfeature.COLORS['water'] * 255]], dtype=np.uint8),[2, 2, 1]),
        origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -180, 180])
    ax.add_feature(
        cfeature.NaturalEarthFeature('physical', 'land', resolution,
                                     edgecolor='black',
                                     facecolor=cfeature.COLORS['land']))

    # Add HALO circle
    ax.add_patch(mpatches.Circle(xy=[lon, lat], radius=r_ortho, color='red',
                                 alpha=0.3, transform=proj, zorder=30, fill=False))
    fig.tight_layout()

    return ax


if __name__ == '__main__':
    main()
