# Tools for working with Twin-Otter data

Generate a summary .csv of flight data within a directory

    $> python -m twinotter.generate_summary <data_directory>

To plot a flight track with altitude:

    $> python -m twinotter.plots.basic_flight_track <flight_data_path>

Interactive flight track with leg labelling:

    $> python -m twinotter.plots.interactive_flight_track <flight_data_path>
