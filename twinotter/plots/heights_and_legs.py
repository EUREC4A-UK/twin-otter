from pathlib import Path

from tqdm import tqdm
import matplotlib.pyplot as plt

from .. import load_flight, load_segments


colors = {
    'level': 'cyan',
    'profile': 'magenta',
}


def main():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')
    argparser.add_argument('legs_file')
    argparser.add_argument('--show-gui', default=False, action="store_true")
    args = argparser.parse_args()

    generate(args.flight_data_path, args.legs_file, show_gui=args.show_gui)


def generate(flight_data_path, legs_file, show_gui=False):
    ds = load_flight(flight_data_path)
    legs = load_segments(legs_file)

    # Produce the basic time-height plot
    fig, ax1 = plt.subplots()
    ax1.plot(ds.Time, ds.ROLL_OXTS, color='k', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Roll Angle')
    ax2 = ax1.twinx()
    ax2.plot(ds.Time, ds.ALT_OXTS / 1000, color='k')
    ax2.set_ylabel('Altitude (km)')

    # For each leg overlay a coloured line onto the time-height plot
    for leg in tqdm(legs["segments"]):
        ds_section = ds.sel(Time=slice(leg["start"], leg["end"]))

        label = leg["kinds"][0]
        ax2.plot(ds_section.Time, ds_section.ALT_OXTS / 1000,
                 color=colors[label], linewidth=2, alpha=0.75)

    if hasattr(ax2, 'secondary_yaxis'):
        # `ax.secondary_yaxis` was added in matplotlib v3.1
        ax2_fl = ax2.secondary_yaxis(
            location=1.2,
            functions=(lambda y: (y*1000*3.281)/100, lambda x: x)
        )
        ax2_fl.set_ylabel(r"Flight level [100ft]")

    for label in ax1.get_xmajorticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment("right")

    if show_gui:
        plt.show()
    else:
        p = Path(flight_data_path)/"figures"/'height-time-with-legs.png'
        p.parent.mkdir(exist_ok=True)
        plt.savefig(str(p), bbox_inches="tight")


if __name__ == '__main__':
    main()
