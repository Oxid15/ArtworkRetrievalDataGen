import os

# import sys

import bpy

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(SCRIPT_DIR)

from utils import *
from settings import (
    source_folder,
    destination_folder,
    camera_angles_range,
    camera_distance_range,
    render_per_input,
)


class Generator:
    def __init__(
        self,
        src,
        dest,
        camera_angles_range=((90, 0), (90, 0)),
        camera_distance_range=(5, 5),
        render_per_input=1,
    ) -> None:
        self.src = src
        self.dest = dest
        self.camera_angles_range = camera_angles_range
        self.camera_distance_range = camera_distance_range
        self.render_per_input = render_per_input

        self.parse_images()

    def parse_images(self):
        self.img_names = os.listdir(self.src)

    def _clear_scene(self):
        while len(bpy.data.objects):
            obj = bpy.data.objects[-1]
            obj.select_set(True)
            bpy.ops.object.delete(use_global=False)

    def _add_camera(self):
        ang = self.camera_angles_range
        first_min, first_max = ang[0][0], ang[1][0]
        second_min, second_max = ang[0][1], ang[1][1]
        first_ang = np.random.random() * (first_max - first_min) + first_min
        second_ang = np.random.random() * (second_max - second_min) + second_min

        d_max, d_min = self.camera_distance_range
        dist = np.random.random() * (d_max - d_min) + d_min

        loc = spherical2cartesian((deg2rad(first_ang), deg2rad(second_ang)), dist)

        bpy.ops.object.camera_add(
            align="VIEW",
            enter_editmode=False,
            location=loc,
            rotation=((0.0, 0.0, 0.0)),
        )

        cam = bpy.data.objects["Camera"]
        constraint = cam.constraints.new(type="LIMIT_LOCATION")
        constraint.use_min_z = True

        constraint = cam.constraints.new("TRACK_TO")
        # constraint.target = self.image
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

    def _add_lights(self):
        bpy.ops.object.light_add(
            type="POINT", radius=1, align="VIEW", location=(2, -2, 2)
        )

    def _add_objects(self, img_name):
        # bpy.ops.import_image.to_plane(
        #     files=[{"name": img_name}],
        #     directory=self.src,
        #     filter_image=True,
        #     filter_movie=True,
        #     filter_glob="",
        #     relative=False,
        #     location=(0, 0, 0),
        # )
        # name = img_name.split(".")[0]
        # self.image = bpy.data.objects[name]
        # self.image.rotation_euler[0] = deg2rad(90)
        # self.image.rotation_euler[2] = deg2rad(90)

        # Wall
        bpy.ops.mesh.primitive_plane_add(
            size=1, align="VIEW", enter_editmode=False, location=(-0.01, 0, 0)
        )
        plane = bpy.data.objects["Plane"]
        y_scale = np.random.random() * 3 + 1
        plane.scale[0] = y_scale
        plane.rotation_euler[0] = deg2rad(90)
        plane.rotation_euler[2] = deg2rad(90)

        bpy.ops.material.new()
        plane.data.materials.append(bpy.data.materials[0])
        plane.data.materials[0].diffuse_color = np.random.random(4)

        # Floor
        bpy.ops.mesh.primitive_plane_add(
            size=1, align="VIEW", enter_editmode=False, location=(0, 0, -0.7)
        )
        plane = bpy.data.objects["Plane.001"]
        plane.scale[0] = 10
        plane.scale[1] = 10

        bpy.ops.material.new()
        plane.data.materials.append(bpy.data.materials[1])
        plane.data.materials[0].diffuse_color = np.random.random(4)

    def _arrange_scene(self, img_name):
        self._clear_scene()
        self._add_lights()
        self._add_objects(img_name)
        self._add_camera()

    def _render(self, index, img_name):
        bpy.context.scene.camera = bpy.data.objects["Camera"]

        base, ext = img_name.split(os.extsep)
        img_name = base + "_{0:0>5d}".format(index)
        ".".join((img_name, ext))

        bpy.context.scene.render.filepath = os.path.join(self.dest, img_name)
        bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)

    def mainloop(self):
        for name in self.img_names:
            for i in range(self.render_per_input):
                self._arrange_scene(name)
                self._render(i, name)


if __name__ == "__main__":
    gen = Generator(
        src=source_folder,
        dest=destination_folder,
        camera_angles_range=camera_angles_range,
        camera_distance_range=camera_distance_range,
        render_per_input=render_per_input,
    )
    gen.mainloop()
