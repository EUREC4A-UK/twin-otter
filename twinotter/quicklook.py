"""Quicklook plots for each leg over a single flight.

Use the flight-legs csv produced from :mod:`twinotter.plots.interactive_flight_track`


Usage::

    $ python -m twinotter.quicklook <flight_data_path> <flight_legs>

"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import scipy.constants
import metpy.calc
from metpy.units import units

from . import load_flight, load_legs, leg_times_as_datetime, derive, extract_legs
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

    plot_individual_phases(ds, legs, "Leg", plot_leg)
    plot_individual_phases(ds, legs, "Profile", plot_profile)

    # Make a combined plot of all profiles
    profiles = extract_legs(ds, legs, "Profile")
    figures = plot_profile(profiles)
    savefigs(figures, ds.attrs["flight_number"], "profile", "_combined")


def plot_individual_phases(ds, legs, leg_type, plot_func):
    for n in range(legs["Label"].value_counts()[leg_type]):
        ds_section = extract_legs(ds, legs, leg_type, n)
        figures = plot_func(ds_section)
        savefigs(figures, ds.attrs["flight_number"], leg_type, n)


def plot_leg(ds):
    figures = []

    fig, axes = plt.subplots(nrows=5, ncols=1, sharex="all", figsize=[16, 15])

    # Temperature and Dewpoint
    ds.TAT_ND_R.plot(ax=axes[0], label=r"True")
    ds.TDEW_BUCK.plot(ax=axes[0], label=r"Dewpoint")
    add_labels(axes[0], "Temperature (K)")
    axes[0].legend()

    # Velocities
    ds.U_OXTS.plot(ax=axes[1], label=r"Zonal")
    ds.V_OXTS.plot(ax=axes[1], label=r"Meridional")
    add_labels(axes[1], "Velocity (m s$^{-1}$)")
    axes[1].legend()

    ds.W_OXTS.plot(ax=axes[2])
    add_labels(axes[2], "Vertical Velocity (m s$^{-1}$)")

    # Shortwave radiation
    ds.SW_DN_C.plot(ax=axes[3], label=r"SW Downwelling")
    ds.SW_UP_C.plot(ax=axes[3], label=r"SW Upwelling")
    axes[3].legend()

    # Longwave radiation
    ds.LW_DN_C.plot(ax=axes[3], label=r"LW Downwelling")
    ds.LW_UP_C.plot(ax=axes[3], label=r"LW Upwelling")
    add_labels(axes[3], "Irradiance (W m$^{-2}$)")
    axes[3].legend()

    # CPC Concentration
    ds.CPC_CONC.plot(ax=axes[4])
    add_labels(axes[4], "CPC Concentration (m$^{-3}$)")

    figures.append([fig, "quicklook"])

    # Not all flights have LICOR data
    try:
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex="all", figsize=[16, 15])
        # LICOR data
        ds.CO2_LICOR.plot(ax=axes[0], label=r"CO$_2$ LICOR")
        ds.H2O_LICOR.plot(ax=axes[0], label=r"H$_2$O LICOR")
        add_labels(axes[0], "Mole Fraction")
        axes[0].legend()

        axes[1].plot(ds.Time, derive.specific_humidity(ds))
        add_labels(axes[1], "Specific Humidity")

        figures.append([fig, "quicklook_LICOR"])
    except AttributeError:
        pass

    fig, ax = plt.subplots(figsize=[8, 5])

    ax.scatter(
        derive.calculate("equivalent_potential_temperature", ds),
        metpy.calc.specific_humidity_from_dewpoint(ds.PS_AIR, ds.TDEW_BUCK),
        alpha=0.1,
    )
    ax.set_xlabel(r"$\theta_e$")
    ax.set_ylabel("Specific Humidity")
    figures.append([fig, "paluch"])

    return figures


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
