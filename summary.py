import matplotlib.pyplot as plt

import util
import profile


def main():
    flight_number = 330
    generate(flight_number)

    return


def generate(flight_number):
    dataset = util.load_flight(flight_number)

    plot_all(flight_number, dataset, 'leg', plot_leg)
    plot_all(flight_number, dataset, 'profile', plot_profile)

    print('Completed')

    return


def plot_all(flight_number, dataset, leg_type, plot_func):
    n = 0
    while True:
        try:
            idx = util.flight_leg_index(flight_number, leg_type, n)
            print(n)

            prefix = 'flight{}_{}{}'.format(flight_number, leg_type, n)
            plot_func(dataset, idx, prefix)
            n += 1
        except IndexError:
            break

    return


def plot_leg(dataset, idx, prefix):
    xmin, xmax = dataset.Time[idx.start], dataset.Time[idx.stop]

    # Temperature and Dewpoint
    dataset.TAT_ND_R[idx].plot(label=r'Temperature (K)')
    dataset.TDEW_BUCK[idx].plot(label=r'Dewpoint Temperature (K)')
    set_axes_and_labels(xmin, xmax, prefix, 'temperature')

    # Shortwave radiation
    dataset.SW_DN_C[idx].plot(label=r'SW Downwelling Irradiance (W m$^{-2}$)')
    dataset.SW_UP_C[idx].plot(label=r'SW Upwelling Irradiance (W m$^{-2}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'sw_fluxes')

    # Longwave radiation
    dataset.LW_DN_C[idx].plot(label=r'LW Downwelling Irradiance (W m$^{-2}$)')
    dataset.LW_UP_C[idx].plot(label=r'LW Upwelling Irradiance (W m$^{-2}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'lw_fluxes')

    # CPC Concentration
    dataset.CPC_CONC[idx].plot(label=r'CPC Concentration (m$^{-3}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'cpc')

    # Velocities
    dataset.U_OXTS[idx].plot(label=r'Zonal Velocity (m s$^{-1}$)')
    dataset.V_OXTS[idx].plot(label=r'Meridional Velocity (m s$^{-1}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'velocities')

    dataset.U_OXTS[idx].plot(label=r'Vertical Velocity (m s$^{-1}$)')
    set_axes_and_labels(xmin, xmax, prefix, 'vertical_wind')

    return


def plot_profile(dataset, idx, prefix):
    p = dataset.PS_AIR[idx]
    T = dataset.TAT_ND_R[idx] - 273.15
    Td = dataset.TDEW_BUCK[idx] - 273.15
    u = dataset.U_OXTS[idx]
    v = dataset.V_OXTS[idx]
    profile.skewt(p, T, Td, u, v)

    plt.savefig('figures/{}_{}.png'.format(prefix, 'skewt'))

    plt.close()

    return


def set_axes_and_labels(xmin, xmax, prefix, figure_name):
    plt.xlim(xmin, xmax)
    plt.xlabel('')
    plt.ylabel('')
    plt.legend()

    plt.savefig('figures/{}_{}.png'.format(prefix, figure_name))
    plt.close()

    return


if __name__ == '__main__':
    main()
