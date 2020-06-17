import xarray as xr
from metpy import constants
import metpy.calc


def calculate(name, ds):

    # If the variable is in the dataset, just return it
    if name in ds:
        return ds[name]

    # Otherwise calculate the requested variable using variables in the dataset
    elif name in available:
        arguments = []
        for argument_name in available[name]["arguments"]:
            arguments.append(calculate(argument_name, ds))

        # Metpy functions return a pint.Quantity so convert to an xarray.DataArray
        # consistent with the input dataset
        quantity = available[name]["function"](*arguments)
        return _pint_to_xarray(quantity, ds, name)

    else:
        raise ValueError("Can not calculate {} from dataset".format(name))


def specific_humidity(dataset):

    x_h20 = dataset.H2O_LICOR
    q = constants.water_molecular_weight * x_h20 / (
            constants.water_molecular_weight * x_h20 +
            constants.dry_air_molecular_weight*(1-x_h20)
    )

    return q


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
    potential_temperature=dict(
        function=metpy.calc.potential_temperature,
        arguments=["pressure", "temperature"]
    )
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
    relative_humidity="HUM_ROSE",
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
# air_temperature="TAT_DI_R",
# air_temperature="TAT_ND_R",

# platform_speed_wrt_air="TAS_DI_AIR",
# platform_speed_wrt_air="TAS_ND_AIR",
# platform_speed_wrt_air="TAS",

# height="HGT_RADR1",
# height="HGT_RADR2",
