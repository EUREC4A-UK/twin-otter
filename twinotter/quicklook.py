"""Quicklook plots for each leg over a single flight.

Use the flight-legs csv produced from :mod:`twinotter.plots.interactive_flight_track`


Usage::

    $ python -m twinotter.quicklook <flight_data_path> <flight_legs>

"""

from pathlib import Path

import matplotlib.pyplot as plt
import scipy.constants
import xarray as xr
from tqdm import tqdm
import metpy.calc
from metpy.units import units

from . import load_flight, load_legs, leg_times_as_datetime, derive
from .plots import vertical_profile


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("flight_data_path")
    argparser.add_argument("legs_file")

    args = argparser.parse_args()

    generate(flight_data_path=args.flight_data_path, legs_file=args.legs_file)

    return


def generate(flight_data_path, legs_file):
    ds = load_flight(flight_data_path)
    legs = load_legs(legs_file)
    leg_times_as_datetime(legs, ds.Time[0].dt.floor("D").data)

    path_figures = Path(flight_data_path) / "figures"
    path_figures.mkdir(exist_ok=True)

    counters = dict(Leg=0, Profile=0)

    for (idx, leg) in tqdm(legs.iterrows(), total=legs.shape[0]):
        label = leg.Label

        n = counters[label]
        if label == "Leg":
            plot_func = plot_leg
        elif label == "Profile":
            plot_func = plot_profile
        else:
            raise NotImplementedError(label)
        counters[label] += 1

        ds_section = ds.sel(Time=slice(leg.Start, leg.End))
        figures = plot_func(ds_section)

        savefigs(figures, ds.attrs["flight_number"], label.lower(), n)

    # Make a combined plot of all profiles
    profiles = legs.loc[legs.Label == "Profile"]
    ds_profiles = []
    for idx, profile in profiles.iterrows():
        ds_sub = ds.sel(Time=slice(profile.Start, profile.End))
        ds_profiles.append(ds_sub)

    ds_profiles = xr.concat(ds_profiles, dim="Time")
    figures = plot_profile(ds_profiles)
    savefigs(figures, ds.attrs["flight_number"], "profile", "_combined")


def plot_leg(ds):
    fig1, axes1 = plt.subplots(nrows=5, ncols=1, sharex="all", figsize=[16, 15])

    # Temperature and Dewpoint
    ds.TAT_ND_R.plot(ax=axes1[0], label=r"True")
    ds.TDEW_BUCK.plot(ax=axes1[0], label=r"Dewpoint")
    add_labels(axes1[0], "Temperature (K)")
    axes1[0].legend()

    # Velocities
    ds.U_OXTS.plot(ax=axes1[1], label=r"Zonal")
    ds.V_OXTS.plot(ax=axes1[1], label=r"Meridional")
    add_labels(axes1[1], "Velocity (m s$^{-1}$)")
    axes1[1].legend()

    ds.W_OXTS.plot(ax=axes1[2])
    add_labels(axes1[2], "Vertical Velocity (m s$^{-1}$)")

    # Shortwave radiation
    ds.SW_DN_C.plot(ax=axes1[3], label=r"SW Downwelling")
    ds.SW_UP_C.plot(ax=axes1[3], label=r"SW Upwelling")
    axes1[3].legend()

    # Longwave radiation
    ds.LW_DN_C.plot(ax=axes1[3], label=r"LW Downwelling")
    ds.LW_UP_C.plot(ax=axes1[3], label=r"LW Upwelling")
    add_labels(axes1[3], "Irradiance (W m$^{-2}$)")
    axes1[3].legend()

    # CPC Concentration
    ds.CPC_CONC.plot(ax=axes1[4])
    add_labels(axes1[4], "CPC Concentration (m$^{-3}$)")

    # Not all flights have LICOR data
    try:
        fig2, axes2 = plt.subplots(nrows=2, ncols=1, sharex="all", figsize=[16, 15])
        # LICOR data
        ds.CO2_LICOR.plot(ax=axes2[0], label=r"CO$_2$ LICOR")
        ds.H2O_LICOR.plot(ax=axes2[0], label=r"H$_2$O LICOR")
        add_labels(axes2[0], "Mole Fraction")
        axes2[0].legend()

        axes2[1].plot(ds.Time, derive.specific_humidity(ds))
        add_labels(axes2[1], "Specific Humidity")

        return [(fig1, "quicklook"), (fig2, "quicklook_LICOR")]
    except AttributeError:
        return [(fig1, "quicklook")]


def plot_profile(dataset):
    p = dataset.PS_AIR
    T = dataset.TAT_ND_R
    Td = dataset.TDEW_BUCK
    u = dataset.U_OXTS
    v = dataset.V_OXTS
    fig1 = vertical_profile.skewt(
        p, T - scipy.constants.zero_Celsius, Td - scipy.constants.zero_Celsius, u, v
    )

    theta = metpy.calc.potential_temperature(p * units("hPa"), T * units("K"))
    fig2 = plt.figure()
    plt.plot(theta, dataset.ALT_OXTS, "k.")
    plt.xlim(295, 320)
    plt.ylim(0, 4000)
    plt.xlabel("Potential Temperature (K)")
    plt.ylabel("Altitude (m)")
    plt.title("Flight {}".format(dataset.attrs["flight_number"]))

    rh = metpy.calc.relative_humidity_from_dewpoint(T * units("K"), Td * units("K"))
    fig3 = plt.figure()
    plt.plot(rh, dataset.ALT_OXTS, "b.")
    plt.xlim(0, 1)
    plt.ylim(0, 4000)
    plt.xlabel("Relative Humidity")
    plt.ylabel("Altitude (m)")
    plt.title("Flight {}".format(dataset.attrs["flight_number"]))

    return [(fig1, "skewt"), (fig2, "theta_0-4km"), (fig3, "rh_0-4km")]


def add_labels(ax, ylabel):
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)

    return


def savefigs(figures, flight_number, label, n):
    for fig, figname in figures:
        fn = "flight{}_{}{}_{}.png".format(flight_number, label, n, figname)
        print(fn)
        fig.savefig(fn)
        plt.close(fig)


if __name__ == "__main__":
    main()
