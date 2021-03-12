"""
> python -m twinotter.plots.basic_flight_track /path/to/data
"""

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

from .. import load_flight
from .. import plots
from ..external import eurec4a


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("flight_data_path", nargs="+")
    argparser.add_argument("--show-gui", default=False, action="store_true")

    args = argparser.parse_args()

    for flight_data_path in args.flight_data_path:
        generate(flight_data_path=flight_data_path, show_gui=args.show_gui)


def generate(flight_data_path, show_gui=False):
    flight_data_path = Path(flight_data_path)

    # create figure
    bbox = [-60, -56.4, 12, 14.4]
    domain_aspect = (bbox[3] - bbox[2]) / (bbox[1] - bbox[0])
    fig = plt.figure(figsize=(11.0, domain_aspect * 10), dpi=96)
    ax = plt.axes(projection=ccrs.PlateCarree())
    add_features(ax)
    ax.set_extent(bbox, crs=ccrs.PlateCarree())
    fig.tight_layout()

    ds = load_flight(flight_data_path, debug=True)
    plots.flight_path(ax=ax, ds=ds)

    fig = ax.figure
    caption = "created {} from {}".format(datetime.now(), ds.source_file)
    ax.text(0.0, 0.0, caption, transform=fig.transFigure)

    if flight_data_path.is_file():
        path_fig = flight_data_path.parent
    else:
        path_fig = flight_data_path
    path_fig = (
        path_fig / "figures" / "flight{}_track_altitude.png".format(ds.flight_number)
    )
    path_fig.parent.mkdir(exist_ok=True, parents=True)

    if show_gui:
        plt.show()
    else:
        plt.savefig(str(path_fig), bbox_inches="tight")
        print("Saved flight track to `{}`".format(str(path_fig)))


def add_features(ax):
    # Shade land and sea
    plots.add_land_and_sea(ax)

    # Add HALO circle
    eurec4a.add_halo_circle(ax)

    return


if __name__ == "__main__":
    main()
