from core.models import Color


def _weighted_euclidian(c1: Color, c2: Color) -> float:
    """
    Calculate the distance between two colors using a weighted Euclidian metric
    :param c1: color 1
    :param c2: color 2
    :return: The distance between the two colors
    """
    r_bar = (c1.red + c2.red) / 2
    dr = c1.red - c2.red
    dg = c1.green - c2.green
    db = c1.blue - c2.blue
    return (2 + r_bar / 256) * dr * dr + 4 * dg * dg + (2 + (255 - r_bar) / 256) * db * db


def color_distance(c1: Color, c2: Color) -> float:
    """
    Calculate the distance between two colors
    :param c1: color 1
    :param c2: color 2
    :return: The distance between the two colors
    """
    return _weighted_euclidian(c1, c2)


# Recipe borrowed from easyrgb.com
def _rgb_to_xyz(color: Color) -> (float, float, float):
    """
    Converts an RGB color to XYZ
    :param color: RGB color
    :return: 3-tuple containing XYZ values
    """
    var_r = color.red / 255
    var_g = color.green / 255
    var_b = color.blue / 255

    values = (var_r, var_g, var_b)
    new_values = []

    for value in values:
        if value > 0.04045:
            new_values.append(((value + 0.055) / 1.055) ** 2.4)
        else:
            new_values.append(value / 12.92)

    new_values = [val * 100 for val in new_values]
    coeffs = [[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]
    xyz = [sum([val * coeff for val, coeff in zip(new_values, coeffs[i])]) for i in range(3)]

    return tuple(xyz)


# Recipe borrowed from easyrgb.com
def _xyz_to_cielab(xyz: (float, float, float)) -> (float, float, float):
    """
    Converts XYZ color to CIEL*ab color
    :param xyz: 3-tuple containing XYZ color
    :return: 3-tuple containing CIEL*ab color
    """
    # Using Illuminant D65
    x_norm = 95.047
    y_norm = 100
    z_norm = 108.883

    x, y, z = xyz
    x /= x_norm
    y /= y_norm
    z /= z_norm

    values = (x, y, z)
    new_values = []

    for value in values:
        if value > 0.008856:
            new_values.append(value ** (1 / 3))
        else:
            new_values.append(value * 7.787 + 16 / 116)

    x, y, z = new_values

    return 116 * y - 16, 500 * (x - y), 200 * (y - z)


# Recipe borrowed from easyrgb.com
def _cie_delta_e_sq(c1: Color, c2: Color) -> float:
    """
    Calculate the (squared) distance between two colors using the CIEL*ab Delta E* metric
    :param c1: color 1
    :param c2: color 2
    :return: The distance between the two colors
    """
    lab1 = _xyz_to_cielab(_rgb_to_xyz(c1))
    lab2 = _xyz_to_cielab(_rgb_to_xyz(c2))

    return sum((elem1 - elem2) ** 2 for elem1, elem2 in zip(lab1, lab2))
