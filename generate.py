import os
import logging
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

from datagen import Generator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

args = {
    # The folder with images to render
    "src": os.path.join(BASE_DIR, "src"),
    # The folder to place renders
    # The "image" folder will be created there
    "dst": os.path.join(BASE_DIR, "dst"),
    # The angles and distance are the spherical coordinates of the camera
    # given that the position of the object in the scene is (0,0,0)
    # render_per_input times different angles and distances are sampled
    # from these ranges
    "camera_angles_range_v": (90, 90),
    "camera_angles_range_h": (-60, 60),
    "camera_distance_range": (3, 5),
    "render_per_input": 2,
    "max_images_to_render": 100,
    # Creates the table linking original images with rendered
    "generate_table": True,
    # Creates the file with metadata of dataset
    "generate_meta": True,
}

if __name__ == "__main__":
    gen = Generator(**args).run()
