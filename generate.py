import os
import sys
import argparse
import yaml

import bpy


argv = sys.argv[sys.argv.index('--') + 1:]
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cfg', type=str)
args = parser.parse_known_args(argv)[0]

if __name__ == '__main__':
    with open(args.cfg, 'r') as f:
        cfg = yaml.safe_load(f)

    bpy.data.objects['Cube'].select = True
    bpy.ops.object.delete(use_global=False)

    # bpy.data.objects['Camera'].select = True

    bpy.ops.import_image.to_plane(
        files=[{"name":""}], 
        directory="", 
        filter_image=True, filter_movie=True, filter_glob="", relative=False)

    bpy.context.object.rotation_euler[0] = 1.5708
    bpy.context.object.location[0] = 0
    bpy.context.object.location[1] = 0
    bpy.context.object.location[2] = 0

    bpy.context.scene.render.filepath = cfg['destination_folder'] + '\\01.png'
    bpy.ops.render.render(write_still=True)
