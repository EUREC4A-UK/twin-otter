import numpy as np


def geocolor(ax, ds, projection):
    """
    https://unidata.github.io/python-gallery/examples/mapping_GOES16_TrueColor.html
    """
    maxval = 120
    gamma = 2.2

    red = (ds.refl_0_65um_nom / maxval) ** (1/gamma)
    green = (ds.refl_0_86um_nom / maxval) ** (1/gamma)
    blue = (ds.refl_0_47um_nom / maxval) ** (1/gamma)

    true_green = 0.45*red + 0.1*green + 0.45*blue

    rgb = np.dstack([red, true_green, blue])

    x = ds.longitude
    y = ds.latitude
    return ax.imshow(
        rgb,
        origin='upper',
        extent=(x.min(), x.max(), y.min(), y.max()),
        transform=projection)


