import numpy as np
import scipy.constants

import xarray as xr
from metpy import constants
import metpy.calc


# TODO: As we add more functions to this there will be multiple paths to calculate
# a single variable. Need to decide a way of figuring out the preferred path. e.g.
# the current specific humidity calculation uses the LICOR data
# TODO: add an avoid/ignore argument so that we can avoid calculations using broken
# measurements
# TODO: Add an option to append intermediate results to the dataset
def calculate(name, ds):
    """Calculate a variable from the given dataset

    Args:
        name (str): The CF standard name
        ds (xarray.DataSet): The twin-otter MASIN dataset

    Returns:
        xarray.DataArray:

    Raises:
        ValueError: If the requested variable (or a variable required to calculate it)
            is not available in the dataset
    """
    # If the variable is in the dataset, just return it
    if name in ds:
        return ds[name]

    # If the variable name is in the translation table return the variable but renamed
    elif name in translation_table:
        result = ds[translation_table[name]].copy()
        _rename_xarray(result, name)
        return result

    # Otherwise calculate the requested variable using variables in the dataset
    elif name in available:
        arguments = []
        for argument_name in available[name]["arguments"]:
            arguments.append(calculate(argument_name, ds))

        result = available[name]["function"](*arguments)

        _rename_xarray(result, name)
        return result

    else:
        raise ValueError("Can not calculate {} from dataset".format(name))


def specific_humidity(dataset):

    x_h20 = dataset.H2O_LICOR
    q = (
        constants.water_molecular_weight
        * x_h20
        / (
            constants.water_molecular_weight * x_h20
            + constants.dry_air_molecular_weight * (1 - x_h20)
        )
    )

    return q


def along_track_wind(ds):
    angle = np.arctan2(ds.U_OXTS, ds.V_OXTS)
    magnitude = np.sqrt(ds.U_OXTS ** 2 + ds.V_OXTS ** 2)

    flight_angle = np.deg2rad(ds.HDG_OXTS)

    return magnitude * np.cos(angle - flight_angle)


def combine_temperatures(nondeiced_temperature, deiced_temperature):
    # Use the non-deiced temperature by default
    temperature = nondeiced_temperature.copy()

    # Replace with the deiced temperature where the non-deiced temperature is below
    # freezing
    frozen = np.where(temperature < scipy.constants.zero_Celsius)
    temperature[frozen] = deiced_temperature[frozen]

    return temperature


def _rename_xarray(array, name):
    array.rename(name)
    array.attrs["standard_name"] = name

    if "long_name" in array.attrs:
        del array.attrs["long_name"]


def _pint_to_xarray(quantity, ds, name):
    """The metpy functions return pint quantities but we want a DataArray consistent
    with the input DataSet

    Args:
        quantity (pint.Quantity):
        ds (xarray.DataSet):
        name (str):

    Returns:
        xarray.DataArray:
    """
    return xr.DataArray(
        data=quantity.magnitude,
        coords=ds.coords,
        dims=ds.dims,
        name=name,
        attrs=dict(
            long_name=name,
            units=quantity.units.format_babel(),
        ),
        indexes=ds.indexes,
    )


# A dictionary mapping variables that can be calculated to the functions to calculate
# them and arguments required as input to those functions
available = dict(
    air_temperature=dict(
        function=combine_temperatures,
        arguments=["TAT_ND_R", "TAT_DI_R"],
    ),
    air_potential_temperature=dict(
        function=metpy.calc.potential_temperature,
        arguments=["air_pressure", "air_temperature"],
    ),
    equivalent_potential_temperature=dict(
        function=metpy.calc.equivalent_potential_temperature,
        arguments=["air_pressure", "air_temperature", "dew_point_temperature"],
    ),
    humidity_mixing_ratio=dict(
        function=metpy.calc.mixing_ratio_from_relative_humidity,
        arguments=["air_pressure", "air_temperature", "relative_humidity"],
    ),
    relative_humidity=dict(
        function=metpy.calc.relative_humidity_from_dewpoint,
        arguments=["air_temperature", "dew_point_temperature"],
    ),
    virtual_potential_temperature=dict(
        function=metpy.calc.virtual_temperature,
        arguments=["air_potential_temperature", "humidity_mixing_ratio"],
    ),
)

# Mapping from twin-otter variable names to CF standard names. This was generated from
# an existing MASIN file. It doesn't work to just look at the standard names in the
# DataSet because some standard names are duplicated and have been removed from this
# mapping. e.g. air_temperature refers to temperature from both the deiced and
# non-deiced measurements so needs to be calculated separately
translation_table = dict(
    dew_point_temperature="TDEW_BUCK",
    brightness_temperature="BTHEIM_U",
    air_pressure="PS_AIR",
    # Q_AIR has no standard name
    downwelling_shortwave_flux_in_air="SW_DN_C",
    upwelling_shortwave_flux_in_air="SW_UP_C",
    downwelling_longwave_flux_in_air="LW_DN_C",
    upwelling_longwave_flux_in_air="LW_UP_C",
    # relative_humidity="HUM_ROSE",
    mole_fraction_of_water_vapor_in_air="H2O_LICOR",
    mole_fraction_of_carbon_dioxide_in_air="CO2_LICOR",
    flow_rate="L_FLOW_S",
    # CPC_CONC has no standard name
    latitude="LAT_OXTS",
    longitude="LON_OXTS",
    altitude="ALT_OXTS",
    platform_speed_wrt_ground_northward="VELN_OXTS",
    platform_speed_wrt_ground_eastward="VELE_OXTS",
    platform_speed_wrt_ground_upward="VELZ_OXTS",
    platform_roll_angle="ROLL_OXTS",
    platform_pitch_angle="PTCH_OXTS",
    platform_yaw_angle="HDG_OXTS",
    northward_wind="V_OXTS",
    eastward_wind="U_OXTS",
    upward_air_velocity="W_OXTS",
)

# Duplicate CF standard names
# TODO: write functions to combine these observations

# platform_speed_wrt_air="TAS_DI_AIR",
# platform_speed_wrt_air="TAS_ND_AIR",
# platform_speed_wrt_air="TAS",

# height="HGT_RADR1",
# height="HGT_RADR2",
