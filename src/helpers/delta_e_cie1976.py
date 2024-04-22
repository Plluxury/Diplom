from colormath import color_diff_matrix
from colormath.color_objects import LabColor
import numpy


def delta_e_cie1976(color1: tuple, color2: tuple) -> float:
    """
    Calculate the CIE 1976 color difference between two colors.

    Parameters
        color1 : tuple
            RGB values of color1 in the form (R, G, B).
        color2 : tuple
            RGB values of color2 in the form (R, G, B).
    Returns
        float :
            The CIE 1976 color difference.
    """
    lab_color1 = LabColor(color1[2], color1[1], color1[0])
    lab_color2 = LabColor(color2[2], color2[1], color2[0])

    color1_vector = numpy.array([lab_color1.lab_l, lab_color1.lab_a, lab_color1.lab_b])
    color2_matrix = numpy.array([(lab_color2.lab_l, lab_color2.lab_a, lab_color2.lab_b)])

    delta_e = color_diff_matrix.delta_e_cie1976(color1_vector, color2_matrix)[0]

    return delta_e
