"""Functionality related to the EUREC4A field campaign from 2020
"""

import requests
import yaml
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


TO_segs_url = (
    "https://raw.githubusercontent.com/"
    "EUREC4A-UK/flight-phase-separation/twinotter/"
    "flight_phase_files/TO/EUREC4A_TO_Flight-Segments_{}_0.1.yaml"
)
segs_url = (
    "https://raw.githubusercontent.com/"
    "eurec4a/flight-phase-separation/master/"
    "flight_phase_files/"
)

HALO_flight_numbers = [
    119,
    122,
    124,
    126,
    128,
    130,
    131,
    202,
    205,
    207,
    209,
    211,
    213,
    215,
    218,
]

P3_flight_numbers = [117, 119, 123, 124, 131, 203, 204, 205, 209, 210, 211]
flight_segs_urls = dict(
    TO={
        330: TO_segs_url.format("20200124a"),
        331: TO_segs_url.format("20200124b"),
        332: TO_segs_url.format("20200126a"),
        333: TO_segs_url.format("20200126b"),
        334: TO_segs_url.format("20200128a"),
        335: TO_segs_url.format("20200128b"),
        336: TO_segs_url.format("20200130a"),
        337: TO_segs_url.format("20200131a"),
        338: TO_segs_url.format("20200131b"),
        339: TO_segs_url.format("20200202a"),
        340: TO_segs_url.format("20200205a"),
        341: TO_segs_url.format("20200205b"),
        342: TO_segs_url.format("20200206a"),
        343: TO_segs_url.format("20200207a"),
        344: TO_segs_url.format("20200207b"),
        345: TO_segs_url.format("20200209a"),
        346: TO_segs_url.format("20200209b"),
        347: TO_segs_url.format("20200210a"),
        348: TO_segs_url.format("20200211a"),
        349: TO_segs_url.format("20200211b"),
        350: TO_segs_url.format("20200213a"),
        351: TO_segs_url.format("20200213b"),
        352: TO_segs_url.format("20200214a"),
        353: TO_segs_url.format("20200215a"),
        354: TO_segs_url.format("20200215b"),
    },
    HALO={
        flight_number: segs_url
        + "HALO/EUREC4A_HALO_Flight-Segments_20200{}.yaml".format(flight_number)
        for flight_number in HALO_flight_numbers
    },
    P3={
        flight_number: segs_url
        + "P3/EUREC4A_ATOMIC_P3_Flight-segments_20200{}_v0.5.yaml".format(flight_number)
        for flight_number in P3_flight_numbers
    },
)


def load_segments(flight_number, platform="TO"):
    """Load flight segments yaml file from EUREC4A github repository

    See https://github.com/eurec4a/flight-phase-separation

    Args:
        flight_number (int):
        platform (str): The short name for the platforms used in EUREC4A. Currently
            either "TO", "HALO", or "P3".

    Returns:
        dict:

    """
    yaml_file = requests.get(flight_segs_urls[platform][flight_number]).text

    return yaml.safe_load(yaml_file)
