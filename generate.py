import os
import sys
import argparse
import yaml

import bpy


class Generator():
    def _parse_config(self, config_path):
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        
        self.dest = cfg['destination_folder']


    def __init__(self, config_path) -> None:
        self._parse_config(config_path)

    def _arrange_scene(self):
        bpy.data.objects['Cube'].select = True
        bpy.ops.object.delete(use_global=False)

        # bpy.data.objects['Camera'].select = True
        # bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0.999982, -0.699609, 0.00561283), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

        bpy.ops.import_image.to_plane(
            files=[{"name":""}], 
            directory=r"", 
            filter_image=True, filter_movie=True, filter_glob="", relative=False)

        bpy.context.object.rotation_euler[0] = 1.5708
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = 0

    def _render(self):
        bpy.context.scene.render.filepath = self.dest + '\\01.png'
        bpy.ops.render.render(write_still=True)

    def mainloop(self):
        self._arrange_scene()
        self._render()


argv = sys.argv[sys.argv.index('--') + 1:]
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cfg', type=str)
args = parser.parse_known_args(argv)[0]

if __name__ == '__main__':
    gen = Generator(args.cfg)
    gen.mainloop()
