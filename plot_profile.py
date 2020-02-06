import matplotlib.pyplot as plt
from metpy.plots import SkewT

import util


def main():
    flight_number = 333
    leg_type = 'profile'
    leg_number = 0

    ds = util.load_flight(flight_number)
    p, T, Td, u, v = extract_data(ds, flight_number, leg_type, leg_number)

    skewt(p, T, Td, u, v)

    plt.show()

    return


def extract_data(ds, flight_number, leg_type, leg_number):
    idx = util.flight_leg_index(flight_number, leg_type, leg_number)
    p = ds.PS_AIR[idx]
    T = ds.TAT_ND_R[idx] - 273.15
    Td = ds.TDEW_BUCK[idx] - 273.15
    u = ds.U_OXTS[idx]
    v = ds.V_OXTS[idx]

    return p, T, Td, u, v


def skewt(p, T, Td, u, v):
    """

    Adapted from the Metpy advanced sounding example
    (https://unidata.github.io/MetPy/latest/examples/Advanced_Sounding.html#sphx-glr-examples-advanced-sounding-py)

    """
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig)

    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot.
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p, u, v)


    # Calculate LCL height and plot as black dot. Because `p`'s first value is
    # ~1000 mb and its last value is ~250 mb, the `0` index is selected for
    # `p`, `T`, and `Td` to lift the parcel from the surface. If `p` was inverted,
    # i.e. start from low value, 250 mb, to a high value, 1000 mb, the `-1` index
    # should be selected.
    #lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    #skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

    # Calculate full parcel profile and add to plot as black line
    #prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    #skew.plot(p, prof, 'k', linewidth=2)

    # Shade areas of CAPE and CIN
    #skew.shade_cin(p, T, prof, Td)
    #skew.shade_cape(p, T, prof)

    # An example of a slanted line at constant T -- in this case the 0
    # isotherm
    #skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    skew.ax.set_ylim(1000, 600)
    skew.ax.set_xlim(0, 60)

    return


if __name__ == '__main__':
    main()
