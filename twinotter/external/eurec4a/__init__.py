"""Functionality related to the EUREC4A field campaign from 2020
"""

import cartopy.crs as ccrs
import matplotlib.patches as mpatches

#: A dictionary of standard colours for the various platforms
colors = dict(
    ATR="DeepOrange",
    Atalante="Fuchsia",
    BCO="royalblue",
    HALO="teal",
    P3="grey",
    TO="tab:red",
    MSM="indigo",
    Meteor="darkblue",
    RHB="deepskyblue",
)

# HALO circle attributes
lat = 13 + (18 / 60)
lon = -(57 + (43 / 60))
r = 1


def _compute_radius(ortho, radius_degrees):
    phi1 = lat + radius_degrees if lat <= 0 else lat - radius_degrees
    _, y1 = ortho.transform_point(lon, phi1, ccrs.PlateCarree())
    return abs(y1)


def add_halo_circle(ax, color=colors["HALO"], alpha=0.3, **kwargs):
    """Add the HALO circle to the current

    Projection of the HALO circle adapted from AJDawson's answer on stackoverflow
    https://stackoverflow.com/questions/52105543/drawing-circles-with-cartopy-in-orthographic-projection

    Args:
        ax ():
        color (str): The circle of the colour. Any matplotlib compatible colour. Default
            is teal (set in the dictionary :data:colors:).
        alpha (float): The transparancy of the circle (between 0 and 1). Default is 0.3
        **kwargs: Other keywords to pass to :meth:matplotlib.axes.Axes.add_patch:
    """
    # Define the projection used to display the circle:
    proj = ccrs.Orthographic(central_longitude=lon, central_latitude=lat)

    # Compute the required radius in projection native coordinates:
    r_ortho = _compute_radius(proj, r)
    ax.add_patch(
        mpatches.Circle(
            xy=[lon, lat],
            radius=r_ortho,
            transform=proj,
            zorder=30,
            fill=False,
            color=color,
            alpha=alpha,
            **kwargs
        )
    )
