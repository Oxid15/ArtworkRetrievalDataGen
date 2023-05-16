import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from datagen import Generator
from settings import (
    source_folder,
    destination_folder,
    camera_angles_range,
    camera_distance_range,
    render_per_input,
)


if __name__ == "__main__":
    gen = Generator(
        src=source_folder,
        dest=destination_folder,
        camera_angles_range=camera_angles_range,
        camera_distance_range=camera_distance_range,
        render_per_input=render_per_input,
    )
    gen.mainloop()
