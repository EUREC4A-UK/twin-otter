#!/usr/bin/env python
# coding: utf-8
"""
Utility plot to examine if there appear to be gradients in the sea-surface temperature
by looking at the near-surface upwelling long-wave radiation
"""
if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from tqdm import tqdm
from pathlib import Path

import twinotter
import twinotter.external.eurec4a


def main(flight_data_path, alt_max=100.0):
    ds = twinotter.load_flight(flight_data_path)

    da_alt = ds.ALT_OXTS
    da_lat = ds.LAT_OXTS
    da_lon = ds.LON_OXTS

    da_lw_up = ds.LW_UP_C

    fig, axes = plt.subplots(
        subplot_kw=dict(projection=ccrs.PlateCarree()), nrows=2,
        figsize=(10, 12), sharey=True,
    )
    def _bootstrap(ax):
        ax.coastlines(resolution='10m')
        twinotter.external.eurec4a.add_halo_circle(ax=ax)
        gl = ax.gridlines(draw_labels=True)
        gl.top_labels = False
        gl.right_labels = False

    ax = axes[0]
    _bootstrap(ax)
    sc = ax.scatter(da_lon, da_lat, c=da_lw_up.where(da_alt < alt_max, np.nan))
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label(xr.plot.utils.label_from_attrs(da_lw_up))

    ax = axes[1]
    _bootstrap(ax)
    sc = ax.scatter(da_lon, da_lat, c=da_alt.where(da_alt < alt_max, np.nan))
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label(xr.plot.utils.label_from_attrs(da_alt))

    plt.tight_layout()
    date = ds.Time.isel(Time=0).dt.strftime("%d/%m/%Y").item()
    plt.suptitle(f"Flight {ds.flight_number} - {date} - below {alt_max}m")

    return fig, ds


if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path', nargs="+")

    args = argparser.parse_args()

    for flight_data_path in tqdm(args.flight_data_path):
        fig, ds = main(flight_data_path=flight_data_path)
        fn = f"flight{ds.flight_number}__lw_up_surface.png"
        plt.savefig(Path(flight_data_path)/"figures"/fn)
