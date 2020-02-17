"""Interactive flight track plot

Plot a variable of interest and the flight track then click on either figure
to mark the corresponding points on both figures.

> python -m twinotter.plots.interactive_flight_track /path/to/data
"""
import datetime
import tkinter

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs

from twinotter import load_flight
from twinotter.plots import plot_flight_path


def main(flight_data_path):
    ds = load_flight(flight_data_path)

    root = tkinter.Tk()
    root.wm_title("Interactive Flight Track")

    # Plot the main variable of interest
    # Change this to whatever variable you want or add additional figures here
    fig1, ax1a = plt.subplots()
    ax1a.plot(ds.Time, ds.ROLL_OXTS, linestyle='--', alpha=0.5)
    ax1a.set_label('Roll Angle')
    ax1b = ax1a.twinx()
    ax1b.plot(ds.Time, ds.ALT_OXTS/1000)
    ax1b.set_ylabel('Altitude (km)')

    # Plot flight path with colours for altitude
    fig2, ax2 = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()),)
    ax2.gridlines(draw_labels=True)
    ax2.coastlines()
    plot_flight_path(ax=ax2, ds=ds)

    fig1.tight_layout()
    fig2.tight_layout()

    # Save flight leg start and end points
    leg_times = []

    # Drag mouse from the start to the end of a leg and save the corresponding
    # times
    def highlight_leg(start, end):
        idx_start = find_nearest_point(start, ds.Time)
        idx_end = find_nearest_point(end, ds.Time)

        leg_times.append([format_timedelta(ds, idx_start),
                          format_timedelta(ds, idx_end)])

        print(leg_times)

        return

    # Add the figures to as TK window
    canvas = FigureCanvasTkAgg(fig1, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

    canvas = FigureCanvasTkAgg(fig2, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=1)

    # Add a span selector to the time-height plot to highlight legs
    selector = SpanSelector(
        ax1b, highlight_leg, direction='horizontal')

    def _quit():
        root.quit()  # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    button = tkinter.Button(master=root, text="Quit", command=_quit)
    button.grid(row=1, column=1)

    textbox = tkinter.Text(master=root)
    textbox.grid(row=1, column=0)

    tkinter.mainloop()

    return


def find_nearest_point(value, points):
    return int(np.argmin(np.abs(value-points)))


def format_timedelta(ds, idx):
    return str(datetime.timedelta(seconds=float(ds.Time[idx])))


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')

    args = argparser.parse_args()

    main(flight_data_path=args.flight_data_path)
