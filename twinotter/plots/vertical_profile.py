import matplotlib.pyplot as plt
from metpy.plots import SkewT
import dateutil.parser

from .. import load_flight


def main(
    flight_data_path, filter_by=dict(time_interval=(None, None)), plot_type="skewt"
):
    ds = load_flight(flight_data_path, debug=True)

    if "time_interval" in filter_by:
        ds_filtered = ds.sel(Time=slice(*filter_by["time_interval"]))
        if ds_filtered.Time.count() == 0:
            raise Exception(
                "Nothing found in selected time range, data"
                " time range: [{} : {}]".format(
                    ds.Time.min().values, ds.Time.max().values
                )
            )
        else:
            ds = ds_filtered
        title = "flight {}, extract: {} to {}".format(
            ds.flight_number, *filter_by["time_interval"]
        )
    elif "leg" in filter_by:
        raise NotImplementedError("Filter by leg not currently implemented")
        # ds = _filter_by_flight_leg(ds, flight_data_path, *filter_by['leg'])
        title = "leg: {} {}".format(*filter_by["leg"])
    else:
        raise NotImplementedError

    alt, p, T, Td, u, v = _extract_plot_data(ds)

    if plot_type == "skewt":
        skewt(p, T, Td, u, v)
    elif plot_type == "linear_altitude":
        _plot_linear_altitude(ds)
    else:
        raise NotImplementedError(plot_type)

    plt.title(title)
    plt.show()


def _plot_linear_altitude(ds):
    fig, ax = plt.subplots()

    ds_ = ds.swap_dims(dict(Time="ALT_OXTS"))

    ds_.TAT_ND_R.plot(y="ALT_OXTS", ax=ax, color="green")
    ds_.TDEW_BUCK.plot(y="ALT_OXTS", ax=ax, color="red")


def _extract_plot_data(ds):
    p = ds.PS_AIR
    T = ds.TAT_ND_R - 273.15
    Td = ds.TDEW_BUCK - 273.15
    u = ds.U_OXTS
    v = ds.V_OXTS
    alt = ds.HGT_RADR1

    return alt, p, T, Td, u, v


def skewt(p, T, Td, u, v):
    """

    Adapted from the Metpy advanced sounding example
    (https://unidata.github.io/MetPy/latest/examples/Advanced_Sounding.html#sphx-glr-examples-advanced-sounding-py)

    """
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig)

    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot.
    skew.plot(p, T, "r")
    skew.plot(p, Td, "g")

    # Calculate LCL height and plot as black dot. Because `p`'s first value is
    # ~1000 mb and its last value is ~250 mb, the `0` index is selected for
    # `p`, `T`, and `Td` to lift the parcel from the surface. If `p` was inverted,
    # i.e. start from low value, 250 mb, to a high value, 1000 mb, the `-1` index
    # should be selected.
    # lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    # skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

    # Calculate full parcel profile and add to plot as black line
    # prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    # skew.plot(p, prof, 'k', linewidth=2)

    # Shade areas of CAPE and CIN
    # skew.shade_cin(p, T, prof, Td)
    # skew.shade_cape(p, T, prof)

    # An example of a slanted line at constant T -- in this case the 0
    # isotherm
    # skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    skew.ax.set_ylim(1050, p.min())
    skew.ax.set_xlim(-10, 30)

    return fig


if __name__ == "__main__":

    def _flight_leg(s):
        leg_type, leg_number = s.split(":")
        return leg_type, int(leg_number)

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("flight_data_path")
    argparser.add_argument(
        "--time-interval",
        help="e.g. 2020-01-17T14:00Z 2020-01-17T15:00Z",
        nargs=2,
        type=dateutil.parser.parse,
    )
    argparser.add_argument("--leg", help="e.g. profile:0", type=_flight_leg)
    argparser.add_argument(
        "--type", choices=["skewt", "linear_altitude"], default="skewt"
    )

    args = argparser.parse_args()

    kws = dict(plot_type=args.type)

    if args.time_interval is not None:
        kws["filter_by"] = dict(time_interval=args.time_interval)
    elif args.leg:
        kws["filter_by"] = dict(leg=args.leg)
    else:
        raise NotImplementedError

    main(args.flight_data_path, **kws)
