from bokeh.palettes import Viridis256
import numpy as np


def get_viridis_pallette(n: int):
    """Creates a viridis pallette with n colors"""
    idx = np.round(np.linspace(0, len(Viridis256) - 1, n, dtype="int"))
    viridis = [Viridis256[i] for i in idx]
    return viridis


def format_string(s):
    # Replace underscores with spaces
    s = s.replace("_", " ")

    # Capitalize first letter of each word
    s = s.title()

    return s
