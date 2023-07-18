from typing import Tuple

import numpy as np


def deg2rad(deg: float):
    return np.pi * deg / 180.

def spherical2cartesian(two_angles: Tuple[float, float], radius: float) -> Tuple[float, float, float]:
    alpha, beta = two_angles
    return (radius * np.sin(alpha) * np.cos(beta),
            radius * np.sin(alpha) * np.sin(beta),
            radius * np.cos(alpha))
