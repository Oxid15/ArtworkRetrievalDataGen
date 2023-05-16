import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

from datagen import Generator


# The folder with images to render
source_folder = os.path.join(BASE_DIR, "src")

# The folder to place renders
destination_folder = os.path.join(BASE_DIR, "dst")

# The angles and distance are the spherical coordinates of the camera
# given that the position of the object in the scene is (0,0,0)
# render_per_input times different angles and distances are sampled
# from these ranges
camera_angles_range = [[70, -60], [110, 60]]

camera_distance_range = [3, 5]

render_per_input = 2


if __name__ == "__main__":
    gen = Generator(
        src=source_folder,
        dest=destination_folder,
        camera_angles_range=camera_angles_range,
        camera_distance_range=camera_distance_range,
        render_per_input=render_per_input,
    ).run()
