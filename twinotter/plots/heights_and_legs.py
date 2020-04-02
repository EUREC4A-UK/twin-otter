import matplotlib.pyplot as plt
import pandas as pd

import twinotter


colors = {
    'Leg': 'cyan',
    'Profile': 'magenta',
}


def main():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')
    argparser.add_argument('legs_file')
    args = argparser.parse_args()

    generate(args.flight_data_path, args.legs_file)

    return


def generate(flight_data_path, legs_file):
    ds = twinotter.load_flight(flight_data_path)
    legs = pd.read_csv(legs_file)

    # Produce the basic time-height plot
    fig, ax1 = plt.subplots()
    ax1.plot(ds.Time, ds.ROLL_OXTS, color='k', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Roll Angle')
    ax2 = ax1.twinx()
    ax2.plot(ds.Time, ds.ALT_OXTS / 1000, color='k')
    ax2.set_ylabel('Altitude (km)')

    # For each leg overlay a coloured line onto the time-height plot
    for n in range(legs.shape[0]):
        print(n)
        leg_type = legs['Label'][n]
        start = legs['Start'][n]
        end = legs['End'][n]

        idx_start = twinotter.index_from_time(start, ds.Time)
        idx_end = twinotter.index_from_time(end, ds.Time)
        idx = slice(idx_start, idx_end)

        ax2.plot(ds.Time[idx], ds.ALT_OXTS[idx] / 1000,
                 color=colors[leg_type], linewidth=2, alpha=0.75)

    plt.savefig('flight{}/height-time-with-legs.png'.format(
        ds.attrs['flight_number']))

    return


if __name__ == '__main__':
    main()
