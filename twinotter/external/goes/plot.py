import numpy as np


def geocolor(ax, ds, projection):
    """
    Follows
    https://unidata.github.io/python-gallery/examples/mapping_GOES16_TrueColor.html

    Use origin="lower" for imshow because we are using an interpolated grid of data not
    the native layout for data used in the link.
    """
    maxval = 120
    gamma = 2.2

    red = (ds.refl_0_65um_nom / maxval) ** (1 / gamma)
    green = (ds.refl_0_86um_nom / maxval) ** (1 / gamma)
    blue = (ds.refl_0_47um_nom / maxval) ** (1 / gamma)

    true_green = 0.45 * red + 0.1 * green + 0.45 * blue

    color_array = np.dstack([red, true_green, blue])

    x = ds.longitude
    y = ds.latitude

    return ax.imshow(
        color_array,
        origin="lower",
        extent=[x.min(), x.max(), y.min(), y.max()],
        transform=projection,
    )
