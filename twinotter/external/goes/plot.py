import numpy as np


def geocolor(ax, ds, projection):
    """
    Follows
    https://unidata.github.io/python-gallery/examples/mapping_GOES16_TrueColor.html

    Fixes to allow plotting an RGB image with 2d x/y coordinates
    https://github.com/matplotlib/matplotlib/issues/4277#issuecomment-594420340
    https://stackoverflow.com/questions/22222733/how-to-plot-an-irregular-spaced-rgb-image-using-python-and-basemap
    """
    maxval = 120
    gamma = 2.2

    red = (ds.refl_0_65um_nom / maxval) ** (1/gamma)
    green = (ds.refl_0_86um_nom / maxval) ** (1/gamma)
    blue = (ds.refl_0_47um_nom / maxval) ** (1/gamma)

    true_green = 0.45*red + 0.1*green + 0.45*blue

    color_array = np.array(
        [color.values.flatten() for color in [red, true_green, blue]]).transpose()

    x = get_corners(ds.longitude)
    y = get_corners(ds.latitude)

    return ax.pcolormesh(
        x,
        y,
        np.ones_like(red),
        color=color_array,
        transform=projection,
    )


def get_corners(coordinate):
    nx, ny = coordinate.shape
    corners = np.zeros([nx+1, ny+1])

    # Interpolate in the middle (average of the four surrounding points)
    corners[1:-1, 1:-1] = 0.25 * (
            coordinate[:-1, :-1] +
            coordinate[1:, :-1] +
            coordinate[:-1, 1:] +
            coordinate[1:, 1:]
    )

    # Extrapolate round the edges
    corners[0, 1:-1] = (
            0.75 * (coordinate[0, 1:] + coordinate[0, :-1]) -
            0.25 * (coordinate[1, 1:] + coordinate[0, :-1])
    )
    corners[-1, 1:-1] = (
            0.75 * (coordinate[-1, 1:] + coordinate[-1, :-1]) -
            0.25 * (coordinate[-2, 1:] + coordinate[-2, :-1])
    )
    corners[1:-1, 0] = (
            0.75 * (coordinate[1:, 0] + coordinate[:-1, 0]) -
            0.25 * (coordinate[1:, 1] + coordinate[:-1, 0])
    )
    corners[1:-1, -1] = (
            0.75 * (coordinate[1:, -1] + coordinate[:-1, -1]) -
            0.25 * (coordinate[1:, -2] + coordinate[:-1, -2])
    )

    # Double extrapolation for the corners
    corners[0, 0] = (
            2 * coordinate[0, 0] - 0.5 * (coordinate[0, 1] + coordinate[1, 0]))
    corners[0, -1] = (
            2 * coordinate[0, -1] - 0.5 * (coordinate[0, -2] + coordinate[1, -1]))
    corners[-1, 0] = (
            2 * coordinate[-1, 0] - 0.5 * (coordinate[-1, 1] + coordinate[-2, 0]))
    corners[-1, -1] = (
            2 * coordinate[-1, -1] - 0.5 * (coordinate[-1, -2] + coordinate[-2, -1]))

    return corners


