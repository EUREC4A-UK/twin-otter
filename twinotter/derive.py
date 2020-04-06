from twinotter import constants


def specific_humidity(dataset):

    x_h20 = dataset.H2O_LICOR
    q = constants.m_h20 * x_h20 / (constants.m_h20 * x_h20 + constants.m_d*(1-x_h20))

    return q
