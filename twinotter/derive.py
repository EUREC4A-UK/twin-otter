from metpy import constants


def specific_humidity(dataset):

    x_h20 = dataset.H2O_LICOR
    q = constants.water_molecular_weight * x_h20 / (
            constants.water_molecular_weight * x_h20 +
            constants.dry_air_molecular_weight*(1-x_h20)
    )

    return q
