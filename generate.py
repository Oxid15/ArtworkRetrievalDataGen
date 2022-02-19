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
        if 'camera_angles' in cfg:
            self.camera_angles = [deg2rad(a) for a in cfg['camera_angles']]
        else:
            self.camera_angles = (deg2rad(90), 0)
        
        if 'camera_distance' in cfg:
            self.camera_distance = cfg['camera_distance']
        else:
            self.camera_distance = 5

        self.parse_images()

    def __init__(self, config_path) -> None:
        self._parse_config(config_path)

    def _clear_scene(self):
        while(len(bpy.data.objects)):
            obj = bpy.data.objects[-1]
            obj.select = True
            bpy.ops.object.delete(use_global=False)

    def _add_camera(self):
        loc = spherical2cartesian(self.camera_angles, self.camera_distance)
        ang = self.camera_angles

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

    def _add_object(self, img_name):
        bpy.ops.import_image.to_plane(
            files=[{"name": img_name}], 
            directory=self.src,
            filter_image=True, filter_movie=True, filter_glob="", relative=False,
            location=(0,0,0))
        
        name = img_name.split('.')[0]
        self.image = bpy.data.objects[name]
        self.image.rotation_euler[0] = deg2rad(90)
        self.image.rotation_euler[2] = deg2rad(90)

    def _arrange_scene(self, img_name):
        self._clear_scene()
        self._add_lights()
        self._add_object(img_name)
        self._add_camera()

    def _render(self, img_name):
        bpy.context.scene.camera = bpy.data.objects['Camera']
        bpy.context.scene.render.filepath = os.path.join(self.dest, img_name)
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)

    def mainloop(self):
        for name in self.img_names:
            self._arrange_scene(name)
            self._render(name)


argv = sys.argv[sys.argv.index('--') + 1:]
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cfg', type=str)
args = parser.parse_known_args(argv)[0]

if __name__ == '__main__':
    gen = Generator(args.cfg)
    gen.mainloop()
