import numpy as np


def deg2rad(deg):
    return np.pi * deg / 180.

def spherical2cartesian(two_angles, radius):
    alpha, beta = two_angles
    return (radius * np.sin(alpha) * np.cos(beta),
            radius * np.sin(alpha) * np.sin(beta),
            radius * np.cos(alpha))
