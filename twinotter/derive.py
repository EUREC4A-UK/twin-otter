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
