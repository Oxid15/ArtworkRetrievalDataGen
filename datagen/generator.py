import csv
import json
import logging
import os
from typing import Tuple, Union
from random import shuffle

import bpy

from .utils import *


class Generator:
    def __init__(
        self,
        src: str,
        dst: str,
        camera_angles_range_h: Tuple[float, float] = (0, 0),
        camera_angles_range_v: Tuple[float, float] = (90, 90),
        camera_distance_range: Tuple[float, float] = (5, 5),
        render_per_input: int = 1,
        max_images_to_render: Union[int, None] = None,
        generate_table: bool = False,
        generate_meta: bool = False,
        shuffle_input=False
    ) -> None:
        self.src = src
        self.dst = dst
        self.camera_angles_range_h = camera_angles_range_h
        self.camera_angles_range_v = camera_angles_range_v
        self.camera_distance_range = camera_distance_range
        self.render_per_input = render_per_input
        self.max_images_to_render = max_images_to_render
        self.generate_table = generate_table
        self.generate_meta = generate_meta
        self.shuffle_input = shuffle_input

        self.parse_images()

    def parse_images(self) -> None:
        self.img_names = sorted(os.listdir(self.src))
        if self.shuffle_input:
            shuffle(self.img_names)

    def _clear_scene(self) -> None:
        while len(bpy.data.objects):
            obj = bpy.data.objects[-1]

            obj.select_set(True)
            bpy.ops.object.delete(use_global=False)

        for img in bpy.data.images:
            bpy.data.images.remove(img)

    def _add_camera(self) -> None:
        v_min, v_max = self.camera_angles_range_v
        h_min, h_max = self.camera_angles_range_h
        v_ang = np.random.random() * (v_max - v_min) + v_min
        h_ang = np.random.random() * (h_max - h_min) + h_min

        d_max, d_min = self.camera_distance_range
        dist = np.random.random() * (d_max - d_min) + d_min

        loc = spherical2cartesian((deg2rad(v_ang), deg2rad(h_ang)), dist)

        bpy.ops.object.camera_add(
            align="VIEW",
            enter_editmode=False,
            location=loc,
            rotation=((0.0, 0.0, 0.0)),
        )

        cam = bpy.data.objects["Camera"]
        # constraint = cam.constraints.new(type="LIMIT_LOCATION")
        # constraint.use_min_z = True

        constraint = cam.constraints.new("TRACK_TO")
        constraint.target = self.image
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

    def _add_lights(self) -> None:
        bpy.ops.object.light_add(
            type="POINT", radius=1, align="VIEW", location=(2, -2, 2)
        )
        bpy.data.objects["Point"].data.energy = 1000

    def _add_objects(self, img_name: str) -> None:
        bpy.ops.import_image.to_plane(
            files=[{"name": img_name}],
            directory=self.src,
            filter_image=True,
            filter_movie=True,
            filter_folder=False,
            relative=False,
            location=(0, 0, 0),
        )
        name = img_name.split(".")[0]
        self.image = bpy.data.objects[name]
        self.image.rotation_euler[0] = deg2rad(90)
        self.image.rotation_euler[2] = deg2rad(90)

        # Wall
        bpy.ops.mesh.primitive_plane_add(
            size=1, align="VIEW", enter_editmode=False, location=(-0.01, 0, 0)
        )
        plane = bpy.data.objects["Plane"]
        plane.scale[0] = 1000
        plane.scale[1] = 1000
        plane.rotation_euler[0] = deg2rad(90)
        plane.rotation_euler[2] = deg2rad(90)

        bpy.ops.material.new()
        mat = bpy.data.materials["Material.001"]
        mat.name = "Wall-Material"
        bpy.data.materials["Wall-Material"].node_tree.nodes["Principled BSDF"].inputs[
            0
        ].default_value = np.random.random(4)
        plane.data.materials.append(bpy.data.materials["Wall-Material"])

        # Floor
        bpy.ops.mesh.primitive_plane_add(
            size=1, align="VIEW", enter_editmode=False, location=(0, 0, -1)
        )
        plane = bpy.data.objects["Plane.001"]
        plane.scale[0] = 100
        plane.scale[1] = 100

        bpy.ops.material.new()
        mat = bpy.data.materials["Material.001"]
        mat.name = "Floor-Material"
        bpy.data.materials["Floor-Material"].node_tree.nodes["Principled BSDF"].inputs[
            0
        ].default_value = np.random.random(4)
        plane.data.materials.append(bpy.data.materials["Floor-Material"])

    def _arrange_scene(self, img_name: str):
        self._clear_scene()
        self._add_lights()
        self._add_objects(img_name)
        self._add_camera()

    def _render(self, render_name: str):
        bpy.context.scene.camera = bpy.data.objects["Camera"]
        bpy.context.scene.render.filepath = os.path.join(
            self.dst, "images", render_name
        )
        bpy.context.scene.render.image_settings.file_format = "JPEG"
        bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)

    def _write_meta(self) -> None:
        meta = {
            "src": self.src,
            "dst": self.dst,
            "camera_angles_range_h": self.camera_angles_range_h,
            "camera_angles_range_v": self.camera_angles_range_v,
            "camera_distance_range": self.camera_distance_range,
            "render_per_input": self.render_per_input,
            "size": self.generated_count,
        }

        with open(os.path.join(self.dst, "meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

    def _rendering_loop(self, writer: Union[csv.DictWriter, None]) -> None:
        if writer:
            writer.writeheader()

        self.generated_count = 0
        for i, base_name in enumerate(self.img_names):
            name, _ = os.path.splitext(base_name)
            for j in range(self.render_per_input):
                render_name = f"{name}_{j:0>5d}.jpg"
                try:
                    self._arrange_scene(base_name)
                    self._render(render_name)
                except Exception as e:
                    logging.exception(f"Error with {i}: ", e)
                else:
                    if writer:
                        writer.writerow(
                            {"base_img": os.path.join(self.src, base_name), "query_img": os.path.join(self.dst, "images", render_name)}
                        )
                    self.generated_count += 1

                if (
                    self.max_images_to_render is not None
                    and self.generated_count >= self.max_images_to_render
                ):
                    logging.info("Finished at max images")
                    return

            logging.info(f"Generated images for {i + 1} inputs")

    def run(self) -> None:
        os.makedirs(os.path.join(self.dst, "images"))

        csv_file = None
        writer = None

        if self.generate_table:
            csv_file = open(os.path.join(self.dst, "map.csv"), "w")
            writer = csv.DictWriter(csv_file, ["base_img", "query_img"])

        logging.info("Starting generation process")
        try:
            self._rendering_loop(writer)
        except Exception as e:
            logging.exception(e)
            logging.info("Exception occured while rendering, stopping...")

            if csv_file:
                csv_file.close()
                logging.info("Map file closed")

        if self.generate_meta:
            logging.info("Writing meta")
            self._write_meta()

        logging.info("Done!")
