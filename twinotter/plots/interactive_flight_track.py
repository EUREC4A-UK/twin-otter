"""Interactive flight track plot

Plot a variable of interest and the flight track then click on either figure
to mark the corresponding points on both figures.

> python -m twinotter.plots.interactive_flight_track /path/to/data
"""
import datetime
import tkinter
from tkinter import filedialog

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs
import pandas as pd

from twinotter import load_flight
from twinotter.plots import plot_flight_path


def main():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('flight_data_path')

    args = argparser.parse_args()

    start_gui(flight_data_path=args.flight_data_path)

    return


def start_gui(flight_data_path):
    ds = load_flight(flight_data_path)

    root = tkinter.Tk()
    root.wm_title("Interactive Flight Track: Flight {}".format(
        ds.attrs['flight_number']))

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
    leg_info = pd.DataFrame(columns=['Label', 'Start', 'End'])

    # Add the figures to as TK window
    figure_area = tkinter.Frame()
    figure_area.grid(row=0, column=0, columnspan=2)

    canvas = FigureCanvasTkAgg(fig1, master=figure_area)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

    canvas = FigureCanvasTkAgg(fig2, master=figure_area)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=1)

    # Add an area for buttons beneath the figures
    button_area = tkinter.Canvas(root)
    button_area.grid(row=1, column=1)

    def _save():
        filename = filedialog.asksaveasfilename(
            initialfile="flight{}-legs.csv".format(ds.attrs['flight_number']))
        leg_info.to_csv(filename)

        return

    save_button = tkinter.Button(master=button_area, text="Save", command=_save)
    save_button.grid(row=0, column=0)

    def _quit():
        root.quit()  # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

        return

    quit_button = tkinter.Button(master=button_area, text="Quit", command=_quit)
    quit_button.grid(row=0, column=1)

    # Use an Entry textbox to label the legs
    textbox = tkinter.Entry(master=root)
    textbox.grid(row=1, column=0)

    # Add a span selector to the time-height plot to highlight legs
    # Drag mouse from the start to the end of a leg and save the corresponding
    # times
    def highlight_leg(start, end):
        nonlocal leg_info

        label = textbox.get()
        idx_start = find_nearest_point(start, ds.Time)
        idx_end = find_nearest_point(end, ds.Time)

        leg_info = leg_info.append({
            'Label': label,
            'Start': format_timedelta(ds, idx_start),
            'End': format_timedelta(ds, idx_end)
        }, ignore_index=True)

        return

    selector = SpanSelector(
        ax1b, highlight_leg, direction='horizontal')

    tkinter.mainloop()

    return


def find_nearest_point(value, points):
    return int(np.argmin(np.abs(value-points)))


def format_timedelta(ds, idx):
    return str(datetime.timedelta(seconds=float(ds.Time[idx])))


if __name__ == '__main__':
    main()
