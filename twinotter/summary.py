"""
Check a directory for core_masin netCDF files and generate a summary .csv file
of the flights in these files

> python -m twinotter.summary /path/to/data /path/to/summary.csv
"""
import datetime
from pathlib import Path

import parse
import pandas as pd
import xarray as xr

from . import generate_file_path, MASIN_CORE_FORMAT

time_format = "{hours:02d}:{minutes:02d}:{seconds:02d} UTC"


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("flight_data_path")
    argparser.add_argument("flight_summary_path")

    args = argparser.parse_args()

    generate(
        flight_data_path=args.flight_data_path,
        flight_summary_path=args.flight_summary_path,
    )

    return


def generate(flight_data_path, flight_summary_path):
    # Get a list of netCDF files in the obs/ folder which match the expected
    # file pattern
    fn_pattern = MASIN_CORE_FORMAT.format(
        date="*", revision="*", flight_num="*", freq="*"
    )

    file_paths = list(Path(flight_data_path).rglob(fn_pattern))

    # Check if the flight summary file already exists
    if Path(flight_summary_path).exists():
        flight_summary = pd.read_csv(Path(flight_summary_path))

        for index, entry in flight_summary.iterrows():
            # Get the filename of existing entries in flight_information.csv
            file_path = generate_file_path(
                flight_number=entry["Flight Number"],
                date=entry["Date"],
                frequency=entry["Frequency"],
                revision=entry["Revision"],
                flight_data_path=flight_data_path,
            )

            # Check which files are already contained in the .csv
            if file_path in file_paths:
                print("{} already in .csv".format(file_path.name))
                file_paths.remove(file_path)

            # Other files in the .csv but not in the folder
            else:
                print("{} not available".format(file_path.name))

    else:
        flight_summary = pd.DataFrame(
            columns=["Flight Number", "Date", "Start", "End", "Revision", "Frequency"]
        )

    # Remaining files are present but not in the .csv
    # Add these new files to the .csv
    for path in file_paths:
        # Get date, flight number, revision and frequency from the filename
        flight_info = parse.parse(MASIN_CORE_FORMAT, path.name)

        # Format the date so it is more readable in the csv
        date = flight_info["date"]
        YYYY, MM, DD = int(date[0:4]), int(date[4:6]), int(date[6:8])
        date = datetime.datetime(YYYY, MM, DD)

        # Extract flight start and end from the netCDF file
        dataset = xr.open_dataset(path, decode_times=False)
        start = extract_time(dataset, "time_coverage_start")
        end = extract_time(dataset, "time_coverage_end")

        # Add flight information to .csv
        flight_summary = flight_summary.append(
            {
                "Flight Number": int(flight_info["flight_num"]),
                "Date": date.strftime("%Y-%m-%d"),
                "Start": str(start),
                "End": str(end),
                "Revision": int(flight_info["revision"]),
                "Frequency": int(flight_info["freq"]),
            },
            ignore_index=True,
        )

    flight_summary.sort_values("Flight Number", inplace=True)
    print(flight_summary)

    # Overwrite the old csv
    flight_summary.to_csv(flight_summary_path, index=False)

    return


def extract_date(dataset):
    # Get date, flight number, revision and frequency from the filename
    flight_info = parse.parse(MASIN_CORE_FORMAT, dataset.attrs["source_file"].name)

    date = flight_info["date"]
    YYYY, MM, DD = int(date[0:4]), int(date[4:6]), int(date[6:8])
    return datetime.datetime(YYYY, MM, DD)


def extract_time(dataset, name):
    time = dataset.attrs[name]

    # parse returns a dictionary when the format string has named entries.
    # use .named to get the dictionary and pass directly as keyword arguments
    # to datetime.timedelta
    return datetime.timedelta(**parse.parse(time_format, time).named)


if __name__ == "__main__":
    main()
