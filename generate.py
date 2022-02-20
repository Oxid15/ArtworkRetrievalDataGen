import os
import sys
import argparse
import yaml

import bpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from utils import *


class Generator():
    def parse_images(self):
        self.img_names = os.listdir(self.src)

    def _parse_config(self, config_path):
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)

        # Required parameters
        if 'source_folder' in cfg:
            self.src = cfg['source_folder']
        else:
            raise KeyError('"source_folder" is not found in {config_path}')

        if 'destination_folder' in cfg:
            self.dest = cfg['destination_folder']
        else:
            raise KeyError('"destination_folder" is not found in {config_path}')

        # Not required parameters
        if 'camera_angles_range' in cfg:
            self.camera_angles_range = [[b for b in a] for a in cfg['camera_angles_range']]
        else:
            self.camera_angles_range = ((90, 0), (90, 0))
        
        if 'camera_distance_range' in cfg:
            self.camera_distance_range = cfg['camera_distance_range']
        else:
            self.camera_distance_range = (5, 5)
        
        if 'render_per_input' in cfg:
            self.render_per_input = cfg['render_per_input']
        else:
            self.render_per_input = 1

        self.parse_images()

    def __init__(self, config_path) -> None:
        self._parse_config(config_path)

    def _clear_scene(self):
        while(len(bpy.data.objects)):
            obj = bpy.data.objects[-1]
            obj.select = True
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
            view_align=True,
            enter_editmode=False,
            location=loc,
            rotation=((0., 0., 0.)))

        cam = bpy.data.objects['Camera']
        constraint = cam.constraints.new('TRACK_TO')
        constraint.target = self.image
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

    def _add_lights(self):
        bpy.ops.object.lamp_add(type='POINT', 
            radius=1, view_align=False, 
            location=(2, -2, 2))

    def _add_objects(self, img_name):
        bpy.ops.import_image.to_plane(
            files=[{"name": img_name}], 
            directory=self.src,
            filter_image=True, filter_movie=True, filter_glob="", relative=False,
            location=(0,0,0))
        name = img_name.split('.')[0]
        self.image = bpy.data.objects[name]
        self.image.rotation_euler[0] = deg2rad(90)
        self.image.rotation_euler[2] = deg2rad(90)
        
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, 
            location=(-0.01, 0, 0))
        plane = bpy.data.objects['Plane']
        plane.scale[0] = np.random.random() * 3 + 1
        plane.rotation_euler[0] = deg2rad(90)
        plane.rotation_euler[2] = deg2rad(90)

        bpy.ops.material.new()
        plane.data.materials.append(bpy.data.materials[0])
        plane.data.materials[0].diffuse_color = np.random.random(3)


    def _arrange_scene(self, img_name):
        self._clear_scene()
        self._add_lights()
        self._add_objects(img_name)
        self._add_camera()

    def _render(self, index, img_name):
        bpy.context.scene.camera = bpy.data.objects['Camera']

        base, ext = img_name.split(os.extsep)
        img_name = base + "_{0:0>5d}".format(index)
        '.'.join((img_name, ext))

        bpy.context.scene.render.filepath = os.path.join(self.dest, img_name)
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)

    def mainloop(self):
        for name in self.img_names:
            for i in range(self.render_per_input):
                self._arrange_scene(name)
                self._render(i, name)


argv = sys.argv[sys.argv.index('--') + 1:]
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cfg', type=str)
args = parser.parse_known_args(argv)[0]

if __name__ == '__main__':
    gen = Generator(args.cfg)
    gen.mainloop()
