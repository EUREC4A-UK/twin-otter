"""Interactive flight track plot

Plot a variable of interest and the flight track then click on either figure
to mark the corresponding points on both figures.

.. code-block:: console

    $ python -m twinotter.plots.interactive_flight_track /path/to/data
"""

import datetime
import tkinter
from tkinter import filedialog, ttk

import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from .. import load_flight
from . import flight_path


yaml.Dumper.ignore_aliases = lambda *args: True

masin_date_format = "{year:04d}{month:02d}{day:02d}"
masin_time_format = "{hour:02d}:{minute:02d}:{second:02d} UTC"

yaml_file_format = (
    "EUREC4A_TO_Flight-Segments_{year:04d}{month:02d}{day:02d}_{version}.yaml"
)


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("flight_data_path")

    args = argparser.parse_args()

    ds = load_flight(flight_data_path=args.flight_data_path)

    root = tkinter.Tk()
    app = FlightPhaseGenerator(ds, root)
    app.mainloop()
    root.destroy()

    return


class FlightPhaseGenerator(tkinter.Frame):
    def __init__(self, ds, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.grid()

        self.ds = ds
        self.flight_information = flight_information(ds)

        # Use datetime functionality as xarray and pandas makes this difficult
        self.time = pd.to_datetime(self.ds.Time.values).to_pydatetime()

        # Flight leg times will be recorded as time since the start of the flight day
        self.flight_day_start = pd.to_datetime(
            ds.Time[0].dt.floor("D").data
        ).to_pydatetime()

        entries = {}
        for n, entry_label in enumerate(self.flight_information):
            label = ttk.Label(self, text=entry_label)
            entry = ttk.Entry(self)

            entry.insert(tkinter.END, self.flight_information[entry_label])

            label.grid(row=n, column=0)
            entry.grid(row=n, column=1)

            entries[entry_label] = entry

        self.quit_button = ttk.Button(self, text="Start", command=self.start)
        self.quit_button.grid(row=n + 1, column=0, columnspan=2)

    def start(self):
        self.root = tkinter.Tk()
        self.root.wm_title(
            "Interactive Flight Track: Flight {}".format(self.ds.attrs["flight_number"])
        )

        # Plot the main variable of interest
        # Change this to whatever variable you want or add additional figures here
        fig, self.ax1 = plt.subplots()
        self.ax1.plot(self.ds.Time, self.ds.ROLL_OXTS, linestyle="--", alpha=0.5)
        self.ax1.set_label("Roll Angle")
        self.ax2 = self.ax1.twinx()
        self.ax2.plot(self.ds.Time, self.ds.ALT_OXTS / 1000)
        self.ax2.set_ylabel("Altitude (km)")

        fig.tight_layout()

        # Add the figures to the TK window
        self.figure_area = tkinter.Frame(self.root)
        self.figure_area.grid(row=0, column=0, columnspan=2)

        canvas = FigureCanvasTkAgg(fig, master=self.figure_area)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=2)

        # Add an area for buttons beneath the figures
        self.button_area = tkinter.Canvas(self.root)
        self.button_area.grid(row=1, column=1)

        save_button = tkinter.Button(
            master=self.button_area, text="Save", command=self.save
        )
        save_button.grid(row=0, column=0)

        self.quit_button = tkinter.Button(
            master=self.button_area, text="Quit", command=self.quit
        )
        self.quit_button.grid(row=0, column=1)

        # Use an Entry textbox to label the legs
        self.textbox = tkinter.Entry(master=self.root)
        self.textbox.grid(row=1, column=0)

        self.selector = SpanSelector(
            self.ax2, self.highlight_leg, direction="horizontal"
        )

    def save(self):
        year = self.flight_day_start.year
        month = self.flight_day_start.month
        day = self.flight_day_start.day
        filename = filedialog.asksaveasfilename(
            initialfile=yaml_file_format.format(
                year=year, month=month, day=day, version="0.1"
            )
        )
        with open(filename, "w") as f:
            f.write(
                yaml.dump(
                    self.flight_information, default_flow_style=False, sort_keys=False
                )
            )

    # Add a span selector to the time-height plot to highlight legs
    # Drag mouse from the start to the end of a leg and save the corresponding
    # times
    def highlight_leg(self, start, end):
        self.ax2.axvspan(start, end, alpha=0.25, color="r")
        start = _convert_wacky_date_format(start)
        end = _convert_wacky_date_format(end)

        idx_start = find_nearest_point(start, self.time)
        idx_end = find_nearest_point(end, self.time)

        kinds = self.textbox.get().split(", ")
        self.flight_information["segments"].append(
            dict(
                kinds=kinds,
                name="",
                irregularities=[],
                segment_id=self.flight_information["flight_id"] + "_",
                start=self.time[idx_start],
                end=self.time[idx_end],
            )
        )

        self.flight_information["segments"].sort(key=lambda x: x["start"])

        return


def flight_information(ds):
    date = datetime.datetime.strptime(ds.attrs["data_date"], "%Y%m%d").date()
    start_time = datetime.datetime.strptime(
        ds.attrs["time_coverage_start"], "%H:%M:%S UTC"
    ).time()
    end_time = datetime.datetime.strptime(
        ds.attrs["time_coverage_end"], "%H:%M:%S UTC"
    ).time()

    start_time = datetime.datetime.combine(date, start_time)
    end_time = datetime.datetime.combine(date, end_time)

    flight_number = int(ds.attrs["flight_number"])
    return dict(
        name="RF{:02d}".format(flight_number - 329),
        mission="EUREC4A",
        platform="TO",
        flight_id="TO-{:04d}".format(flight_number),
        contacts=[],
        date=date,
        flight_report="",
        takeoff=start_time,
        landing=end_time,
        events=[],
        remarks=[ds.attrs["comment"]],
        segments=[],
    )


def find_nearest_point(value, points):
    return int(np.argmin(np.abs(value - points)))


# Zeroth datetime in twinotter MASIN files
# TODO: This is not the same as the first files we had because it was updated to be
# consistent with EUREC4A. We should be able to read this from the file/dataset rather
# than assume it
t0 = datetime.datetime(1970, 1, 1)


def _convert_wacky_date_format(wacky_time):
    # The twinotter MASIN data is loaded in with a datetime coordinate but when this is
    # used on the interactive plot the value returned from the click is in days from the
    # "zeroth" datetime. Use this zeroth datetime (t0) to get the date again.
    return t0 + datetime.timedelta(days=wacky_time)


if __name__ == "__main__":
    main()
